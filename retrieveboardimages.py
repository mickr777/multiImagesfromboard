from typing import Literal
from invokeai.invocation_api import (
    BaseInvocation,
    InvocationContext,
    invocation,
    InputField,
    ImageField,
    ImageCollectionOutput,
    BoardField,
)
from invokeai.app.services.image_records.image_records_common import ImageCategory
from invokeai.app.services.shared.sqlite.sqlite_common import SQLiteDirection


@invocation(
    "Retrieve_Board_Images",
    title="Retrieve Images from Board",
    tags=["image", "board"],
    category="image",
    version="0.5.0",
    use_cache=False,
)
class RetrieveBoardImagesInvocation(BaseInvocation):
    input_board: BoardField = InputField(
        description="Input board containing images to be retrieved"
    )
    num_images: str = InputField(
        description="Number of images to retrieve: can specify a range like '30-50', specific indices like '1,4,6', a single index like '10', or 'all' for all images.",
        default="all",
    )
    category: Literal["images", "assets"] = InputField(
        description="Category of images to retrieve; select either 'images' or 'assets'",
        default="images",
    )

    def invoke(self, context: InvocationContext) -> ImageCollectionOutput:
        if self.category == "images":
            category_enum = ImageCategory.GENERAL
        elif self.category == "assets":
            category_enum = ImageCategory.USER

        image_records = context._services.image_records
        if not image_records:
            raise ValueError("Image records service is not available.")

        image_results = image_records.get_many(
            board_id=self.input_board.board_id,
            categories=[category_enum],
            order_dir=SQLiteDirection.Descending,
        )

        all_images_in_board = [record.image_name for record in image_results.items]
        if not all_images_in_board:
            raise ValueError("No images found for the specified board and category.")

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
                            f"Invalid range: {segment}. Start cannot be greater than end."
                        )
                    selected_images.extend(all_images_in_board[start - 1 : end])
                elif segment.isdigit():
                    index = int(segment)
                    if 1 <= index <= len(all_images_in_board):
                        selected_images.append(all_images_in_board[index - 1])
                    else:
                        raise ValueError(
                            f"Invalid index {index}. Please select an index between 1 and {len(all_images_in_board)}. "
                            f"There are only {len(all_images_in_board)} images available in the selected board."
                        )

        output_images = [
            ImageField(image_name=image_name) for image_name in selected_images
        ]
        return ImageCollectionOutput(collection=output_images)
