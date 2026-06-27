Read CLAUDE.md, then invoke the **planner** agent to produce an implementation plan for the feature named `$ARGUMENTS`.

Before invoking the planner agent, assess task complexity:
- **Use Sonnet** (pass `model: sonnet` to the agent) for: single-file changes, routine CRUD, test gap fills, single-module refactors, typo/naming fixes.
- **Use Opus** (default, no override needed) for: cross-cutting concerns, ambiguous specs, multi-module changes, architectural decisions, dependency upgrades.

Instructions for the planner agent:
- The feature name is: `$ARGUMENTS`
- Write the plan to `docs/plans/$ARGUMENTS.md`
- If `docs/specs/$ARGUMENTS/` exists, read `requirements.md` and `design.md` there before planning
- Follow the output format in your system prompt exactly (scope, approach, endpoints, models, store interface, test plan, open questions)
- Identify at least two implementation approaches; choose one and state why in the `## Approach` section
- Read all relevant existing source files before writing

After the plan is written, print:
```
Plan written to docs/plans/$ARGUMENTS.md
Next: run /implement to build it.
```
