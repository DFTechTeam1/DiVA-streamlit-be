import os
import mimetypes
from pathlib import Path
from utils.logger import logging
from typing import Optional
from pytz import timezone
from datetime import datetime
from fastapi import Response
from fastapi.responses import StreamingResponse


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

    def format_path(self, filtered_image: list, prefix_path: str) -> list:
        return [prefix_path + entry["filepath"] for entry in filtered_image]

    def stream_image(self, file_path: str) -> StreamingResponse:
        """Streams an image from a local file path."""
        image_path = Path(file_path)

        if not image_path.exists():
            return Response(content="File not found", status_code=404)

        # Guess MIME type (default to 'image/jpeg' if unknown)
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type if mime_type else "image/jpeg"

        def iterfile():
            with open(image_path, "rb") as image_file:
                yield from image_file

        return StreamingResponse(iterfile(), media_type=mime_type)
