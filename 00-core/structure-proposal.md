---
title: Repo Structure Proposal — Cleaner Layout
type: core
status: draft
owner: Ian Jennings
updated: 2026-03-31
tags: [repo, structure, proposal, governance]
source_of_truth: false
summary: Proposed cleaner repo structure to address fragmentation, redundant nesting, inconsistent naming, and scattered data. Not yet implemented. Review and approve before acting.
---

# Repo Structure Proposal — Cleaner Layout

> **Status: DRAFT — Do not implement until approved by Ian.**
> This is a proposal only. No files have been moved. All paths in the current repo still work.

*Authored: 2026-03-31*

---

## Why Bother

The current structure has grown organically and has accumulated several friction points that make both humans and agents work harder than they should:

1. **`OIO Brain/` folder with spaces** — Every CLI command touching this path needs quoting or escaping. The entire repo is the brain, so naming a subfolder "OIO Brain" is redundant overhead.
2. **Dual governance layers** — `00-core/` at root AND `OIO Brain/00 - Start Here/` AND `OIO Brain/07 - Admin/` all serve governance. Hard to know where the canonical rule lives.
3. **Two template folders** — `00-core/templates/` (10 files) and `OIO Brain/07 - Admin/Templates/` (5 files). Split means agents and humans check only one and miss half.
4. **Two indexes** — `INDEX.md` at root AND `OIO Brain/00 - Start Here/OIO-Master-Index.md`. Same job, two files to keep in sync.
5. **Two priorities files** — `01-active/active-priorities.md` AND `OIO Brain/00 - Start Here/OIO-Current-Priorities.md`. Drift happens constantly.
6. **Three brand voice documents** — `OIO Brain/00 - Start Here/OIO-Brand-Guide.md`, `OIO Brain/01 - Brand/Voice-and-Tone.md`, and `OIO Brain/02 - Content/OIO-Brand-Voice-Guide.md`. All overlap. Agents pick the wrong one.
7. **Number prefixes on folders** (`00 - Start Here`, `01 - Brand`) — Friction in paths. Add a new section and everything renumbers.
8. **Root clutter** — `OIO-Video-Catalog.md` (44 KB!), `PHOTO-INDEX.md`, `OIO-Master-Brief.md`, `skill.md`, `todo/` all floating at root alongside `00-core/` and `01-active/`. Visually noisy.
9. **Scattered data files** — Race results JSON in `OIO Brain/data/`, season results JSON in `OIO Brain/04 - Events/Results/`, social posts in `OIO Brain/data/social-posts/`. No single data home.
10. **Two intake zones** — `docdump/` and `picdump/` as separate root folders. Same concept, split for no good reason.
11. **`todo/` folder** — Redundant with `01-active/next-actions.md`.
12. **Car folder naming inconsistency** — Some have year (`1985 MR2`), some just model (`ST205`). All have spaces. No slug convention.
13. **`OIO Brain/02 - Content/Video Scripts/`** — These are auto-fetched transcripts, same content type as `transcripts/` at root. Two homes for the same artifact.

---

## Proposed Structure

The guiding principles:

- Flatten the `OIO Brain/` nesting — promote all sections to root level
- Remove number prefixes from folder names
- No spaces in folder or file names (kebab-case throughout)
- One home for every type of content
- Root stays clean: only entry-point files and intake/operational folders

