import torch
import time
from typing import Union
from PIL import Image
from torch import Tensor
from utils.helper import total_runtime
from utils.logger import logging
from sentence_transformers import SentenceTransformer, util


class CLIP:
    def __init__(self):
        self.model_name = 'clip-ViT-B-32'
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self._load_model()

    def _load_model(self) -> SentenceTransformer:
        return SentenceTransformer(model_name_or_path=self.model_name, device=self.device)

    def encode(self, image: list, batch_size: int):
        start_time = time.time()
        embeddings = self.model.encode(image, batch_size=batch_size, convert_to_tensor=True, show_progress_bar=True)
        total_runtime('encoding', start_time)
        return embeddings

    def query(self, query_image: torch, encoded_image: torch, k: int) -> list:
        start_time = time.time()
        total_runtime('query', start_time)
        return util.semantic_search(query_image, encoded_image, top_k=k)[0]


query_model = CLIP()
