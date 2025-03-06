import logging
import os

BASE_FORMAT = "%(asctime)s %(levelname)s %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

os.makedirs(name="logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format=BASE_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(filename="logs/server.log"),
    ],
)
