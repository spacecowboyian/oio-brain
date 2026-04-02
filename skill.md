---
title: How to Use the OIO Brain — Agent Skill Guide
name: oio-brain
description: Operational brain for OIO Outside Inside Outside Racing. Agent onboarding guide covering orientation sequence, folder structure, document classes, read/write rules, key workflows, and standing rules.
type: reference
status: active
owner: Ian Jennings
updated: 2026-03-30
tags: [agents, onboarding, skill, reference]
source_of_truth: true
summary: The onboarding guide for new AI agents working in this repo. Covers orientation sequence, folder roles, document classes, read/write rules, key workflows, and standing rules. Read this before doing anything else.
---

# How to Use the OIO Brain — Agent Skill Guide

This document is for AI agents entering this repository for the first time (or any time). Follow it before reading anything else or taking any action.

---

## Step 1: Orient Yourself (Read in This Order)

Every agent session must start with orientation. Do not skip or reorder these reads.

| Step | File | What You Learn |
|---|---|---|
| 1 | [`README.md`](README.md) | What OIO is and how this repo is organized |
| 2 | [`active/current-state.md`](active/current-state.md) | What is happening right now — vehicles, content, blockers |
| 3 | [`active/priorities.md`](active/priorities.md) | What matters most and why |
| 4 | [`active/open-loops.md`](active/open-loops.md) | Unresolved questions and pending decisions |
| 5 | [`active/next-actions.md`](active/next-actions.md) | Concrete next steps by area |
| 6 | [`INDEX.md`](INDEX.md) | Full map of the repo — use this to navigate to domain files |

Only after orienting yourself should you read domain-specific files in ``.

---

## Step 2: Understand the Folder Structure

```
/
├── README.md                    ← Human entry point
├── INDEX.md                     ← Full section navigation
├── skill.md                     ← This file
├── OIO-Master-Brief.md          ← Original source brief (do not overwrite)
├── OIO-Video-Catalog.md         ← Published YouTube video catalog
├── PHOTO-INDEX.md               ← Master index of all OIO photos
│
├── .github/
│   └── copilot-instructions.md  ← Full standing instructions for agents (authoritative)
│
├── core/                     ← Governance, standards, decisions log, templates
│   ├── repo-standards.md        ← The operational manual for this repo
│   ├── decisions-log.md         ← Log of significant decisions
│   └── templates/               ← File templates (use these when creating new docs)
│
├── active/                   ← Live memory layer — read first, update constantly
│   ├── current-state.md
│   ├── priorities.md
│   ├── open-loops.md
│   └── next-actions.md
│
├──                    ← Canonical knowledge organized by domain
│   ├── 00 - Start Here/         ← Brand identity, operating system, standing rules
│   ├── 01 - Brand/              ← Mission, audience, voice, tone, team bios
│   ├── 02 - Content/            ← Video pipeline, ideas, published log, summaries
│   ├── 03 - Cars/               ← All vehicles organized by driver
│   ├── 04 - Events/             ← Schedules, results, event notes
│   ├── 05 - Production/         ← SOPs, workflows, camera, audio, assets
│   ├── 06 - Business/           ← Budget, sponsors, merch, website
│   ├── 07 - Admin/              ← Contacts, accounts, policies
│   └── data/                    ← Structured data (social posts, results JSON)
│
├── intake/docs/                     ← Intake zone for raw documents from Ian
│   └── dailies/                 ← Raw daily video transcripts from Ian
│
├── photos/                      ← Photo library organized by driver/car
├── intake/photos/                     ← Intake queue for new photos
├── transcripts/                 ← Auto-fetched YouTube video transcripts
└── scripts/                     ← Data processing scripts
```

---

## Step 3: Know the Document Classes

Every file in this repo belongs to one of four classes. This determines how much you trust it and how you should handle it.

| Class | How to Identify | Trust Level | Agent Behavior |
|---|---|---|---|
| **Canonical** | `source_of_truth: true` in frontmatter | Highest | Read with high confidence. Update only when reality changes. Log significant changes. |
| **Working** | `status: active` or `status: draft`, no `source_of_truth: true` | Medium | Read and update freely. Flag stale entries. Don't treat as permanent. |
| **Capture** | No frontmatter, `type: notes`, or lives in `notes/` or raw intake | Low | Treat with caution. Do not promote to canonical without validation. |
| **Archive** | `status: archived` or lives in `archive/` subfolder | Reference only | Do not update. Do not treat as current. Reference only if explicitly needed. |

---

## Step 4: Know How to Write

### Always Prefer Updating Over Creating

Before creating a new file, check if the content belongs in an existing one. Creating near-duplicate files is a violation of repo standards.

- New facts about a car → update the car's `Overview.md` or `Maintenance-Log.md`
- New decisions → log in `core/decisions-log.md`
- New open questions → add to `active/open-loops.md`
- New completed actions → update `active/next-actions.md`
- New video ideas → add to `content/video-backlog.md`

### Frontmatter Is Required

All new files in ``, `core/`, and `active/` must include this frontmatter block:

