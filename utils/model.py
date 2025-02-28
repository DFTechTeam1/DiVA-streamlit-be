import os
import torch
import json
from PIL import Image
from torch import Tensor
from torch.nn import Module
from utils.logger import logging
from collections import OrderedDict
from typing import Literal, Optional
from utils.preprocessing import ImageProcessing
from sentence_transformers import SentenceTransformer, util
from transformers import AutoImageProcessor, AutoModelForImageClassification


class CLIP:
    def __init__(
        self,
        model_name: Literal[
            "clip-ViT-B-32", "clip-ViT-B-16", "clip-ViT-L-14"
        ] = "clip-ViT-B-32",
    ) -> None:
        """
        Load Visual Transformers model.
        This uses the CLIP model for encoding.

        |   Model 	        |   Top 1 Performance   |
        |   clip-ViT-B-32 	|   63.3                |
        |   clip-ViT-B-16 	|   68.1                |
        |   clip-ViT-L-14 	|   75.4                |
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.init_model()

    def init_model(self) -> SentenceTransformer:
        loaded_model = SentenceTransformer(
            model_name_or_path=self.model_name, device=self.device
        )
        logging.info(f"Model {self.model_name} loaded into {self.device}.")
        return loaded_model

    def encode(self, image: list[type[Image]], batch_size: int = 10) -> Tensor:
        logging.info("Start encoding process.")
        embeddings = self.model.encode(
            image, batch_size=batch_size, convert_to_tensor=True, show_progress_bar=True
        ).to(self.device)
        logging.info(f"Encoding completed. Total encoded image: {embeddings.shape[0]}.")
        return embeddings

    def search(self, query: type[Image], encoded_image: Tensor, k: int = 10) -> list:
        logging.info("Start query images.")
        resized_image = query.resize((255, 255))
        query_emb = self.model.encode(resized_image, convert_to_tensor=True).to(
            self.device
        )
        results = util.semantic_search(
            query_emb, encoded_image.to(self.device), top_k=k
        )[0]
        logging.info("Query process completed.")
        return results

    def filter_output(self, actual_path: list, clip_result: list) -> list:
        formatted_results = []

        for entry in clip_result:
            formatted_results.append(
                {
                    "filepath": actual_path[entry["corpus_id"]],
                    "accuracy": round(entry["score"], 2),
                }
            )

        return formatted_results


class SigLIP(ImageProcessing):
    def __init__(self, model_path: str = "models/SIGLIP_custom_model.pth"):
        super().__init__()
        self.model_path = model_path
        self.label_path = "utils/trained_label.json"
        self.base_model = "google/siglip-so400m-patch14-384"
        self.problem_type = "multi_label_classification"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.trained_label = self.init_label()
        self.model = self.init_model()

    def init_model(self) -> Module:
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model {self.model_path} not found!")

        loaded_state = torch.load(self.model_path, map_location="cpu")
        loaded_model = AutoModelForImageClassification.from_pretrained(
            pretrained_model_name_or_path=self.base_model,
            problem_type=self.problem_type,
            id2label=self.trained_label,
        )

        formatted_state = self.format_architecture(state_dict=loaded_state)
        loaded_model.load_state_dict(formatted_state, strict=False)
        loaded_model.to(self.device)
        loaded_model.eval()
        logging.info(f"Model {self.model_path} loaded into {self.device}.")

        return loaded_model

    def init_label(self) -> dict:
        if not os.path.exists(self.label_path):
            raise FileNotFoundError(f"Label {self.label_path} not found!")

        with open(self.label_path, "r") as file:
            logging.info("Load trained label.")
            label = json.load(file)
            formatted_label = self.format_label(label=label)

        return formatted_label

    def format_architecture(self, state_dict: dict) -> dict:
        logging.info("Formating model architecture.")
        formatted_state = OrderedDict()
        for key, value in state_dict.items():
            new_key = key.replace("module.", "")
            formatted_state[new_key] = value
        return formatted_state

    def format_label(self, label: dict) -> dict:
        logging.info("Formatting trained label.")
        return {int(key): value for key, value in label.items()}

    def format_predicted_data(self, predicted_label: dict) -> dict:
        return {label: True for label, score in predicted_label.items()}

    def load_image(self, decoded_image: Image) -> Optional[dict]:
        try:
            logging.info(f"Loading image {decoded_image}.")
            processor = AutoImageProcessor.from_pretrained(
                self.base_model, use_fast=True
            )
            processed = processor(images=decoded_image, return_tensors="pt")
            loaded_image = {k: v.to(self.device) for k, v in processed.items()}
        except Exception as e:
            logging.error(f"Error loading image: {e}")
            return None
        return loaded_image

    def predict(
        self, decoded_image: type[Image], threshold: float = 0.8
    ) -> Optional[dict]:
        try:
            loaded_image = self.load_image(decoded_image=decoded_image)

            logging.info(f"Performing inference model: {self.model}.")
            with torch.no_grad():
                outputs = self.model(**loaded_image)
                logits = outputs.logits

            probs = torch.sigmoid(logits).squeeze().cpu().numpy()
            predicted_labels = {
                self.trained_label[i]: round(float(probs[i]), 2)
                for i in range(len(probs))
                if probs[i] > threshold
            }

            logging.info("Inference completed.")
        except Exception as e:
            logging.error(f"Error predicting image: {e}")
            return None

        return predicted_labels if predicted_labels else None
