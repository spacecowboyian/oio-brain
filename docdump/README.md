---
title: Docdump — Inbound Document Processing Folder
type: notes
status: active
owner: Ian Jennings
updated: 2026-03-28
tags: [workflow, processing, ingest, docdump]
source_of_truth: false
summary: Drop raw documents here for processing by Copilot. When Ian drops a file here and asks Copilot to process it, Copilot will extract the data into the appropriate brain files and then delete the original source file from this folder.
---

# Docdump

> Drop documents here. Tell Copilot to process them. They will be absorbed into the brain and deleted.

---

## Purpose

This folder is the intake zone for raw documents that need to be processed into the OIO Brain.

Ian drops a file here — a spreadsheet export, a YouTube catalog, a notes dump, a CSV from an event timer, a sponsor brief, anything — and then tells Copilot: *"Process the file in docdump."*

Copilot reads the file, extracts the relevant data, distributes it into the appropriate brain files, and **deletes the original file from this folder**.

The docdump folder should normally be empty. If there's a file here, it hasn't been processed yet.

---

## Workflow

1. **Ian drops a file** into `docdump/`
2. **Ian tells Copilot** to process it (e.g., "Process the file in docdump" or "The docdump has a new race results CSV — update the brain")
3. **Copilot reads the file**, identifies the relevant brain destinations, and distributes the data
4. **Copilot deletes the original file** from `docdump/` once the data has been successfully written to the brain
5. **Copilot updates** the relevant `01-active/` files to reflect any state changes

---

## Rules for Agents Processing Docdump Files

- **Always read the file fully** before determining where the data belongs
- **Distribute to existing files first** — update before creating new files
- **Follow all repo standards** — frontmatter, document classes, source of truth rules
- **Delete the source file after processing** — do not leave originals in the folder
- **Confirm deletion** in your progress report — note which file was processed and deleted
- **If data is ambiguous**, make your best determination and note any uncertainties in a `TODO:` comment in the destination file
- **If a file cannot be fully processed**, document what was done and what remains in `01-active/open-loops.md` before deleting

---

## Supported Document Types

Any document type can be dropped here. Common ones:

| Type | Likely Destination |
|---|---|
| YouTube video catalog / export | `OIO Brain/02 - Content/Published-Videos.md` + car Overview files |
| Race event results | `OIO Brain/04 - Events/Results/` |
| Expense / budget data | `OIO Brain/06 - Business/` |
| Sponsor info / pitch notes | `OIO Brain/06 - Business/` |
| Build notes / spec sheets | Relevant car `Overview.md` or `Setup-Notes.md` |
| Raw video ideas | `OIO Brain/02 - Content/Video-Ideas-Backlog.md` |
| Event schedule | `OIO Brain/04 - Events/Schedules.md` |
| General notes | `01-active/` appropriate file |

---

## This Folder Should Be Empty

If you see files here, they are waiting to be processed. Tell Copilot: *"Process the file(s) in docdump."*
