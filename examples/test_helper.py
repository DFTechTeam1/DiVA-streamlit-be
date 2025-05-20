import pytest
from datetime import datetime
from utils.helper import local_time


@pytest.mark.asyncio
async def test_local_time() -> None:
    """Should return datetime type of UTC now."""
    assert type(local_time()) is datetime
