import aiofiles
from utils.logger import logging
from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

router = APIRouter(tags=['Query'], prefix='/query')

CHUNK_SIZE = 16 * 256


async def stream(image_path: str):
    async def file_iterator():
        try:
            async with aiofiles.open(image_path, mode='rb') as f:
                while chunk := await f.read(CHUNK_SIZE):
                    yield chunk
        except Exception as e:
            logging.info(f'Error streaming {image_path}: {str(e)}')

    return StreamingResponse(file_iterator(), media_type='image/jpeg')


router.add_api_route(
    methods=['GET'],
    path='/stream',
    endpoint=stream,
    status_code=status.HTTP_200_OK,
)
