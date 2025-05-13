import os
import time
import base64
from PIL import Image
from io import BytesIO
from typing import Optional, Union
from utils.logger import logging
from utils.helper import total_runtime, local_time


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

    def encode(self, image_path: str) -> str:
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read())

    def decode(self, encoded_data: str) -> str:
        root_path = 'temp'
        sub_dir = 'saved_images'

        full_path = os.path.join(root_path, sub_dir)
        os.makedirs(full_path, exist_ok=True)
        image = Image.open(BytesIO(base64.b64decode(encoded_data))).convert('RGB')
        filepath = f'{full_path}/{local_time().strftime("%Y%m%d%H%M")}.jpeg'
        image.save(filepath, 'JPEG')

        return filepath