```yaml
---
title: Human-readable title
type: core | state | sop | checklist | vehicle | content | event | finance | reference | notes | archive
status: active | draft | reference | archived
owner: Ian Jennings
updated: YYYY-MM-DD
tags: [tag1, tag2]
source_of_truth: true | false
summary: 1–3 sentences describing what this file contains and when to use it.
---
```

### After Any Task — Update the Memory Layer

When you finish work, update the relevant `active/` file to reflect what changed. Do not let the memory layer go stale.

---

## Step 5: Know the Key Workflows

### Docdump Processing

When Ian drops a file in `intake/docs/`:

1. Read the full file
2. Identify where the data belongs in the brain
3. Distribute data — update existing files first, create new ones only if needed
4. Delete the source file from `intake/docs/` when done
5. Confirm deletion in your progress report
6. Update `active/` files to reflect any state changes

**Rules:** Always delete source files after processing. If a file can't be fully processed, document gaps in `active/open-loops.md`, then still delete the source.

### Dailies Processing

When Ian drops a raw daily transcript in `intake/dailies/`:

1. Read the full transcript
2. Generate a structured summary using the template at `core/templates/transcript-summary.md`
3. Save the summary to `content/summaries/YYYY-MM-DD_description.md`
4. Update relevant brain files (car overviews, maintenance logs, video ideas, events, active state)
5. Delete the source file from `intake/dailies/` when done
6. **Never delete** `intake/dailies/` itself or `intake/dailies/README.md`

### Photo Processing

When images are pushed to `intake/photos/`:

- A GitHub Action (`process-picdump-photos.yml`) auto-spawns a Copilot agent to file them
- Photos are organized into `photos/[Driver]/[Car]/`
- `PHOTO-INDEX.md` at repo root is the master index — update it when filing photos
- Each car folder has a `photo-log.md` — update it with new entries

### YouTube Transcripts

- Final YouTube transcripts are auto-fetched by `.github/workflows/fetch-youtube-transcripts.yml`
- They are stored in `transcripts/YYYY-MM-DD_title/` (transcript.md + metadata.json)
- Do not manually edit these — they are the auto-fetch archive

### Social Posts

- Facebook + Instagram posts are fetched automatically by `scripts/fetch_social_posts.py`
- Stored in `data/social-posts/facebook/` and `.../instagram/`
- `scripts/analyze_social_posts.py` runs after each fetch and injects arc data into car/driver files and a stats appendix into `brand/social-voice.md`
- Arc data lives in each car's `Overview.md` and each driver's section of `Team-Bios.md` — injected via `<!-- social-arc:{key}:start/end -->` markers
- Cross-cutting arcs (championship, Fit-Off) live in `content/story-arcs.md`
- **`brand/social-voice.md` is hand-authored** (`source_of_truth: true`) — the script only updates the live stats appendix at the bottom (inside `<!-- social-voice-stats:start/end -->` markers). The guide content above those markers is never overwritten.
- See `brand/social-voice.md` for the canonical voice guide, tone buckets, post patterns, CTAs, and hashtag strategy

---

## Step 6: Confidence Calibration

| Situation | What to Do |
|---|---|
| Answer is clearly in the repo | State it confidently. Cite the source file. |
| Answer is partially in the repo | Share what you know, flag what's missing, ask for the rest. |
| Answer is not in the repo at all | Say so. Ask Ian. Do not invent. |
| Conflicting info across files | Flag the conflict, ask for clarification, update once resolved. |
| Information is uncertain | Use `TODO:` or `[unknown]` — never fill gaps with guesses. |

---

## Standing Rules (Never Break)

1. **Do not invent facts.** Use `TODO:` or `[unknown]` instead.
2. **Do not create near-duplicate files.** Update existing ones.
3. **Do not delete content — archive it.** Mark as `status: archived` and move to `archive/` if needed.
4. **Do not treat capture notes as source of truth.**
5. **Do not skip frontmatter** on new files in governed folders.
6. **Do not let `active/` files go stale.** They are the memory layer — update them when things change.
7. **Log significant decisions** in `core/decisions-log.md` with date and rationale.
8. **Always delete source files** from `intake/docs/` and `intake/dailies/` after processing.

---

## Quick Reference: Where Does It Go?

| Type of content | Where it lives |
|---|---|
| Brand voice, tone, persona | `brand/` |
| Video ideas and pipeline | `content/` |
| Car builds and maintenance | `cars/[driver]/[car-slug]/` |
| Race results and events | `events/` |
| Filming and editing SOPs | `production/` |
| Budget and business | `business/` |
| Contacts and accounts | `ops/` |
| Current state snapshot | `active/current-state.md` |
| New decisions | `core/decisions-log.md` |
| Open questions | `active/open-loops.md` |
| Next concrete steps | `active/next-actions.md` |
| New video ideas | `content/video-backlog.md` |
| Daily transcript summaries | `content/Summaries/` |
| Photos | `photos/[Driver]/[Car]/` |

---

*For the full standing instructions and behavioral rules, see [`.github/copilot-instructions.md`](.github/copilot-instructions.md). That file is the authoritative source. This skill guide is the fast-entry version.*
