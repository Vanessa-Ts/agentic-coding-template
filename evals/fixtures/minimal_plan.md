# Plan: ping-endpoint

## Scope

Add a single read-only health-check endpoint `GET /ping` that returns `{"status": "ok"}` with
HTTP 200. No persistence, no authentication. Wire into `main.py` via a new router module. Does
not touch any existing route.

## Endpoints

| Method | Path    | Request body | Response body          | Status codes |
|--------|---------|--------------|------------------------|--------------|
| GET    | /ping   | —            | `{"status": "ok"}`     | 200          |

## Models

```python
class PingResponse(BaseModel):
    status: str
```

## Store interface

None required.

## Test plan

- `GET /ping` · happy path · 200 with `{"status": "ok"}`
- `GET /ping` · wrong method (POST) · 405
- `GET /ping` · response schema correct · assert `status` field present

## Open questions

None.
