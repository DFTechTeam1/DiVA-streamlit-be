import os
import re
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
from utils.logger import logging
from utils.helper import save_json, total_runtime
from typing import Optional


class DataMonitoring:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.base_depth: int = len(self.file_path.resolve().parts)

    def get_preview_paths(self, year_depth: int = 2, preview_depth: int = 5) -> Optional[list]:
        start_time = time.time()
        year_pattern = re.compile(r'^\d{4}')
        preview_paths = []

        for root, dirs, files in os.walk(str(self.file_path)):
            current_depth = Path(root).resolve().parts.__len__() - self.base_depth

            if current_depth == year_depth:
                dirs[:] = [d for d in dirs if year_pattern.match(d)]

            if current_depth == preview_depth:
                for dirname in dirs:
                    if dirname.lower() == 'preview':
                        full_path = os.path.join(root, dirname)
                        logging.info(f'Found preview path: {full_path}')
                        preview_paths.append(full_path)

        total_runtime('get_preview_paths', start_time)
        return preview_paths if preview_paths else None

    def get_client_preview(self, paths: Optional[list]) -> Optional[dict]:
        start_time = time.time()
        if not paths:
            raise FileNotFoundError('No preview paths found.')

        client_prev_pattern = re.compile(r'^\d{4}_\d{2}_\d{2}')
        all_matched_files = []

        for path in paths:
            entries = os.listdir(path)
            matched_files = [
                os.path.join(path, entry)
                for entry in entries
                if client_prev_pattern.match(entry)
                and entry.lower().endswith(('png', 'jpg', 'jpeg'))
            ]

            if not matched_files:
                logging.warning(f'No valid preview files found in: {path}')
                continue

            all_matched_files.extend(matched_files)
        total_runtime('get_client_preview', start_time)
        return {'paths': all_matched_files} if all_matched_files else None


BASE_DIR = Path(__file__).resolve().parents[2]
MOUNT_DIR = BASE_DIR / 'mount'
DESTINATION_DIR = BASE_DIR / 'json' / 'client_preview.json'

monitor = DataMonitoring(MOUNT_DIR)
paths = monitor.get_preview_paths()
client_previews = monitor.get_client_preview(paths)
save_json(destination=DESTINATION_DIR, data=client_previews)
