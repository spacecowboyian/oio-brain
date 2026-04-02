---
title: The Goblin — Maintenance Log
type: vehicle
status: active
owner: Ian Jennings
updated: 2026-03-29
tags: [vehicle, mr2, goblin, maintenance, engine, diagnostic, steering, quick-rack]
source_of_truth: true
summary: Maintenance and diagnostic history for The Goblin (1985 MR2 AW11). Append-only log — new entries go at the top.
---

# The Goblin — Maintenance Log

> Append-only. New entries go at the top.

---

## 2026-03-18 — Quick Rack Recovery and Installation

**Context:** KCRX E1 was scheduled for Sunday March 22. The Goblin needed the quicker-than-stock steering rack installed before that event. Ian went to Alex's house to recover the rack from the old rallycross MR2 that had been sold to Alex for $200. Alex knew the rack was coming back. The rack was pulled and installed on the Goblin the same day.

---

### What Was Done

- Drove to Alex's house to recover the upgraded steering rack from the old rallycross car
- Removed rack from Alex's car (disassembly: AC line access, brackets, tie rod ends, rack mounting hardware)
- Rack inspected and confirmed in excellent condition — nearly new, only used for a few rallycross events
- Rack brought home and installed on the Goblin same day
- Goblin ready for KCRX E1 on March 22

---

### Key Lesson: Steering Column U-Joint Connector

The **steering column U-joint connector** is the main recurring pain point in MR2 rack removal. Even when the rack itself is fine and surrounding hardware is manageable, the U-joint connector creates bad tool angles, poor access, and significant frustration. This is the part that turns what should be a straightforward job into a multi-attempt grind under the car. Budget extra time whenever this connector is involved.

---

### Condition of Recovered Rack

| Attribute | Status |
|---|---|
| Overall condition | Excellent — nearly new |
| Rallycross events on it | A few only |
| Reusable | Yes — worth every bit of the recovery effort |

---

### Status After Work

- **Quick rack now installed on The Goblin** — upgrade over stock
- Goblin competed at KCRX E1 (March 22, Ray Rocks) with the new rack installed
- Steering feel improvement immediately noticeable

---

## 2026-03-28 — Follow-Up Diagnostic Findings

**Context:** Additional testing performed after the initial post-rallycross diagnostic (see entry below). Wet compression test on cyl 4 and a focused borescope re-inspection of cyl 4 valves.

---

### Wet Compression Test — Cylinder 4

| Condition | PSI |
|---|---|
| Dry (initial) | 35 |
| Wet (oil added) | ~60 |

**Observations:**
- Compression increased after oil was introduced to cylinder 4
- Recovery was partial — compression did not return to a range consistent with a healthy cylinder
- The partial increase suggests ring sealing is a contributing factor, but rings alone do not account for the full compression loss

---

### Additional Borescope — Cylinder 4 (Focused Re-Inspection)

**Valve Motion**
- Piston rotated while observing valves
- Both intake and exhaust valves observed to open and close during engine rotation
- No visible indication of a stuck valve or mechanical interference

**Valve Condition (All Cylinders)**
- Valve faces and edges are heavily carbon-coated across all inspected cylinders
- Carbon buildup is significant enough to obscure clean sealing surfaces
- Whether carbon is interfering with sealing cannot be confirmed visually

**Cylinder 4 Oil (Reconfirmed)**
- Oil remains visible in cylinder 4
- Appears to be present from upper region of cylinder — source still unconfirmed

---

### Key Findings (Non-Interpretive)

- Cyl 4 compression increased from 35 PSI to ~60 PSI with oil added — partial recovery only
- Cyl 4 valves exhibit normal motion during engine rotation
- No obvious mechanical damage visible in piston or valve movement in cyl 4
- Valve sealing surfaces cannot be visually confirmed due to carbon buildup
- Carbon accumulation on valves is significant across all inspected cylinders
- Oil remains present in cyl 4 despite low compression

---

### Updated Unknowns (as of 2026-03-28 follow-up)

- Exact contribution of ring sealing vs. valve sealing in cyl 4 — wet test narrows but does not resolve
- Whether carbon buildup is interfering with valve sealing in cyl 4
- Exact source of oil entering cyl 4
- Relationship between cyl 4 sealing loss and bottom-end bearing failure
- Sequence of failure events (top-end vs. bottom-end)

---

### Status After Follow-Up

- **Engine: Non-operational**
- Wet compression test confirms partial ring involvement in cyl 4 — but valve sealing remains unverified due to carbon
- Evidence continues to indicate multiple unresolved failure mechanisms
- Next step: rebuild vs. replace decision pending

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
