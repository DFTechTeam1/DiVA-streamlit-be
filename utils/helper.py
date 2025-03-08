import os
import io
from PIL import Image
from pathlib import Path
from utils.logger import logging
from typing import Optional
from pytz import timezone
from datetime import datetime
from fastapi.responses import StreamingResponse
from utils.error.custom_error import DataNotFoundError


class CustomHelper:
    def local_time(self, zone: str = "Asia/Jakarta") -> datetime:
        return datetime.now(timezone(zone)).replace(tzinfo=None)

    def find_image(self, directory: str) -> Optional[list]:
        if not os.path.exists(path=directory):
            logging.error(f"Directory {directory} not exist!")
            raise FileNotFoundError("Cannot find image into non-existing directory.")

        image_extensions = {".jpg", ".jpeg", ".png"}
        images = [
            str(path)
            for path in Path(directory).rglob("*")
            if path.suffix.lower() in image_extensions
        ]

        if not images:
            logging.error(f"No image data found in directory {directory}.")
            return None

        logging.info(f"Loaded {len(images)} images from {directory}.")
        return images

    def stream_image(self, file_path: str) -> StreamingResponse:
        if not os.path.exists(file_path):
            logging.error(f"Image file {file_path} does not exist!")
            raise DataNotFoundError(detail=f"Image file {file_path} not found.")

        try:
            with Image.open(file_path) as img:
                img_format = img.format
                img_buffer = io.BytesIO()
                img.save(img_buffer, format=img_format)
                img_buffer.seek(0)

            return StreamingResponse(
                img_buffer, media_type=f"image/{img_format.lower()}"
            )

        except Exception as e:
            logging.error(f"Error while processing image {file_path}: {e}")
            raise DataNotFoundError(detail=f"Error processing image {file_path}.")
