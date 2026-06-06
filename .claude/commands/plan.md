Read CLAUDE.md, then invoke the **planner** agent to produce an implementation plan for the feature named `$ARGUMENTS`.

Instructions for the planner agent:
- The feature name is: `$ARGUMENTS`
- Write the plan to `docs/plans/$ARGUMENTS.md`
- Follow the output format in your system prompt exactly (scope, endpoints, models, store interface, test plan, open questions)
- Read all relevant existing source files before writing
- Keep the plan under 150 lines

If `$ARGUMENTS` ends with `--opus`, use the claude-opus-4-8 model for this planning session (more complex features that need deeper reasoning).

After the plan is written, print:
```
Plan written to docs/plans/$ARGUMENTS.md
Next: run /implement to build it.
```
