# Retrieve Images from Board for multi image input or to save board to zip
(retrieveboardimages.py)

## Community Node For InvokeAI

![image](https://github.com/mickr777/multiImagesfromboard/assets/115216705/ebf8bbfb-e35e-4f1a-8172-8564b8fdbbd9)

## Description
Retrieves Images from any board and output them as a collection, to be used as a multi image input

For Number of Images
* Range of images Eg. `30-50` or `45-50, 68-78`
* Group of single images Eg. `4,23,45` or a single image `567,`
* Single number without the `,` Eg. `35` will give you last 35 images
* `all` for all images

### Inputs
| Parameter     | Description                                 
|---------------|---------------------------------------------|
| `input_board`  | Input board containing images to be retrieved.|
| `num_images` | Number of images to retrieve from the end.|
| `save_metadata` | Save metadata as JSON files for each image if available.|
| `save_to_zip` | Saves all retrieved images to a zip file.|
| `save_location` | Specify the save location for the ZIP file.|


# Upload bulk images from folder or zip to add to board (using save to gallery) or use in work flow (Alpha)
(importimages.py)

## Community Node For InvokeAI

![image](https://github.com/mickr777/multiImagesfromboard/assets/115216705/93a7f50b-cbf8-49e5-b8da-8f0ab6e235bf)


### Inputs
| Parameter     | Description                                 
|---------------|---------------------------------------------|
| `zip_path`  | Path to the ZIP file containing images.|
| `folder_path` | Path to the folder containing images.|
| `board` | Pick Board to add output to.|
