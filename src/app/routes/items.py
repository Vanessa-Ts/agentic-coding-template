from fastapi import APIRouter, Depends, HTTPException, status

from app.models.item import Item, ItemCreate, ItemUpdate
from app.store.item_store import ItemStore, get_item_store


router = APIRouter()


@router.post("", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: ItemCreate,
    store: ItemStore = Depends(get_item_store),
) -> Item:
    return await store.create(payload)


@router.get("", response_model=list[Item], status_code=status.HTTP_200_OK)
async def list_items(
    store: ItemStore = Depends(get_item_store),
) -> list[Item]:
    return await store.list()


@router.get("/{item_id}", response_model=Item, status_code=status.HTTP_200_OK)
async def get_item(
    item_id: str,
    store: ItemStore = Depends(get_item_store),
) -> Item:
    try:
        return await store.get(item_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )


@router.put("/{item_id}", response_model=Item, status_code=status.HTTP_200_OK)
async def update_item(
    item_id: str,
    payload: ItemUpdate,
    store: ItemStore = Depends(get_item_store),
) -> Item:
    try:
        return await store.update(item_id, payload)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )


@router.delete(
    "/{item_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_item(
    item_id: str,
    store: ItemStore = Depends(get_item_store),
) -> None:
    try:
        await store.delete(item_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
