---
title: How to Use the OIO Brain — Agent Skill Guide
name: oio-brain
description: Operational brain for OIO Outside Inside Outside Racing. Agent onboarding guide covering orientation sequence, folder structure, document classes, read/write rules, key workflows, and standing rules.
type: reference
status: active
owner: Ian Jennings
updated: 2026-03-29
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
| 2 | [`01-active/current-state.md`](01-active/current-state.md) | What is happening right now — vehicles, content, blockers |
| 3 | [`01-active/active-priorities.md`](01-active/active-priorities.md) | What matters most and why |
| 4 | [`01-active/open-loops.md`](01-active/open-loops.md) | Unresolved questions and pending decisions |
| 5 | [`01-active/next-actions.md`](01-active/next-actions.md) | Concrete next steps by area |
| 6 | [`INDEX.md`](INDEX.md) | Full map of the repo — use this to navigate to domain files |

Only after orienting yourself should you read domain-specific files in `OIO Brain/`.

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
├── 00-core/                     ← Governance, standards, decisions log, templates
│   ├── repo-standards.md        ← The operational manual for this repo
│   ├── decisions-log.md         ← Log of significant decisions
│   └── templates/               ← File templates (use these when creating new docs)
│
├── 01-active/                   ← Live memory layer — read first, update constantly
│   ├── current-state.md
│   ├── active-priorities.md
│   ├── open-loops.md
│   └── next-actions.md
│
├── OIO Brain/                   ← Canonical knowledge organized by domain
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
├── docdump/                     ← Intake zone for raw documents from Ian
│   └── dailies/                 ← Raw daily video transcripts from Ian
│
├── photos/                      ← Photo library organized by driver/car
├── picdump/                     ← Intake queue for new photos
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
- New decisions → log in `00-core/decisions-log.md`
- New open questions → add to `01-active/open-loops.md`
- New completed actions → update `01-active/next-actions.md`
- New video ideas → add to `OIO Brain/02 - Content/Video-Ideas-Backlog.md`

### Frontmatter Is Required

All new files in `OIO Brain/`, `00-core/`, and `01-active/` must include this frontmatter block:

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

When you finish work, update the relevant `01-active/` file to reflect what changed. Do not let the memory layer go stale.

---

## Step 5: Know the Key Workflows

### Docdump Processing

When Ian drops a file in `docdump/`:

1. Read the full file
2. Identify where the data belongs in the brain
3. Distribute data — update existing files first, create new ones only if needed
4. Delete the source file from `docdump/` when done
5. Confirm deletion in your progress report
6. Update `01-active/` files to reflect any state changes

**Rules:** Always delete source files after processing. If a file can't be fully processed, document gaps in `01-active/open-loops.md`, then still delete the source.

### Dailies Processing

When Ian drops a raw daily transcript in `docdump/dailies/`:

1. Read the full transcript
2. Generate a structured summary using the template at `00-core/templates/transcript-summary.md`
3. Save the summary to `OIO Brain/02 - Content/Summaries/YYYY-MM-DD_description.md`
4. Update relevant brain files (car overviews, maintenance logs, video ideas, events, active state)
5. Delete the source file from `docdump/dailies/` when done
6. **Never delete** `docdump/dailies/` itself or `docdump/dailies/README.md`

### Photo Processing

When images are pushed to `picdump/`:

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
- Stored in `OIO Brain/data/social-posts/facebook/` and `.../instagram/`
- `scripts/analyze_social_posts.py` regenerates `Social-Post-Voice.md` and `Car-and-Driver-Story-Arcs.md` after each fetch
- **Do not hand-edit** those two generated files — they are overwritten each run

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
6. **Do not let `01-active/` files go stale.** They are the memory layer — update them when things change.
7. **Log significant decisions** in `00-core/decisions-log.md` with date and rationale.
8. **Always delete source files** from `docdump/` and `docdump/dailies/` after processing.

---

## Quick Reference: Where Does It Go?

| Type of content | Where it lives |
|---|---|
| Brand voice, tone, persona | `OIO Brain/01 - Brand/` |
| Video ideas and pipeline | `OIO Brain/02 - Content/` |
| Car builds and maintenance | `OIO Brain/03 - Cars/[Driver]/[Car]/` |
| Race results and events | `OIO Brain/04 - Events/` |
| Filming and editing SOPs | `OIO Brain/05 - Production/` |
| Budget and business | `OIO Brain/06 - Business/` |
| Contacts and accounts | `OIO Brain/07 - Admin/` |
| Current state snapshot | `01-active/current-state.md` |
| New decisions | `00-core/decisions-log.md` |
| Open questions | `01-active/open-loops.md` |
| Next concrete steps | `01-active/next-actions.md` |
| New video ideas | `OIO Brain/02 - Content/Video-Ideas-Backlog.md` |
| Daily transcript summaries | `OIO Brain/02 - Content/Summaries/` |
| Photos | `photos/[Driver]/[Car]/` |

---

*For the full standing instructions and behavioral rules, see [`.github/copilot-instructions.md`](.github/copilot-instructions.md). That file is the authoritative source. This skill guide is the fast-entry version.*
