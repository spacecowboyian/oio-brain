---
title: The Goblin — Maintenance Log
type: vehicle
status: active
owner: Ian Jennings
updated: 2026-03-28
tags: [vehicle, mr2, goblin, maintenance, engine, diagnostic]
source_of_truth: true
summary: Maintenance and diagnostic history for The Goblin (1985 MR2 AW11). Append-only log — new entries go at the top.
---

# The Goblin — Maintenance Log

> Append-only. New entries go at the top.

---

## 2026-03-28 — Post-Rallycross Engine Failure Diagnostic

**Context:** Engine failed during/after a rallycross event. This is the full diagnostic MRI conducted on 2026-03-28.

---

### Symptoms During Event

- Loss of power / inability to rev
- White smoke observed
- Audible knock present
- Engine condition worsened progressively over the event
- Bearings reported to have locked up near the end of the event

---

### Ignition Inspection

- Cylinder #1 spark plug wire found **loose / not fully seated**

---

### Spark Plug Inspection (Pulled in order: 4-3-2-1)

| Cylinder | Condition |
|---|---|
| 4 | Dry, dark |
| 3 | Slight oil contamination |
| 2 | Oily |
| 1 | Most oil contamination |

**Pattern:** Oil presence increases from cylinder 4 → 1.

---

### Compression Test Results

| Cylinder | PSI |
|---|---|
| 1 | 165 |
| 2 | 152 |
| 3 | 142 |
| 4 | **35** |

**Observations:**
- Cylinders 1–3 show a decreasing compression trend
- Cylinder 4 is significantly lower than all others — catastrophic drop

---

### Borescope Inspection

**Cylinder Walls**
- Vertical witness marks present on all cylinders
- No scoring detectable by fingernail

**Pistons**
- No visible damage
- No visible impact or deformation

**Valves**
- Heavy carbon buildup observed across cylinders

**Cylinder 4 (notable)**
- Visible oil present in cylinder
- Oil source appears to be from upper area — not confirmed
- Possible localized horizontal marking observed (not circumferential)

---

### Bottom End

- Audible knock confirmed
- Bearing failure confirmed — bearings locked up during event

---

### Key Findings (Non-Interpretive)

- Cylinder 4 has severely reduced compression (35 PSI)
- Oil present in cylinder 4 despite low compression
- Cylinders 1–3 maintain higher compression but show decreasing trend
- Oil contamination pattern across plugs does **not** match compression pattern
- Bottom end has confirmed failure (bearing lock-up)
- Top end shows heavy carbon buildup and oil presence in at least cylinder 4
- Ignition issue on cylinder 1 (loose plug wire) — may be pre-existing or event-related

---

### Unknowns (as of 2026-03-28)

- Exact source of oil in cylinder 4
- Exact failure point(s) in the bottom end
- Whether top-end and bottom-end failures are causally related
- Whether compression loss in cylinder 4 is due to valves, head gasket, rings, or other factors
- Timing and sequence of failure events during the rallycross run

---

### Status After Diagnostic

- **Engine: Non-operational**
- Multiple confirmed failure modes: compression loss (especially cyl 4), oil contamination, bearing failure
- Root cause not yet isolated
- Next step: decide whether to rebuild this 4AG or replace it
