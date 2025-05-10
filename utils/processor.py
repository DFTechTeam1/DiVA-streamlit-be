import os
import time
from PIL import Image
from typing import Optional, Union
from utils.logger import logging
from utils.helper import total_runtime


class ImageProcessor:
    def __init__(self, width: int = 255, height: int = 255):
        self.width = width
        self.height = height

    def resize(self, paths: Union[str, list]) -> Optional[list]:
        start_time = time.time()
        if isinstance(paths, str):
            logging.info(f'Processing single image: {paths}.')
            paths = [paths]
        else:
            logging.info(f'Processing multiple images: {len(paths)}.')
        processed = [
            Image.open(p).convert('RGB').resize((self.width, self.height))
            for p in paths
            if os.path.exists(p)
        ]
        if not processed:
            logging.warning('No images were processed. Check the paths.')
            return None
        total_runtime('resize', start_time)
        return processed
