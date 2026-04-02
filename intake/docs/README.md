---
title: Docdump — Inbound Document Processing Folder
type: notes
status: active
owner: Ian Jennings
updated: 2026-03-29
tags: [workflow, processing, ingest]
source_of_truth: false
summary: Drop raw documents here for processing by Copilot. When Ian drops a file here and asks Copilot to process it, Copilot will extract the data into the appropriate brain files and then delete the original source file from this folder.
---

# Docdump

> Drop documents here. Tell Copilot to process them. They will be absorbed into the brain and deleted.

---

## Purpose

This folder is the intake zone for raw documents that need to be processed into the OIO Brain.

Ian drops a file here — a spreadsheet export, a YouTube catalog, a notes dump, a CSV from an event timer, a sponsor brief, anything — and then tells Copilot: *"Process the file in intake/docs."*

Copilot reads the file, extracts the relevant data, distributes it into the appropriate brain files, and **deletes the original file from this folder**.

The intake/docs folder should normally be empty. If there's a file here, it hasn't been processed yet.

---

## Workflow

1. **Ian drops a file** into `intake/docs/`
2. **Ian tells Copilot** to process it (e.g., "Process the file in docdump" or "The docdump has a new race results CSV — update the brain")
3. **Copilot reads the file**, identifies the relevant brain destinations, and distributes the data
4. **Copilot deletes the original file** from `intake/docs/` once the data has been successfully written to the brain
5. **Copilot updates** the relevant `active/` files to reflect any state changes

---

## Rules for Agents Processing Docdump Files

- **Always read the file fully** before determining where the data belongs
- **Distribute to existing files first** — update before creating new files
- **Follow all repo standards** — frontmatter, document classes, source of truth rules
- **Delete the source file after processing** — do not leave originals in the folder
- **Confirm deletion** in your progress report — note which file was processed and deleted
- **If data is ambiguous**, make your best determination and note any uncertainties in a `TODO:` comment in the destination file
- **If a file cannot be fully processed**, document what was done and what remains in `active/open-loops.md` before deleting

---

## Supported Document Types

Any document type can be dropped here. Common ones:

| Type | Where to Drop | Likely Destination |
|---|---|---|
| YouTube video catalog / export | `intake/docs/` (root) | `content/published-videos.md` + car Overview files |
| Race event results | `intake/docs/` (root) | `events/results/` |
| Expense / budget data | `intake/docs/` (root) | `business/` |
| Sponsor info / pitch notes | `intake/docs/` (root) | `business/` |
| Build notes / spec sheets | `intake/docs/` (root) | Relevant car `Overview.md` or `Setup-Notes.md` |
| Raw video ideas | `intake/docs/` (root) | `content/video-backlog.md` |
| Event schedule | `intake/docs/` (root) | `events/schedules.md` |
| General notes | `intake/docs/` (root) | `active/` appropriate file |
| **Raw daily video transcripts** | **`intake/docs/dailies/`** | **`content/summaries/`** |

---

## Special Intake: Dailies

Daily video transcripts (raw audio dumps from Ian's working video files) have their own subfolder: **`intake/docs/dailies/`**

Drop raw daily transcript files (`.md`, `.txt`, or `.vtt`) there. A separate workflow (`process-dailies`) will auto-trigger and spawn a Copilot agent to generate structured summaries using the `transcript-summary` template. See `intake/docs/dailies/README.md` for full details.

> **Dailies vs. final transcripts:** `intake/docs/dailies/` is for raw working clips — not published videos. Final YouTube video transcripts are stored in `transcripts/` at the repo root and are fetched automatically by the `fetch-youtube-transcripts` workflow.

---

## This Folder Should Be Empty

If you see files here (in the root `intake/docs/`), they are waiting to be processed. The `process-docdump` workflow auto-triggers whenever files are pushed to `intake/docs/` — a Copilot agent will be spawned automatically. You can also manually trigger the workflow from the Actions tab if needed.

The `dailies/` subfolder may contain files while they await processing — that is normal.
