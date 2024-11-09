# Retrieve Images from Board for multi image input
![image](https://github.com/user-attachments/assets/9ede3e16-f17c-44c2-a4a1-af490ad30ba4)

(retrieveboardimages.py)

## Community Node For InvokeAI

## Description
Retrieves Images from any board and output them as a collection, to be used as a multi image input

For Number of Images
* Range of images Eg. `30-50`
* Group of single images Eg. `4,23,45` or a single image `567`
* `all` for all images

### Inputs
| Parameter     | Description                                 
|---------------|---------------------------------------------|
| `input_board`  | Input board containing images to be retrieved.|
| `num_images` | Number of images to retrieve from the end.|
| `category` | Category of images to retrieve; select either 'images' or 'assets'.|
| `starred_only` | Retrieve only starred images if set to True.|


# Upload bulk images from folder or zip to add to board (using save to gallery) or use in work flow (Alpha)
(importimages.py)

## Community Node For InvokeAI

### Inputs
| Parameter     | Description                                 
|---------------|---------------------------------------------|
| `board` | Pick Board to add output to.|
| `zip_path`  | Path to the ZIP file containing images.|
| `folder_path` | Path to the folder containing images.|

