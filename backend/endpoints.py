from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Annotated
from pathlib import Path
from PIL import Image
import imghdr

app = FastAPI()

@app.get("/analyze")
async def analyze(
    image: UploadFile
):
    # Check if the file is an image
    content_type = image.content_type
    if content_type is None or content_type not in ("image/jpeg", "image/jpg", "image/png"):
        return JSONResponse(
            status_code=400,
            content={"message": "No content type"},
        )



    return None
