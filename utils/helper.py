import os
from pathlib import Path
from utils.logger import logging
from typing import Optional
from pytz import timezone
from datetime import datetime


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
