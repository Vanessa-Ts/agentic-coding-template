# Spec-Feature Skill

**Trigger paths**: `docs/specs/**`
**Trigger keywords**: spec, interview, feature request, requirements, spec out, define feature, what should X do

---

## Purpose

Before writing a plan or any code, capture requirements through a structured interview. The output is a `docs/specs/<feature>.md` file that feeds into `/plan`.

---

## Interview — 6 questions

Ask these questions **one at a time** (wait for the answer before asking the next):

1. **Who uses it?** — which user role or system actor triggers this feature?
2. **What does it do?** — one sentence: "Given X, when Y, then Z."
3. **Why now?** — what problem or opportunity drives this? What's the cost of not building it?
4. **Acceptance criteria** — list 3–5 specific, testable conditions that mean "done". Format: "Given / When / Then."
5. **Edge cases & constraints** — what inputs, states, or conditions must be explicitly handled or rejected?
6. **Out of scope** — what related things will NOT be built in this iteration?

---

## Output — `docs/specs/<feature>.md`

```markdown
# Spec: <feature name>

**Date**: <YYYY-MM-DD>
**Author**: <from git config>
**Status**: draft

## Summary
One sentence: Given X, when Y, then Z.

## Actor
<who triggers this>

## Motivation
<why now — cost of not building>

## Acceptance criteria
- [ ] Given <state>, when <action>, then <outcome>
- [ ] ...

## Edge cases & constraints
- <explicit handling required>
- ...

## Out of scope
- <explicitly excluded>
- ...

## Open questions
- <anything unresolved after the interview>
```

---

## Rules

- Never invent requirements — only write what the user confirmed.
- "Open questions" must list anything that could not be resolved in the interview.
- After writing the spec, tell the user: `Spec written to docs/specs/<feature>.md — run /plan <feature> to produce the implementation plan.`
- Do not start the plan or write any code.
