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
        self.root_path = 'temp'
        self.sub_dir = 'saved_images'
        self.encoded_dir = 'encoded'
        self.decoded_dir = 'decoded'
        self.new_image = 'new_image'

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
        save_dir = os.path.join(self.root_path, self.sub_dir, self.encoded_dir)
        os.makedirs(save_dir, exist_ok=True)

        images = self.resize(image_path)
        if not images:
            raise ValueError(f'Image not found or failed to resize: {image_path}')

        resized_img = images[0]
        filename = f'{local_time().strftime("%Y%m%d%H%M")}.jpeg'
        filepath = os.path.join(save_dir, filename)
        resized_img.save(filepath, 'JPEG')

        with open(filepath, 'rb') as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
        logging.info(f'Encoded image saved to: {filepath}')
        return encoded

    def decode(self, encoded_data: str) -> Image:
        save_dir = os.path.join(self.root_path, self.sub_dir, self.decoded_dir)
        os.makedirs(save_dir, exist_ok=True)

        image = (
            Image.open(BytesIO(base64.b64decode(encoded_data)))
            .convert('RGB')
            .resize((self.width, self.height))
        )
        filename = f'{local_time().strftime("%Y%m%d%H%M")}.jpeg'
        filepath = os.path.join(save_dir, filename)
        image.save(filepath, 'JPEG')

        logging.info(f'Decoded image saved to: {filepath}')
        return image

    def save_image(self, encoded_data: str, filename: str) -> None:
        save_dir = os.path.join(self.root_path, self.sub_dir, self.new_image)
        os.makedirs(save_dir, exist_ok=True)

        image = Image.open(BytesIO(base64.b64decode(encoded_data))).convert('RGB')
        filepath = os.path.join(save_dir, filename)

        image.save(filepath, 'JPEG')
        logging.info(f'Decoded image saved to: {filepath}')
        return None
