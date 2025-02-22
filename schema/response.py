from pydantic import BaseModel, Field
from typing import Optional


class ResponseDefault(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: dict = None


class Pagination(BaseModel):
    prediction_label: Optional[dict] = None
    similar_image: list = None
    total_page: int = Field(
        default=1, ge=1, description="Total page available for current chunk data."
    )
    total_image: int = Field(
        default=1, ge=1, description="Total similar image for uploaded data."
    )
