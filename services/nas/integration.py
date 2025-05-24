import httpx
from typing import Literal, Optional
from utils.logger import logging
from src.secret import NAS_PORT_1, NAS_PORT_2
from utils.error.custom_error import NasIntegrationError


class NasIntegration:
    def __init__(self, ip_address: str):
        self.ip_address = ip_address
        self.sid: Optional[str] = None

    def _get_port(self) -> str:
        return NAS_PORT_2 if self.ip_address.endswith('1') else NAS_PORT_1

    def _build_url(self, api: str) -> str:
        port = self._get_port()
        return f'http://{self.ip_address}:{port}/webapi/auth.cgi?api={api}'

    async def send_request(
        self,
        api: str,
        params: dict,
        method: Literal['GET', 'POST'] = 'GET',
        sid: Optional[str] = None,
    ) -> dict:
        url = self._build_url(api)
        if sid:
            logging.info(f'Using SID: {sid[:10]}')
            params['_sid'] = sid

        async with httpx.AsyncClient(timeout=360) as client:
            try:
                response = await client.request(method, url, params=params)
                response.raise_for_status()
                data = response.json()

                if not data.get('success', False):
                    raise NasIntegrationError(detail=data.get('error', {}))

                return data

            except httpx.HTTPStatusError as e:
                raise NasIntegrationError(detail=str(e))
            except httpx.RequestError as e:
                raise NasIntegrationError(detail=str(e))
