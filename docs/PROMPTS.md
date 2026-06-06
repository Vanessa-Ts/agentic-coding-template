# Paste-Ready Plan-Mode Prompts

Ten prompts you can paste directly into a `/plan` invocation. Each targets a common scenario in this codebase.

---

## 1. New resource

```
/plan orders-resource
```

Scope: in-memory CRUD for an `Order` resource (5 endpoints, Pydantic v2 models, asyncio.Lock store, 15 tests). Follow the same pattern as `src/app/routes/items.py`.

---

## 2. Middleware — auth, CORS, rate-limit

```
/plan auth-middleware
```

Scope: add API-key header auth via FastAPI middleware. Requests missing `X-API-Key` return 401. Key is read from settings (Pydantic-settings, `.env.template`). No database. Tests verify 401 on missing key and 200 on valid key.

---

## 3. Dependency upgrade

```
/plan dependency-upgrade
```

Scope: audit `pyproject.toml` for outdated packages (`uv lock --upgrade --dry-run`), upgrade FastAPI and httpx, confirm `uv run pytest -x` passes, confirm `mypy --strict src/` passes. Document any breaking API changes.

---

## 4. Debug a 500 error

```
/plan debug-500
```

Scope: reproduce a 500 from `POST /items` with an empty name field. Trace through `ItemCreate` validation, the store, and the exception handler. Identify whether the issue is a missing `@app.exception_handler`, a Pydantic field constraint, or an unhandled `KeyError`. Propose a fix with a regression test.

---

## 5. Add error-handling layer

```
/plan error-handling-layer
```

Scope: add a global `@app.exception_handler(Exception)` that logs the traceback and returns `{"detail": "internal server error"}` with status 500. Add a specific handler for `KeyError → 404`. Ensure no bare `except` clauses remain in `src/`. Tests verify both handlers fire correctly.

---

## 6. CLAUDE.md audit

```
/plan claudemd-audit
```

Scope: read-only pass over all files in `src/` and `tests/`. Flag every CLAUDE.md violation: missing return types, `TestClient` usage, missing `response_model`/`status_code`, Pydantic v1 idioms (`.dict()`, `.from_orm()`), bare `except`. Output a numbered list with file:line references.

---

## 7. Performance investigation

```
/plan performance-investigation
```

Scope: profile `GET /items` under 1 000 concurrent synthetic requests using `httpx` + `asyncio.gather`. Identify bottlenecks in the in-memory store (lock contention, list copy). Propose a lock-free read path. Do not implement — output a findings report and proposed change set only.

---

## 8. Test gap analysis

```
/plan test-gap-analysis
```

Scope: compare route handlers in `src/app/routes/` against tests in `tests/`. For each route, verify the 3-test minimum (happy path · 422 · 404). List any gaps with the missing scenario. Propose new test cases in the plan's Test Plan section.

---

## 9. Refactor a module

```
/plan refactor-item-store
```

Scope: extract a generic `BaseStore[T]` from `src/app/store/item_store.py`. The base class handles `asyncio.Lock`, CRUD scaffolding, and `KeyError` semantics. `ItemStore` becomes a thin subclass. All 15 existing tests must still pass; no new public API surface.

---

## 10. Pre-merge check

```
/plan pre-merge-check
```

Scope: run the full quality gate (`ruff format --check`, `ruff check`, `mypy --strict src/`, `pytest -x`), then invoke `/review` (quality + security in parallel). If violations exist, propose the minimal diff to fix them. Output a go/no-go recommendation with evidence.
