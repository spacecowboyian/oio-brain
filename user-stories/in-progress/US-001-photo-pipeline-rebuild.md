---
title: "US-001: Album-Driven Photo Pipeline with AI Vision and PostBridge Drafts"
type: reference
status: in-progress
owner: Ian Jennings
updated: 2026-04-05
tags: [photo-pipeline, google-photos, ai-vision, postbridge, agents]
source_of_truth: false
summary: Rebuild the photo ingestion pipeline to poll the OIO Google Photos album directly, identify cars via Claude Vision and photo descriptions, write to car photo logs, and create PostBridge draft posts — all in one unified script run.
---

# US-001: Album-Driven Photo Pipeline with AI Vision and PostBridge Drafts

## Story

**As** Ian (and agents acting on Ian's behalf),  
**I want** photos added to my Google Photos album to be automatically identified, logged to the correct car's photo log, and pushed to PostBridge as a draft social post,  
**So that** I only need to add photos to a Google Photos album — and optionally write a description — for the entire pipeline to run without any manual intervention beyond review in PostBridge.

---

## Background

The current pipeline relies on a "photo picker" intake step (`intake/selected-photos.json`) and three separate scripts. The picker is not being used. The goal is to eliminate it entirely and drive the pipeline solely from the OIO Google Photos album.

Photos that can't be confidently identified at run time go to an unknown log. When Ian adds descriptions to those photos in the Google Photos app, the next script run detects the change and retries identification automatically.

**Album ID:** `AF1QipMW1KCdIEBo2rMA--SpBF2pOt3pf0LkJp5X51DLN21brlvqmYanlJ1_YB11IEKnmA`

---

## Acceptance Criteria

### AC-1: Album polling replaces picker intake
- Given the script runs
- When `intake/selected-photos.json` is empty or absent
- Then the script polls the OIO Google Photos album via the Google Photos API and processes all photos not already present in any photo log

### AC-2: Already-processed photos are skipped
- Given a photo has `workflow_status: draft_created` in any photo log
- When the script runs
- Then that photo is not re-processed

### AC-3: AI vision identifies the car
- Given a new photo is found in the album
- When Claude Vision (`claude-opus-4-6`) analyzes the image with OIO fleet context and any available Google Photos description as a hint
- Then it returns `{vehicle_key, confidence, event_context, reasoning, visual_notes}`

### AC-4: High-confidence photos are routed to the car's log
- Given identification confidence is >= 0.8
- When the photo is processed
- Then an entry is appended to `photos/{driver}/{vehicle-slug}/photo-log.md` with fields: `google_photos_id`, `google_photos_url`, `captured_at`, `source_description`, `vehicle_key`, `identification_confidence`, `notes`, `workflow_status: auto_identified`

### AC-5: A caption is generated for identified photos
- Given a photo has been written to a car photo log with `workflow_status: auto_identified`
- When the script continues
- Then a caption is generated using Claude with brand voice, vehicle overview, story arcs, caption history, and the photo description as context
- And the caption is written as `final_caption` in the photo log entry

### AC-6: A PostBridge draft is created for captioned photos
- Given `final_caption` exists for a photo
- When the script continues
- Then `postbridge_client.py` creates a draft post with the caption and the Google Photos download URL (`baseUrl + '=d'`) as the media URL
- And `postbridge_draft_id` is written to the photo log entry
- And `workflow_status` is updated to `draft_created`

### AC-7: Low-confidence photos are routed to the unknown log
- Given identification confidence is < 0.8 OR `vehicle_key` is `unknown` or `other`
- When the photo is processed
- Then an entry is appended to `photos/unknown/photo-log.md` with `workflow_status: needs_identification` and `last_description` set to the current Google Photos description (empty string if none)

### AC-8: Unknown photos are re-evaluated when a description is added
- Given a photo is in `photos/unknown/photo-log.md` with `workflow_status: needs_identification`
- When the script runs and the current Google Photos description differs from the stored `last_description`
- Then Claude Vision is re-run with the new description as a hint
- And if confidence is now >= 0.8: entry is appended to the correct car log, caption is generated, PostBridge draft is created, and the entry is removed from the unknown log
- And `last_description` is updated in the unknown log regardless of outcome

### AC-9: No Supabase dependency
- The script must not import `supabase`, reference `SUPABASE_URL`, or require `SUPABASE_SERVICE_ROLE_KEY`
- `supabase_url` and `thumbnail_url` are removed from the photo log schema in `photo_log.py`

### AC-10: Unified single script
- All logic (poll → identify → caption → PostBridge) runs from a single entry point: `scripts/process_photos.py`
- The three old scripts (`ingest_photos.py`, `generate_captions.py`, `create_postbridge_drafts.py`) are not deleted but their GitHub Actions workflows are disabled

### AC-11: GitHub Actions workflow
- A new workflow `.github/workflows/process-photos.yml` runs `process_photos.py` on a cron (every 6 hours) and via manual dispatch
- The workflow commits updated photo log files back to the repo after each run
- The three old workflows (`ingest-photos.yml`, `generate-captions.yml`, `create-drafts.yml`) are disabled by removing their `on:` triggers (replace with `on: workflow_dispatch:` only, adding a comment marking them deprecated)

---

## Technical Notes

**Reuse these source files for implementation logic — do not rewrite from scratch:**
- `scripts/ingest_photos.py` — Google Photos API calls, credential loading, Claude Vision prompt
- `scripts/generate_captions.py` — caption generation context loading and Claude prompt
- `scripts/create_postbridge_drafts.py` — PostBridge draft creation logic
- `scripts/postbridge_client.py` — keep as-is, import directly
- `scripts/photo_log.py` — update schema first (see below), then use in new script

**Photo log schema changes required in `photo_log.py` before writing `process_photos.py`:**
- Remove fields: `supabase_url`, `thumbnail_url`, `rough_caption`
- Add fields: `google_photos_url` (stores permanent `productUrl`), `last_description`
- Add `photos/unknown/` to `VEHICLE_FOLDERS` dict with key `unknown`
- New `workflow_status` values: `needs_identification` (replaces `needs_triage`), `draft_created` (new terminal success state)

**Image delivery:**
- Google Photos `baseUrl + '=d'` is fetched fresh at runtime and passed directly to PostBridge and Claude Vision
- `baseUrl` is never stored in the photo log — it expires
- `google_photos_url` (`productUrl`) is the permanent audit trail reference

**`photos/unknown/photo-log.md` must be created** with correct frontmatter before the script can write to it.

**Env vars required:**

| Variable | Notes |
|---|---|
| `GOOGLE_PHOTOS_CREDENTIALS` | Existing — JSON with OAuth2 credentials |
| `GOOGLE_PHOTOS_ALBUM_ID` | New — value: `AF1QipMW1KCdIEBo2rMA--SpBF2pOt3pf0LkJp5X51DLN21brlvqmYanlJ1_YB11IEKnmA` |
| `ANTHROPIC_API_KEY` | Existing |
| `POSTBRIDGE_API_KEY` | Existing |
| `POSTBRIDGE_ACCOUNT_IDS` | Existing |

**Env vars to remove:** `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`

---

## Out of Scope

- The 13 raw JPEGs in `intake/photos/` — not processed by this pipeline; Ian should upload to the OIO album if desired
- Periodic retry of unknowns without a description change (future enhancement)
- Deleting the old scripts (`ingest_photos.py`, `generate_captions.py`, `create_postbridge_drafts.py`)
- `intake/selected-photos.json` processing — the picker path is retired but the file is left in place

---

## Verification Steps

1. Set all required env vars locally, run `python scripts/process_photos.py`
2. Confirm new photos from the OIO album appear in the correct `photos/{driver}/{slug}/photo-log.md` with `workflow_status: draft_created`
3. Confirm low-confidence photos appear in `photos/unknown/photo-log.md` with `workflow_status: needs_identification`
4. Confirm a PostBridge draft was created (check PostBridge UI or API response)
5. Add a description to one photo listed in `photos/unknown/photo-log.md` via the Google Photos app → re-run → confirm it promotes to a car log and a PostBridge draft is created
6. Confirm `.github/workflows/process-photos.yml` runs successfully via manual dispatch in GitHub Actions
