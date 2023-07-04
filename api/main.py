from fastapi import FastAPI
from fastapi import File, UploadFile
from fastapi.responses import FileResponse

from PIL import Image
import io

import model
# from response import Response, Request

app = FastAPI()

@app.get("/")
def home():
    text = """Welcome to the StyleTransfer API"""
    return text


@app.post("/style_transfer")
async def style_transfer(
        content_image: UploadFile = File(...),
        style_image: UploadFile = File(...),
        model_name: str=None,
        model_version: str=None,
        timeout_sec: int=5,
        image_size:int=256,
    ):
    # read the uploaded images and save them
    content_image = Image.open(io.BytesIO(await content_image.read()))
    style_image = Image.open(io.BytesIO(await style_image.read()))
    content_image.save("content_image.png")
    style_image.save("style_image.png")
    
    result_image = Image.fromarray(model.style_transfer(
        content_image,  
        style_image,
        image_size,
        timeout_sec,
    ))
    # img_byte_arr = io.BytesIO()
    # result_image.save(img_byte_arr, format='PNG')
    # img_byte_arr = img_byte_arr.getvalue()
    result_image.save("result.png")
    
    return FileResponse("result.png")


# remove this
from pyngrok import ngrok
import nest_asyncio
import uvicorn

port = 8000

ngrok_tunnel = ngrok.connect(port)
print(f"Public URL: {ngrok_tunnel.public_url}")
nest_asyncio.apply()
uvicorn.run(app, port=port)
# remove this


# @app.post("/style_transfer")
# async def style_transfer(
#         content_image: UploadFile = File(...),
#         style_image: UploadFile = File(...),
#         model_name: str = None,
#         model_version: str = None
#     ):
#     # Read the uploaded files
#     content_image = Image.open(io.BytesIO(await content_image.read()))
#     style_image = Image.open(io.BytesIO(await style_image.read()))
    
#     # Perform style transfer or any other image processing using the provided model
#     result_image = content_image

#     import base64
#     from fastapi.responses import JSONResponse
#     # Convert the result image to bytes
#     img_byte_arr = io.BytesIO()
#     result_image.save(img_byte_arr, format='PNG')
#     img_byte_arr.seek(0)
#     img_data = base64.b64encode(img_byte_arr.read()).decode("utf-8")
    
#     # Prepare the response
#     response_data = {
#         "model_name": model_name,
#         "model_version": model_version,
#         "result_image": img_data,
#     }
    
#     return JSONResponse(content=response_data)