---
title: Picdump — Photo Intake
type: notes
status: active
owner: Ian Jennings
updated: 2026-03-28
tags: [photos, intake, picdump]
source_of_truth: false
summary: Intake folder for raw photos that need to be filed into the OIO photo library. Drop images here and push to main. A GitHub Action will automatically spawn a Copilot agent to identify, file, describe, and index each photo.
---

# Picdump — Photo Intake Zone

> Drop photos here. Push to main. The agent handles the rest.

This is the intake zone for photos that need to be added to the OIO photo library. It works the same way as `docdump/` — it's a processing queue, not a permanent home.

---

## How to Add a Photo

1. Drop your image file(s) into this folder
2. Commit and push (or open a PR) to the `main` branch
3. A GitHub Action fires automatically and creates an issue tagging `@copilot`
4. The Copilot agent:
   - Identifies which car is in the photo (using visual AI + OIO fleet knowledge)
   - Moves the photo to the correct `photos/{Driver}/{Car}/` folder
   - Creates or updates the car's `photo-log.md`
   - Adds the photo to `PHOTO-INDEX.md`
   - Updates the car's `Overview.md` in `OIO Brain/03 - Cars/` with any new visual detail
   - Removes the original from this folder

---

## Rules

- **This folder should always be empty** once photos are processed. It is a queue, not storage.
- **Supported formats:** `.png`, `.jpg`, `.jpeg`, `.heic`, `.webp`
- **Naming:** Keep original filenames. The agent will log them as-is.
- If a photo cannot be identified, the agent will add it to `01-active/open-loops.md` and leave it here with a note.

---

## Current Queue

*(Empty after processing)*