```
/
├── README.md                        ← Human entry point (keep, update paths)
├── INDEX.md                         ← Single master index (keep, drop OIO-Master-Index.md duplicate)
├── skill.md                         ← Agent onboarding (keep at root for discoverability)
├── OIO-Master-Brief.md              ← Archived source doc — move to core/archive/
├── requirements.txt
├── .gitignore
│
├── .github/
│   ├── copilot-instructions.md
│   └── workflows/
│
├── core/                            ← Was 00-core/ (drop numeric prefix)
│   ├── README.md
│   ├── repo-standards.md
│   ├── decisions-log.md
│   ├── archive/
│   │   └── OIO-Master-Brief.md      ← Move from root
│   └── templates/                   ← Consolidate both template folders here
│       ├── (all 10 from 00-core/templates/)
│       └── (all 5 from OIO Brain/07 - Admin/Templates/ — merge, deduplicate)
│
├── active/                          ← Was 01-active/ (drop numeric prefix)
│   ├── current-state.md
│   ├── priorities.md                ← Consolidate active-priorities.md + OIO-Current-Priorities.md
│   ├── next-actions.md              ← todo/ content merged here too
│   └── open-loops.md
│
├── brand/                           ← Was OIO Brain/01 - Brand/ + brand content from 00 - Start Here
│   ├── mission.md                   ← Was Mission-and-Positioning.md
│   ├── voice-and-tone.md            ← Consolidate: Voice-and-Tone.md + OIO-Brand-Guide.md
│   │                                   (OIO-Brand-Voice-Guide.md stays separate — it's tool-specific)
│   ├── brand-voice-social.md        ← Was OIO-Brand-Voice-Guide.md (AI caption tool reference)
│   ├── audience.md                  ← Was Audience-Personas.md
│   ├── team-bios.md                 ← Was Team-Bios.md
│   ├── social-voice.md              ← Was Social-Post-Voice.md (auto-generated, keep separate)
│   └── sponsorship-pitch.md         ← Was Sponsorship-Pitch.md
│
├── content/                         ← Was OIO Brain/02 - Content/
│   ├── video-backlog.md             ← Was Video-Ideas-Backlog.md
│   ├── story-arcs.md                ← Was Season-Story-Arcs.md
│   ├── schedule.md                  ← Was 2026-Content-Schedule.md
│   ├── shorts-social.md             ← Was Shorts-and-Social-Posts.md
│   ├── titles-thumbnails.md         ← Was Titles-and-Thumbnails.md
│   ├── published-videos.md          ← Was Published-Videos.md
│   ├── video-catalog.md             ← Move OIO-Video-Catalog.md from root (drop OIO- prefix)
│   └── summaries/                   ← Was Summaries/ (daily video summaries, keep as-is)
│
├── cars/                            ← Was OIO Brain/03 - Cars/
│   ├── future-builds.md
│   ├── ian/
│   │   ├── README.md
│   │   ├── mr2-goblin/              ← Was "1985 MR2" — nickname slug, no spaces
│   │   │   ├── overview.md          ← Lowercase filenames
│   │   │   ├── setup.md
│   │   │   ├── mods.md
│   │   │   └── maintenance.md
│   │   ├── celica-dale/             ← Was "1972 Celica"
│   │   ├── fit-fittycent/           ← Was "2009 Honda Fit"
│   │   ├── cressida-nessie/         ← Was "1982 Cressida Wagon"
│   │   ├── corolla-killer/          ← Was "1977 Corolla"
│   │   ├── dauphine-geoffrey/       ← Was "1962 Dauphine"
│   │   └── tundra/                  ← Was "2014 Tundra"
│   ├── ryan/
│   │   ├── README.md
│   │   ├── ae86/                    ← Was "1985 AE86"
│   │   ├── mgb-gt/                  ← Was "1973 MGB GT"
│   │   └── camry/                   ← Was "2001 Camry"
│   ├── keegan/
│   │   ├── README.md
│   │   ├── tercel-81/               ← Was "1981 Tercel" (year suffix to disambiguate twins)
│   │   ├── tercel-85/               ← Was "1985 Tercel"
│   │   ├── prelude/                 ← Was "1982 Honda Prelude"
│   │   ├── lumina-apv/              ← Was "1996 Lumina APV"
│   │   ├── tundra/                  ← Was "2003 Tundra"
│   │   └── lincoln/                 ← Was "1979 Lincoln Continental"
│   ├── karen/
│   │   ├── README.md
│   │   └── tootie/                  ← Was "1965 Suburban"
│   └── richard/
│       ├── README.md
│       ├── st205/                   ← Was "ST205" (already no year — keep)
│       ├── starlet/                 ← Was "1983 Starlet"
│       └── miata/                   ← Was "2001 Miata"
│
├── events/                          ← Was OIO Brain/04 - Events/
│   ├── autocross.md
│   ├── rallycross.md
│   ├── schedules.md
│   ├── travel.md
│   ├── results/                     ← Was Results/ (markdown result files stay here)
│   │   ├── README.md
│   │   ├── OIO-Combined-Achievements.md
│   │   ├── KCRSCCA-RX-Historical-2017-2024.md
│   │   ├── KSRX-Historical-2018-2024.md
│   │   ├── KCRSCCA-Results-Links.md
│   │   ├── 2025-Season-Results.md
│   │   └── 2026-Season-Results.md
│   └── notes/                       ← Was Event Notes/
│
├── production/                      ← Was OIO Brain/05 - Production/
│   ├── camera-audio.md              ← Was Camera-and-Audio-Workflow.md
│   ├── editing-sops.md              ← Was Editing-SOPs.md
│   ├── b-roll-index.md              ← Was B-roll-Library-Index.md
│   ├── music-assets.md              ← Was Music-and-Assets.md
│   └── shot-lists/                  ← Was Shot Lists/
│
├── business/                        ← Was OIO Brain/06 - Business/
│   ├── budget.md
│   ├── expenses.md
│   ├── sponsorship-leads.md         ← Was Sponsorship-Leads.md
│   ├── partnerships.md
│   ├── merch.md
│   └── website.md
│
├── ops/                             ← Was OIO Brain/07 - Admin/ (trimmed)
│   ├── contacts.md                  ← Was Contacts.md
│   ├── accounts.md                  ← Was Accounts.md
│   └── policies.md                  ← Was Policies.md
│   (Backlog → move story cards to active/open-loops.md or a dedicated backlog.md)
│
├── data/                            ← Centralized structured data (was scattered)
│   ├── README.md
│   ├── racing-results.json          ← Was OIO Brain/data/oio_racing-results.json
│   ├── season-results/              ← Move JSON files from events/results/
│   │   ├── oio-2026-season-results.json
│   │   └── (future season files)
│   └── social-posts/                ← Was OIO Brain/data/social-posts/
│       ├── README.md
│       ├── facebook/
│       └── instagram/
│
├── transcripts/                     ← Keep as-is (auto-fetched YouTube transcripts)
│   ├── README.md
│   ├── UNAVAILABLE.md
│   └── YYYY-MM-DD_title/
│       ├── transcript.md
│       └── metadata.json
│   NOTE: OIO Brain/02 - Content/Video Scripts/ contains the same artifact type.
│         Merge into transcripts/ and delete Video Scripts/ folder.
│
├── photos/                          ← Keep, with index moved inside
│   ├── README.md                    ← Absorb PHOTO-INDEX.md from root
│   ├── ian/                         ← Lowercase driver names (was Ian/)
│   │   └── mr2-goblin/              ← Slug-style car names (was 1985-MR2-Goblin)
│   ├── ryan/
│   ├── keegan/
│   ├── karen/
│   └── richard/
│
├── docs/                            ← Technical pipeline documentation (keep as-is)
│   ├── README.md
│   ├── caption-generation-service.md
│   ├── slackbot-social-media.md
│   ├── social-media-deployment.md
│   ├── social-media-integration-testing.md
│   ├── social-media-system-architecture.md
│   ├── social-media-troubleshooting.md
│   └── transcript-pipeline.md
│
├── scripts/                         ← Automation scripts (keep as-is)
│   └── ...
│
└── intake/                          ← Unified intake zone (was docdump/ + picdump/ + todo/)
    ├── README.md                    ← Explain all three intake types
    ├── docs/                        ← Was docdump/
    ├── dailies/                     ← Was docdump/dailies/
    └── photos/                      ← Was picdump/
```

