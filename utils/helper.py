import json
import time
from pathlib import Path
from pytz import timezone
from datetime import datetime
from utils.logger import logging


def local_time(zone: str = 'Asia/Jakarta') -> datetime:
    return datetime.now(timezone(zone)).replace(tzinfo=None)


def load_json(filepath: str) -> dict:
    logging.info(f'Loading JSON data from {filepath}.')
    return json.loads(Path(filepath).read_text())


def save_json(destination: str, data: dict) -> None:
    logging.info(f'Data saved to {destination}.')
    file = open(destination, 'w')
    try:
        json.dump(data, file, indent=4)
    finally:
        file.close()
    return


def total_runtime(function_name: str, finished_time: float) -> None:
    elapsed = time.time() - finished_time
    logging.info(f'Total {function_name} completed in {elapsed:.2f}s.')
    return
