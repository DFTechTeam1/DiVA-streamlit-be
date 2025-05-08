import os
import json
import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
from utils.logger import logging
from typing import Optional

class DataMonitoring:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.base_depth: int = self.file_path.rstrip(os.sep).count(os.sep)

    def _proccess(self, path: str) -> tuple:
        parts = path.split('/')
        ip_last_octet = int(parts[1].split('.')[-1])
        queue = int(re.search(r'\d+', parts[2]).group())
        year = int(parts[3])
        day_match = re.match(r'^(\d{2})_', parts[5])
        day = int(day_match.group(1)) if day_match else 0

        return (ip_last_octet, queue, year, day)

    def get_preview_paths(self) -> Optional[list]:
        year_pattern = re.compile(r"^\d{4}")
        preview_paths = []

        for root, dirs, files in os.walk(self.file_path):
            current_depth = root.count(os.sep) - self.base_depth

            if current_depth == 2:
                dirs[:] = [d for d in dirs if year_pattern.match(d)]

            if current_depth == 5:
                for dirname in dirs:
                    if dirname.lower() == "preview":
                        full_path = os.path.join(root, dirname)
                        logging.info(f"Found preview path: {full_path}")
                        preview_paths.append(full_path)

        sorted_paths = sorted(preview_paths, key=self._proccess)
        return sorted_paths if sorted_paths else None
    

    def get_client_preview(self, paths: Optional[list]) -> Optional[dict]:
        if not paths:
            raise FileNotFoundError("No preview paths found.")

        client_prev_pattern = re.compile(r"^\d{4}_\d{2}_\d{2}")
        all_matched_files = []

        for path in paths:
            entries = os.listdir(path)
            matched_files = [
                os.path.join(path, entry) for entry in entries
                if client_prev_pattern.match(entry) and entry.lower().endswith(("png", "jpg", "jpeg"))
            ]

            if not matched_files:
                logging.warning(f"No valid preview files found in: {path}")
                continue

            all_matched_files.extend(matched_files)
        
        return {"paths": all_matched_files} if all_matched_files else None

    def save(self, data: dict, save_dir: str = "json", filename="client_preview.json") -> None:
        if not data:
            raise ValueError("No data to save.")

        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.truncate(0)
            json.dump(data, f, indent=4)

        logging.info(f"Saved preview data to {file_path}")


monitor = DataMonitoring("mount")
paths = monitor.get_preview_paths()
client_previews = monitor.get_client_preview(paths)
monitor.save(client_previews)