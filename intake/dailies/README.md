---
title: Docdump — Dailies Intake Folder
type: notes
status: active
owner: Ian Jennings
updated: 2026-03-29
tags: [workflow, processing, ingest, dailies]
source_of_truth: false
summary: Drop raw daily video transcripts here for Copilot to process into brain summaries. Dailies are raw audio/text dumps from working video files — not final published videos. Copilot will generate a structured summary, file it into the brain, and delete the source file. This folder itself is never deleted.
---

# Docdump — Dailies

> Drop raw daily video transcripts here. Copilot will generate structured summaries and file them into the brain.

---

## What Are Dailies?

**Dailies** are raw audio transcripts from Ian's working video files — the raw clips captured before editing. They are **not** transcripts of final published YouTube videos (those live in `transcripts/` at the repo root).

Dailies capture:
- What was said and done on camera during a shoot
- Mechanical work, build progress, and car details
- Story moments, quotes, and ideas that might make it into a final edit

The goal is to use the audio from dailies to **drive data into the brain** and **create a structured summary** that can inform future video outlines and scripts.

---

## Purpose

Drop a raw daily transcript here and Copilot will automatically:

1. Read the transcript in full
2. Generate a structured summary using the `transcript-summary` template
3. File the summary into `content/summaries/`
4. Update any relevant brain files (car overviews, maintenance logs, event logs, video backlog)
5. Delete the source transcript file from this folder

**This folder itself is never deleted.** Only the individual transcript files inside it are removed after processing.

---

## How to Drop a Daily

1. **Get the transcript** — export from a transcription tool, copy from YouTube auto-captions, or paste the raw text into a `.md` or `.txt` file
2. **Name the file** using the format: `YYYY-MM-DD_description.md` (or `.txt`)
   - Example: `2026-03-22_goblin-rallycross-e1.md`
   - If date is unknown: `undated_description.md`
3. **Drop the file** into this `intake/docs/dailies/` folder
4. **Push to main** — the `process-dailies` workflow will auto-trigger
5. **Done** — Copilot handles the rest

---

## What Copilot Does With It

- Reads the full transcript
- Identifies car(s), people, events, build/mechanical details, and key topics
- Generates a summary using `core/templates/transcript-summary.md`
- Saves the summary to `content/summaries/YYYY-MM-DD_title.md`
- Updates relevant brain files (car Overview, Maintenance-Log, Video-Ideas-Backlog, etc.)
- Deletes the source transcript file from this folder
- Updates `active/` as needed

---

## Supported File Types

| Extension | Notes |
|---|---|
| `.md` | Markdown transcript — preferred |
| `.txt` | Plain text — also fine |
| `.vtt` | WebVTT subtitle file — Copilot will parse timestamps |

---

## Dailies vs. Final Transcripts

| Type | Location | Source | Purpose |
|---|---|---|---|
| **Dailies** | `intake/docs/dailies/` | Raw working clips / audio dumps | Drive brain data + create summary for future scripting |
| **Final transcripts** | `transcripts/` (repo root) | Published YouTube videos (auto-fetched) | Full text archive of published content |

---

## This Folder Should Normally Be Empty

If there are transcript files here, they are waiting to be processed. The `process-dailies` workflow will have already triggered automatically — check the GitHub Issues for an active Copilot processing task. You can also manually trigger the workflow from the Actions tab.
