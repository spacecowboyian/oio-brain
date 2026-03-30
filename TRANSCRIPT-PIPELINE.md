# OIO Racing Transcript Generation Pipeline

## Overview

Automated workflow that generates YouTube video transcripts and clean readable scripts, committing them to the oio-brain repository.

## Current Status: Complete ✅

### ✅ What Exists

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

#### 2. **Clean Script Generator** (`scripts/clean_transcripts.py`)
- **Method**: Claude AI (Anthropic API)
- **Features**:
  - Removes filler words (um, uh, like, you know)
  - Fixes incomplete sentences and thoughts
  - Corrects speech-to-text errors
  - Maintains authentic voice and style
  - Generates readable script versions
  - Processes all transcripts missing clean versions

#### 3. **Output Structure**
Each transcript saved to: `OIO Brain/02 - Content/Video Scripts/YYYY-MM-DD_video-title/`
- `transcript.md` — Raw transcript with timestamps, YAML frontmatter
- `clean-script.md` — Clean, readable version without filler words
- `metadata.json` — Structured metadata (video_id, title, date, URL, segment count)

#### 4. **Catalog Linker** (`scripts/update_catalog_transcripts.py`)
- Updates `OIO-Video-Catalog.md` with transcript links
- Adds "Transcript" column with links to available transcripts
- Format: `[📄](OIO Brain/02 - Content/Video Scripts/YYYY-MM-DD_video-title/transcript.md)`

#### 5. **GitHub Actions Workflow** (`.github/workflows/fetch-youtube-transcripts.yml`)
- **Automatic**: Runs every 2 hours via cron schedule
- **Triggers**:
  - Scheduled: Every 2 hours
  - Manual: workflow_dispatch with options
  - Automatic: On push to `OIO-Video-Catalog.md`
- **Steps**:
  1. Fetch transcripts (raw)
  2. Generate clean scripts
  3. Update catalog links
  4. Commit all changes
- **Commits**: Direct to main with `[skip ci]`
- **Options**:
  - `batch_size` (default: 25)
  - `fetch_all` (re-fetch all transcripts)

## Pipeline Flow

1. **Trigger**: Cron (every 2 hours) OR manual dispatch OR catalog update
2. **Fetch**: `fetch_transcripts.py` fetches up to 25 new transcripts → `OIO Brain/02 - Content/Video Scripts/`
3. **Clean**: `clean_transcripts.py` generates clean readable scripts
4. **Link**: `update_catalog_transcripts.py` adds links to catalog
5. **Commit**: Commits transcripts, clean scripts, and updated catalog
6. **Repeat**: Next run picks up remaining videos

## Setup

### Prerequisites

1. **Python dependencies** (install from `requirements.txt`):
   ```bash
   pip install -r requirements.txt
   ```

2. **Anthropic API Key** (required for clean script generation):
   - Get your API key from: https://console.anthropic.com/
   - **For local use**: Set environment variable:
     ```bash
     export ANTHROPIC_API_KEY='your-api-key-here'
     ```
   - **For GitHub Actions**: Add as repository secret named `ANTHROPIC_API_KEY`
     1. Go to repository Settings → Secrets and variables → Actions
     2. Click "New repository secret"
     3. Name: `ANTHROPIC_API_KEY`
     4. Value: your API key
     5. Click "Add secret"

### Migration Status

✅ All existing transcripts (26) have been migrated from `transcripts/` to `OIO Brain/02 - Content/Video Scripts/`

## Usage

### Automatic Operation
- Pipeline runs every 2 hours automatically
- Processes 25 videos per run (fetch + clean)
- No intervention needed once API key is configured

### Manual Operation

**Fetch specific batch size**:
```bash
python scripts/fetch_transcripts.py --batch-size 50
```

**Re-fetch all transcripts**:
```bash
python scripts/fetch_transcripts.py --all
```

**Generate clean scripts** (requires ANTHROPIC_API_KEY):
```bash
# Clean all transcripts missing clean versions
python scripts/clean_transcripts.py

# Re-clean all transcripts
python scripts/clean_transcripts.py --all

# Clean specific video
python scripts/clean_transcripts.py --video-id VIDEO_ID
```

**Update catalog links**:
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
- `youtube-transcript-api>=1.0.0` — Primary transcript fetching
- `yt-dlp>=2026.02.21` — Fallback for videos without API transcripts
- `requests>=2.31.0` — HTTP requests
- `anthropic>=0.39.0` — Claude AI for clean script generation

## File Structure

```
OIO Brain/
└── 02 - Content/
    └── Video Scripts/
        ├── README.md
        ├── 2024-03-01_can-we-race-a-honda-fit-jazz/
        │   ├── transcript.md          # Raw transcript with timestamps
        │   ├── clean-script.md         # Clean readable version
        │   └── metadata.json           # Video metadata
        ├── 2024-03-21_honda-fit-jazz-valve-adjustment/
        │   ├── transcript.md
        │   ├── clean-script.md
        │   └── metadata.json
        └── ...
```

## Next Steps

To complete the clean script generation for all existing transcripts:

1. **Set ANTHROPIC_API_KEY** (see Setup section above)
2. **Run clean script generator**:
   ```bash
   cd /path/to/oio-brain
   python scripts/clean_transcripts.py
   ```
3. **Commit the results**:
   ```bash
   git add "OIO Brain/02 - Content/Video Scripts/"
   git commit -m "chore: generate clean scripts for existing transcripts"
   git push
   ```

## References

- Video catalog: `OIO-Video-Catalog.md`
- Video Scripts folder: `OIO Brain/02 - Content/Video Scripts/`
- Unavailable log: `transcripts/UNAVAILABLE.md` (legacy location)
- Fetch script: `scripts/fetch_transcripts.py`
- Clean script generator: `scripts/clean_transcripts.py`
- Catalog linker: `scripts/update_catalog_transcripts.py`
- Workflow: `.github/workflows/fetch-youtube-transcripts.yml`
