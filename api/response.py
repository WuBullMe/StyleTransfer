from pydantic import BaseModel
from typing import Optional
from fastapi import File, UploadFile
from fastapi.responses import FileResponse

class Request(BaseModel):
    content_image: UploadFile = File(...)
    style_image: UploadFile = File(...)
    model_name: Optional[str] = None
    model_version: Optional[str] = None


class Response(BaseModel):
    status: str
    message: str
    # result_image: UploadFile
    model_version: Optional[str] = None
    model_name: Optional[str] = None
    