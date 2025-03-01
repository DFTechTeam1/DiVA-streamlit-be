from pydantic import BaseModel, Field
from typing import Optional


class ResponseDefault(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None


class Pagination(BaseModel):
    prediction_label: Optional[dict] = None
    similar_image: list = None
    total_page: Optional[int] = Field(
        default=None, ge=1, description="Total page available based on query database.."
    )
    total_image: Optional[int] = Field(
        default=None,
        ge=1,
        description="Total similar image for uploaded data based on query database.",
    )
    total_chungked_image: Optional[int] = Field(
        default=None,
        ge=1,
        description="Total chuked image based on pagination on relative offset and limit.",
    )
