# Paste-Ready Plan-Mode Prompts

Ten prompts you can paste directly into a `/plan` invocation. Each targets a common scenario for AI engineers building on this template.

---

## 1. Claude streaming chat endpoint

```
/plan streaming-chat-endpoint
```

Scope: add `POST /chat` that accepts `{"messages": [...], "model": "claude-sonnet-4-6"}` and streams the response as Server-Sent Events using the Anthropic SDK (`stream=True`). Use the `ai-service-generator` agent. Return `data: <token>\n\n` chunks; send `data: [DONE]\n\n` on completion. Tests verify: happy path SSE stream, 422 on missing messages field, 400 on unsupported model string.

---

## 2. API-key auth middleware

```
/plan auth-middleware
```

Scope: add API-key header auth via FastAPI middleware. Requests missing `X-API-Key` return 401. Key is read from settings (Pydantic-settings, `.env.template`). No database. Tests verify 401 on missing key and 200 on valid key.

---

## 3. Structured output extraction

```
/plan structured-output-extraction
```

Scope: add `POST /extract` that accepts `{"text": str, "schema": dict}` and uses `claude-sonnet-4-6` with tool use to extract structured data matching the caller-supplied JSON Schema. Return a validated Pydantic model. Use the `ai-service-generator` agent. Tests verify: correct extraction on a fixture text, 422 on missing fields, graceful 400 when the model cannot satisfy the schema.

---

## 4. Debug a streaming truncation issue

```
/plan debug-stream-truncation
```

Scope: reproduce a bug where `POST /chat` stops emitting SSE tokens mid-response on long outputs. Trace through the Anthropic SDK stream iterator, the FastAPI `StreamingResponse`, and the ASGI send loop. Identify whether the cause is a missing `content_block_delta` handler, a response buffer flush issue, or a client timeout. Propose a fix with a regression test using a mocked stream.

---

## 5. Add error-handling layer

```
/plan error-handling-layer
```

Scope: add a global `@app.exception_handler(Exception)` that logs the traceback and returns `{"detail": "internal server error"}` with status 500. Add specific handlers for `anthropic.RateLimitError → 429`, `anthropic.APIStatusError → 502`, and `KeyError → 404`. Ensure no bare `except` clauses remain in `src/`. Tests verify all handlers fire correctly.

---

## 6. CLAUDE.md audit

```
/plan claudemd-audit
```

Scope: read-only pass over all files in `src/` and `tests/`. Flag every CLAUDE.md violation: missing return types, `TestClient` usage, missing `response_model`/`status_code`, Pydantic v1 idioms (`.dict()`, `.from_orm()`), bare `except`. Output a numbered list with file:line references.

---

## 7. LLM cost and latency profiling

```
/plan llm-cost-latency-profiling
```

Scope: instrument every Anthropic SDK call in `src/` to record input tokens, output tokens, latency (ms), and model name. Expose `GET /metrics` returning aggregated totals per model. Use an in-memory store with `asyncio.Lock`. Do not implement a database. Tests verify: metrics increment on a mocked SDK call, the endpoint returns correct totals, concurrent calls do not race.

---

## 8. Conversation thread resource

```
/plan conversation-threads
```

Scope: add a `threads` resource — `POST /threads` creates a thread and returns `thread_id`; `POST /threads/{thread_id}/messages` appends a user turn and calls `claude-sonnet-4-6` with the full history, returning the assistant reply. Store threads in memory (`asyncio.Lock`). Use the `ai-service-generator` agent. Tests: create thread, append two turns, verify history grows, 404 on unknown thread.

---

## 9. Prompt template module

```
/plan prompt-template-module
```

Scope: add `src/app/prompts/` with a `PromptTemplate` class that loads `.txt` templates from `src/app/prompts/templates/`, performs `{variable}` substitution via `str.format_map`, and raises a typed `MissingVariableError` on unresolved keys. Expose `POST /prompts/render` accepting `{"template": str, "variables": dict}`. Tests: happy path render, missing variable → 400, unknown template name → 404.

---

## 10. Pre-merge check

```
/plan pre-merge-check
```

Scope: run the full quality gate (`ruff format --check`, `ruff check`, `mypy --strict src/`, `pytest -x`), then invoke `/review` (architecture + performance + security in parallel). If violations exist, propose the minimal diff to fix them. Output a go/no-go recommendation with evidence.
