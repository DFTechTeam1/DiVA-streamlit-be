from services.nas.integration import NasIntegration
from src.schema.nas_params import LoginNasParams, LogoutNasParams
from src.secret import NAS_USERNAME, NAS_PASSWORD


class NasAuthService:
    def __init__(self, nas: NasIntegration):
        self.nas = nas

    async def login(self) -> None:
        params = LoginNasParams(
            api="SYNO.API.Auth",
            version=3,
            method="login",
            session="FileStation",
            account=NAS_USERNAME,
            passwd=NAS_PASSWORD,
            format="cookie",
        )

        response = await self.nas.send_request(
            api=params.api, params=params.model_dump()
        )
        self.nas.sid = response["data"]["sid"]
        return None

    async def logout(self) -> None:
        params = LogoutNasParams(
            api="SYNO.API.Auth",
            version=1,
            method="logout",
            session="FileStation",
        )
        await self.nas.send_request(api=params.api, params=params.model_dump())
        return None
