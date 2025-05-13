from pydantic import BaseModel, Field
from typing import Optional


class ResponseDefault(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None


class ResponsePage(BaseModel):
    predictions: Optional[list] = None
    similar_images: Optional[list] = None
    total_page: Optional[int] = Field(default=None, ge=1, le=100)
    total_image: Optional[int] = Field(default=None, ge=1, le=10000)
