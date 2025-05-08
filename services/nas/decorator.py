from functools import wraps
from utils.error.custom_error import NasIntegrationError


def require_login(method):
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        if not self.nas.sid:
            raise NasIntegrationError(detail="No active session. Please log in first.")
        return await method(self, *args, **kwargs)

    return wrapper
