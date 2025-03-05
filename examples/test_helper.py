import pytest
from datetime import datetime
from utils.helper import CustomHelper


@pytest.mark.asyncio
async def test_local_time() -> None:
    """Should return datetime type of UTC now."""
    helper = CustomHelper()
    assert type(helper.local_time()) is datetime
