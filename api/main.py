from fastapi import FastAPI
from fastapi import File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from typing import Union

from PIL import Image
import io

import utils
import model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to limit origins to a specific list if necessary
    allow_credentials=True,
    allow_methods=["*"],  # Update this to limit HTTP methods if necessary
    allow_headers=["*"],  # Update this to limit headers if necessary
)


@app.get("/")
def home():
    text = """Welcome to the StyleTransfer API, I am alive btw."""
    return text


@app.post("/style_transfer")
async def style_transfer(
        content_image: str = File(...),
        style_image: str = File(...),
        image_height: int = 256,
        image_width: Union[int, None] = 256,
        timeout_sec: int = 5,
        epochs: int = 500,
        content_weight: Union[int, float] = 5e0,
        style_weight: Union[int, float] = 2e2,
        tv_weight: Union[int, float] = 1e-5,
        model_name: str = None,
    ):
    # decode the received images 
    try:
        content_image, content_image_id, content_name = utils.decode_from_base64(
            content_image,
            save=utils.from_path
        )

        style_image, style_image_id, style_name = utils.decode_from_base64(
            style_image,
            save=utils.from_path
        )
    except Exception as e:
        return {
            'status': 'failed',
            'msg': 'got exception while trying to read received images',
            'error': str(e),
        }
    
    image_size = (image_height, image_width)
    if image_width is None:
        image_size = (image_height, image_height)
    
    if utils.from_path:
        content_image = content_name
        style_image = style_name
    
    try:
        result_image, params = model.style_transfer(
            content_image=content_image,
            style_image=style_image,
            image_size=image_size,
            timeout_sec=timeout_sec,
            epochs=epochs,
            content_weight=content_weight,
            style_weight=style_weight,
            tv_weight=tv_weight,
            logs=utils.logs,
            from_path=utils.from_path,
        )
    except Exception as e:
        return {
            'status': 'failed',
            'msg': 'got some exception while trying to transfer style of the given image',
            'error': str(e),
        }
    
    # remove useless parameters from `params`
    params.pop('content_losses', None)
    params.pop('style_losses', None)
    params.pop('tv_losses', None)
    params.pop('logs', None)
    params.pop('from_path', None)
    
    
    # change some `params` to avoid `ValueError` exception, while trying to
    # call the `__dict__` for the object that is not json serializable
    params['device'] = params['device'].type
    
    return {
        'status': 'ok',
        'msg': 'successfuly transfered the style of the image',
        'error': 'none',
        'params': params,
        'content_id': content_image_id,
        'style_id': style_image_id,
        'image': utils.encode_to_base64(result_image),
    }
    

@app.post("/test_style_transfer")
async def test_style_transfer(
        parse_image: bool = True,
        content_image: UploadFile = File(...),
        style_image: UploadFile = File(...),
        image_height: int = 256,
        image_width: Union[int, None] = 256,
        timeout_sec: int = 5,
        epochs: int = 500,
        content_weight: Union[int, float] = 5e0,
        style_weight: Union[int, float] = 2e2,
        tv_weight: Union[int, float] = 1e-5,
        model_name: str = None,
    ):
    try:
        # read the uploaded images and save them
        content_image = Image.open(io.BytesIO(await content_image.read()))
        style_image = Image.open(io.BytesIO(await style_image.read()))
    except Exception as e:
        return {
            'status': 'failed',
            'msg': 'got exception while trying to read received images',
            'error': str(e),
        }
    result = await style_transfer(
        content_image=utils.encode_to_base64(content_image),
        style_image=utils.encode_to_base64(style_image),
        image_height=image_height,
        image_width=image_width,
        timeout_sec=timeout_sec,
        epochs=epochs,
        content_weight=content_weight,
        style_weight=style_weight,
        tv_weight=tv_weight,
        model_name=model_name,
    )
    
    if result['status'] != 'ok' or parse_image is False:
        return result
    
    _, _, image_name = utils.decode_from_base64(
        result["image"],
        save=True
    )
    
    return FileResponse(image_name)
