# FastAPI Conventions


**paths**:
  - "src/app/routes/**"
  - "src/app/models/**"
  - "src/app/main.py"
**trigger**: "Use whenever editing src/app/routes/, src/app/models/, src/app/main.py, or implementing FastAPI endpoints, dependencies, response models, lifespan, middleware, or DI."
---


## Routes

- All route handlers must be `async def`.
- Every route decorator must include both `response_model` and `status_code`.
- Use the lifespan context manager pattern — never `@app.on_event`.
- One resource = one router module, mounted in `main.py` via `app.include_router()`.

## Dependency injection

- Every swappable collaborator (store, settings, client) must be injected via `Depends()`.
- Never instantiate collaborators inside route handlers.

## Pydantic v2

- Use `.model_dump()` and `.model_validate()` — not `.dict()` or `.from_orm()`.
- Prefer `model_config = {"frozen": True}` on read models.

## Error handling

- Map specific exceptions to HTTP responses via `@app.exception_handler`.
- Never use bare `except`; always catch a named exception type.
- Raise `HTTPException` with a meaningful `detail` string.

## Example route skeleton

```python
@router.get("/{item_id}", response_model=Item, status_code=200)
async def get_item(
    item_id: str,
    store: ItemStore = Depends(get_item_store),
) -> Item:
    try:
        return store.get_by_id(item_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
```
