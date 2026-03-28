---
title: OIO Brain — Decisions Log
type: core
status: active
owner: Ian Jennings
updated: 2026-03-28
tags: [decisions, history, rationale]
source_of_truth: true
summary: Append-only log of significant decisions made about OIO — brand, operations, vehicles, content, business. Each entry records what was decided, why, and any follow-up implications.
---

# Decisions Log

Append-only. New entries go at the top. Do not edit past entries — add a follow-up entry instead.

**Format:**
```
## YYYY-MM-DD — [Decision Title]
**Decision:** What was decided.
**Why:** Rationale.
**Implications:** Follow-up actions or consequences, if any.
```

---

## 2026-03-28 — Update Keegan Fleet with Confirmed Vehicle Details

**Decision:** Replaced the generic "Keegan's Tercel (multiple)" and "Lincoln Town Car (multiple)" placeholders with specific, confirmed vehicle records for all 6 cars in Keegan's current fleet.

**Why:** Keegan told Ian his current fleet directly. This is the first time the brain has exact build specs for each individual car rather than fleet-level approximations. Accuracy matters for content planning, event prep, and knowing which car is which.

**Changes made:**
- Renamed "Lincoln Town Car" folder → "1979 Lincoln Continental" with full specs (400 V8, 3-spd auto, Medium Beryl Metallic / white vinyl top)
- Updated "1985 Tercel" with specific details (fleet white, 5+1 spd, 4WD, ~3" lift, 4A-FE swap in progress, pizza hut hat)
- Created new car folder: 1981 Toyota Tercel (burnt metallic orange, turbo 4A-G, gutted, 200TW)
- Created new car folder: 1982 Honda Prelude 1st gen (ice blue, EL1/EK1 build, Weber 32/36, air bag coilovers, 280TW, DIY body kit)
- Created new car folder: 1996 Chevrolet Lumina APV (dark red, Bonneville SSEI wheels, snow tires, dealer decals)
- Created new car folder: 2003 Toyota Tundra (all black, access cab, 4.7L, Limited trim, smoked lights)
- Updated Keegan README fleet index to reflect all 6 cars

**Implications:** If more cars exist or details change, update individual car folders. Video content featuring Keegan's cars should now reference the specific car, not the generic fleet.

---

## 2026-03-27 — Establish OIO Brain Repository

**Decision:** Create a structured, AI-readable/writable knowledge repository (oio-brain) to serve as the canonical operational brain for OIO Racing.

**Why:** OIO operates across multiple domains (racing, vehicles, content, business) with a small team. A centralized brain enables consistent operation, reduces context loss between sessions, and allows AI agents to assist without reinventing context each time.

**Implications:** All canonical OIO knowledge should live here. This repo replaces ad-hoc notes and scattered documents as the source of truth.

---

## 2026-03-27 — Fitty Cent Is the Correct Nickname for the 2009 Honda Fit

**Decision:** The 2009 Honda Fit (GE8) is officially nicknamed "Fitty Cent." All documents have been updated to reflect this.

**Why:** Corrected from an earlier incorrect spelling ("Fittty Scent") in the initial brain build.

**Implications:** Any future documents referencing this car must use "Fitty Cent."

---

## 2026 (pre-season) — Four-Week Content Rotation Established

**Decision:** OIO runs a four-week rotating content schedule: Fit How-To (Week 1), Vlog (Week 2), Church of Combustion (Week 3), Vlog (Week 4).

**Why:** Provides predictability for production planning, ensures the top-of-funnel Fit How-To runs monthly, and allows the big Church of Combustion production to have adequate edit time.

**Implications:** Fit How-To is non-negotiable — one per month, every month. CoC drops on Sunday only, 1–2 weeks post-event.

---

## 2026 (pre-season) — Kids Racing Both Disciplines in 2026

**Decision:** Miles and Hudson will race Fitty Cent in both autocross and rallycross during the 2026 season, with mid-2026 targeted as their documented debut as competitors.

**Why:** Ian's philosophy that track time makes better street drivers. The kids are old enough, and dual-discipline racing with the family car is a compelling content arc.

**Implications:** Fitty Cent must be reliable enough for dual duty. Setup notes must document both autocross and rallycross configurations. Kids' racing is a documented story arc for 2026.

---

## 2026 (pre-season) — Lake Garnett Grand Prix Revival Is the Season Centerpiece

**Decision:** The Lake Garnett Grand Prix Revival (October) is the annual cathedral moment and the centerpiece of the Church of Combustion content calendar.

**Why:** It is the largest event on the OIO calendar, the payoff for season-long build arcs (especially Dale), and the natural climax of the Church of Combustion format.

**Implications:** Dale's entire 2026 arc is framed as a pilgrimage toward Lake Garnett. Pre-planning for the Church of Combustion episode starts early in the season.

---

## 2026-03-28 — Cars Folder Reorganized by Driver/Owner

**Decision:** Restructured `OIO Brain/03 - Cars/` from a flat list of car folders into driver subfolders: `Ian/`, `Ryan/`, `Keegan/`, `Richard/`.

**Why:** With 13+ car folders, the flat layout was disorganized. Owner context is now clear from folder path alone. Team member cars also had the driver name as a folder suffix (e.g., `AE86 - Ryan`) which was redundant once they live under `Ryan/`.

**Structure:**
- `Ian/` — Dale, Goblin, Fitty Cent, Killer Corolla, Nessie, Geoffrey
- `Ryan/` — AE86, MGB GT, 2001 Camry
- `Keegan/` — Tercel, Lincoln Town Car
- `Richard/` — ST205

**Notes:** The kids (Miles, Hudson, Parker) don't own cars — they drive Ian's Fitty Cent.

**Implications:** All relative links in Overview files updated. Owner frontmatter on team member car files corrected to the actual owner.

---

## 2026-03-28 — OIO Video Catalog Processed Into Brain Structure

**Decision:** The root-level `OIO-Video-Catalog.md` file (359 videos, ~156KB) was processed into the appropriate brain files and then deleted.

**Data distributed to:**
- `OIO Brain/02 - Content/Published-Videos.md` — channel stats, top 10, full chronological video index
- `OIO Brain/03 - Cars/[each car]/Overview.md` — Related Videos sections added to all Ian's car files (Dale, Goblin, Fitty Cent, Killer Corolla, Nessie, Geoffrey)
- `OIO Brain/03 - Cars/AE86 - Ryan/` — New car folder created for Ryan's AE86 (16 videos)
- `OIO Brain/03 - Cars/MGB GT - Ryan/` — New car folder created for Ryan's MGB GT (11 videos)
- `OIO Brain/03 - Cars/2001 Camry - Ryan/` — New car folder created for Ryan's 2001 Camry (6 videos)
- `OIO Brain/03 - Cars/Tercel - Keegan/` — New car folder created for Keegan's Tercel (11 videos)
- `OIO Brain/03 - Cars/Lincoln Town Car - Keegan/` — New car folder created for Keegan's Lincoln (4 videos)
- `OIO Brain/03 - Cars/ST205 - Richard/` — New car folder created for Richard's ST205 (2 videos)

**Why:** The raw catalog file at root was an unstructured dump. The brain is now the source of truth for all published video data.

**Implications:** When updating video data in the future, update `Published-Videos.md` and the relevant car Overview files directly. Do not recreate a root-level catalog.

---

## 2026-03-28 — Docdump Folder and Processing Rules Established

**Decision:** Created `docdump/` folder at repo root for Ian to drop raw documents into for Copilot processing. Established rules that (1) processed files must be deleted after ingestion, and (2) any data-processing script must include deletion of its source file.

**Why:** Creates a simple workflow for getting raw documents into the brain without leaving orphaned files cluttering the repo.

**Implications:** The `docdump/` folder should normally be empty. If files are present, they haven't been processed yet.

---



## 2026-03-28 — Car Folder Naming Convention Changed to Year-Model

**Decision:** Renamed all car folders in `OIO Brain/03 - Cars/` to use `YYYY Model` format (e.g., `1972 Celica`, `1985 MR2`). Nicknames removed from folder names.

**Why:** Nicknames are fun for content but create ambiguity in folder paths. Year-model is unambiguous and consistent.

**Folders renamed:**
- `Ian/Dale - Celica` → `Ian/1972 Celica`
- `Ian/Geoffrey - Dauphine` → `Ian/1962 Dauphine`
- `Ian/Honda Fit - Fitty Cent` → `Ian/2009 Honda Fit`
- `Ian/Killer Corolla` → `Ian/1977 Corolla`
- `Ian/MR2 - Goblin` → `Ian/1985 MR2`
- `Ian/Nessie - Cressida Wagon` → `Ian/1982 Cressida Wagon`
- `Ryan/AE86` → `Ryan/1985 AE86`
- `Ryan/MGB GT` → `Ryan/1973 MGB GT`
- `Richard/Starlet` → `Richard/1983 Starlet`
- `Richard/Miata` → `Richard/2001 Miata`

**Exceptions (no year known, no nickname — left as-is):**
- `Keegan/Tercel`, `Keegan/Lincoln Town Car`, `Richard/ST205`

**Implications:** Future car folders should follow `YYYY Model` naming. Nicknames live inside files, not in folder names.

---
