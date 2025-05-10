import os
import json
from typing import Optional
from utils.logger import logging


class ResponseFormatter:
    def __init__(self, prediction: list, client_preview: list, labels: list):
        self.empty_count: int = 0
        self.filled_count: int = 0
        self.result: list = []
        self.prediction = prediction
        self.client_preview = client_preview
        self.labels = labels

    def format(self) -> Optional[dict]:
        if len(self.prediction) != len(self.client_preview):
            raise ValueError('Prediction and client preview lengths should be matched.')

        for path, pred in zip(self.client_preview, self.prediction):
            if not pred:
                logging.warning(f'Prediction for {path} is empty. Skipping.')
                self.empty_count += 1
                continue

            if not os.path.exists(path):
                logging.warning(f'Image path {path} does not exist. Skipping.')
                self.empty_count += 1
                continue

            filename = os.path.basename(path)
            mapped_label = {label: (label in pred) for label in self.labels}
            mapped_label['filename'] = filename
            mapped_label['filepath'] = str(path)
            self.result.append(mapped_label)
            self.filled_count += 1

        logging.info(f'Filled predictions: {self.filled_count}')
        logging.info(f'Empty predictions: {self.empty_count}')

        return json.dumps(self.result, indent=4) if self.result else None
