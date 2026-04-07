# Nessie — Setup Notes

> Drag-focused configuration for the Cressida Wagon.

*Last updated: April 2026*

---

## Current Configuration

| System | Spec / Notes |
|---|---|
| Engine | 5M-GE (inline-six, Toyota) — stock configuration, future V8 swap planned |
| Transmission | [Update as known] |
| Differential | [Update as known] — rear end plan pending (welded vs stock vs 8.8 swap) |
| Suspension | Work in progress — front ride height issues, Celica front springs being tested |
| Tires | Rubbing at fenders — clearance work needed |
| Wheels | Offset/backspacing issues causing tire rub |
| Brakes | [Update as known] |
| Fuel System | Overhaul in progress — moving to generic tank, V8-compatible design |
| Belt/Tensioning | Known issues — needs resolution before performance runs |
| Safety equipment | [Update — required for dragstrip events] |

---

## Dragstrip Safety Requirements

### Thunder Valley Raceway Park

For the Friday Night Test & Tune target:
- Long pants and a shirt with sleeves are required
- No sandals or flip-flops
- Working seatbelt required
- Helmet required at 13.99 or quicker
- Roll bar, 5-point harness, and fire jacket required at 11.49 or quicker
- Roll cage, full fire suit, and window net required at 9.99 or quicker
- 2008 and newer factory-airbag cars can run to 9.99 without roll bar or 5-point harness, but helmet, fire jacket, and pants are still required
- Off-road tires are not permitted

### Mo-Kan Dragway

For Fun Drags fallback:
- Helmet required at 14.00 or quicker in the quarter-mile, or 8.50 or quicker in the eighth-mile
- Seat belt required in all cars
- Three inches of ground clearance required at the starting line
- Catch-can required on all radiators
- Fuel system and battery placement must satisfy track tech
- Loose items should be removed before staging

### Practical Prep Sequence

1. Replace the battery
2. Do a local shakedown
3. Capture baseline RaceBox timing
4. Check fluids, belts, lug nuts, and wheel torque
5. Verify brakes, tires, and driveshaft clearance
6. Bring helmet, long pants, and a sleeved shirt on race day

---

## Build Progress

### Tier 1 — Must Solve to Move Forward
| Task | Status | Notes |
|---|---|---|
| Fix belt/tensioning reliability | Open | Potential accessory drive alignment or pulley issues |
| Resolve front ride height | In Progress | Testing stock Celica front springs |
| Eliminate fender rubbing | Open | Likely requires wheel/tire adjustment or fender clearance work |

### Tier 2 — Foundational System Work
| Task | Status | Notes |
|---|---|---|
| Fuel system overhaul | In Progress | Generic tank, V8-compatible, new lines/sender/pump |
| Rear end planning | Open | Welded diff vs stock vs Ford 8.8/9-inch swap |

### Tier 3 — Event Preparation
| Task | Status | Notes |
|---|---|---|
| Primary track / date | Planned | Thunder Valley Friday Night Test & Tune on May 15, 2026 |
| Fallback track / date | Planned | Mo-Kan Fun Drags on May 29, 2026 |
| Battery replacement | Open | Must happen before shakedown |
| Shakedown / baseline timing | Open | Capture first RaceBox pass before the strip |
| Fluids / nut-and-bolt check | Open | Final pre-track inspection |

---

## Known Problem Areas

### Front Ride Height / Suspension
**Status:** In Progress  
**Impact:** Tire clearance, suspension travel, weight transfer, overall stance

Current setup is not finalized. Testing stock Celica front springs. The ride height may be too low, causing rubbing issues, or the spring rate may not be well-matched to the application. This interacts with fender clearance and wheel/tire choices.

### Fender Rubbing
**Status:** Open  
**Impact:** Limits usable tire size, risks tire damage

Likely causes:
- Wheel/tire size too aggressive
- Ride height too low
- Incorrect offset/backspacing
- Insufficient fender clearance

### Fuel System
**Status:** In Progress  
**Scope:** Full overhaul with future V8 swap in mind

**Strategic intent:** Build it once, avoid rework when moving to higher power.

Planned work:
- Generic fuel tank (replacement or custom mounting)
- Pump selection and placement
- Feed/return routing
- Venting system
- Filtration
- Electrical (relay, wiring)
- Compatibility with future EFI

### Belt / Tensioning Issues
**Status:** Open  
**Impact:** Reliability issue, potential failure under load

Possible causes:
- Accessory drive alignment
- Worn or incorrect pulleys
- Improper tensioning method
- Mismatched components from prior work

---

## Build Philosophy

Based on current direction:

1. **Practical Over Perfect** — Not chasing OEM correctness; willing to mix parts across platforms (e.g., Celica springs)
2. **Future-Proofing Key Systems** — Fuel system designed for future V8; avoiding rework
3. **Solve Constraints First** — Ride height, clearance, basic mechanical reliability before pushing performance
4. **Open-Ended Platform** — Nessie is not locked into a final configuration; flexible project that can evolve significantly

---

## Setup History

| Date | Change | Notes |
|---|---|---|
| 2026-04 | Front suspension testing | Evaluating stock Celica front springs for ride height |
| 2026-04 | Fuel system planning | Designing V8-compatible fuel system with generic tank |
| | | |
