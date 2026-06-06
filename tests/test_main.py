from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_index_returns_200() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        r = await c.get("/")
    assert r.status_code == 200


async def test_index_contains_app_name() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        r = await c.get("/")
    assert "agentic-coding-template" in r.text


async def test_index_not_found() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        r = await c.get("/nonexistent-route")
    assert r.status_code == 404
