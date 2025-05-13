import base64
from utils.error.custom_error import RequestValidationError


def validate_base64(value: str) -> str:
    if not value:
        raise RequestValidationError('Encoded image cannot be empty.')

    try:
        decoded_bytes = base64.b64decode(value, validate=False)
        if not decoded_bytes:
            raise RequestValidationError(
                'Decoded image is empty. Ensure the Base64 input is correct.'
            )
    except base64.binascii.Error:
        raise RequestValidationError(
            'Invalid Base64 encoding. Please provide a properly encoded image.'
        )
    except Exception:
        raise RequestValidationError('Encoded image must be a valid base64-encoded string.')

    return value
