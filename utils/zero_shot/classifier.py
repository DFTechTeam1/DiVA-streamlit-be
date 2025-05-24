import os
import re
import sys
import asyncio
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from pathlib import Path
from typing import Union

sys.path.append(str(Path(__file__).resolve().parents[2]))
from services.postgre.models import ImageMetadata
from services.postgre.connection import get_db
from utils.database.query import QueryDatabase
from utils.vector.faiss import FAISS
from utils.json import JSON
from utils.logger import logging
from utils.helper import formatter


class ZeroShotClassifier:
    def __init__(self, model_name: str = "laion/CLIP-ViT-H-14-laion2B-s32B-b79K") -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model = CLIPModel.from_pretrained(model_name,).to(self.device).eval()
        self.model.half()
        logging.info(f"Model {model_name} loaded to {self.device} in half precision.")
    
    def extract_feature(self, image: Union[Image, str], image_size: tuple[int, int] = (224, 224)):
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")

        image = image.resize(image_size)
        input = self.processor(images=image, return_tensors="pt")
        input = {k: v.to(self.device).half() for k, v in input.items()}

        with torch.no_grad():
            output = self.model.get_image_features(**input)
        return output.squeeze().cpu().numpy()

class VectorDatabase:
    @staticmethod
    def create(base_path: str, filename: str):
        return os.path.join(base_path, filename)
    
    @staticmethod
    def total_vector(base_path: str):
        numbers = []
        for filename in os.listdir(base_path):
            match = re.search(r'\d+', filename)
            if match:
                numbers.append(int(match.group()))
        
        return max(numbers) if numbers else 0

    @staticmethod
    def load(base_path: str, total_image: int):
        matched_files = [
            os.path.join(base_path, filename)
            for filename in os.listdir(base_path)
            if str(total_image) in filename
        ]

        metadata_path = next((f for f in matched_files if f.endswith(".pkl")), None)
        index_path = next((f for f in matched_files if f.endswith(".faiss")), None)
        return index_path, metadata_path


MODEL = ZeroShotClassifier()
FAISS_IDX = FAISS()

PROJECT_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = os.path.join(PROJECT_DIR, "models")
MOUNT_PATH = os.path.join(PROJECT_DIR, "mount")

PREVIEW_PATH = os.path.join(PROJECT_DIR, "json", "client_preview.json")
TOTAL_SAVED_VECTOR = VectorDatabase.total_vector(MODEL_PATH)

CLIENT_PREVIEW = JSON.load_json(PREVIEW_PATH)["paths"]

TOTAL_IMAGE = len(CLIENT_PREVIEW)

async def main():

    if TOTAL_IMAGE > TOTAL_SAVED_VECTOR:
        logging.info(f"Creating new FAISS index for {TOTAL_IMAGE} images.")

        embeddings = [MODEL.extract_feature(path) for path in CLIENT_PREVIEW]

        INDEX_PATH = VectorDatabase.create(MODEL_PATH, f"index_{TOTAL_IMAGE}.faiss")
        METADATA_PATH = VectorDatabase.create(MODEL_PATH, f"image_paths_{TOTAL_IMAGE}.pkl")

        logging.info(f"Formatting client preview path into relative path.")
        
        FAISS_IDX.add_embedding(embeddings, CLIENT_PREVIEW)
        FAISS_IDX.save(INDEX_PATH, METADATA_PATH)

        formatted_json = [formatter(entry) for entry in CLIENT_PREVIEW]

        async for session in get_db():
            db = QueryDatabase(session=session)
            try:
                await db.truncate(ImageMetadata)
                for entry in formatted_json:
                    await db.insert(ImageMetadata, entry)
            except Exception as e:
                logging.error(f'Failed to insert record: {e}')
    else:
        INDEX_PATH, METADATA_PATH = VectorDatabase.load(MODEL_PATH, TOTAL_IMAGE)
        logging.info(f"Loading existing FAISS index from {INDEX_PATH} and metadata from {METADATA_PATH}")
        FAISS_IDX.load(INDEX_PATH, METADATA_PATH)
        logging.info("Number of items in FAISS index:", FAISS_IDX.index.ntotal)

    return FAISS_IDX

if __name__ == "__main__":
    asyncio.run(main())