---

## Consolidations Required

These are the specific merges and deduplication actions needed:

| What to Consolidate | From | Into | Notes |
|---|---|---|---|
| Master index | `INDEX.md` + `OIO Brain/00 - Start Here/OIO-Master-Index.md` | `INDEX.md` | Drop OIO-Master-Index.md |
| Priorities | `01-active/active-priorities.md` + `OIO Brain/00 - Start Here/OIO-Current-Priorities.md` | `active/priorities.md` | Merge content, one file |
| Brand voice (canonical) | `OIO Brain/00 - Start Here/OIO-Brand-Guide.md` + `OIO Brain/01 - Brand/Voice-and-Tone.md` | `brand/voice-and-tone.md` | One authoritative doc |
| Templates | `00-core/templates/` + `OIO Brain/07 - Admin/Templates/` | `core/templates/` | Merge, remove dupes |
| Video transcripts | `OIO Brain/02 - Content/Video Scripts/` + `transcripts/` | `transcripts/` | Same artifact, one home |
| Intake zones | `docdump/` + `picdump/` + `todo/` | `intake/` | Rename subfolders as above |
| Photo index | `PHOTO-INDEX.md` (root) | `photos/README.md` | Move + rename |
| Video catalog | `OIO-Video-Catalog.md` (root) | `content/video-catalog.md` | Move + rename |
| Archived brief | `OIO-Master-Brief.md` (root) | `core/archive/OIO-Master-Brief.md` | Move into archive |
| Race data | `OIO Brain/data/oio_racing-results.json` + `OIO Brain/04 - Events/Results/*.json` | `data/` | Centralize |
| Admin backlog | `OIO Brain/07 - Admin/Backlog/` | `active/open-loops.md` or `ops/backlog.md` | Story cards → one place |

---

## What Stays the Same

