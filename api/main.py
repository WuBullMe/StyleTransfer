from fastapi import FastAPI
from fastapi import File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

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
        model_name: str=None,
        model_version: str=None,
        timeout_sec: int=5,
        image_size: int=256,
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
        logs=True,
    )
    result_image.save("assets/result.png")
    
    return FileResponse("assets/result.png")
