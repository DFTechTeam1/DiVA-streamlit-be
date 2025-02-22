import torch
import os
from PIL import Image
from utils.logger import logging
from collections import OrderedDict
from utils.error.custom_error import ServiceError
from transformers import AutoImageProcessor, AutoModelForImageClassification


class CustomSigLipModel:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.base_model = "google/siglip-so400m-patch14-384"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.problem_type = "multi_label_classification"
        self.id2label = {
            0: "nature",
            1: "artifacts",
            2: "living_beings",
            3: "conceptual",
            4: "art_deco",
            5: "architectural",
            6: "artistic",
            7: "sci_fi",
            8: "fantasy",
            9: "afternoon",
            10: "sunset_sunrise",
            11: "night",
            12: "warm",
            13: "cool",
            14: "neutral",
            15: "gold",
        }
        self.model = self.load_model()

    def format_architecture(self, state_dict: dict) -> dict:
        formatted_state = OrderedDict()
        for key, value in state_dict.items():
            new_key = key.replace("module.", "")
            formatted_state[new_key] = value
        return formatted_state

    def load_model(self) -> torch.nn.Module:
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file '{self.model_path}' not found!")

        logging.info("Loading model checkpoint...")
        state_dict = torch.load(self.model_path, map_location="cpu")

        try:
            model = AutoModelForImageClassification.from_pretrained(
                pretrained_model_name_or_path=self.base_model,
                problem_type=self.problem_type,
                id2label=self.id2label,
            )

            formatted_state_dict = self.format_architecture(state_dict)
            model.load_state_dict(formatted_state_dict, strict=False)
            model.to(self.device)
            model.eval()

            logging.info("Model successfully loaded.")

        except Exception as e:
            logging.error(f"Error loading model: {e}")
            raise RuntimeError("Failed to load the model.")
        return model

    def preprocess_image(self, image: str) -> dict:
        try:
            logging.info("Preprocessing image...")
            processor = AutoImageProcessor.from_pretrained(
                self.base_model, use_fast=True
            )
            inputs = processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            logging.info("Image preprocessing complete.")

        except Exception as e:
            logging.error(f"Error decoding or preprocessing image: {e}")
            raise ValueError("Invalid base64 image format.")
        return inputs

    def predict_image(self, image: Image.Image, threshold: float = 0.8) -> dict:
        try:
            inputs = self.preprocess_image(image)

            logging.info("Performing inference...")
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits

            probs = torch.sigmoid(logits).squeeze().cpu().numpy()
            predicted_labels = {
                self.id2label[i]: round(float(probs[i]), 2)
                for i in range(len(probs))
                if probs[i] > threshold
            }

            logging.info("Inference completed.")
        except Exception as e:
            logging.error(f"Error decoding or preprocessing image: {e}")
            raise ServiceError(detail="Invalid base64 image format.")

        return predicted_labels if predicted_labels else None
