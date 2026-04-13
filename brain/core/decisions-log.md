---
title: OIO Brain — Decisions Log
type: core
status: active
owner: Ian Jennings
updated: 2026-04-13
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

## 2026-04-13 — Fitty Cent EST Build Arc Locked and Imported Into Brain

**Decision:** Committed to the Fitty Cent EST Build Arc as an active 4-episode content arc for Summer–Fall 2026. Arc documents imported into brain across three files: car profile update, EST rules reference, and active arc document.

**Key locked decisions within the arc:**
1. Triage the spare L15 long block as normal shop work (off-camera), not a content moment
2. Episode 2 (rebuild + swap) runs as a vlog — not a scripted How-To — hard 6-hour edit cap
3. Episode 4 IS a full scripted COC episode, not a vlog with a COC cold open
4. No baseline dyno pull on the tired motor — savings vs. tired-motor dyno session

**Why:** Arc gives the Fitty Cent a proper narrative arc that converts SEO search traffic (Fit How-To episodes) into brand investment (COC payoff). Having the spare motor on the shop floor enables parallel build with no downtime to the car.

**Files created/updated:**
- `cars/ian/fit-fittycent/Overview.md` — updated with April 2026 state, EST class, spare motor, dual-role notes
- `resources/scca-est-rules-reference.md` — new file, 2026 EST rulebook reference
- `active/arcs/fitty-cent-est-build.md` — new file, full arc document

**Implications:** Next step is spare motor triage. Everything else in the arc is blocked on that decision point.

---

## 2026-04-12 — Fitty Cent EST Dry Tire Strategy Decided

