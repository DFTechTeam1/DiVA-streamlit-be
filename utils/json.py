import json
from pathlib import Path
from utils.logger import logging

class JSON:
    @staticmethod
    def load_json(filepath: str):
        logging.info(f"Loading JSON data from {filepath}.")
        return json.loads(Path(filepath).read_text())

    @staticmethod
    def save_json(destination: str, data: dict):
        destination_path = Path(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        logging.info(f"Saving data to {destination_path}.")
        with destination_path.open('w') as file:
            json.dump(data, file, indent=4)