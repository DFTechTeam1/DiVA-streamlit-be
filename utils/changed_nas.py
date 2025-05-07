import http
import json
from pathlib import Path
from utils.helper import CustomHelper
from utils.logger import logging
from typing import Optional, Literal
from src.secret import Config
from utils.error.custom_error import RequestValidationError


class NasIntegration:
    def __init__(self, ip_address: str) -> None:
        self.config = Config()
        self.ip_address: Literal[
            "192.168.100.101",
            "192.168.100.102",
            "192.168.100.103",
            "192.168.100.104",
            "192.168.100.105",
        ] = ip_address
        self.formatted_data: Optional[dict] = None
        self.helper = CustomHelper()

    def port_matcher(self, ip_address: str) -> str:
        if ip_address.endswith("1"):
            return self.config.NAS_PORT_2
        return self.config.NAS_PORT_1

    def send_request(self, path: str) -> dict:
        port = self.port_matcher(ip_address=self.ip_address)
        conn = http.client.HTTPConnection(host=self.ip_address, port=port, timeout=10)

        try:
            logging.info(f"Sending request to: {self.ip_address}")
            conn.request("GET", path)

            response = conn.getresponse()

            if response.status != 200:
                raise RequestValidationError(
                    detail=f"HTTP {response.status}: {response.reason}"
                )

            data = response.read().decode("utf-8")
            return json.loads(data)

        except Exception as e:
            logging.error(f"Error ocurred during request: {e}")
            raise RequestValidationError(detail=str(e))

        finally:
            conn.close()

    def login(self) -> str:
        base_url = "/webapi/auth.cgi"
        params = (
            f"?api=SYNO.API.Auth&version=3&method=login"
            f"&account={self.config.NAS_USERNAME}&passwd={self.config.NAS_PASSWORD}&session=FileStation"
        )

        response = self.send_request(base_url + params)

        if not response.get("success"):
            logging.error(f"Unable to perform login to {self.ip_address}.")
            error_msg = response.get("error", {})
            raise RequestValidationError(detail=error_msg)

        return response["data"]["sid"]

    def shared_folder(self, sid: str) -> list:
        base_url = "/webapi/entry.cgi"
        params = f"?api=SYNO.FileStation.List&version=2&method=list_share&_sid={sid}"

        response = self.send_request(base_url + params)

        if not response.get("success"):
            logging.error(f"Unable to retrieve shared folders from {self.ip_address}.")
            error_msg = response.get("error", {})
            raise RequestValidationError(detail=error_msg)

        return response["data"]["shares"]

    def format_response(self, api_response: list) -> dict:
        logging.info("Formatting API response.")
        formatted = [
            f"//{self.ip_address}{entry['path']}"
            for entry in api_response
            if " " not in entry["path"]
        ]
        self.formatted_data = {"paths": formatted}

        return self.formatted_data

    def save_response(self) -> None:
        project_root = Path(__file__).resolve().parents[1]

        ip_directory = project_root / "temp" / self.ip_address
        ip_directory.mkdir(parents=True, exist_ok=True)

        file_path = ip_directory / f"{self.helper.local_time()}.json"

        logging.info(f"Saving shared folder data into {ip_directory} directory.")

        with open(file_path, "w") as file:
            json.dump(self.formatted_data, file, indent=4)

        logging.info(f"Shared folder data saved in {file_path}.")
