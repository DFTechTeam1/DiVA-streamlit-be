import torch
from typing import Optional
from PIL import ImageOps, Image
from sentence_transformers import SentenceTransformer


class CustomCLIPModel:
    def __init__(self, model_path: Optional[str] = None):
        """
        Load Visual Transformers model.
        This uses the CLIP model for encoding.

        |   Model 	        |   Top 1 Performance   |
        |   clip-ViT-B-32 	|   63.3                |
        |   clip-ViT-B-16 	|   68.1                |
        |   clip-ViT-L-14 	|   75.4                |
        """
        self.base_model = "clip-ViT-L-14"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.load_model()

    def load_model(self) -> Optional[SentenceTransformer]:
        return SentenceTransformer(
            model_name_or_path=self.base_model, device=self.device
        )

    def preprocess_image(self, image_paths: list) -> list:
        preprocessed_image = []
        converted_image = [Image.open(image) for image in image_paths]
        for image in converted_image:
            preprocessed = ImageOps.fit(image, (224, 224))
            preprocessed = ImageOps.autocontrast(image)
            preprocessed_image.append(preprocessed)

        return preprocessed_image

    def encode_image(self) -> None:
        """Encode preprocessed images"""
        pass

    def normalize_embedding(self) -> None:
        """Normalize embedding from 0-255 into 0-1"""
        pass

    def auto_encode(self) -> None:
        """Method for trigger auto encoding if there is additional 50 image (lte 50)"""
        pass

    def query(self) -> list:
        """Method for query similar images based on cosine similarity"""
        pass
