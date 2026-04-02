---
title: Intake — Inbound Processing Folder
type: notes
status: active
owner: Ian Jennings
updated: 2026-04-02
tags: [workflow, processing, ingest, intake]
source_of_truth: false
summary: Unified intake zone for all inbound content. Drop documents into intake/docs/, photos into intake/photos/, and raw daily transcripts into intake/dailies/. Copilot agents process each queue and delete source files after processing.
---

# Intake

> Drop content here. Tell Copilot to process it. It will be absorbed into the brain and deleted.

This is the unified intake zone for all inbound content that needs to be processed into the OIO Brain.

---

## Queues

### `intake/docs/` — Documents

Drop any raw document here for processing: spreadsheet exports, race results CSVs, notes dumps, sponsor briefs, YouTube catalogs, video ideas, etc.

Ian drops a file here and tells Copilot: *"Process the file in intake/docs."*

Copilot reads the file, extracts the relevant data, distributes it into the appropriate brain files, and **deletes the original file**.

**Common destinations:**

| Type | Likely Destination |
|---|---|
| YouTube video catalog / export | `content/published-videos.md` + car overview files |
| Race event results | `events/results/` |
| Expense / budget data | `business/` |
| Sponsor info / pitch notes | `business/sponsorship-leads.md` |
| Build notes / spec sheets | Relevant car `overview.md` or `setup.md` |
| Raw video ideas | `content/video-backlog.md` |
| Event schedule | `events/schedules.md` |
| General notes | Appropriate `active/` file |

### `intake/photos/` — Photos

Drop image files here. A GitHub Action fires automatically and creates an issue tagging `@copilot`. The Copilot agent:

1. Identifies which car is in the photo (using visual AI + OIO fleet knowledge)
2. Moves the photo to the correct `photos/{driver}/{car}/` folder
3. Creates or updates the car's `photo-log.md`
4. Adds the photo to `photos/README.md`
5. Updates the car's `overview.md` with any new visual detail
6. Removes the original from this folder

**Supported formats:** `.png`, `.jpg`, `.jpeg`, `.heic`, `.webp`

### `intake/dailies/` — Daily Transcripts

Drop raw daily video transcripts (raw audio/text from working video files — not published YouTube videos) here.

See [`intake/dailies/README.md`](dailies/README.md) for full workflow details.

---

## Rules for All Queues

- **These folders should normally be empty** — files are processing queues, not storage
- **Always read the full file** before determining where data belongs
- **Distribute to existing files first** — update before creating new files
- **Follow all repo standards** — frontmatter, document classes, source of truth rules
- **Delete the source file after processing** — confirm deletion in your progress report
- **If data is ambiguous**, note uncertainties with `TODO:` comments in the destination file
- **If a file cannot be fully processed**, document what was done in `active/open-loops.md` — then still delete the source file

---

## Naming

Files can keep their original names. For dailies, the preferred format is `YYYY-MM-DD_description.md`.
