from typing import Optional
from pydantic import BaseModel, Field


class SearchByImage(BaseModel):
    encoded_image: str = None
    threshold: float = Field(
        default=0.2,
        ge=0.1,
        le=1.0,
        description="Threshold accuracy for classification model.",
    )
    page: int = Field(default=1, ge=1, description="Current page for extracted data.")
    image_per_page: int = Field(
        default=50, ge=1, description="Splitted total image into current chunk data."
    )
    prediction_label: Optional[list] = None
