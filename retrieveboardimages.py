import os
from invokeai.invocation_api import (
    BaseInvocation,
    InvocationContext,
    invocation,
    InputField,
    ImageField,
    ImageCollectionOutput,
    BoardField,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

@invocation(
    "Retrieve_Board_Images",
    title="Retrieve Images from Board",
    tags=["image", "board"],
    category="image",
    version="0.4.0",
    use_cache=False,
)
class RetrieveBoardImagesInvocation(BaseInvocation):
    input_board: BoardField = InputField(
        description="Input board containing images to be retrieved"
    )
    num_images: str = InputField(
        description="Number of images to retrieve from the end, a range like '30-50', or 'all' for all images.",
        default="all",
    )

    def get_metadata(self, image_name, context):
        metadata = context.images.get_metadata(image_name)

        if metadata:
            print(f"Metadata for image {image_name}: {metadata}")
        else:
            print(f"No metadata found for image {image_name}")

        return metadata

    def invoke(self, context: InvocationContext) -> ImageCollectionOutput:
        all_images_in_board = context.boards.get_all_image_names_for_board(
            self.input_board.board_id
        )

        if not all_images_in_board:
            raise ValueError("No images found for the specified board.")

        selected_images = []

        if self.num_images.lower() == "all":
            selected_images = all_images_in_board
        else:
            segments = self.num_images.split(",")
            for segment in segments:
                if "-" in segment:
                    start, end = map(int, segment.split("-"))
                    selected_images.extend(all_images_in_board[-end:])
                elif segment.isdigit():
                    index = int(segment)
                    if len(segments) == 1:
                        selected_images.extend(all_images_in_board[-index:])
                    else:
                        selected_images.append(all_images_in_board[-index])

        output_images = [
            ImageField(image_name=image_name) for image_name in selected_images
        ]
        return ImageCollectionOutput(
            collection=output_images
        )
