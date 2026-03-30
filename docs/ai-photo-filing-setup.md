---
title: AI Photo Filing Agent Setup
type: guide
status: active
owner: Social Media Engineer
updated: 2026-03-29
tags: [ai, photos, automation, claude, github-actions]
---

# AI Photo Filing Agent Setup

The AI Photo Filing Agent uses Claude vision API to automatically analyze and file racing photos from the `picdump/` folder into the organized photo library.

## How It Works

```
picdump/ (new photos)
    ↓
[Claude Vision API] → Analyze photo
    ↓
Extract: car model, driver, event, context
    ↓
IF confidence ≥ 70%:
    → File to photos/{Driver}/{Car}/
    → Update photo-log.md
    → Update PHOTO-INDEX.md
    → Update car Overview.md
    → Commit changes
ELSE:
    → Move to photos/unidentified/
    → Post to Slack for manual review
```

## Requirements

### GitHub Secrets

The workflow requires two secrets to be configured in GitHub repository settings:

1. **`ANTHROPIC_API_KEY`** (Required)
   - Your Anthropic API key for Claude
   - Get one at: https://console.anthropic.com/settings/keys
   - Needs access to `claude-opus-4-20250514` model

2. **`SLACK_WEBHOOK_URL`** (Optional)
   - Slack incoming webhook URL for notifications
   - Used to alert team when photos need manual review (< 70% confidence)
   - If not configured, flagged photos are still moved to `photos/unidentified/` but no Slack alert is sent

### Setting Up Secrets

```bash
# Via GitHub CLI
gh secret set ANTHROPIC_API_KEY

# Or via GitHub web UI:
# Repository → Settings → Secrets and variables → Actions → New repository secret
```

## Usage

### Automatic Trigger

The workflow automatically runs when photos are pushed to the `picdump/` folder:

```bash
# Add photos to picdump
cp ~/Downloads/race-photo.jpg picdump/

# Commit and push
git add picdump/
git commit -m "Add new race photos"
git push

# GitHub Action runs automatically:
# 1. Detects new photos
# 2. Analyzes with Claude vision
# 3. Files photos to appropriate locations
# 4. Updates documentation
# 5. Commits and pushes changes
```

### Manual Trigger

You can also manually trigger the workflow for all existing photos in `picdump/`:

```bash
# Via GitHub CLI
gh workflow run process-picdump-photos.yml

# Or via GitHub web UI:
# Actions → Process Picdump Photos → Run workflow
```

## What Gets Updated

When a photo is successfully filed, the agent automatically updates:

1. **`photos/{Driver}/{Car}/`** - Photo filed to correct location
2. **`photos/{Driver}/{Car}/photo-log.md`** - Log entry with metadata
3. **`PHOTO-INDEX.md`** - Master index entry
4. **`OIO Brain/03 - Cars/{Driver}/{Car}/Overview.md`** - Car documentation (future)
5. **`{photo}.analysis.json`** - AI analysis metadata stored alongside photo

## Low Confidence Handling

Photos with confidence < 70% are:

1. Moved to `photos/unidentified/`
2. Analysis metadata saved as `{filename}.analysis.json`
3. Slack notification sent (if webhook configured) with:
   - Photo filename
   - Best guess (car model, driver)
   - Confidence score
   - Reasoning

Manual review process:
- Check Slack notification
- View photo in `photos/unidentified/`
- Review `.analysis.json` file
- Manually file to correct location or provide more context

## Confidence Threshold

Current threshold: **70%**

To adjust, edit `scripts/ai_photo_filing_agent.py`:

```python
CONFIDENCE_THRESHOLD = 0.7  # Change this value (0.0 - 1.0)
```

Higher threshold = fewer automatic filings, more manual reviews
Lower threshold = more automatic filings, potential misidentifications

## Fleet Context

The agent uses these files to identify cars:

- `PHOTO-INDEX.md` - Visual ID markers for each car
- `OIO Brain/03 - Cars/*/Overview.md` - Car specifications and details

Keep these updated with distinctive visual features to improve accuracy.

## Debugging

### View Results

After workflow runs, check:

```bash
cat .photo-filing-results.json
```

This contains the full analysis for each photo processed.

### Test Locally

```bash
# Set environment variable
export ANTHROPIC_API_KEY="your-key-here"

# Optional Slack webhook
export SLACK_WEBHOOK_URL="your-webhook-url"

# Run the agent
python scripts/ai_photo_filing_agent.py
```

### Common Issues

**Issue:** `Error: ANTHROPIC_API_KEY not set`
- **Solution:** Configure the GitHub secret (see Requirements)

**Issue:** Photos not detected
- **Solution:** Ensure photos are in `picdump/` folder (not subdirectories)
- Supported formats: `.png`, `.jpg`, `.jpeg`, `.heic`, `.webp`

**Issue:** All photos flagged as low confidence
- **Solution:** Check that fleet context files are up to date
- Add more visual ID markers to `PHOTO-INDEX.md`
- Check Claude API response in workflow logs

## Cost Estimation

Claude Opus 4 vision API pricing (as of 2025):
- ~$0.015 per image (varies by image size and prompt length)
- Example: 100 photos/month = ~$1.50/month

## Success Criteria

- ✅ Filing accuracy > 80%
- ✅ Low-confidence photos flagged appropriately
- ✅ End-to-end pipeline: Google Photos → picdump → filed photos
- ✅ Automated documentation updates
- ✅ Audit trail of all decisions

## Related

- Parent Project: [Social Media Tooling](/OUT/issues/OUT-14)
- Workflow: `.github/workflows/process-picdump-photos.yml`
- Script: `scripts/ai_photo_filing_agent.py`
- Google Photos sync: `.github/workflows/sync-google-photos.yml` (coming soon)
