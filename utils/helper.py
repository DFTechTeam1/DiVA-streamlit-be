import os
from pathlib import Path
from utils.logger import logging
from typing import Optional
from pytz import timezone
from datetime import datetime


class CustomHelper:
    def local_time(self, zone: str = "Asia/Jakarta") -> datetime:
        return datetime.now(timezone(zone)).replace(tzinfo=None)

    def find_image(self, directory: str, **kwargs) -> Optional[list]:
        if not os.path.exists(path=directory):
            logging.error(f"Directory {directory} not exist!")
            raise FileNotFoundError("Cannot find image into non-existing directory.")

        default_extensions = {"jpg": True, "jpeg": True, "png": True}
        default_extensions.update(kwargs)

        extensions = {
            f".{ext}" for ext, enabled in default_extensions.items() if enabled
        }
        try:
            images = [
                str(path)
                for path in Path(directory).rglob("*")
                if path.suffix.lower() in extensions
            ]

            if not images:
                logging.error(f"No image data found in directory {directory}.")
                return None

            return images
        except Exception as e:
            logging.info(f"Error occured when finding an images {e}.")
            return None
