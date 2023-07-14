import base64
import time
import uuid
import io

# Parameters for the API
root = "assets/"

def encode_to_base64(result_image):
    img_bytes_arr = io.BytesIO()
    result_image.save(img_bytes_arr, format='PNG')
    img_bytes_arr.seek(0)
    img_data = base64.b64encode(img_bytes_arr.read()).decode("utf-8")
    return img_data


def decode_from_base64(image: str, save=False):
    image = base64.b64decode(image.encode())
    image_id = get_new_id()
    image_name = root + image_id + ".png"
    
    if save:
        # read and save `image`
        with open(image_name, "wb") as f:
            f.write(image)
    
    return image, image_id, image_name


def get_new_id():
    return str(uuid.uuid4()) + ":" + str(int(time.time()))