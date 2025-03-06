import base64
from typing import Optional
from utils.error.custom_error import RequestValidationError


class RequestValidator:
    def validate_label(
        self, actual_label: list, predicted_label: list
    ) -> tuple[bool, Optional[list]]:
        if not predicted_label:
            return (False, None)

        non_existing_label = [
            entry for entry in predicted_label if entry not in actual_label
        ]
        if non_existing_label:
            return (False, None)

        return (True, predicted_label)


class Base64ValidatorMixin:
    @classmethod
    def validate_base64(cls, value: str) -> str:
        if not value:
            raise RequestValidationError("Encoded image cannot be empty.")

        try:
            decoded_bytes = base64.b64decode(value, validate=False)
            if not decoded_bytes or len(decoded_bytes) == 0:
                raise RequestValidationError(
                    "Decoded image is empty. Ensure the Base64 input is correct."
                )
        except base64.binascii.Error:
            raise RequestValidationError(
                "Invalid Base64 encoding. Please provide a properly encoded image."
            )
        except Exception:
            raise RequestValidationError(
                "Encoded image must be a valid base64-encoded string."
            )

        return value
