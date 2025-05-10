import os
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
BASE_FORMAT = '%(asctime)s %(levelname)s %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_DIR = BASE_DIR / 'logs' / 'server.log'

os.makedirs(name='logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format=BASE_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(filename=LOG_DIR),
    ],
)
