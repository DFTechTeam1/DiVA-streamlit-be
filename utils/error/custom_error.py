from utils.logger import logging
from typing import Callable
from fastapi import Request
from fastapi.responses import JSONResponse


class DiVA(Exception):
    def __init__(
        self,
        detail: str = "Service is unavailable.",
        name: str = None,
    ) -> None:
        self.detail = detail
        self.name = name
        super().__init__(self.detail, self.name)


def create_exception_handler(
    status_code: int, detail_message: str
) -> Callable[[Request, DiVA], JSONResponse]:
    detail = {"message": detail_message}

    async def exception_handler(_: Request, exc: DiVA) -> JSONResponse:
        if exc:
            detail["message"] = exc.detail

        if exc.name:
            detail["message"] = f"{detail['message']} [{exc.name}]"

        logging.error(exc)
        return JSONResponse(
            status_code=status_code,
            content={"detail": detail["message"]},
        )

    return exception_handler


class ServiceError(DiVA):
    """Failures in internal Image Search Engine services."""

    pass


class DataNotFoundError(DiVA):
    """Error occurred when target data not found."""

    pass


class ServicesConnectionError(DiVA):
    """Error occurred when try to connecting third party services."""

    pass


class DatabaseQueryError(DiVA):
    """Error occurred when performing database query."""

    pass


class NasIntegrationError(DiVA):
    """Error occurred when performing query, data view, etc into NAS."""

    pass


class AccessUnauthorized(DiVA):
    """Error occurred when user with blacklisted IP try to access server."""

    pass
