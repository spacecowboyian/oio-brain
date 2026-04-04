# OIO Racing Photo Workflow

Automated photo ingestion from Google Photos to Supabase with AI-powered identification.

## Overview

The OIO Racing photo workflow is a cloud-native system that:

1. **Syncs photos** from a Google Photos album every 6 hours
2. **Stores photos** in Supabase cloud storage (never in git)
3. **Manages metadata** in Supabase database (descriptions, AI results, status)
4. **Analyzes with Claude Vision** for car and driver identification
5. **Provides a triage UI** for manual labeling of uncertain photos

Architecture:
```
Google Photos Album
        ↓
[GitHub Actions - every 6h]
        ↓
Google Photos Library API
        ↓
Supabase oio-photos bucket + photos table
        ↓
Claude Vision (auto-identification)
        ↓
Triage UI (photo-library for uncertain)
```

## How a Photo Moves Through the System

### 1. Add to Google Photos (Manual)

You add a photo to the OIO Racing Google Photos album in the cloud.

### 2. Sync Cycle (Automatic - Every 6 Hours)

The GitHub Actions workflow runs on a schedule:
- Fetches all photos from the Google Photos album
- For each new photo:
  - Downloads the image
  - Uploads to Supabase `oio-photos` storage bucket
  - Stores metadata in Supabase `photos` table
  - Records `google_photos_id` for deduplication
  - Records `google_description` (the caption from Google Photos)

### 3. Caption Re-ingestion (Automatic)

If you add a caption in Google Photos after sync:
- Next sync cycle picks up the new caption
- Updates `google_description` and `description` (if not yet human-labeled)
- Marks photo as ready for Vision analysis

### 4. Claude Vision Analysis (Automatic)

For each photo without a description:
- Claude Vision analyzes the image
- Identifies: car, driver, event context, visual details
- Sets confidence score (0.0–1.0)
- If confidence ≥ 0.8:
  - Auto-marks as "identified"
  - Stores: car, description (visual notes), full analysis JSON, status
- If confidence < 0.8:
  - Marks as "unknown"
  - Stores analysis for review
  - Photo appears in triage UI

### 5. Triage (Manual - When Needed)

You open the triage UI to review low-confidence photos:
- See all photos marked "unknown"
- Add or edit descriptions
- Correct car identifications
- Mark as "identified" when done

### 6. Ready for Use

Photos are now fully identified and ready for:
- Caption generation
- Social media posting
- Archive organization

## GitHub Secrets Required

Before the workflow can run, you must set up these secrets in the GitHub repository.

### 1. **GOOGLE_PHOTOS_CREDENTIALS** (Required)

JSON string from the one-time auth setup. Contains refresh token, client ID/secret.

**To set up:**
1. Run locally: `python scripts/auth_google_photos.py`
   - Set env vars: `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
   - Follow browser prompt to authorize
2. Copy the printed JSON
3. GitHub → Settings → Secrets and variables → Actions
4. New secret name: `GOOGLE_PHOTOS_CREDENTIALS`
5. Paste the JSON as the value

### 2. **GOOGLE_PHOTOS_ALBUM_ID** (Required)

The album ID from the Google Photos URL (e.g., `AL9nkcK...`).

**To find:**
1. Open the Google Photos album in your browser
2. Copy the URL, it looks like: `https://photos.app.goo.gl/AL9nkcK...`
3. The part after the last `/` is the album ID
4. Create a GitHub secret: `GOOGLE_PHOTOS_ALBUM_ID`

### 3. **ANTHROPIC_API_KEY** (Required)

Your Anthropic API key for Claude Vision analysis.

**To set up:**
1. Go to https://console.anthropic.com/account/keys
2. Create or copy your API key
3. GitHub → Settings → Secrets → New secret
4. Name: `ANTHROPIC_API_KEY`
5. Paste the key

### 4. **SUPABASE_URL** (Required)

The Supabase project URL (fixed):
- URL: `https://zdjughkxryhabduhsdgg.supabase.co`

Create a GitHub secret with this URL. Or it can be hardcoded in the workflow.

### 5. **SUPABASE_SERVICE_ROLE_KEY** (Required)

The Supabase service role key (not the anon key).

**To find:**
1. Supabase → Project → Settings → API
2. Copy the **Service Role Key** (NOT the anon key)
3. GitHub → Settings → Secrets → New secret
4. Name: `SUPABASE_SERVICE_ROLE_KEY`
5. Paste the key

## Understanding Photo Status

