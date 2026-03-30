# OIO Racing Transcript Generation Pipeline

## Overview

Automated workflow that generates and commits YouTube video transcripts to the oio-brain repository.

## Current Status: 90% Complete ✅

### ✅ What Already Exists

#### 1. **Transcript Fetching Script** (`scripts/fetch_transcripts.py`)
- **Primary method**: `youtube-transcript-api` (fast, no download)
- **Fallback**: `yt-dlp` auto-subtitle download + VTT parsing
- **Features**:
  - Parses `OIO-Video-Catalog.md` for video list
  - Excludes YouTube Shorts (≤60 seconds)
  - Batches processing (default: 25 videos per run)
  - Rate limiting (1 request/second)
  - Tracks processed videos via metadata.json
  - Logs unavailable transcripts to `UNAVAILABLE.md`

#### 2. **Output Structure**
Each transcript saved to: `transcripts/YYYY-MM-DD_video-title/`
- `transcript.md` — Full transcript with timestamps, YAML frontmatter
- `metadata.json` — Structured metadata (video_id, title, date, URL, segment count)

#### 3. **GitHub Actions Workflow** (`.github/workflows/fetch-youtube-transcripts.yml`)
- **Automatic**: Runs every 2 hours via cron schedule
- **Triggers**:
  - Scheduled: Every 2 hours
  - Manual: workflow_dispatch with options
  - Automatic: On push to `OIO-Video-Catalog.md`
- **Commits**: Direct to main with `[skip ci]`
- **Options**:
  - `batch_size` (default: 25)
  - `fetch_all` (re-fetch all transcripts)

### ❌ Missing Feature: Catalog Linking

**Requirement**: Link transcripts back in `OIO-Video-Catalog.md`

The catalog currently has tables with columns:
```
| Date | Title | Duration | Views | Likes |
```

**Solution**: Add a "Transcript" column with links to generated transcripts.

## Implementation Plan

### Script: `scripts/update_catalog_transcripts.py`

**Purpose**: Update `OIO-Video-Catalog.md` with transcript links after generation.

**Algorithm**:
1. Parse `OIO-Video-Catalog.md` to find all video tables
2. Scan `transcripts/` folder for available transcripts
3. Match videos to transcripts by video_id
4. Add/update "Transcript" column in tables
5. Insert links like: `[📄](transcripts/YYYY-MM-DD_video-title/transcript.md)`
6. Preserve existing table structure and data

**Workflow Integration**:
Add step after "Fetch transcripts" in the workflow:
```yaml
- name: Update catalog with transcript links
  run: python scripts/update_catalog_transcripts.py

- name: Commit catalog updates
  run: |
    git add OIO-Video-Catalog.md
    if ! git diff --cached --quiet; then
      git commit -m "chore: update catalog with transcript links [skip ci]"
      git push
    fi
```

## Pipeline Flow (Complete)

1. **Trigger**: Cron (every 2 hours) OR manual dispatch OR catalog update
2. **Fetch**: `fetch_transcripts.py` fetches up to 25 new transcripts
3. **Commit**: Commits transcript files to `transcripts/`
4. **Link**: `update_catalog_transcripts.py` adds links to catalog
5. **Commit**: Commits updated catalog
6. **Repeat**: Next run picks up remaining videos

## Usage

### Automatic Operation
- Pipeline runs every 2 hours automatically
- Processes 25 videos per run
- No intervention needed

### Manual Operation

**Fetch specific batch size**:
```bash
python scripts/fetch_transcripts.py --batch-size 50
```

**Re-fetch all transcripts**:
```bash
python scripts/fetch_transcripts.py --all
```

**Update catalog links** (after fetching):
```bash
python scripts/update_catalog_transcripts.py
```

**Manual workflow trigger**:
1. Go to Actions → "Fetch YouTube Transcripts"
2. Click "Run workflow"
3. Set `batch_size` (default: 25)
4. Set `fetch_all` (default: false)

## Dependencies

From `requirements.txt`:
- `youtube-transcript-api` — Primary transcript fetching
- `yt-dlp` — Fallback for videos without API transcripts

## References

- Video catalog: `OIO-Video-Catalog.md`
- Transcripts folder: `transcripts/`
- Unavailable log: `transcripts/UNAVAILABLE.md`
- Fetch script: `scripts/fetch_transcripts.py`
- Catalog update script: `scripts/update_catalog_transcripts.py` (to be created)
- Workflow: `.github/workflows/fetch-youtube-transcripts.yml`
