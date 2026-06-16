from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

import app.services.agent_catalogue as _catalogue_module
from app.main import app


@pytest.fixture(autouse=True)
def reset_catalogue_cache() -> None:
    _catalogue_module._catalogue = None


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
