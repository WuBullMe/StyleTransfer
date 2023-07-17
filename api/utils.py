import base64
import time
import uuid
import io
from PIL import Image
import os

# Parameters for the API
root = "assets/"
from_path = True
logs = True
autoremove_period = 1800 # how much an image can be stored locally in sec, 1800 = 30min
autoremove_check = 10 # check if you can remove images

def encode_to_base64(result_image):
    img_bytes_arr = io.BytesIO()
    result_image.save(img_bytes_arr, format='PNG')
    img_bytes_arr.seek(0)
    img_data = base64.b64encode(img_bytes_arr.read()).decode("utf-8")
    return img_data


def decode_from_base64(image: str, save=False):
    image = base64.b64decode(image.encode())
    image_id = get_new_id()
    image_name = os.path.join(root, image_id + ".png")
    
    if save:
        # read and save `image`
        with open(image_name, "wb") as f:
            f.write(image)
    
    image = Image.open(io.BytesIO(image))
    return image, image_id, image_name


def check_id(image_id: str):
    if not os.path.exists(os.path.join(root, image_id + ".png")):
        raise ValueError(f"Could not find the id {image_id}, it's incorrect or removed!")
    

def get_new_id():
    return str(uuid.uuid4()) + ":" + str(int(time.time()))

last_autoremove = 0
def clean():
    global last_autoremove
    cur_time = time.time()
    
    if cur_time - last_autoremove > autoremove_check:
        last_autoremove = cur_time
        autoremove_image()
    
    

# remove files from `root` which are stored more than `autoremove_period`
def autoremove_image():
    for file in os.listdir(root):
        if os.path.isfile(os.path.join(root, file)):
            id_time = file.split(':')
            if len(id_time) != 2:
                continue
            id_time = int(id_time[1].split('.')[0])
            
            if time.time() - id_time > autoremove_period:
                os.remove(os.path.join(root, file))
            