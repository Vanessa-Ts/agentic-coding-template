from httpx import AsyncClient


async def test_index_returns_200(client: AsyncClient) -> None:
    r = await client.get("/")
    assert r.status_code == 200


async def test_index_contains_app_name(client: AsyncClient) -> None:
    r = await client.get("/")
    assert "agentic-coding-template" in r.text


async def test_index_not_found(client: AsyncClient) -> None:
    r = await client.get("/nonexistent-route")
    assert r.status_code == 404
