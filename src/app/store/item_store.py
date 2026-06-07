import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from app.models.item import Item, ItemCreate, ItemUpdate


class ItemStore:
    def __init__(self) -> None:
        self._store: dict[str, Item] = {}
        self._lock = asyncio.Lock()

    async def create(self, data: ItemCreate) -> Item:
        async with self._lock:
            item = Item(
                id=str(uuid4()),
                name=data.name,
                description=data.description,
                created_at=datetime.now(tz=timezone.utc),
            )
            self._store[item.id] = item
            return item

    async def get(self, item_id: str) -> Item:
        async with self._lock:
            return self._store[item_id]

    async def list(self) -> list[Item]:
        async with self._lock:
            return list(self._store.values())

    async def update(self, item_id: str, data: ItemUpdate) -> Item:
        async with self._lock:
            existing = self._store[item_id]
            updated = Item(
                id=existing.id,
                name=data.name if data.name is not None else existing.name,
                description=data.description
                if data.description is not None
                else existing.description,
                created_at=existing.created_at,
            )
            self._store[item_id] = updated
            return updated

    async def delete(self, item_id: str) -> None:
        async with self._lock:
            del self._store[item_id]


_item_store = ItemStore()


def get_item_store() -> ItemStore:
    return _item_store
