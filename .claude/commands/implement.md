Read the most recently modified plan in `docs/plans/`, then invoke the **implementer** agent to build it.

Instructions for the implementer agent:
- Locate the latest plan: `ls -t docs/plans/*.md | head -1`
- Read the plan in full before writing any code
- If not already on a feature branch, create one: `git checkout -b feat/<feature-name>` where feature-name matches the plan filename
- Implement in order: models → store → routes → wire into main.py → tests
- Do not modify files outside `src/` and `tests/`
- Every new route needs happy / validation / not-found tests
- Commit each logical unit separately with a descriptive message

After implementation is complete, print a summary of files created/modified and suggest running `/review`.
