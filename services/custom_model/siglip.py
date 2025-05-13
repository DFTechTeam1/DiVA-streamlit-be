import sys
import json
import time
import torch
import asyncio
import numpy as np
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
from utils.logger import logging
from utils.helper import load_json, save_json, total_runtime
from utils.processor import ImageProcessor
from utils.formatter import ResponseFormatter
from utils.query import QueryDatabase
from collections import OrderedDict
from services.postgre.connection import get_db
from services.postgre.models import ClientPreview
from transformers import (
    AutoConfig,
    AutoImageProcessor,
    AutoModelForImageClassification,
)


class CustomModel:
    def __init__(self, model_path: str, label_path: str):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.base_model = 'google/siglip-so400m-patch14-384'
        self.problem_type = 'multi_label_classification'
        self.model_path = model_path
        self.label_path = label_path
        self.labels = self._load_labels()
        self.model = self._load_model()
        self.processor = AutoImageProcessor.from_pretrained(self.base_model, use_fast=True)

    def _load_labels(self) -> dict:
        raw = json.loads(Path(self.label_path).read_text())
        return {int(k): v for k, v in raw.items()}

    def _load_config(self):
        config = AutoConfig.from_pretrained(self.base_model)
        config.problem_type = self.problem_type
        config.id2label = self.labels
        config.label2id = {v: k for k, v in self.labels.items()}
        return config

    def _format_model_state(self, state_dict: dict) -> dict:
        return OrderedDict((k.replace('module.', ''), v) for k, v in state_dict.items())

    def _load_model(self):
        config = self._load_config()
        model = AutoModelForImageClassification.from_config(config)
        state = torch.load(self.model_path, map_location=self.device)
        formatted_state = self._format_model_state(state)
        missing_keys, unexpected_keys = model.load_state_dict(formatted_state)

        if missing_keys:
            logging.warning(f'Missing keys: {missing_keys}')
        if unexpected_keys:
            logging.warning(f'Unexpected keys: {unexpected_keys}')

        model.to(self.device)
        return model.eval()

    def _results(self, probs: np.ndarray, threshold: float) -> list:
        all_labels = []
        for prob_vector in probs:
            labels = [self.labels[i] for i, prob in enumerate(prob_vector) if prob >= threshold]
            all_labels.append(labels)
        return all_labels

    def predict(self, images: list, threshold: float, batch_size: int) -> list:
        logging.info('Starting image prediction.')
        start_time = time.time()
        all_results = []

        for i in range(0, len(images), batch_size):
            batch = images[i : i + batch_size]
            logging.info(
                f'Processing batch {i // batch_size + 1} of {((len(images) - 1) // batch_size) + 1} '
                f'({len(batch)} image(s))'
            )

            inputs = self.processor(images=batch, return_tensors='pt')
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)

            logits = outputs.logits
            probs = torch.sigmoid(logits).cpu().numpy()
            batch_results = self._results(probs, threshold)
            all_results.extend(batch_results)

        total_runtime('predict', start_time)
        return all_results

    def to_dict(self, prediction: list) -> dict:
        return {entry: True for entry in prediction}


BASE_DIR = Path(__file__).resolve().parents[2]
CLIENT_PREVIEW = BASE_DIR / 'json' / 'client_preview.json'
TRAINED_LABEL = BASE_DIR / 'json' / 'trained_label.json'
MODEL_PATH = BASE_DIR / 'models' / 'SIGLIP_custom_model.pth'
SAVED_JSON = BASE_DIR / 'json' / 'prediction_result.json'

cls_model = CustomModel(model_path=MODEL_PATH, label_path=TRAINED_LABEL)


async def main():
    processor = ImageProcessor()
    cp = load_json(filepath=CLIENT_PREVIEW)
    image_path = [BASE_DIR / Path(p) for p in cp['paths']]
    images = processor.resize(image_path)
    results = cls_model.predict(images=images, threshold=0.4, batch_size=10)

    loaded_label = load_json(filepath=TRAINED_LABEL)
    loaded_label = list(loaded_label.values())
    formatter = ResponseFormatter(
        prediction=results, client_preview=image_path, labels=loaded_label
    )
    formatted_json = json.loads(formatter.format_cls_pred())
    save_json(destination=SAVED_JSON, data=formatted_json)

    async for session in get_db():
        db = QueryDatabase(session=session)
        try:
            await db.truncate(ClientPreview)
            for entry in formatted_json:
                await db.insert(ClientPreview, entry)
        except Exception as e:
            logging.error(f'Failed to insert record: {e}')


if __name__ == '__main__':
    asyncio.run(main())
