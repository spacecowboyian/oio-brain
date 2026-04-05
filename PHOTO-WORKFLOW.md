# OIO Racing Photo Workflow

Automated pipeline from Google Photos picker/album intake to PostBridge draft social posts,
with photo metadata tracked in the OIO brain.

## Architecture

```
Google Photos Picker (preferred) OR Google Photos Album (fallback)
        ↓
[ingest-photos.yml — every 6h]
        ↓
Google Photos Library API
  → first process intake/selected-photos.json pending selections
  → fallback to album polling if no pending selections
  → upload binary to Supabase oio-photos bucket (storage only, no DB)
  → Claude Vision (auto vehicle identification)
  → write entry to photos/{driver}/{vehicle-slug}/photo-log.md
    or photos/triage/photo-log.md if unidentified
        ↓
Commit photo-log.md to repo
        ↓
[generate-captions.yml — daily]
  → read photo-log.md entries with eligible workflow_status
  → generate caption with Claude + OIO brain context
  → update photo-log.md with final_caption and workflow_status=caption_generated
        ↓
Commit photo-log.md to repo
        ↓
[create-drafts.yml — daily]
  → read photo-log.md entries with workflow_status=caption_generated
  → create PostBridge draft with media URL and caption
  → assign tentative publish date (Tue/Fri 10 AM CT cadence)
  → update photo-log.md with postbridge_draft_id and tentative_publish_at
        ↓
Commit photo-log.md to repo
        ↓
Ian reviews draft in PostBridge → approves → publishes
```

## Where Photo Data Lives

| Data | Location |
|---|---|
| Picker-selected intake queue | `intake/selected-photos.json` |
| Binary photo files | Supabase Storage — `oio-photos` bucket |
| Photo metadata and workflow state | `photos/{driver}/{vehicle-slug}/photo-log.md` |
| Unidentified / triage photos | `photos/triage/photo-log.md` |
| Approved caption examples | `photos/{driver}/{vehicle-slug}/caption_history.md` |

## Photo Log Entry Format

Each photo has an entry in the appropriate `photo-log.md` file:

```markdown
## IMG_1234.JPG
- google_photos_id: ABC123xyz
- supabase_url: https://....supabase.co/storage/v1/object/public/oio-photos/...
- thumbnail_url: https://lh3.googleusercontent.com/...=w400-h300-no
- captured_at: 2026-04-05
- source_description: Ian sliding at RayRocks
- rough_caption: Ian sliding at RayRocks
- vehicle_key: goblin
- auto_identified_vehicle_key: goblin
- identification_confidence: 0.92
- workflow_status: caption_generated
- final_caption: The Goblin doing what it does best.
- postbridge_draft_id: pb_abc123
- tentative_publish_at: 2026-04-08T16:00:00Z
- posted_at: none
- notes: Blue AW11 MR2 mid-slide on dirt, 2MR door graphics, dust trail.
```

## Workflow States

Each photo entry has a `workflow_status` field that tracks progress:

| Status | Meaning |
|---|---|
| `ingested` | Logged but not yet identified (Vision unavailable) |
| `auto_identified` | Claude Vision identified the vehicle at ≥80% confidence |
| `needs_triage` | Low confidence — entry in `photos/triage/photo-log.md` |
| `metadata_complete` | Human reviewed and set vehicle_key + rough_caption |
| `caption_generated` | AI-generated final_caption written to photo-log.md |
| `draft_created` | PostBridge draft created with tentative date |
| `approved` | Ian approved the draft (set manually) |
| `posted` | Published (set manually after PostBridge publishes) |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/photo_log.py` | Shared utility — reads and writes photo-log.md entries |
| `scripts/ingest_photos.py` | `selected-photos.json`/album → Supabase Storage + photo-log.md |
| `scripts/generate_captions.py` | Caption generation via Claude + OIO brain context |
| `scripts/create_postbridge_drafts.py` | PostBridge draft creation with Tue/Fri scheduling |
| `scripts/postbridge_client.py` | PostBridge API client library |
| `scripts/auth_google_photos.py` | One-time Google Photos OAuth2 setup helper |

## GitHub Actions Workflows

| Workflow | Schedule | Purpose |
|---|---|---|
| `ingest-photos.yml` | Every 6 hours | Process selected intake first, then fallback album polling, run Vision, write photo-log.md |
| `generate-captions.yml` | Daily at 8:30 AM UTC | Generate captions, update photo-log.md |
| `create-drafts.yml` | Daily at 9:00 AM UTC | Create PostBridge drafts, update photo-log.md |

All three workflows commit and push photo-log.md changes back to the repo.
All three support manual dispatch (with optional `google_id` and `dry_run` inputs).

## Required Secrets

| Secret | Used By |
|---|---|
| `GOOGLE_PHOTOS_CREDENTIALS` | JSON blob: client_id, client_secret, refresh_token |
| `GOOGLE_PHOTOS_ALBUM_ID` | Target album ID from Google Photos URL |
| `ANTHROPIC_API_KEY` | Claude Vision + caption generation |
| `SUPABASE_URL` | Supabase project URL (storage only) |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service-role key (storage only) |
| `POSTBRIDGE_API_KEY` | PostBridge API key |
| `POSTBRIDGE_ACCOUNT_IDS` | Comma-separated social account IDs (optional) |

Note: No Supabase database is used. Supabase is only used as a binary photo
storage bucket. All metadata lives in the brain as markdown.

## Initial Setup

### 1. Supabase Storage bucket

Create a public bucket named `oio-photos` in Supabase Storage.
No database tables needed.

### 2. Google Photos OAuth2

Run the auth helper locally once to generate a refresh token:

```bash
export GOOGLE_CLIENT_ID=<your-client-id>
export GOOGLE_CLIENT_SECRET=<your-client-secret>
pip install google-auth-oauthlib
python scripts/auth_google_photos.py
```

Save the output JSON as the `GOOGLE_PHOTOS_CREDENTIALS` GitHub secret.

### 3. Intake path

Preferred:

- Use `intake/web/` to prepare and commit `intake/selected-photos.json`.
- The ingestion workflow consumes pending selected IDs and marks them ingested.

Fallback:

- Keep `GOOGLE_PHOTOS_ALBUM_ID` configured to use album polling when no pending selected items exist.

### 4. Google Photos album

Create a dedicated Google Photos album for OIO social posting.
Copy the album ID from the URL and save it as `GOOGLE_PHOTOS_ALBUM_ID`.

## Triage Workflow

Photos that Claude Vision cannot identify go to `photos/triage/photo-log.md`.

To promote a triage photo:
1. Open `photos/triage/photo-log.md`
2. Find the entry
3. Set `vehicle_key` to the correct vehicle
4. Optionally improve `rough_caption`
5. Change `workflow_status` to `metadata_complete`
6. Commit and push

The next `generate-captions.yml` run will pick it up.

## Caption Tuning

To improve caption quality over time, add approved captions to:
```
photos/{driver}/{vehicle-slug}/caption_history.md
```

Format: one caption per line starting with `- `.
The caption generation script loads these as style examples.

## Scheduling

Tentative publish dates use a Tue/Fri at 10:00 AM CT cadence (approximated as
16:00 UTC). The scheduler avoids putting two photos on the same day.

Override the posting hour with the `POSTBRIDGE_POST_HOUR_UTC` environment variable.

## Post-Publish State Sync

After Ian approves and publishes in PostBridge, update the photo-log entry manually:
```
- workflow_status: posted
- posted_at: 2026-04-08
```

A future version may add a webhook or polling step to auto-sync publish status.
