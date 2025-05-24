from pydantic import BaseModel, Field
from typing import Optional


class ResponseDefault(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None


class ResponsePage(BaseModel):
    similar_image: Optional[list] = None
    total_page: Optional[int] = Field(default=None, ge=1)
