import zipfile
import os
import json
from PIL import Image
from io import BytesIO
from typing import Optional, Union, List
from invokeai.app.invocations.baseinvocation import (
    BaseInvocation,
    Input,
    InvocationContext,
    invocation,
    InputField,
)
from invokeai.app.invocations.primitives import ImageField, ImageOutput, BoardField, ImageCollectionOutput
from invokeai.app.services.image_records.image_records_common import ImageCategory, ResourceOrigin

@invocation(
    "add_images_to_board",
    title="Add Images from ZIP or Folder to Board",
    tags=["image", "zip", "folder", "board"],
    category="image",
    version="0.3.5",
)
class ImagesToBoardInvocation(BaseInvocation):
    """Add images from a ZIP file or Folder to the Board"""

    zip_path: Optional[str] = InputField(default=None, description="Path to the ZIP file containing images")
    folder_path: Optional[str] = InputField(default=None, description="Path to the folder containing images")
    board: Optional[BoardField] = InputField(
        default=None, description="Pick Board to add output to", input=Input.Direct
    )

    def process_image(self, image_input: Union[str, Image.Image], context: InvocationContext, file_number: int, total_files: int, output_images: List[ImageOutput]) -> None:
        try:
            if isinstance(image_input, str):
                with Image.open(image_input) as image:
                    image_output = self.save_image_to_board(image, context, file_number, total_files)
            else:
                image_output = self.save_image_to_board(image_input, context, file_number, total_files)
            output_images.append(ImageField(image_name=image_output.image.image_name))
        except Exception as e:
            print(f"Error processing {image_input}. Skipping. Error: {e}")

    def save_image_to_board(self, image: Image.Image, context: InvocationContext, file_number: int, total_files: int) -> ImageOutput:
        """Save an image to the specified board."""
        extracted_metadata = image.info

        for key, value in extracted_metadata.items():
            if isinstance(value, str):
                try:
                    extracted_metadata[key] = json.loads(value)
                except json.JSONDecodeError:
                    pass

        image_dto = context.services.images.create(
            image=image,
            image_origin=ResourceOrigin.INTERNAL,
            image_category=ImageCategory.GENERAL,
            board_id=self.board.board_id if self.board else None,
            node_id=self.id,
            session_id=context.graph_execution_state_id,
            is_intermediate=self.is_intermediate,
        )

        return ImageOutput(
            image=ImageField(image_name=image_dto.image_name),
            width=image_dto.width,
            height=image_dto.height,
            file_number=file_number,
            total_files=total_files,
        )

    def invoke(self, context: InvocationContext) -> ImageCollectionOutput:
        output_images = []

        if self.folder_path:
            filepaths = [
                os.path.join(self.folder_path, file)
                for file in os.listdir(self.folder_path)
                if file.lower().endswith((".png", ".jpg"))
            ]
            sorted_filepaths = sorted(filepaths)
            total_files = len(sorted_filepaths)
            for file_number, image_path in enumerate(sorted_filepaths, 1):
                print(f"Processing file {file_number} of {total_files}: {os.path.basename(image_path)}")
                self.process_image(image_path, context, file_number, total_files, output_images)

        elif self.zip_path:
            with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                file_names = sorted(zip_ref.namelist())
                total_files = len(file_names)
                for file_number, file_name in enumerate(file_names, 1):
                    print(f"Extracting and processing entry {file_number} of {total_files}: {file_name}")
                    try:
                        with zip_ref.open(file_name) as file:
                            with Image.open(BytesIO(file.read())) as image:
                                self.process_image(image, context, file_number, total_files, output_images)
                    except Exception as e:
                        print(f"Error extracting or processing {file_name}. Skipping. Error: {e}")

        return ImageCollectionOutput(collection=output_images)
