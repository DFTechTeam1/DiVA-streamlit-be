from fastapi import APIRouter, Query
from utils.helper import CustomHelper

router = APIRouter(tags=["Query"], prefix="/query")
helper = CustomHelper()


@router.get("/stream-image")
async def stream_image(
    image_path: str = Query(..., description="Full path of the image to stream"),
):
    return helper.stream_image(file_path=image_path)
