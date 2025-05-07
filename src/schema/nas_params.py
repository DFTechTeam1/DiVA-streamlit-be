from typing import Literal
from pydantic import BaseModel


class NasApi(BaseModel):
    api: Literal["SYNO.API.Auth", "SYNO.FileStation.List"]


class NasVersion(BaseModel):
    version: int


class NasMethod(BaseModel):
    method: Literal["login", "logout", "list_share"]


class NasSession(BaseModel):
    session: Literal["FileStation"]


class LoginNasParams(NasApi, NasVersion, NasMethod, NasSession):
    account: str
    passwd: str
    format: Literal["cookie"]


class LogoutNasParams(NasApi, NasVersion, NasMethod, NasSession):
    pass


class ListShareNasParams(NasApi, NasVersion, NasMethod):
    pass