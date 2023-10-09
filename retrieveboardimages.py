from invokeai.app.invocations.baseinvocation import BaseInvocation, Input, InvocationContext, invocation, InputField
from invokeai.app.invocations.primitives import ImageField, ImageCollectionOutput, BoardField
import zipfile
import os
from pydantic import BaseModel
from typing import List, Optional

class ImageZipResult(BaseModel):
    message: str

@invocation(
    "Retrieve_Board_Images",
    title="Retrieve Images from Board",
    tags=["image", "board"],
    category="image",
    version="0.0.6",
    use_cache=False,
)
class RetrieveBoardImagesInvocation(BaseInvocation):
    """Retrieve specified range or last n images from a board or all images if specified as 'all'"""

    input_board: BoardField = InputField(description="Input board containing images to be retrieved")

    num_images: str = InputField(
        description="Number of images to retrieve from the end, a range like '30-50', or 'all' for all images.",
        default="all",
    )
    save_to_zip: bool = InputField(
        description="Save all retrieved images to a ZIP file.",
        default=False
    )

    def invoke(self, context: InvocationContext) -> ImageCollectionOutput:
        all_images_in_board = context.services.board_images.get_all_board_image_names_for_board(
            self.input_board.board_id
        )
        from invokeai.app.api.dependencies import ApiDependencies

        selected_images = []

        if self.num_images.lower() == "all":
            selected_images = all_images_in_board
        else:
            segments = self.num_images.split(",")
            for segment in segments:
                if "-" in segment:
                    start, end = map(int, segment.split("-"))
                    selected_images.extend(all_images_in_board[-end : -start + 1])
                elif segment.isdigit():
                    index = int(segment)

                    if len(segments) == 1:
                        selected_images.extend(all_images_in_board[-index:])
                    else:
                        selected_images.append(all_images_in_board[-index])

        if self.save_to_zip:
            zip_file_name = "board_images.zip"
            with zipfile.ZipFile(zip_file_name, 'w') as zipf:
                for image_name in selected_images:
                    image_path = ApiDependencies.invoker.services.images.get_path(image_name)
                    zipf.write(image_path, os.path.basename(image_path))
            
            result_message = f"Your images are saved in {zip_file_name}"
        else:
            result_message = ""

        output_images = [ImageField(image_name=image_name) for image_name in selected_images]
        return ImageCollectionOutput(collection=output_images, zip_result=ImageZipResult(message=result_message))
