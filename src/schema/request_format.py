from typing import Optional
from pydantic import BaseModel, Field, field_validator
from utils.validator import Base64ValidatorMixin


class SearchByImage(BaseModel, Base64ValidatorMixin):
    encoded_image: str = None
    threshold: float = Field(
        default=0.2,
        ge=0.1,
        le=1.0,
        description="Threshold accuracy for classification model.",
    )
    page: int = Field(default=1, ge=1, description="Current page for extracted data.")
    prediction_label: Optional[list] = None

    @field_validator("encoded_image")
    @classmethod
    def validate_base64(cls, value: str) -> str:
        return Base64ValidatorMixin.validate_base64(value)
