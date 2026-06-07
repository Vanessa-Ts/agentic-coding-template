# Troubleshooting Hook Blocks

Every `Blocked:` message comes from a hook in `.claude/hooks/`. This page decodes each one and tells you exactly what to do.

---

## `Blocked: direct write to .env file`

**Hook:** `block_secrets_and_env.py`

**Cause:** A tool attempted to write directly to a `.env` file.

**What to do instead:**
- Edit `.env.template` to add the new variable with a placeholder value.
- Run `cp .env.template .env` locally and fill in the real value by hand.
- Never commit `.env` — it is in `.gitignore`.
- In tests, use `monkeypatch.setenv(...)` to override environment values.

---

## `Blocked: secret pattern '...' found in <file>`

**Hook:** `block_secrets_and_env.py`

**Cause:** The content being written matched one of the secret regexes. Patterns detected include AWS access keys (`AKIA…`), GitHub personal access tokens (`ghp_…`), OpenAI keys (`sk-…`), Anthropic keys (`sk-ant-…`), and PEM private key headers.

**What to do instead:**
- Move the value to `.env` (via `.env.template` → copy).
- Reference it through `settings` (`src/app/core/config.py`) using `pydantic-settings`.
- If this is test data, use a clearly-fake placeholder (e.g., `test-key-not-real`).

---

## `Blocked: dangerous pattern '...' in command`

**Hook:** `block_bash_dangers.py`

**Cause:** The Bash command matched one of the blocked patterns:
- `rm -rf` — recursive force delete
- `git push --force` / `git push -f` (without `--force-with-lease`) — rewrites remote history
- `git reset --hard` — discards working-tree changes irreversibly
- `git push ... main` — direct push to the main branch

**What to do instead:**
- For `rm -rf`: use targeted `rm` with explicit paths; or `git clean -fd` after verifying scope.
- For force-push: use `git push --force-with-lease` (safe force) if you genuinely need it.
- For `reset --hard`: use `git restore .` (working tree only) or `git reset HEAD~1` (soft) first.
- For pushing to main: push to a feature branch (`git push origin feat/<name>`) and open a PR.

---

## `Blocked: git commit directly on main branch`

**Hook:** `block_bash_dangers.py`

**Cause:** A `git commit` was attempted while on the `main` branch.

**What to do instead:**

```bash
git checkout -b feat/<your-feature-name>
git commit -m "your message"
```

All work must happen on a `feat/<name>` branch. See CLAUDE.md branch rules.

---

## `Blocked: use uv add <pkg> instead — see uv-workflows skill`

**Hook:** `enforce_uv.py`

**Cause:** The Bash command contained `pip install`, `pip3 install`, `python -m pip`, or `poetry add`.

**What to do instead:**

```bash
uv add <pkg>           # runtime dependency
uv add --dev <pkg>     # dev/test-only dependency
```

`uv` is the only approved dependency manager. It writes to `uv.lock` and keeps the environment reproducible. Always commit both `pyproject.toml` and `uv.lock`.

---

## `Blocked: quality gate failed — <check>`

**Hook:** `pre_push_quality_gate.py`

**Cause:** A `git push` was attempted but one of the four quality checks failed:
- `ruff format --check .` — file not formatted
- `ruff check .` — lint violation
- `mypy --strict src/` — type error
- `pytest -x -q` — test failure

The full output of the failing check is printed below the block message.

**What to do:**
1. Read the output — it tells you exactly which file and line failed.
2. Fix the issue locally.
3. Stage and commit the fix.
4. Re-run `git push` — the gate runs again inline.

**Quick commands:**

```bash
uv run ruff format .                  # auto-format
uv run ruff check --fix .             # auto-fix lint
uv run mypy --strict src/             # type errors (manual fix)
uv run pytest -x                      # first failing test
```

Run all four manually before pushing to catch failures early:

```bash
uv run ruff format --check . && uv run ruff check . && uv run mypy --strict src/ && uv run pytest -x
```
