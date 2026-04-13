---
title: Template — Decision Entry
type: core
status: draft
owner: Ian Jennings
updated: YYYY-MM-DD
tags: [template, decision]
source_of_truth: false
summary: Template for a single decision entry to be added to core/decisions-log.md. Copy the formatted block below and append it to the log, newest first.
---

# Decision Entry Template

Copy the block below and paste it at the top of `core/decisions-log.md` (below the format instructions and above the previous entry).

```markdown
## YYYY-MM-DD — [Decision Title]

**Decision:** [What was decided. One or two clear sentences.]

**Why:** [Rationale. What made this the right call? What alternatives were considered?]

**Implications:** [What changes as a result? Any follow-up actions, documents to update, or things that now depend on this decision?]
```

---

## Example

```markdown
## 2026-04-15 — Goblin Will Skip the April Rallycross Event

**Decision:** The Goblin will not compete at the April 15 rallycross event. Ian will attend in Fitty Cent only.

**Why:** Motor rebuild is not complete and a shakedown run at a competitive event is too risky without a proper test day first.

**Implications:** Update current-state.md and active-priorities.md. Plan a test day before the next event. The Goblin's season debut episode moves to May at the earliest.
```

---

## Where to Log It

File: [`core/decisions-log.md`](../decisions-log.md)

Add newest entries at the top, below the format instructions block.
