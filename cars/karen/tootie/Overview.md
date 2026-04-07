---
title: Tootie — 1965 Chevrolet Suburban
type: vehicle
status: active
owner: Karen
updated: 2026-04-06
tags: [vehicle, suburban, tootie, karen, classic, family, airbags, air-suspension]
source_of_truth: true
summary: Overview of Tootie — Karen's 1965 Chevrolet Suburban. Full-size classic truck on air suspension. Currently in systems-integration phase with focus on ride-height stability, steering behavior, electrical cleanup, and interior finish work. Primary issue is highway steering wander related to air bag pressure/height management. Ian and the kids wrench on it.
---

# Tootie — 1965 Chevrolet Suburban

> Karen's '65 Suburban on airbags. Systems-integration phase: making a functional custom truck trustworthy.

*Last updated: April 2026*

---

## Quick Reference

| Field | Value |
|---|---|
| Nickname | Tootie |
| Year / Make / Model | 1965 Chevrolet Suburban |
| Owner | Karen |
| Wrenched On By | Ian Jennings + kids |
| Status | **Active — refinement phase** |
| Primary Use | Family hauler / daily driver |
| Current Phase | Systems integration + finish work |
| Primary Issue | Steering wander at speed (ride-height related) |
| Suspension | Air bags (custom install) |
| Tire Size | 205/75R15 |
| Lug Pattern | 6-lug (stock, under verification) |
| OIO Role | Occasional content appearance |

---

## Background

Tootie is Karen's 1965 Chevrolet Suburban — a large full-size classic truck running on custom air suspension. The vehicle is past the major build phase and is operational enough for road testing and family use, but is currently in a serious refinement stage focused on making the truck pleasant and trustworthy for daily driving.

Ian and the kids do maintenance and project work on it. The truck may appear in OIO videos from time to time, though it's a quality-of-life vehicle rather than a racing build.

The build philosophy is to keep it road-usable and comfortable while improving drivability, stability, and finishing the systems integration that makes an old custom vehicle reliable.

---

## Current Status (April 2026)

Tootie is **running and testable** but not yet finished. The truck is in a **systems-integration phase** rather than a basket case or early teardown phase.

### What's working
- Vehicle is operational
- Air suspension installed and functional
- Road-testable with passengers

### Primary active issues
1. **Steering wander at highway speeds** — most significant current problem
2. **Ride height management** — currently manual pressure-based tuning, needs standardization
3. **Air system electrical** — compressor on constant power instead of switched
4. **Interior/finish work** — multiple small mounting and trim tasks remain

The steering issue appears closely tied to ride-height setup, especially front/rear bag pressure balance and how the truck responds to passenger load. This is the highest-priority problem blocking confident daily use.

---

## Air Suspension System

### Current Configuration
- **Suspension type:** Air bags (custom installation)
- **Current control:** Manual gauge pressure adjustment
- **Known baseline pressure settings (older):**
  - Front: **65 PSI**
  - Rear: **70 PSI**

### Recent Pressure History (March 2026)
During testing with steering wander issues:
- Rear was running around **110 PSI** at one point (too high)
- Adjusted to approximately:
  - Front: **75 PSI**
  - Rear: **90 PSI** while driving
- Vehicle was "leveled by sight" rather than measured to true drive height
- Described as both "stiff" and "sitting really low" at different points
- Testing included 2 people in back seat, with scenarios considering 5 total occupants

### Known Problems
1. **No repeatable drive-height standard** — pressure-only tuning is not consistent enough
2. **Load sensitivity** — passenger weight meaningfully changes behavior
3. **Height affects steering geometry** — rake and alignment shift with bag pressure
4. **Visual leveling insufficient** — "looks level" is not precise enough for this size vehicle

### Automation Goal
Ian wants an **automatic ride-height system** for Tootie. This would provide:
- Repeatable preset drive heights
- Better load compensation
- Less manual guessing with bag pressures
- Improved highway behavior and stability
- More confidence when carrying passengers

The automation goal is not just convenience — it's a path to consistency and stability. For a big airbagged Suburban, pressure alone is not the same as actual ride height.

---

## Steering and Handling

### Primary Complaint
**Highway speed wandering** — reported during March 2026 testing with the truck carrying passengers. This is the clearest known steering issue.

### Context of the Issue
- Speed-related (wander increases at highway speeds)
- Rear ride height was higher than baseline during complaint
- Truck had 2 people in back during testing
- Discussion included scenario of 5 people total in vehicle
- Tire size: 205/75R15 (relatively tall, compliant sidewall)

