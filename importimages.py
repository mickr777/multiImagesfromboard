import zipfile
import os
from PIL import Image
from io import BytesIO
from typing import Optional, Union, List
from invokeai.invocation_api import (
    BaseInvocation,
    InvocationContext,
    invocation,
    InputField,
    ImageField,
    ImageOutput,
    ImageCollectionOutput,
)
from invokeai.app.invocations.fields import WithBoard
 
@invocation(
    "add_images_to_board",
    title="Add Images from ZIP or Folder to Board",
    tags=["image", "zip", "folder", "board"],
    category="image",
    version="0.4.0",
)
class ImagesToBoardInvocation(BaseInvocation, WithBoard):
    """Add images from a ZIP file or Folder to the Board"""

    zip_path: Optional[str] = InputField(default=None, description="Path to the ZIP file containing images")
    folder_path: Optional[str] = InputField(default=None, description="Path to the folder containing images")

    def process_image(self, image_input: Union[str, Image.Image], context: InvocationContext, output_images: List[ImageField]) -> None:
        try:
            if isinstance(image_input, str):
                with Image.open(image_input) as image:
                    image_output = self.save_image_to_board(image, context)
            else:
                image_output = self.save_image_to_board(image_input, context)
            
            output_images.append(ImageField(image_name=image_output.image.image_name))
        except Exception as e:
            print(f"Error processing {image_input}. Skipping. Error: {e}")
            import traceback
            traceback.print_exc()

    def save_image_to_board(self, image: Image.Image, context: InvocationContext) -> ImageOutput:
        """Save an image to the specified board."""
        try:
            image_dto = context.images.save(image=image)
            return ImageOutput.build(image_dto)
        except Exception as e:
            print(f"Error saving image to board. Error: {e}")
            import traceback
            traceback.print_exc()
            raise

    def invoke(self, context: InvocationContext) -> ImageCollectionOutput:
        output_images = []

        if self.folder_path:
            filepaths = [
                os.path.join(self.folder_path, file)
                for file in os.listdir(self.folder_path)
                if file.lower().endswith((".png", ".jpg"))
            ]
            sorted_filepaths = sorted(filepaths)
            for image_path in sorted_filepaths:
                print(f"Processing file: {os.path.basename(image_path)}")
                self.process_image(image_path, context, output_images)

        elif self.zip_path:
            with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                file_names = sorted(zip_ref.namelist())
                for file_name in file_names:
                    print(f"Extracting and processing entry: {file_name}")
                    try:
                        with zip_ref.open(file_name) as file:
                            with Image.open(BytesIO(file.read())) as image:
                                self.process_image(image, context, output_images)
                    except Exception as e:
                        print(f"Error extracting or processing {file_name}. Skipping. Error: {e}")
                        import traceback
                        traceback.print_exc()

        return ImageCollectionOutput(collection=output_images)
