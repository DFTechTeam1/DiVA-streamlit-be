import pytest
from datetime import datetime
from utils.helper import local_time


@pytest.mark.asyncio
async def test_local_time() -> None:
    """Should return datetime type of UTC now."""
    current_time = local_time()
    assert type(current_time) is datetime
