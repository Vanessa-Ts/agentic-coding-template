# Hooks

| Hook | Event | Purpose | Failure mode prevented |
|---|---|---|---|
| `block_secrets_and_env.py` | PreToolUse Edit\|Write\|MultiEdit | Blocks writes to `.env` and files containing secret patterns (AWS keys, GH tokens, Anthropic keys, private keys) | Accidental secret commit |
| `block_bash_dangers.py` | PreToolUse Bash | Blocks `rm -rf`, force-push, `--hard` reset, push to main, and commit on main branch | Destructive repo/history operations |
| `enforce_uv.py` | PreToolUse Bash | Blocks `pip install`, `pip3 install`, `python -m pip`, `poetry add` | Dependency drift outside uv lockfile |
| `autoformat_python.py` | PostToolUse Edit\|Write\|MultiEdit | Runs `ruff format` then `ruff check --fix` on any changed `.py` file | Stale formatting, auto-fixable lint violations |
| `pre_push_quality_gate.py` | PreToolUse Bash | Blocks `git push` unless `ruff`, `mypy --strict`, and `pytest` all pass inline | Pushing code that fails the quality gate |

## Exit codes

- `exit(0)` — allow the tool use to proceed.
- `exit(2)` — block the tool use and print reason to stderr. Never use `exit(1)`.

## Adding a new hook

1. Create `<name>.py` in this directory (stdlib only — no third-party imports).
2. Read `sys.stdin` as JSON to access `tool_name` and `tool_input`.
3. Register it in `.claude/settings.json` under the appropriate event and matcher.
