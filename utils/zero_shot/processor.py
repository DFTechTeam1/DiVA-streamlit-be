import os
import time
import base64
import hashlib
from PIL import Image
from io import BytesIO
from typing import Union
from utils.logger import logging


class ImageProcessor:
    def __init__(self, width: int = 255, height: int = 255):
        self.width = width
        self.height = height
        self.root_path = 'saved_images'

    def resize(self, paths: Union[str, list]):
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
        return processed

    def encode(self, image_path: str):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        with open(image_path, "rb") as f:
            image_bytes = f.read()
            encoded = base64.b64encode(image_bytes).decode("utf-8")
        return encoded

    def decode(self, encoded_data: str):
        return (
            Image.open(BytesIO(base64.b64decode(encoded_data)))
            .convert('RGB')
            .resize((self.width, self.height))
        )

    def save(self, decoded: Image, filename: str):
        save_dir = os.path.join(self.root_path)
        os.makedirs(save_dir, exist_ok=True)

        filename = f"{filename}.jpeg"
        filepath = os.path.join(save_dir, filename)

        decoded.save(filepath, 'JPEG')
        logging.info(f'Decoded image saved to: {filepath}')

    def hash(self, decoded: Image) -> str:
        with BytesIO() as buffer:
            decoded.save(buffer, format='JPEG')
            image_bytes = buffer.getvalue()
        
        md5_hash = hashlib.md5(image_bytes).hexdigest()
        logging.info(f"MD5 Hash: {md5_hash}")
        return md5_hash