- `scripts/` — no changes needed
- `docs/` — technical pipeline docs, keep as-is
- `transcripts/` structure — folder-per-video pattern is good
- Car file template: `overview.md`, `setup.md`, `mods.md`, `maintenance.md` — just rename to lowercase
- Frontmatter schema — no changes
- Document class system (Canonical / Working / Capture / Archive) — no changes
- Agent instruction files in `.github/` — no changes

---

## Root Before and After

**Before (17 items at root):**
```
.github/   00-core/   01-active/   docs/   docdump/   INDEX.md   OIO Brain/
OIO-Master-Brief.md   OIO-Video-Catalog.md   PHOTO-INDEX.md   picdump/
README.md   requirements.txt   scripts/   skill.md   todo/   transcripts/
```

**After (16 items at root, all purposeful):**
```
.github/   active/   brand/   business/   cars/   content/   core/
data/   docs/   events/   INDEX.md   intake/   ops/   photos/   production/
README.md   requirements.txt   scripts/   skill.md   transcripts/
```
*(OIO Brain/ absorbed into root-level domain folders; todo, docdump, picdump collapsed into intake/)*

---

## Path Impact on Scripts and Workflows

Before implementing, these scripts and workflows reference paths that will need updating:

| File | Paths to Update |
|---|---|
| `scripts/fetch_transcripts.py` | `transcripts/` — no change |
| `scripts/fetch_social_posts.py` | `OIO Brain/data/social-posts/` → `data/social-posts/` |
| `scripts/analyze_social_posts.py` | `OIO Brain/01 - Brand/Social-Post-Voice.md` → `brand/social-voice.md`; `OIO Brain/02 - Content/Car-and-Driver-Story-Arcs.md` (if exists) |
| `scripts/sync_google_photos.py` | `photos/Ian/`, etc. → `photos/ian/` |
| `scripts/oio-video-fetcher.js` | `OIO-Video-Catalog.md` → `content/video-catalog.md` |
| `scripts/update_catalog_transcripts.py` | `OIO-Video-Catalog.md` → `content/video-catalog.md` |
| `.github/workflows/fetch-social-posts.yml` | Same paths as `fetch_social_posts.py` |
| `.github/workflows/fetch-oio-videos.yml` | `OIO-Video-Catalog.md` → `content/video-catalog.md` |
| `.github/workflows/process-picdump-photos.yml` | `picdump/` → `intake/photos/` |
| `.github/workflows/process-docdump.yml` | `docdump/` → `intake/docs/` |
| `.github/workflows/process-dailies.yml` | `docdump/dailies/` → `intake/dailies/` |
| `.github/copilot-instructions.md` | All path references throughout |
| `00-core/repo-standards.md` | Folder roles table |
| `README.md` | Repo structure diagram |
| `INDEX.md` | All section links |
| `skill.md` | Any path references |

---

## Implementation Order (When Approved)

If Ian approves this proposal, suggested implementation order to minimize breakage:

1. **Flatten `OIO Brain/`** — Move all subfolders to root, update all internal links
2. **Rename folders** — Drop number prefixes, apply kebab-case
3. **Consolidate duplicates** — Merge indexes, priorities, brand voice, templates
4. **Centralize data** — Move JSONs to `data/`
5. **Unify intake** — Rename `docdump/` → `intake/docs/`, `picdump/` → `intake/photos/`, kill `todo/`
6. **Update scripts and workflows** — Fix all hardcoded paths
7. **Update navigation docs** — `README.md`, `INDEX.md`, `skill.md`, `repo-standards.md`, `copilot-instructions.md`
8. **Rename car folders** — Apply nickname-slug convention

Each step should be a separate commit so it's easy to roll back.

---

## Open Questions for Ian

Before implementing, please confirm:

1. **Car folder naming** — Nickname slug (`mr2-goblin`, `celica-dale`) vs year-model (`1985-mr2`, `1972-celica`)? Nicknames are more OIO-flavored but require knowing the nickname. Year-model is more discoverable for new team members.
2. **Sponsorship docs** — Should `brand/sponsorship-pitch.md` and `business/sponsorship-leads.md` be fully merged or stay separate (pitch = brand asset, leads = working CRM)?
3. **`OIO Brain/07 - Admin/Backlog/`** — Move story cards to `active/open-loops.md` or give them their own `ops/backlog.md`?
4. **`OIO-Master-Brief.md`** — Archive into `core/archive/` or keep at root as a historical reference? It's read-only but useful for context.
5. **Timing** — Do this all at once or section by section? Section by section is safer but means living with a mixed structure during the transition.
