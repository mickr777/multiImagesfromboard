from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from invokeai.invocation_api import (
    BaseInvocation,
    InvocationContext,
    invocation,
    InputField,
    ImageField,
    ImageCollectionOutput,
    WithMetadata,
)
from invokeai.app.services.image_records.image_records_common import ImageCategory
from invokeai.app.services.shared.sqlite.sqlite_common import SQLiteDirection


class BoardField(BaseModel):
    """A board primitive field."""

    board_id: Optional[str] = Field(default=None, description="The id of the board.")


@invocation(
    "Retrieve_Board_Images",
    title="Retrieve Images from Board",
    tags=["image", "board"],
    category="image",
    version="0.6.6",
    use_cache=False,
)
class RetrieveBoardImagesInvocation(BaseInvocation, WithMetadata):
    input_board: Optional[BoardField] = InputField(
        default=None,
        description="Input board containing images to be retrieved. If not provided or set to None, will will grab images from uncategorized.",
    )
    num_images: str = InputField(
        description="Number of images to retrieve: specify 'all', a single index like '10', specific indices like '1,4,6', or a range like '30-50'.",
        default="all",
    )
    category: Literal["images", "assets"] = InputField(
        description="Category of images to retrieve; select either 'images' or 'assets'.",
        default="images",
    )
    starred_only: bool = InputField(
        description="Retrieve only starred images if set to True.",
        default=False,
    )
    keyword: Optional[str] = InputField(
        description="Keyword to filter images by metadata. Only images with metadata containing this keyword will be retrieved.",
        default=None,
    )

    def invoke(self, context: InvocationContext) -> ImageCollectionOutput:
        if self.category == "images":
            category_enum = ImageCategory.GENERAL
        else:
            category_enum = ImageCategory.USER

        image_records = context._services.image_records
        if not image_records:
            raise ValueError("Image records service is unavailable.")

        board_id = (
            self.input_board.board_id
            if self.input_board and self.input_board.board_id
            else "none"
        )

        image_results = image_records.get_many(
            board_id=board_id,
            categories=[category_enum],
            order_dir=SQLiteDirection.Descending,
            limit=-1,
            offset=0,
            search_term=self.keyword,
        )

        selected_images = self.select_images(image_results.items)

        if not selected_images:
            return ImageCollectionOutput(collection=[])

        output_images = [
            ImageField(image_name=image_name) for image_name in selected_images
        ]
        return ImageCollectionOutput(collection=output_images)

    def select_images(self, image_results: List) -> List[str]:
        """Helper method to filter and select images based on num_images and starred_only."""
        all_images_in_board = [
            record.image_name
            for record in image_results
            if not self.starred_only or record.starred
        ]

        if not all_images_in_board:
            return []

        selected_images = []

        if self.num_images.lower() == "all":
            selected_images = all_images_in_board
        else:
            segments = self.num_images.split(",")
            for segment in segments:
                if "-" in segment:
                    start, end = map(int, segment.split("-"))
                    if start > end:
                        raise ValueError(
                            f"Invalid range '{segment}': start cannot be greater than end."
                        )
                    selected_images.extend(all_images_in_board[start - 1 : end])
                elif segment.isdigit():
                    index = int(segment)
                    if 1 <= index <= len(all_images_in_board):
                        selected_images.append(all_images_in_board[index - 1])
                    else:
                        raise ValueError(
                            f"Invalid index '{index}': choose between 1 and {len(all_images_in_board)}."
                        )

        return selected_images
