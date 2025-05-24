from pathlib import Path
from typing import Optional
from src.schema.nas_params import ListShareNasParams
from services.nas.integration import NasIntegration
from services.nas.decorator import require_login
from utils.helper import local_time
from utils.json import JSON
from utils.logger import logging


class NasFolderService:
    def __init__(self, nas: NasIntegration):
        self.nas = nas

    def format_response(self, response: list, filter: Optional[str] = None) -> Optional[dict]:
        if filter:
            paths = [
                f'//{self.nas.ip_address}/{entry["name"]}'
                for entry in response
                if (entry['name'].lower().startswith(filter) and ' ' not in entry['name'])
            ]
            if paths:
                return {'paths': paths}

        return None

    def migrate_response(self, formatted_response: Optional[dict] = None) -> None:
        if not formatted_response:
            logging.warning('Formatted response is empty. Skipping migration.')
            return None

        project_root = Path(__file__).resolve().parents[2]
        ip_directory = project_root / 'temp' / self.nas.ip_address
        ip_directory.mkdir(parents=True, exist_ok=True)
        file_path = ip_directory / f'{local_time()}.json'
        JSON.save_json(destination=str(file_path), data=formatted_response)
        return None

    @require_login
    async def list_share(self) -> list:
        params = ListShareNasParams(api='SYNO.FileStation.List', version=2, method='list_share')
        payload = params.model_dump()
        response = await self.nas.send_request(api=params.api, params=payload, sid=self.nas.sid)
        return response['data']['shares']
