from pydantic import AfterValidator, BaseModel, Field
from typing import Optional, Annotated
from utils.validator import validate_base64

ValidatedEncoder = Annotated[str, AfterValidator(validate_base64)]


class QueryPayload(BaseModel):
    encoded_image: Optional[ValidatedEncoder] = None
    threshold: float = Field(default=0.3, ge=0.1, le=1.0)
    page: int = Field(default=1, ge=1, le=50)
