import base64
from PIL import Image
from io import BytesIO
from typing import Union
from typing import Optional
from utils.logger import logging
from concurrent.futures import ThreadPoolExecutor


class ImageProcessing:
    def open_image(self, image_path: str) -> Image:
        logging.info(f"Opening image: {image_path}")
        image = Image.open(image_path).convert("RGB")
        return self.resize_image(image=image)

    def resize_image(self, image: Image, image_size: tuple = (255, 255)) -> Image:
        return image.resize(image_size)

    def process_single_image(self, image_path: str) -> Image:
        image = self.open_image(image_path)
        return self.resize_image(image)

    def process_image(
        self, image_paths: Union[str, list], workers: Optional[int] = 10
    ) -> Union[Image, list[Image]]:
        if isinstance(image_paths, str):
            return self.process_single_image(image_paths)

        logging.info(f"Processing {len(image_paths)} images with {workers} workers.")
        with ThreadPoolExecutor(max_workers=workers) as executor:
            resized_images = list(executor.map(self.process_single_image, image_paths))
        logging.info("Resizing process completed.")
        return resized_images

    def decode_image(self, encoded_image: str) -> type[Image]:
        logging.info("Start decoding image.")
        image_data = base64.b64decode(encoded_image)
        with BytesIO(image_data) as image_stream:
            image = Image.open(image_stream).convert("RGB")
        logging.info("Decoding image completed.")
        return self.resize_image(image)
