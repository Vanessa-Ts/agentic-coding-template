# Walkthrough: items-resource Session

A step-by-step record of the `/items` CRUD feature being built using the full agentic loop. Includes real hook blocks and a deliberately-broken push attempt.

---

## Phase 4 commit graph

```
$ git log --oneline feat/items-resource
a3f91c2 tests: 15 async tests for /items CRUD (happy · 422 · 404)
7e84b01 routes: wire items_router into main.py via include_router
c2d150b routes: POST/GET/PUT/DELETE /items endpoints with Depends(get_item_store)
91d4a88 store: in-memory ItemStore with asyncio.Lock
4b7e053 models: ItemCreate, ItemUpdate, Item with frozen config
```

Each commit covers exactly one logical unit, as required by CLAUDE.md branch rules.

---

## Hook block: attempt to use pip

During the session, the implementer attempted to install `httpx` via pip rather than uv:

```
Tool: Bash
Command: pip install httpx

Blocked: use `uv add <pkg>` instead — see uv-workflows skill
```

Corrected to:

```bash
uv add --dev httpx
```

---

## Hook block: attempt to commit on main

Early in the session, before creating the feature branch:

```
Tool: Bash
Command: git commit -m "add item model"

Blocked: git commit directly on main branch
```

The implementer then created the correct branch:

```bash
git checkout -b feat/items-resource
```

---

## Deliberately broken push: mypy gate fires

To demonstrate the push gate, a function with a missing type annotation was added to `src/app/routes/items.py`:

```python
def bad_untyped(x):  # no type annotation
    return x
```

Attempting to push:

```
Tool: Bash
Command: git push origin feat/items-resource

Blocked: quality gate failed — mypy --strict src/

src/app/routes/items.py:7: error: Function is missing a type annotation [no-untyped-def]
    def bad_untyped(x):  # deliberate mypy violation for WALKTHROUGH demo
    ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Found 1 error in 1 file (checked 10 source files)
```

The push was blocked inline — no state file, no marker, just `exit(2)` from `pre_push_quality_gate.py`. The fix (removing the untyped function) unblocked the push on the next attempt.

---

## /review output (post-fix)

```
## Quality Review

LGTM — no quality violations found.

## Security Review

LGTM — no security issues found.
```

Both reviewers ran in parallel against `git diff main...HEAD`.

---

## /ship run

```bash
$ uv run ruff format --check .
All checks passed!

$ uv run ruff check .
All checks passed!

$ uv run mypy --strict src/
Success: no issues found in 10 source files

$ uv run pytest -x -q
18 passed in 0.30s
```

All four gates green. PR created:

```
gh pr create \
  --title "feat/items-resource" \
  --body "..."

https://github.com/Vanessa-Ts/agentic-coding-template/pull/1
```

---

## Session cost

```
$ /cost
Session total: ~$0.14
  planner (Sonnet 4.6):            $0.03
  implementer (Sonnet 4.6):        $0.09
  quality-reviewer (Haiku 4.5):    $0.01
  security-reviewer (Haiku 4.5):   $0.01
```

---

## Lessons from this session

1. **The push gate is the last line of defence, not the first.** Running `uv run pytest -x` locally before pushing saves a round-trip.
2. **Hook blocks are informative, not cryptic.** Every `Blocked:` message names the hook and the exact pattern that fired. See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
3. **Two reviewer agents in parallel is faster than one.** Quality and security concerns are independent — running them concurrently cuts review time roughly in half.
4. **The 3-commit minimum per logical unit pays off in review.** When the quality-reviewer cited a violation, it was easy to point to the exact commit responsible.
