import os
import hashlib
from pytz import timezone
from urllib.parse import quote
from datetime import datetime


def formatter(file_path: str) -> dict:
    filename = os.path.basename(file_path)
    md5_hash = hashlib.md5()

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5_hash.update(chunk)

    return {'filename': filename, 'checksum': md5_hash.hexdigest()}


def local_time(zone: str = 'Asia/Jakarta') -> datetime:
    return datetime.now(timezone(zone)).replace(tzinfo=None)


def format(entry: tuple, base_url: str):
    return {
        'image_stream': f'{base_url}{quote(entry[0])}',
        'score': int(round(entry[1])),
        'path': entry[0],
    }
