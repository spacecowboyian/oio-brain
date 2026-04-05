# OIO Racing Photo Workflow

Automated pipeline from Google Photos album to PostBridge draft social posts.

## Overview

Photos added to the OIO Google Photos album move through a structured workflow:

```
Google Photos Album
        ↓
[ingest-photos.yml — every 6h]
        ↓
Google Photos Library API
        ↓
Supabase storage (oio-photos bucket) + photos table
        ↓
Claude Vision (auto vehicle identification)
        ↓
[generate-captions.yml — daily]
        ↓
Claude caption generation using OIO brain context
        ↓
[create-drafts.yml — daily]
        ↓
PostBridge draft post with tentative schedule date
        ↓
Human review → approve → publish
```

## Workflow States

Each photo record in Supabase has a `workflow_status` field:

| Status | Meaning |
|---|---|
| `ingested` | New photo stored in Supabase — awaiting identification |
| `auto_identified` | Claude Vision identified the vehicle at ≥80% confidence |
| `needs_triage` | Low confidence — needs human to assign vehicle/category |
| `metadata_complete` | Human has reviewed, vehicle assigned, rough caption set |
| `caption_generated` | AI-generated caption saved to `final_caption` |
| `draft_created` | PostBridge draft created with tentative publish date |
| `approved` | Ian has approved the draft for publishing |
| `posted` | Published to social media |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/ingest_photos.py` | Google Photos → Supabase ingestion + Claude Vision identification |
| `scripts/generate_captions.py` | Caption generation using Claude + OIO brain context |
| `scripts/create_postbridge_drafts.py` | PostBridge draft creation with tentative scheduling |
| `scripts/postbridge_client.py` | PostBridge API client library |
| `scripts/auth_google_photos.py` | One-time Google Photos OAuth2 setup helper |

## GitHub Actions Workflows

| Workflow | Schedule | Purpose |
|---|---|---|
| `ingest-photos.yml` | Every 6 hours | Detects new photos, uploads to Supabase, runs Vision |
| `generate-captions.yml` | Daily at 8:30 AM UTC | Generates captions for eligible photos |
| `create-drafts.yml` | Daily at 9:00 AM UTC | Creates PostBridge drafts for captioned photos |

All three workflows can also be triggered manually via GitHub Actions → workflow_dispatch.

## Required Secrets

| Secret | Used By |
|---|---|
| `GOOGLE_PHOTOS_CREDENTIALS` | JSON blob with OAuth2 client_id, client_secret, refresh_token |
| `GOOGLE_PHOTOS_ALBUM_ID` | Target album ID from Google Photos URL |
| `ANTHROPIC_API_KEY` | Claude Vision + caption generation |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service-role key |
| `POSTBRIDGE_API_KEY` | PostBridge API key |
| `POSTBRIDGE_ACCOUNT_IDS` | Comma-separated social account IDs (optional) |

## Initial Setup

### 1. Supabase database schema

Run `data/supabase-schema.sql` once in the Supabase SQL editor.

This creates:
- `photos` table with full workflow state machine fields
- `caption_history` table for style tuning over time
- `photo_processing_runs` table for run audit logs

### 2. Supabase storage bucket

Create a public bucket named `oio-photos` in Supabase Storage.

### 3. Google Photos OAuth2

Run the auth helper locally to generate a refresh token:

```bash
export GOOGLE_CLIENT_ID=<your-client-id>
export GOOGLE_CLIENT_SECRET=<your-client-secret>
pip install google-auth-oauthlib
python scripts/auth_google_photos.py
```

Save the output JSON as the `GOOGLE_PHOTOS_CREDENTIALS` GitHub secret.

### 4. Google Photos album

Create a dedicated Google Photos album for OIO social posting.
Copy the album ID from the URL and save it as `GOOGLE_PHOTOS_ALBUM_ID`.

## Manual Triage

Photos flagged `needs_triage` require human input before captioning.

For each triage photo in Supabase, set:
- `vehicle_key` — one of: `goblin`, `dale`, `fittycent`, `nessie`, `killer-corolla`,
  `geoffrey`, `tootie`, `mgb-gt`, `ae86`, `other`
- `rough_caption` — a brief description or caption seed
- `workflow_status` → `metadata_complete` when ready for caption generation

Human edits always override automation. The system will not overwrite
`vehicle_key` or `rough_caption` once they are set by a human.

## Caption Rules

Generated captions follow strict OIO brand voice rules:
- No emoji
- No em dashes
- Write like a real human
- Grounded in vehicle history and current season context
- Improves on the rough caption rather than ignoring it

See `brand/voice-and-tone.md` for the full brand voice reference.

## Scheduling

Tentative publish dates default to Tuesday and Friday at 10:00 AM CT.
The scheduler avoids placing two photos on the same day.

Dates are stored in `tentative_publish_at` in Supabase and passed to PostBridge
as the scheduled date on the draft. All posts go to draft status — not immediate publishing.
