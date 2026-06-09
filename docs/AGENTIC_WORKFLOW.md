# Agentic Workflow

This document explains how the Research→Plan→Execute→Review→Ship loop works, when to escalate to a more powerful model, the hook system, and the self-correcting review loop.

---

## Loop Diagram

```
┌─────────────┐
│  Research   │  Read codebase, open questions, understand context
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Plan     │  /plan <feature>  →  planner agent  →  docs/plans/<feature>.md
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Execute   │  /implement  →  implementer agent  →  feat/<name> branch
└──────┬──────┘
       │
       ▼
┌─────────────┐     violations found
│   Review    │  ─────────────────────► fix → re-review (max 2 iterations)
└──────┬──────┘
       │ LGTM
       ▼
┌─────────────┐
│    Ship     │  /ship  →  quality gate  →  gh pr create
└─────────────┘
```

Each phase maps to a command:

| Phase | Command | Agent invoked |
|---|---|---|
| Plan | `/plan <feature>` | `planner` |
| Execute | `/implement` | `implementer` |
| Review | `/review` | `architecture-reviewer` + `performance-reviewer` + `security-reviewer` (parallel) |
| Ship | `/ship` | none — runs shell commands directly |

---

## When to Escalate to `--opus`

Append `--opus` to `/plan` to use `claude-opus-4-8` (deeper reasoning, higher cost):

```
/plan auth-middleware --opus
/plan dependency-upgrade --opus
```

Use `--opus` when:

- The feature touches multiple cross-cutting concerns (auth, middleware, global error handling).
- The spec is ambiguous and the planner needs to weigh trade-offs rather than follow a clear pattern.
- A previous planning attempt produced a plan that the implementer could not execute without backtracking.
- The change involves upgrading a major dependency with potential breaking API surface.

Keep the default (Sonnet) for routine CRUD features, test gap fills, and single-module refactors — the quality is comparable and the cost is significantly lower.

---

## Hook Semantics

Hooks are Python scripts in `.claude/hooks/`. The harness injects a JSON payload via stdin and interprets the exit code.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Allow the tool use to proceed |
| `2` | Block the tool use; print reason to stderr |

Never use `exit(1)` — it is reserved for unexpected Python exceptions and will produce confusing output.

### Stdin JSON shape

```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "git push origin feat/items-resource"
  }
}
```

For file-writing tools (`Edit`, `Write`, `MultiEdit`), `tool_input` contains `file_path`, `content` / `new_string`, etc.

### How to add a hook

1. Create `<name>.py` in `.claude/hooks/`. Use stdlib only — no third-party imports.
2. Read and parse `sys.stdin` as JSON to access `tool_name` and `tool_input`.
3. Perform your check. On failure: print a human-readable reason to `sys.stderr`, then `sys.exit(2)`.
4. Register the hook in `.claude/settings.json` under the correct event key and matcher:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "python .claude/hooks/<name>.py" }]
      }
    ]
  }
}
```

Events: `PreToolUse`, `PostToolUse`. Matchers: `Bash`, `Edit`, `Write`, `MultiEdit`, or a regex.

### Current hooks

| Hook | Event | Matcher |
|---|---|---|
| `block_secrets_and_env.py` | PreToolUse | `Edit\|Write\|MultiEdit` |
| `block_bash_dangers.py` | PreToolUse | `Bash` |
| `enforce_uv.py` | PreToolUse | `Bash` |
| `autoformat_python.py` | PostToolUse | `Edit\|Write\|MultiEdit` |
| `pre_push_quality_gate.py` | PreToolUse | `Bash` |

---

## Self-Correcting Review Loop

`/review` invokes both reviewer agents in parallel. If either finds violations:

```
Iteration 1:
  /review  →  violations found
  →  fix violations  →  /review again

Iteration 2:
  /review  →  violations found
  →  fix violations  →  /review again

Iteration 3 (if still failing):
  Escalate to human — do not auto-fix further
```

**Maximum 2 self-correcting iterations.** On the third failure, the review stops and surfaces all remaining violations to the user for a manual decision. This prevents infinite fix loops when a violation is ambiguous or the fix itself introduces a new violation.

Each iteration counts as one round: both agents run, both outputs are collected, violations are addressed together.