### Likely Contributing Factors
Based on the pattern of issues and setup changes:
1. **Ride height mismatch front to rear** — rear was pushed too high
2. **Alignment change caused by bag height** — geometry shifts with air pressure
3. **Passenger load changes** — enough weight to move truck outside alignment sweet spot
4. **Tall compliant tires** — 205/75R15 adds sidewall flex and steering response delay
5. **No standardized drive height** — "level by sight" insufficient for stable geometry

### What's NOT confirmed
- Whether alignment has been done at proper drive height
- Whether there are worn steering/suspension components
- Whether front end geometry is stock or modified beyond airbags

### Working Theory
The most likely explanation is that Tootie behaves best near a certain **true drive height** (measured, not visual), and the current setup has drifted outside that sweet spot. The rear being too high relative to the front, combined with passenger load, is probably changing the front geometry in a way that makes the steering unstable.

---

## Wheels and Tires

### Current Known Information
- **Tire size:** 205/75R15
- **Lug pattern:** Stock appears to be **6-lug** (Ian was confirming this during March 2026)
- **Wheel decision:** There was an earlier wheel selection discussion, but the exact chosen wheel model is not currently documented

### Tire Characteristics
The 205/75R15 is a relatively tall, compliant tire. On a large older vehicle this can contribute to:
- More sidewall flex
- Less precise steering feel
- Extra steering response delay
- More sensitivity to ride-height and alignment changes

This doesn't mean the tire is wrong — it's just part of the steering feel equation.

### Open Questions
- What exact wheels were chosen in the earlier decision?
- What is the exact bolt pattern and hub configuration?
- Are current wheels stock or aftermarket?
- What tire pressure is being run?

---

## Electrical System

### Known Issue: Compressor Power
- **Current state:** Compressor wiring is on **constant power**
- **Desired state:** Change to **switched power**
- **Priority:** Fairly important — constant-power air system wiring can cause:
  - Compressor running when it shouldn't
  - Battery drain risk
  - Undesirable parked behavior

This is one of the clearest known actionable electrical fixes on Tootie.

### Other Electrical Items
- Sniper screen (likely Holley Sniper EFI display/controller) needs proper mounting/wiring integration

---

## Interior and Finish Work

Tootie has several smaller detail tasks that matter for everyday usability:

| Item | Status | Notes |
|---|---|---|
| Speedometer replacement | Open | Unknown if gauge failure, sender issue, or calibration problem |
| Sniper screen mounting | Open | Likely Holley Sniper display — needs finalized mount/location |
| Visor magnet clips | Open | 3D printed parts needed |
| Antenna installation | Open | Detail/trim work |
| General trim/mounting cleanup | Open | Various interior refinement tasks |

These are not glamorous but they're the tasks that make the difference between a project truck and a finished truck you want to drive every day.

---

## Known Problems List (Consolidated)

### A. Handling / Geometry / Suspension (HIGH PRIORITY)
- ⚠️ **Wandering at speed** — primary active issue
- Ride height likely not standardized to true measurements
- Rear may have been too high relative to front during testing
- Load sensitivity from passengers affects behavior significantly
- Pressure-based tuning not repeatable enough

### B. Air Ride System (MEDIUM-HIGH PRIORITY)
- No automated height control yet (goal for future)
- Current setup manually managed by gauge pressure
- Needs true preset ride heights with actual measurements

### C. Electrical (MEDIUM PRIORITY)
- ⚠️ **Compressor on constant power** — should be switched power (actionable fix)

### D. Instrumentation (MEDIUM PRIORITY)
- Speedometer needs replacement

### E. Interior / Finish Work (LOW-MEDIUM PRIORITY)
- Sniper screen mount needs finalization
- Antenna details need attention
- Visor magnet clips need attention (3D print project)
- Miscellaneous trim/detail tasks remain

### F. Wheel / Fitment (INFORMATION GAP)
- Wheel choice was being discussed in March 2026
- Lug pattern confirmation was needed (6-lug stock assumption)
- Final selected wheel details not captured

---

## 2026 Story Arc

Tootie's 2026 narrative is about **systems integration and refinement**. The truck is assembled enough to expose the real problems: ride-height consistency, steering stability, electrical cleanup, and finishing details.

The strongest theme is that Tootie needs a **true, repeatable drive-height setup** instead of visual leveling and pressure guessing. Everything else branches from that: better steering, more confidence with passengers, and a clearer path to automating the suspension later.

This is not a basket case rescue story. This is the harder, less dramatic work of taking a mostly-functional custom truck and making it **trustworthy**.

---

## Build Direction and Philosophy

