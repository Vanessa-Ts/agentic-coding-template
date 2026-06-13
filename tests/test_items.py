import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture(autouse=True)
async def store_reset() -> None:
    from app.store.item_store import _item_store

    _item_store._store.clear()


# POST /items


async def test_create_item_happy(client: AsyncClient) -> None:
    r = await client.post("/items", json={"name": "widget", "description": "a widget"})
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "widget"
    assert body["description"] == "a widget"
    assert "id" in body
    assert "created_at" in body


@pytest.mark.parametrize(
    "payload",
    [
        {"name": ""},
        {"name": "x" * 101},
        {},
    ],
)
async def test_create_item_validation(
    client: AsyncClient, payload: dict[str, object]
) -> None:
    r = await client.post("/items", json=payload)
    assert r.status_code == 422


# GET /items


async def test_list_items_happy(client: AsyncClient) -> None:
    await client.post("/items", json={"name": "alpha"})
    await client.post("/items", json={"name": "beta"})
    r = await client.get("/items")
    assert r.status_code == 200
    names = [i["name"] for i in r.json()]
    assert "alpha" in names
    assert "beta" in names


async def test_list_items_empty(client: AsyncClient) -> None:
    r = await client.get("/items")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_list_items_no_404(client: AsyncClient) -> None:
    r = await client.get("/items")
    assert r.status_code != 404


@pytest.mark.parametrize(
    "limit,offset,expected_count,expected_status",
    [
        (20, 0, 3, 200),  # default pagination, fewer items than limit
        (2, 0, 2, 200),  # custom limit clips result
        (2, 2, 1, 200),  # offset skips into list
        (20, 99, 0, 200),  # offset beyond length → empty list
    ],
)
async def test_list_items_pagination(
    client: AsyncClient,
    limit: int,
    offset: int,
    expected_count: int,
    expected_status: int,
) -> None:
    for i in range(3):
        await client.post("/items", json={"name": f"item-{i}"})
    r = await client.get("/items", params={"limit": limit, "offset": offset})
    assert r.status_code == expected_status
    assert len(r.json()) == expected_count


@pytest.mark.parametrize(
    "params,expected_status",
    [
        ({"limit": 0}, 422),  # below ge=1
        ({"limit": 101}, 422),  # above le=100
        ({"offset": -1}, 422),  # below ge=0
    ],
)
async def test_list_items_pagination_validation(
    client: AsyncClient,
    params: dict[str, int],
    expected_status: int,
) -> None:
    r = await client.get("/items", params=params)
    assert r.status_code == expected_status


# GET /items/{item_id}


async def test_get_item_happy(client: AsyncClient) -> None:
    create = await client.post("/items", json={"name": "gadget"})
    item_id = create.json()["id"]
    r = await client.get(f"/items/{item_id}")
    assert r.status_code == 200
    assert r.json()["id"] == item_id


async def test_get_item_validation_missing_name(client: AsyncClient) -> None:
    r = await client.post("/items", json={"description": "no name"})
    assert r.status_code == 422


async def test_get_item_not_found(client: AsyncClient) -> None:
    r = await client.get("/items/does-not-exist")
    assert r.status_code == 404


# PUT /items/{item_id}


async def test_update_item_happy(client: AsyncClient) -> None:
    create = await client.post("/items", json={"name": "old"})
    item_id = create.json()["id"]
    r = await client.put(f"/items/{item_id}", json={"name": "new"})
    assert r.status_code == 200
    assert r.json()["name"] == "new"


async def test_update_item_validation(client: AsyncClient) -> None:
    create = await client.post("/items", json={"name": "valid"})
    item_id = create.json()["id"]
    r = await client.put(f"/items/{item_id}", json={"name": ""})
    assert r.status_code == 422


async def test_update_item_not_found(client: AsyncClient) -> None:
    r = await client.put("/items/no-such-id", json={"name": "x"})
    assert r.status_code == 404


# DELETE /items/{item_id}


async def test_delete_item_happy(client: AsyncClient) -> None:
    create = await client.post("/items", json={"name": "doomed"})
    item_id = create.json()["id"]
    r = await client.delete(f"/items/{item_id}")
    assert r.status_code == 204
    r2 = await client.get(f"/items/{item_id}")
    assert r2.status_code == 404


async def test_delete_item_validation(client: AsyncClient) -> None:
    r = await client.post("/items", json={"name": ""})
    assert r.status_code == 422


async def test_delete_item_not_found(client: AsyncClient) -> None:
    r = await client.delete("/items/ghost-id")
    assert r.status_code == 404
