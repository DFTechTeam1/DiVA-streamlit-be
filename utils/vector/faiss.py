import os
import logging
import faiss
import pickle
import numpy as np

class FAISS:
    def __init__(self, dimension: int = 1024) -> None:
        self.index = faiss.IndexFlatIP(dimension)
        self.image_paths = []
        self._last_search_result = []
    
    def _normalize(self, vectors: np.ndarray):
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.clip(norms, 1e-8, None)
    
    def add_embedding(self, embedding: list, path: list):
        norm_embedding = self._normalize(np.stack(embedding).astype("float32"))
        self.index.add(norm_embedding)
        self.image_paths.extend(path)

    def save(self, index_path: str, metadata_path: str):
        index_dir = os.path.dirname(index_path)
        if not os.path.exists(index_dir):
            os.makedirs(index_dir, exist_ok=True)
            logging.info(f"Created directory for FAISS index at {index_dir}")

        faiss.write_index(self.index, index_path)
        logging.info(f"Saving {index_path}.")
        
        with open(metadata_path, "wb") as file:
            logging.info(f"Saving {metadata_path}")
            pickle.dump(self.image_paths, file)


    def load(self, index_path: str, metadata_path: str):
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError("Vector DB and metadata file not found.")
        
        self.index = faiss.read_index(index_path)
        with open(metadata_path, "rb") as f:
            self.image_paths = pickle.load(f)

    def search(self, embedding: np.ndarray, threshold: float):
        query = self._normalize(embedding.astype("float32").reshape(1, -1))
        distances, indices = self.index.search(query, self.index.ntotal)

        if self.index.ntotal != len(self.image_paths):
            raise ValueError(
                f"FAISS index has {self.index.ntotal} vectors, but metadata has {len(self.image_paths)} entries."
            )

        result = []
        for i, score in zip(indices[0], distances[0]):
            if i == -1:
                continue
            if score >= threshold:
                similarity_percent = round(score * 100, 2)
                result.append((self.image_paths[i], similarity_percent))

        self._last_search_result = result
        return result
    
    def move_page(self, page: int, page_size: int):
        start = (page - 1) * page_size
        end = page * page_size
        return self._last_search_result[start:end]