### High-Level Goals
1. Keep it road-usable and comfortable
2. Improve drivability and stability
3. Solve suspension/ride-height behavior problems
4. Clean up wiring and mounting details inside the vehicle
5. Move toward smarter automation for the air suspension system

### Build Phase Assessment
- ✅ Major concept and assembly: **complete**
- 🔄 Systems integration and tuning: **in progress**
- ⏳ Finish work and refinement: **in progress**
- ⏳ Automation upgrades: **future phase**

The truck is in the "make it work right, then refine it" phase rather than a fully finished show build.

---

## Maintenance

- **Oil / Filter + Air Filter:** Every 6 months (longer interval than the race cars)

---

## Timeline of Key Events

### Undated (Long-Term Context)
- Tootie acquired by Karen
- Air suspension installed (custom build)
- Various interior and electrical work ongoing

### March 28, 2026 — Ride Height / Steering Discussion
- Ian reported steering wander at speed with passengers
- Ride height analysis and pressure adjustments made
- Baseline pressures reviewed (65F/70R)
- Testing showed rear at ~110 PSI (too high)
- Adjusted to ~75F/90R while driving
- Vehicle described as stiff but also sitting low
- Testing with 2 people in back, discussing 5-person scenario
- Tire size confirmed: 205/75R15

### March 30, 2026 — Wheels Discussion
- Ian asked about previously decided wheel choice
- Confirmed stock lug pattern verification needed (6-lug)

### April 6, 2026 — Comprehensive Documentation
- Full "Tootie Knowledge Dump" document created consolidating all known information
- This overview document updated to match

---

## Open Questions / Information Gaps

These important questions are NOT currently answered:

### Suspension / Geometry
- What actual measured heights define Tootie's best drive height?
- Has alignment been done at intended drive height?
- Are there worn steering/suspension components contributing to wander?
- Is front end geometry stock or modified beyond airbags?

### Wheels / Tires
- What exact wheels were chosen in the earlier decision?
- What is exact bolt pattern and hub configuration currently on truck?
- What tire pressure is being run?

### Air Management
- What controller/manifold/tank/compressor setup is installed?
- Is there already an electronic management system, or only manual gauges/switches?
- Is the automatic ride-height system a future upgrade or partially installed plan?

### Drivetrain / Engine / Fuel
- What engine is in Tootie?
- Is the Sniper screen definitely for Holley Sniper EFI?
- Are there any known fuel, tune, or drivability issues beyond suspension/steering?

### Interior / Body
- What is current state of interior overall?
- What exactly are the visor magnet clips for?
- Is speedometer replacement a restoration item or functionality repair?

---

## Best Current Understanding

Based on the full set of notes and conversations:

Tootie appears to be:
- ✅ Running or close to usable
- ✅ Past the "major concept" stage  
- 🔄 Still in serious refinement stage
- ⚠️ Most in need of:
  - Repeatable suspension setup with measured heights
  - Steering stability solution
  - Reliable electrical behavior (compressor wiring)
  - Cleanup/finalization of cabin and accessory mounting

It does **not** read like a basket case. It reads like a vehicle that is **mostly assembled and functional enough to test**, but is still missing the systems tuning and finish work that make an old custom vehicle pleasant and trustworthy for daily family use.

---

## Suggested Next Actions (Priority Order)

### 1. Establish True Drive Height (CRITICAL)
- Measure actual ride height front and rear (fender-to-ground or frame-to-ground)
- Define and document the target drive height measurements (not "looks level")
- Mark or label the bags/controllers with the correct pressures for that height
- Test and validate with various passenger loads

### 2. Steering Stability Investigation (CRITICAL)
- Verify alignment at newly established drive height
- Check for worn steering components while investigating
- Road test at proper height to see if wander resolves
- Document results

### 3. Compressor Electrical Fix (HIGH)
- Rewire compressor from constant power to switched power
- Verify proper operation and no battery drain when parked

### 4. Speedometer Replacement (MEDIUM)
- Diagnose exact issue (gauge vs sender vs calibration)
- Source replacement parts
- Install and verify operation

### 5. Interior Finish Work (MEDIUM-LOW)
- Finalize Sniper screen mount and wiring
- Complete antenna installation
- 3D print and install visor magnet clips
- Address remaining trim/mounting tasks

### 6. Future: Automation System (LONG-TERM)
- Research automatic ride-height controller options
- Plan sensor placement and wiring
- Budget and timeline for installation
- Install and tune when ready

---

## Related Content

→ [Maintenance Log](Maintenance-Log.md)
→ [Karen's Fleet](../README.md)
→ [Full Tootie Knowledge Dump (April 2026)](/OUT/issues/OUT-306#document-tootie-knowledge-dump)
