---
paths:
  - "tests/**"
  - "**/conftest.py"
trigger: "Use whenever editing tests/, conftest.py, or writing tests. Triggers on pytest, async test, httpx, fixture, parametrize, or TestClient mentions."
---

# Pytest Patterns

## Async client — never TestClient

```python
# CORRECT
from httpx import AsyncClient, ASGITransport
from app.main import app

async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
    response = await client.get("/items")

# WRONG — do not use
from starlette.testclient import TestClient
```

## Fixtures

- Use `@pytest_asyncio.fixture` for async fixtures (not `@pytest.fixture`).
- Keep fixture chains ≤ 2 levels deep.
- Use `monkeypatch` to override env vars — never mutate `os.environ` directly.

## Parametrize over loops

```python
# CORRECT
@pytest.mark.parametrize("name,status", [("", 422), ("x" * 101, 422)])
async def test_create_invalid(client, name, status): ...

# WRONG
for name in ["", "x" * 101]:
    ...
```

## Minimum test coverage per route

Every new route requires at least 3 tests:

| # | Scenario | Assert |
|---|---|---|
| 1 | Happy path | Expected status + response shape |
| 2 | Validation failure | 422 + error detail |
| 3 | Not found / missing resource | 404 |

## conftest.py baseline

```python
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from collections.abc import AsyncGenerator

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
```