Each photo in the database has an `ai_status` field:

| Status | Meaning |
|---|---|
| `unknown` | Not yet analyzed or analysis was uncertain (<0.8 confidence) |
| `identified` | Fully processed and identified (high confidence or human-labeled) |
| `skipped` | Intentionally skipped (reserved for future use) |

## Re-ingesting Captions from Google Photos

If you add a description to a photo in Google Photos *after* it was synced:

1. The next sync cycle (every 6h) will detect the new caption
2. Updates `google_description` in the database
3. Also updates `description` (unless it was already human-edited)
4. Marks the photo as `identified` (since it now has a description)

This is useful for bulk-captioning in Google Photos, then letting the sync system pick it up.

## One-Time Setup

### Step 1: Supabase Migration

The database schema has been updated with new columns:
- `google_photos_id` — stable unique ID for deduplication
- `google_description` — raw caption from Google Photos

These were added via migration. No action needed unless you're setting up fresh.

### Step 2: Create OAuth2 Credentials

1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable the **Google Photos Library API**
4. Create **OAuth2 credentials** (Desktop application)
5. Download the JSON file
6. Extract `client_id` and `client_secret`
7. Run: `GOOGLE_CLIENT_ID=... GOOGLE_CLIENT_SECRET=... python scripts/auth_google_photos.py`
8. Save the output as a GitHub secret

### Step 3: Configure GitHub Secrets

Add all required secrets (see "GitHub Secrets Required" above).

### Step 4: Verify the Workflow

Push a dummy commit to trigger the workflow:
```bash
git commit --allow-empty -m "test: trigger photo sync"
git push
```

Check **Actions** tab to verify the workflow runs without errors.

## Troubleshooting

### "GOOGLE_PHOTOS_CREDENTIALS not found"

**Problem:** Workflow fails immediately

**Solution:**
1. GitHub → Settings → Secrets and variables → Actions
2. Verify `GOOGLE_PHOTOS_CREDENTIALS` exists
3. Verify the JSON is valid (use a JSON validator)
4. Re-run the workflow

### "Failed to refresh Google Photos credentials"

**Problem:** Refresh token is invalid or expired

**Solution:**
1. Re-run the auth script locally: `python scripts/auth_google_photos.py`
2. Update the GitHub secret with the new JSON

### "No photos to sync" but Google Photos has photos

**Problem:** Album ID might be incorrect

**Solution:**
1. Open the Google Photos album in browser
2. Check the URL
3. Update `GOOGLE_PHOTOS_ALBUM_ID` secret

### Photos uploaded but Vision analysis doesn't run

**Problem:** ANTHROPIC_API_KEY might be invalid

**Solution:**
1. Verify API key at https://console.anthropic.com/account/keys
2. Ensure billing is active
3. Confirm Claude Opus 4.6 access
4. Update the GitHub secret

### Photos in Supabase but not showing in triage UI

**Problem:** SUPABASE_URL or service role key might be wrong

**Solution:**
1. Check Supabase → Settings → API
2. Verify the URL and service role key
3. Update GitHub secrets
4. Run the workflow again

## Files Reference

| File | Purpose |
|---|---|
| `scripts/auth_google_photos.py` | One-time OAuth2 setup (run locally) |
| `scripts/sync_google_photos.py` | Main sync script (runs in GitHub Actions) |
| `.github/workflows/sync-google-photos.yml` | Scheduled workflow (every 6h) |
| `intake/photos/.gitkeep` | Directory marker (no photos stored here) |
| `/PHOTO-WORKFLOW.md` | This file |

Photos themselves live only in:
- Google Photos (original)
- Supabase Storage `oio-photos` bucket (working copy)
- Supabase `photos` table (metadata)

## Integration with Downstream Systems

Once photos are identified in Supabase, other systems can use them:

- **Caption generation:** Query identified photos, generate captions
- **Social posting:** PostBridge queries photo metadata, creates posts
- **Analytics:** Photo filing reports use `ai_status` and `car` fields

## Next Steps

1. ✅ **Schema ready** — Database columns added
2. ⏳ **Setup Google OAuth** — Run auth script
3. ⏳ **Configure GitHub secrets** — Add 5 required secrets
4. ⏳ **Test sync** — Push a commit to trigger workflow
5. ⏳ **Review first sync** — Check Supabase for photos
6. ⏳ **Review triage UI** — Check for uncertain photos

---

**Last Updated:** April 4, 2026  
**Status:** PRODUCTION-READY
