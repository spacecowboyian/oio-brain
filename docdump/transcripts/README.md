---
title: Docdump — Transcripts Intake Folder
type: notes
status: active
owner: Ian Jennings
updated: 2026-03-29
tags: [workflow, processing, ingest, transcripts, docdump]
source_of_truth: false
summary: Drop raw video transcripts here for Copilot to process into summaries. Copilot will read each transcript, generate a structured summary using the transcript-summary template, store it in the brain, and delete the source file. The transcripts/ folder itself is never deleted.
---

# Docdump — Transcripts

> Drop raw video transcripts here. Copilot will generate structured summaries and file them into the brain.

---

## Purpose

This folder is the intake zone for **raw video transcripts** — text you've exported, copied, or had AI generate from a video's audio. 

Drop a transcript file here (any `.md`, `.txt`, or `.vtt` format), push to main, and Copilot will automatically:

1. Read the transcript in full
2. Generate a structured summary using the `transcript-summary` template
3. File the summary into `OIO Brain/02 - Content/Summaries/`
4. Update any relevant brain files (car overviews, event logs, video catalog)
5. Delete the source transcript file from this folder

**This folder itself is never deleted.** Only the individual transcript files inside it are removed after processing.

---

## How to Drop a Transcript

1. **Get the transcript** — export from YouTube Studio, copy from a transcript AI tool, or paste raw text into a `.md` or `.txt` file
2. **Name the file** using the format: `YYYY-MM-DD_video-title.md` (or `.txt`)
   - Example: `2026-03-22_goblin-rallycross-e1.md`
3. **Drop the file** into this `docdump/transcripts/` folder
4. **Push to main** — the `process-transcripts` workflow will auto-trigger
5. **Done** — Copilot handles the rest

---

## What Copilot Does With It

- Reads the full transcript
- Identifies the video, car(s), people, events, and key topics
- Generates a summary using `00-core/templates/transcript-summary.md`
- Saves the summary to `OIO Brain/02 - Content/Summaries/YYYY-MM-DD_title.md`
- Updates relevant brain files (car Overview, Maintenance-Log, Published-Videos, etc.)
- Deletes the source transcript file from this folder
- Updates `01-active/` as needed

---

## Supported File Types

| Extension | Notes |
|---|---|
| `.md` | Markdown transcript — preferred |
| `.txt` | Plain text — also fine |
| `.vtt` | WebVTT subtitle file — Copilot will parse timestamps |

---

## This Folder Should Normally Be Empty

If there are transcript files here, they are waiting to be processed. The `process-transcripts` workflow will have already triggered automatically — check the GitHub Issues for an active Copilot processing task. You can also manually trigger the workflow from the Actions tab.
