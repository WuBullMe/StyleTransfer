from fastapi import FastAPI
from fastapi import File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from typing import Union, Optional, List, Tuple

from PIL import Image
import io

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
    text = """Welcome to the StyleTransfer API"""
    return text


@app.post("/style_transfer")
async def style_transfer(
        content_image: UploadFile = File(...),
        style_image: UploadFile = File(...),
        image_size: Union[int, List, Tuple] = 256,
        timeout_sec: int = 5,
        epochs: int = 500,
        content_weight: Union[int, float] = 5e0,
        style_weight: Union[int, float] = 2e2,
        tv_weight: Union[int, float] = 1e-5,
        content_layers: Union[List, Tuple] = ('relu4_2'),
        style_layers: Union[List, Tuple] = ('relu1_1', 'relu2_1', 'relu3_1', 'relu4_1', 'relu5_1'),
        model_name: str = None,
        model_version: str = None,
    ):
    # read the uploaded images and save them
    content_image = Image.open(io.BytesIO(await content_image.read()))
    style_image = Image.open(io.BytesIO(await style_image.read()))
    content_image.save("assets/content_image.png")
    style_image.save("assets/style_image.png")
    
    result_image, _ = model.style_transfer(
        content_image_path="assets/content_image.png",
        style_image_path="assets/style_image.png",
        image_size=image_size,
        timeout_sec=timeout_sec,
        epochs=epochs,
        content_weight=content_weight,
        style_weight=style_weight,
        tv_weight=tv_weight,
        content_layers=content_layers,
        style_layers=style_layers,
        logs=True,
        from_path=True,
    )
    result_image.save("assets/result.png")
    
    return FileResponse("assets/result.png")
