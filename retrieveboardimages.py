import os
import zipfile
import json
from invokeai.app.invocations.baseinvocation import (
    BaseInvocation,
    InvocationContext,
    invocation,
    InputField,
)
from invokeai.app.invocations.primitives import (
    ImageField,
    ImageCollectionOutput,
    BoardField,
)
from pydantic import BaseModel


class ImageZipResult(BaseModel):
    message: str


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


@invocation(
    "Retrieve_Board_Images",
    title="Retrieve Images from Board",
    tags=["image", "board"],
    category="image",
    version="0.3.5",
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
    save_metadata: bool = InputField(
        description="Save metadata as JSON files for each image.", default=False
    )
    save_to_zip: bool = InputField(
        description="Save all retrieved images to a ZIP file.", default=False
    )
    save_location: str = InputField(
        description="Specify the save location for the ZIP file."
    )

    def get_metadata(self, image_name, context):
        metadata = context.services.image_records.get_metadata(image_name)

        if metadata:
            print(f"Metadata for image {image_name}: {metadata}")
        else:
            print(f"No metadata found for image {image_name}")

        return metadata

    def invoke(self, context: InvocationContext) -> ImageCollectionOutput:
        from invokeai.app.api.dependencies import ApiDependencies

        all_images_in_board = (
            context.services.board_images.get_all_board_image_names_for_board(
                self.input_board.board_id
            )
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
                    selected_images.extend(all_images_in_board[-end : -start + 1])
                elif segment.isdigit():
                    index = int(segment)

                    if len(segments) == 1:
                        selected_images.extend(all_images_in_board[-index:])
                    else:
                        selected_images.append(all_images_in_board[-index])

        if self.save_to_zip:
            if self.save_location:
                board_name = context.services.boards.get_dto(
                    self.input_board.board_id
                ).board_name
                save_path = os.path.join(self.save_location, f"{board_name}_images.zip")
            else:
                board_name = context.services.boards.get_dto(
                    self.input_board.board_id
                ).board_name
                save_path = os.path.join(SCRIPT_DIR, f"{board_name}_images.zip")

            with zipfile.ZipFile(save_path, "w") as zipf:
                for image_name in selected_images:
                    image_path = ApiDependencies.invoker.services.images.get_path(
                        image_name
                    )
                    zipf.write(image_path, os.path.basename(image_path))

                    if self.save_metadata:
                        metadata = context.services.image_records.get_metadata(
                            image_name
                        )

                        # Debug: Print the retrieved metadata
                        print(f"Metadata for image {image_name}: {metadata}")

                        if metadata:
                            metadata_json = metadata.model_dump_json(indent=4)

                            json_file_name = f"{image_name}.json"
                            with zipf.open(json_file_name, "w") as json_file:
                                json_file.write(metadata_json.encode("utf-8"))

            result_message = f"Your images are saved in {save_path}"
            if self.save_metadata:
                result_message += f" along with metadata files."

        else:
            result_message = ""

        output_images = [
            ImageField(image_name=image_name) for image_name in selected_images
        ]
        return ImageCollectionOutput(
            collection=output_images, zip_result=ImageZipResult(message=result_message)
        )
