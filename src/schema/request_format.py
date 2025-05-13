from pydantic import AfterValidator, BaseModel, Field
from typing import Optional, Annotated
from utils.validator import validate_base64

ValidatedEncoder = Annotated[str, AfterValidator(validate_base64)]


class QueryPayload(BaseModel):
    encoded_image: Optional[ValidatedEncoder] = None
    prediction: Optional[list] = None
    filename: Optional[str] = None
    threshold: float = Field(default=0.3, ge=0.1, le=1.0)
    page: int = Field(default=1, ge=1, le=50)


# class SearchByImage(BaseModel, Base64ValidatorMixin):
#     encoded_image: str = None
#     filename: Optional[str] = None
#     threshold: float = Field(
#         default=0.2,
#         ge=0.1,
#         le=1.0,
#         description='Threshold accuracy for classification model.',
#     )
#     page: int = Field(default=1, ge=1, description='Current page for extracted data.')
#     prediction_label: Optional[list] = None

#     @field_validator('encoded_image')
#     @classmethod
#     def validate_base64(cls, value: str) -> str:
#         return Base64ValidatorMixin.validate_base64(value)
