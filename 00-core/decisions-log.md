---
title: OIO Brain — Decisions Log
type: core
status: active
owner: Ian Jennings
updated: 2026-03-27
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


