# Retrieve Images from Board for multi image input
## Community Node For InvokeAI

![image](https://github.com/mickr777/multiImagesfromboard/assets/115216705/860e2822-6b0a-4a11-ac44-652f66bd5169)

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
| `save_metadata` | Save metadata as JSON files for each image.|
| `save_to_zip` | Saves all retrieved images to a zip file.|