**Decision:** For dry autocross events in EST class, run a sticky ~200 treadwear 225 tire on 7.5" wide wheels at the front only; keep the 205 Continental 340 treadwear tires on the rear. Budget: 2 wheels and 2 tires (secondhand wheels preferred).
**Why:** Hudson and Miles both need and want rotation from the rear. Sticky tires all around would tighten the rear too much and require suspension adjustments. Budget doesn't support 4 sticky tires right now. Front grip improvement is the biggest bang for buck. The approach lets the rear slide while providing turning grip up front.
**Implications:** Source 2 wheels (7.5" wide) and 2 tires (~200 treadwear, 225 width) before the next dry event. Secondhand wheels preferred to save money. If this setup proves suboptimal, revisit with suspension tuning.

---

## 2026-04-12 — Miles Smith Assigned as 4AG Teardown Lead

**Decision:** Miles Smith takes the technical lead on the 4AG spare motor teardown, assessment, and measurement (bearing sizing, etc.). Ian acts as "CEO and grunt" — makes the decisions, buys the parts, provides labor support.
**Why:** Ian wants Miles to develop ownership over the project and gain the mechanical experience. Ian will be the execution resource and financial backer. Miles needs to step up and lead.
**Implications:** Miles needs to begin the teardown ASAP. Prerequisite: workbench/table in the garage. Ian must order parts from Battle Garage — verify the existing research kit first.

---

## 2026-04-08 — Goblin Motor Swap at Euro Speedworks + Ian Drives MGB GTS at KCRX E2

**Decision:** Do the Goblin motor swap at Euro Speedworks using their lift, in exchange for Ian helping Ryan Redenbaugh finish the MGB GT build. Ian will drive Ryan's MGB GTS at KCRX E2 (April 19, Holsworth Farm) while the Goblin rebuild is in progress.
**Why:** Euro Speedworks has a lift. Doing the swap on a lift vs. the garage floor is dramatically faster and easier — estimated 1 day. Ian helping Ryan on the MGB prep is a fair exchange that benefits both. Since the Goblin won't be ready by Apr 19, the MGB GTS gives Ian a car to race at that event.
**Implications:** (1) Coordinate swap weekend with Ryan at Euro Speedworks after picking up motor on Apr 9. (2) Ian helps Ryan finish MGB GTS prep before Apr 19. (3) Miles drives the red bomber Miata at Apr 19 with Larry as co-driver.

---

## 2026-04-08 — Goblin: Replace 4AG with 3-Rib Motor from Henry

**Decision:** Source a replacement 3-rib 4age from Henry for $350, with the melted-down motor included as part of the exchange. The new motor will be torn down, inspected, and rebuilt before installation — not installed as-is.
**Why:** The current 4AG has confirmed bearing failure and near-total cylinder 4 compression loss. A full rebuild of the failed motor is not the right call. A 3-rib unit from Henry is available now at a known cost ($350), and trading the melted motor as part of the deal keeps costs controlled. The 2AR swap is a long way off and the Renault (Geoffrey) is not a viable on-track replacement. This is the fastest path back to the rallycross grid.
**Implications:** Ian needs to: (1) acquire motor from Henry (confirmed Friday April 9), (2) tear down the new motor and assess it before rebuild, (3) build a parts list (stock pistons confirmed; slightly higher comp head gasket; full rebuild kit; rings for std pistons; bearings TBD after sizing; new clutch spec TBD; research best value for dollar), (4) research oiling system upgrades (oil pickup, better oil pump, 20-valve pump option), (5) get block and head hot-tanked at C-TEC (Miles's automotive program at North Kansas City High School), (6) rebuild and reinstall with a target of being ready for the 3rd Kansas City rallycross event of 2026 (KCRX E3, May 25).

---

## 2026-04-06 — US-001: Album-Driven Photo Pipeline with AI Vision and PostBridge Drafts

**Decision:** Rebuilt the photo ingestion pipeline as a single unified script (`dev/scripts/process_photos.py`) that polls the OIO Google Photos album, identifies vehicles via Claude Vision, generates captions, and creates PostBridge drafts — all in one run. Removed Supabase dependency entirely. Low-confidence photos route to `photos/unknown/photo-log.md` and are retried automatically when their description changes.
**Why:** The picker-based intake (`intake/selected-photos.json`) was not being used. Three separate scripts and workflows created operational friction. This unification closes the loop from photo-add to PostBridge draft without any manual steps beyond adding a description to unknown photos.
**Implications:** Old workflows (`ingest-photos.yml`, `generate-captions.yml`, `create-drafts.yml`) are deprecated and disabled (workflow_dispatch only). `photo_log.py` schema updated: removed `supabase_url`, `thumbnail_url`, `rough_caption`; added `google_photos_url`, `last_description`. `photos/unknown/photo-log.md` created. New workflow: `.github/workflows/process-photos.yml` runs every 6 hours.

---

## 2026-05-30 — Repository Restructuring Implemented

**Decision:** Implemented the full repo restructuring as documented in `core/structure-proposal.md`.

**Changes made:**
- Renamed `00-core/` → `core/` and `01-active/` → `active/`
- Flattened `OIO Brain/` — all domain sections promoted to root level with clean names: `brand/`, `content/`, `cars/`, `events/`, `production/`, `business/`, `ops/`
- Renamed car folders to nickname slugs (e.g., `1985 MR2` → `mr2-goblin`, `2009 Honda Fit` → `fit-fittycent`)
- Lowercased driver folder names (`Ian/` → `ian/`, etc.)
- Consolidated intake folders: `docdump/` → `intake/docs/`, `picdump/` → `intake/photos/`, `docdump/dailies/` → `intake/dailies/`
- Removed `todo/` (content merged into `active/`)
- Archived `OIO-Master-Brief.md` → `core/archive/OIO-Master-Brief.md`
- Moved `PHOTO-INDEX.md` → `photos/README.md`
- Moved `OIO-Video-Catalog.md` → `content/video-catalog.md`
- Renamed `active/active-priorities.md` → `active/priorities.md`
- Moved Video Scripts transcript folders into `transcripts/`
- Moved data files: `OIO Brain/data/` → `data/` at root
- Updated all scripts, workflows, and documentation with new paths

**Why:** The old structure had 13+ friction points — spaces in paths, redundant nesting, numeric prefixes, scattered data, split governance, duplicate content. The new structure is flat, semantic, and machine-friendly.

**Implications:** All scripts, workflows, and AI agent instructions now reference the new paths. The `core/structure-proposal.md` is marked as implemented/archived.

## 2026-03-31 — Repo Structure Proposal Created (Not Yet Implemented)

**Decision:** Authored `core/structure-proposal.md` — a full proposal for a cleaner, flatter repo structure. Not implemented; pending Ian's review and approval.

**Proposal summary:**
- Flatten `OIO Brain/` — all domain sections promoted to root level (no spaces, no redundant nesting)
- Drop numeric prefixes from folder names (`core/` → `core/`, `active/` → `active/`)
- Consolidate 3 brand voice docs → 1; 2 indexes → 1; 2 priorities files → 1; 2 template folders → 1
- Centralize all structured data under `data/`
- Unify `intake/docs/`, `intake/photos/`, and `todo/` into a single `intake/` folder
- Apply consistent nickname-slug naming to car folders (no spaces, no year prefix)
- Move floating root files (`OIO-Video-Catalog.md`, `photos/README.md`) into their domain folders

**Why:** The repo has 13+ identified friction points (split governance, redundant nesting, spaces in paths, scattered data, duplicate content). A clean structure will reduce agent confusion and human navigation overhead.

**Implications:** Nothing is implemented yet. Review `core/structure-proposal.md` and answer the open questions before implementation begins.

---

## 2026-04-05 — Encode DIY Capacity Constraints as Planning Baseline

**Decision:** Added explicit planning guardrails across core context files so agents assume conservative execution capacity by default: OIO is highly DIY and Ian is the primary hands-on execution bottleneck unless additional owners/time are explicitly named.

**Why:** Planning recommendations were at risk of overcommitting parallel execution lanes. Board direction required codifying operating reality directly in the brain so strategy and execution choices stay runnable.

**Implications:** Agents should now sequence major work by default, treat unstaffed parallel tracks as contingent, and only commit multi-track plans when ownership and calendar capacity are explicitly documented.

---

## 2026-03-31 — Repo Cleanup and Centralization Pass

**Decision:** Performed a general cleanup pass to deduplicate content and centralize around the OIO Brain folder structure.

**Changes made:**
1. **Deleted `issue-report-paperclip-api.txt`** — Stale API bug report artifact with no ongoing value. Nothing referenced it.
2. **Moved `TRANSCRIPT-PIPELINE.md` → `docs/transcript-pipeline.md`** — Technical pipeline documentation belongs with the other pipeline docs in `docs/`.
3. **Added frontmatter to `OIO-Master-Brief.md`** — Marked `status: archived` and `source_of_truth: false`. All content has been migrated to the brain. The file is preserved but clearly labeled as the original source, not the current authority.
4. **Fixed `OIO Brain/02 - Content/OIO-Brand-Voice-Guide.md`** — Set `source_of_truth: false`, changed owner from "AI Copywriter (Paperclip)" to Ian Jennings, added a note clarifying it is a social-media tool reference that defers to `Voice-and-Tone.md` as the canonical brand voice.
5. **Renamed `events/results/oio-racing-results.json` → `oio-2026-season-results.json`** — Prevented name collision with the comprehensive `OIO Brain/data/oio_racing-results.json` (historical dataset, 9000+ lines). Updated Results README with a data files table explaining both.
6. **Moved `todo/` user stories → `OIO Brain/07 - Admin/Backlog/`** — Development backlog stories now live in the brain. The `todo/` folder remains as a redirect stub.
7. **Updated `README.md` and `INDEX.md`** — Reflect the `docs/` section and the move of TRANSCRIPT-PIPELINE.md.

**Why:** The repo had accumulated several root-level artifacts that belonged elsewhere or had become stale. Two `source_of_truth: true` documents existed for brand voice (creating authority confusion). The `todo/` folder was isolated from the brain structure. The transcript pipeline doc was the only technical doc not in `docs/`.

**Implications:** None of the changes affect active workflows or script paths. All referenced file paths remain valid.

---



**Decision:** Processed `intake/docs/oio_results.json` (252KB, 8,458 lines) into structured brain files. Two new canonical result files created. Source file deleted.

**Data distributed to:**
- `events/results/2025-Season-Results.md` — Full 2025 KCR RallyCross (8 events) and KS Region RallyCross (5 events) results, including run-level data, head-to-heads, and season milestones
- `events/results/KSRX-Historical-2018-2024.md` — New file covering KS Region RallyCross 2018–2021 and 2024 (previously undocumented in brain)
- `active/current-state.md` — Added 2025 season data note to Recent Changes
- `active/open-loops.md` — Added: 2025 AX data missing, BDR car data anomaly, process-dailies false-positive trigger issue

**Why:** The JSON contained a complete 2025 season dataset plus historical KS Region data not yet in the brain. Both were distributed to appropriate canonical files.

**Notable findings in 2025 data:**
- Hudson Smith's rallycross debut: KCRX E8, 2025-09-21 (Novice class, 2nd place)
- Ryan won KCRX E9 driving the MGB GT in MR class
- Ian+Ryan+Richard all took class wins at KSRX Plinko (Aug 2025)
- Ian switched to Honda Fit for KCRX season finale — MR2 motor issues
- BDR (Dec 2025): Ian listed as driving "1985 Toyota Celica" — potential source data error (Ian's Celica is 1972 Dale)

**Also noted:** The `process-dailies` workflow triggered a processing issue on `intake/dailies/README.md`, which is the permanent infrastructure README (never to be deleted). That file contains no operational data. Added open loop to fix the workflow filter.

**Implications:** 2025 results are now accessible via the brain. 2025 AX data is absent from source — needs to be sourced separately. BDR car entry needs verification.

---

## 2026-03-29 — Dailies Separated from Final YouTube Transcripts

**Decision:** Renamed `intake/docs/transcripts/` to `intake/dailies/` and replaced `process-transcripts.yml` with `process-dailies.yml`. Clarified the two distinct transcript types in all documentation and copilot instructions.

**Why:** There are two fundamentally different types of transcripts in play:
1. **Final YouTube video transcripts** — full text of published videos, auto-fetched by the `fetch-youtube-transcripts` workflow and stored in `transcripts/` at the repo root.
2. **Dailies** — raw audio dumps from Ian's working video files (unedited clips), manually dropped into `intake/dailies/` for brain processing. These are not published videos.

Mixing these under the generic "transcripts" label created confusion about purpose, workflow, and expectations.

**Changes:**
- `intake/docs/transcripts/` → `intake/dailies/` (renamed)
- `.github/workflows/process-transcripts.yml` → `.github/workflows/process-dailies.yml` (replaced with updated paths and purpose)
- `intake/docs/README.md` — updated to reference dailies
- `copilot-instructions.md` — added "Transcript Types" section distinguishing the two; renamed workflow section to "Dailies Workflow"
- `transcripts/README.md` — added clarifying note that this folder is for final published videos only
- `core/templates/transcript-summary.md` — updated template header and source path for dailies; YouTube ID marked optional

**Implications:** Ian drops raw daily clip transcripts in `intake/dailies/`. The `process-dailies` workflow auto-triggers. Final YouTube transcripts continue to auto-fetch into `transcripts/` on cron schedule. No workflow changes for the final transcript pipeline.

---

## 2026-03-29 — Transcript Fetcher Switched to Batched Execution

**Decision:** Updated `scripts/fetch_transcripts.py` and `.github/workflows/fetch-youtube-transcripts.yml` to process transcripts in configurable batches (default: 25 per run) instead of attempting one large bulk fetch.

**Why:** The previous bulk strategy (all 360+ videos in a single run) was failing — YouTube rate-limits or network timeouts cut the run short before it could complete. Since each run already skips already-processed videos, running repeatedly with a small batch naturally resumes from where the last run stopped.

**Changes:**
- Added `--batch-size N` flag to the script (default 25, 0 = no limit)
- Added a `schedule: cron: '0 */2 * * *'` trigger to the workflow (runs every 2 hours)
- Added `batch_size` as a `workflow_dispatch` input so it can be overridden manually
- Script now reports how many videos remain after each batch run

**Implications:** Transcripts will accumulate automatically over time without manual intervention (~15 batched runs to cover all 360 videos). Manual dispatch is still available with configurable batch size. The `--all` flag still works for a forced full re-fetch, also subject to batch size.

---



**Decision:** Created `scripts/fetch_transcripts.py` and `.github/workflows/fetch-youtube-transcripts.yml` to automatically fetch auto-generated YouTube transcripts for all OIO Racing videos. Transcripts are stored in `transcripts/YYYY-MM-DD_video-title/` with `transcript.md` (timestamped Markdown + frontmatter) and `metadata.json`. The workflow triggers on merge to main when `OIO-Video-Catalog.md` changes, and supports a manual `fetch_all=true` dispatch for the initial bulk run of all 360 videos.

**Why:** 360 published videos have no accessible transcripts, blocking rapid generation of video scripts, captions, and content ideas based on existing structures and patterns. Transcripts enable AI agents and humans to analyze past content, identify recurring structures, extract talking points, and generate new scripts that match the OIO voice.

**Implications:** Run the workflow manually with `fetch_all=true` to pull the first full batch. Going forward, new transcripts are fetched automatically whenever a new video is added to `OIO-Video-Catalog.md` via the `oio-video-fetcher.js` flow. Video markdown can link to transcripts via `transcripts/YYYY-MM-DD_title/transcript.md`.

---

## 2026-03-28 — Photo Library System Established

**Decision:** Created a `photos/` library at the repo root organized by driver and car. Added `photos/README.md` as the master searchable index. Created a GitHub Action (`process-picdump-photos.yml`) that auto-spawns a Copilot agent whenever photos are pushed to `intake/photos/`. The agent identifies the car, files the photo, updates the car description, and updates the index.

**Why:** Ian wants to track all OIO photos in one place, understand which have been posted to social media, and eventually use the photo library as the basis for social media scheduling. The picdump intake pattern mirrors the existing docdump pattern, making it consistent with existing repo workflows.

**Implications:** Ian can now add photos by dropping them in `intake/photos/` and pushing to main. The agent does the rest. Social media tracking lives in `photos/README.md` and per-car `photo-log.md` files. Each car's Overview.md now has a Visual Identification section to help AI match future photos.

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

## 2026-03-28 — 2026 Content Schedule Rebooted

**Decision:** The original tentative 2026 content schedule was replaced with a rebooted version anchored to confirmed race events and the current reality as of March 28.

**Why:** The original schedule was not followed — Feb 26, Mar 5, Mar 15, Mar 19, and Mar 26 planned uploads were all missed. The channel had a 24-day gap since Mar 4. A fresh, realistic schedule was needed that starts from today rather than attempting to backfill missed content.

**What changed:**
- Original missed content (Gyraline How-To, Kids prep vlog, Killer Corolla vlog) re-slotted into April and June
- KCRX E1 (Mar 22) COC rescheduled as April 20 Season Premiere (~4 weeks post-event, still usable)
- Kids' first autocross (Apr 12) documented in Apr 24 vlog
- Full KCRX/KSRX/KCR race calendar added to the brain (`events/schedules.md`)
- COC pipeline map created to track which events have been recapped
- Shorts strategy section added — top-of-funnel growth driver, must not be neglected

**New file created:** `content/schedule.md`

**Implications:** April 2 Fit How-To is the first action. Edit KCRX E1 footage immediately for the Apr 20 COC.

---



**Decision:** Created `intake/docs/` folder at repo root for Ian to drop raw documents into for Copilot processing. Established rules that (1) processed files must be deleted after ingestion, and (2) any data-processing script must include deletion of its source file.

**Why:** Creates a simple workflow for getting raw documents into the brain without leaving orphaned files cluttering the repo.

**Implications:** The `intake/docs/` folder should normally be empty. If files are present, they haven't been processed yet.

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

## 2026-04-13 — Moved brain docs to /brain/ and added Google Drive sync

**Decision:** All OIO brain documentation (knowledge/memory layer) moved from repo root into a dedicated `brain/` directory. Google Drive sync added so active brain docs can be read/written directly in Drive and kept in sync with the repo.

**What moved to brain/:**
- `active/` → `brain/active/`
- `brand/` → `brain/brand/`
- `business/` → `brain/business/`
- `cars/` → `brain/cars/`
- `content/` → `brain/content/`
- `core/` → `brain/core/`
- `data/` → `brain/data/`
- `events/` → `brain/events/`
- `ops/` → `brain/ops/`
- `production/` → `brain/production/`
- `resources/` → `brain/resources/`

**What stayed at root:** `.github/`, `dev/`, `docs/`, `intake/`, `photos/`, `transcripts/`, `user-stories/`, root markdown files (`README.md`, `INDEX.md`, `skill.md`, etc.)

**Google Drive sync added:**
- `dev/scripts/auth_google_drive.py` — one-time OAuth2 auth helper
- `dev/scripts/sync_brain_to_gdrive.py` — push brain/ to Google Drive
- `dev/scripts/sync_brain_from_gdrive.py` — pull brain/ from Google Drive
- `.github/workflows/sync-brain-to-gdrive.yml` — triggers on `brain/**/*.md` push to main
- `.github/workflows/sync-brain-from-gdrive.yml` — cron every 30 min to pull from Drive

**Required secrets (GitHub):** `GOOGLE_DRIVE_CREDENTIALS`, `GOOGLE_DRIVE_BRAIN_FOLDER_ID`

**Why:** Cleaner separation of brain documentation from repo tooling. Google Drive provides easier mobile read/write access to the active memory layer without requiring a git client.

---
