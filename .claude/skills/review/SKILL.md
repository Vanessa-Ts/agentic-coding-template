# Review Skill

**Trigger keywords**: review, code review, check this, LGTM, what's wrong with, is this correct, look at my code

---

## Purpose

Inline code review against project conventions, BCE architecture rules, and Python best practices. For a full automated multi-agent review, use `/review` instead.

---

## BCE architecture checklist

| Layer | File location | Allowed to import from |
|---|---|---|
| Boundary | `routes/` | `models/`, `store/`, `services/` |
| Control | `services/` | `models/`, `store/` |
| Entity | `store/`, `models/` | `models/` only |

Violations to flag:
- Business logic (conditionals, computations) inside route handlers
- `routes/` importing from another `routes/` module
- `store/` or `models/` importing from `routes/` or `services/`
- `main.py` containing any logic beyond router wiring, lifespan, and exception handlers

---

## FastAPI conventions checklist

- [ ] All route handlers are `async def`
- [ ] Every route decorator has `response_model=` and `status_code=`
- [ ] All injectable collaborators use `Depends()` — none instantiated inside handlers
- [ ] Exception handling via `@app.exception_handler` or explicit `HTTPException` — no bare `except`
- [ ] Pydantic v2: `.model_dump()` / `.model_validate()` — never `.dict()` / `.from_orm()`
- [ ] Lifespan via `@asynccontextmanager` — never `@app.on_event`
- [ ] One resource = one router module, mounted in `main.py`

---

## Test conventions checklist

- [ ] `httpx.AsyncClient + ASGITransport` only — `TestClient` is forbidden
- [ ] `@pytest_asyncio.fixture` for async fixtures — never `@pytest.fixture`
- [ ] Each new route has: happy path · validation failure (422) · not-found (404)
- [ ] `pytest.mark.parametrize` over loops
- [ ] No manual event loop management (`asyncio.run`, `loop.run_until_complete`)

---

## Python best practices checklist

- [ ] Full type annotations on every function — no implicit `Any`
- [ ] Return type annotation on every function
- [ ] No mutable default arguments (`def f(x: list = [])` → use `None` + guard)
- [ ] `asyncio.sleep` not `time.sleep` in async context
- [ ] `httpx.AsyncClient` not `requests` in async context
- [ ] `async with` for all context-managed resources

---

## Violation format

When reporting violations, use:
```
[N] <file>:<line> — <rule> — <fix>
```

Group by severity: blocking (must fix before merge) → warning (should fix) → nit (optional).
