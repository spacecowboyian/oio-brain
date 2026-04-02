# OIO Racing Photo Workflow

Automated photo filing and social media integration for OIO Racing.

## Overview

The OIO photo workflow automates the process of:
1. **Uploading photos** to `intake/photos/`
2. **Identifying photos** using AI (car, driver, event)
3. **Filing photos** automatically to `photos/{Driver}/{Car}/`
4. **Generating captions** using Claude
5. **Posting to social media** via PostBridge

---

## Quick Start: Upload a Photo

### For Humans

1. **Add photos to the intake folder:**
   - Drag photos into `intake/photos/` folder
   - Commit and push to GitHub
   - The workflow will process them automatically

2. **Photos will be:**
   - Analyzed by AI
   - Filed into `photos/{Driver}/{Car}/`
   - Notified in Slack if uncertain
   - Ready for caption generation

### For GitHub Actions

The workflow runs automatically when photos are pushed to `intake/photos/`:
- **Trigger:** `process-picdump-photos.yml` (detects new files)
- **Processor:** `file-picdump-photos.yml` (runs AI filing)
- **Script:** `scripts/ai_photo_filing_agent.py` (Claude Vision analysis)

---

## Setup: API Configuration

### Prerequisites

You need two GitHub secrets configured:

#### 1. **ANTHROPIC_API_KEY** (Required)

This enables Claude Vision API for photo analysis.

**Steps to configure:**

1. Go to: **Repository → Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `ANTHROPIC_API_KEY`
4. Value: Your Anthropic API key
   - Get it from: https://console.anthropic.com/account/keys
   - Must have Claude 3.5 Vision API enabled
5. Click **Add secret**

**What it does:**
- Analyzes photos to identify car, driver, event
- Generates filing path: `photos/{Driver}/{Car}/`
- Determines confidence score (80%+ auto-files)
- Triggers Slack notifications for uncertain photos

#### 2. **SLACK_BOT_TOKEN** (Optional but Recommended)

Enables Slack notifications for uncertain photos.

**Steps to configure:**

1. Create Slack Bot in workspace
   - Go to your Slack workspace → Apps → App Directory
   - Search for "Bots" → Create New App
   - Name: "OIO Photo Bot"
   - Choose workspace
2. Get the **Bot Token Xoxb-...**
3. GitHub → Settings → Secrets → New repository secret
4. Name: `SLACK_BOT_TOKEN`
5. Value: Your bot token

#### 3. **SLACK_CHANNEL_ID** (Optional but Recommended)

Channel where bot posts uncertain photo notifications.

1. In Slack, right-click channel → Copy Link
2. Extract the channel ID from the URL: `slack.com/archives/C12345...`
3. GitHub → Settings → Secrets → New repository secret
4. Name: `SLACK_CHANNEL_ID`
5. Value: C12345... (just the channel ID)

---

## How It Works

### 1. Photo Upload

```
You push photos to intake/photos/
         ↓
GitHub Actions detects new files
         ↓
```

### 2. Processing

```
process-picdump-photos.yml
  ├─ Detects image files
  ├─ Counts how many are new
  └─ Triggers: file-picdump-photos.yml

file-picdump-photos.yml
  ├─ Installs Python dependencies
  ├─ Loads OIO context (cars, drivers, events)
  ├─ Calls: ai_photo_filing_agent.py
  └─ Commits results back to repo
```

### 3. AI Analysis (ai_photo_filing_agent.py)

For each photo, Claude Vision API:

1. **Analyzes the image** for:
   - Which car is shown
   - Which driver is shown
   - What event/context (autocross, rallycross, shop, build, etc.)
   - Visual details (color, condition, environment)

2. **Generates filing path** from results:
   - Format: `photos/{Driver}/{Car}/`
   - Example: `photos/ian-jennings/miata-nb/`

3. **Scores confidence** (0-100%):
   - ✅ **≥80%:** Auto-files immediately
   - ⚠️ **<80%:** Notifies you in Slack for review
   - ❌ **Failed:** Returns error + context for debugging

4. **Posts notifications** (if SLACK_BOT_TOKEN set):
   - Uncertain photo: "Manual review needed for photo_123.jpg"
   - Error: "Could not analyze photo_456.jpg (reason)"

### 4. Results

Filed photos are committed to repo:
- Auto-filed to: `photos/{Driver}/{Car}/photo_name.jpg`
- README updated: `photos/README.md`
- Commit message: `chore: file intake/photos photos with AI`

---

## Examples

### Example 1: High-Confidence Photo ✅

```
Input:  intake/photos/miata-at-autocross.jpg
↓
Analysis: 
  - Car: Miata (NB, silver)
  - Driver: Ian Jennings
  - Event: Autocross
  - Confidence: 95%
↓
Result: AUTO-FILED
  → photos/ian-jennings/miata-nb/miata-at-autocross.jpg
  → Ready for caption generation
```

### Example 2: Uncertain Photo ⚠️

```
Input:  intake/photos/blurry-car.jpg
↓
Analysis: 
  - Car: Miata? (unclear angle)
  - Driver: Unknown (not visible)
  - Event: Driving event (generic)
  - Confidence: 62%
↓
Result: REQUIRES REVIEW
  → Slack notification: "Please review blurry-car.jpg"
  → Stays in: intake/photos/
  → Manual filing needed
```

### Example 3: No Photos to Process

```
Input:  intake/photos/ (empty)
↓
Result: SKIPPED
  → Workflow completes
  → No commits made
  → Next push with photos will trigger workflow
```

---

## Understanding the AI Analysis

### Confidence Thresholds

The system uses an **80% confidence threshold** for auto-filing:

| Confidence | Action | Why |
|---|---|---|
| ≥90% | Auto-file immediately | Very certain |
| 80-89% | Auto-file immediately | Reasonably certain |
| 60-79% | Slack notification | Too uncertain for auto |
| <60% | Error + manual review | Insufficient data |

### Adjustment Process

If the AI is consistently uncertain about specific scenarios:

1. **Review Slack notifications** to see patterns
2. **Check confidence scores** in the filing results
3. **Adjust threshold** in `ai_photo_filing_agent.py`:
   ```python
   CONFIDENCE_THRESHOLD = 0.80  # Change this value
   ```
4. **Re-run workflow** with updated threshold

---

## Troubleshooting

### "ANTHROPIC_API_KEY secret is not configured"

**Problem:** Workflow fails immediately

**Solution:**
1. Go to GitHub → Settings → Secrets and variables → Actions
2. Verify `ANTHROPIC_API_KEY` exists
3. Verify it has a value (not empty)
4. Re-push a photo to trigger workflow again

### "Could not resolve authentication method"

**Problem:** API key is set but authentication fails

**Causes:**
- API key is invalid or expired
- API key doesn't have Claude Vision access
- Anthropic account needs billing setup

**Solution:**
1. Verify API key at https://console.anthropic.com/account/keys
2. Check account has active billing
3. Confirm Claude 3.5 Sonnet (Vision) is available
4. Update the secret with correct key

### "No photos found in album" (old error)

**This should no longer appear** since we use direct file uploads now, not Google Photos.

If you see this:
- Check that `intake/photos/` directory exists
- Verify you pushed photos to the correct folder
- Check GitHub Actions logs for actual error

### Workflow runs but photos don't get filed

**Possible causes:**

1. **No ANTHROPIC_API_KEY:** Check GitHub Secrets
2. **Insufficient permissions:** Check file permissions in `photos/` directory
3. **Photo analysis failed:** Check Slack for error notifications
4. **Git push failed:** Check GitHub Actions logs for commit errors

**Debug:**
1. Check GitHub Actions → Workflows → file-picdump-photos
2. Look for error messages in the run logs
3. Post error message in #photo-workflow Slack channel

---

## Integration with Caption Generation

Once photos are filed, they're ready for caption generation:

1. **Photo filed to:** `photos/ian-jennings/miata-nb/photo.jpg`
2. **Caption generator reads:** Filing path + oio-brain context
3. **Generates caption:** Using CAPTION-TEMPLATES.md as reference
4. **Validates caption:** Using validate_captions.py
5. **Posts to social:** Via PostBridge

See `CAPTION-GENERATION-GUIDE.md` for details.

---

## Files Reference

| File | Purpose |
|---|---|
| `scripts/ai_photo_filing_agent.py` | Main filing logic (Claude Vision analysis) |
| `.github/workflows/process-picdump-photos.yml` | Detects new photos |
| `.github/workflows/file-picdump-photos.yml` | Runs filing workflow |
| `intake/photos/` | Where you upload photos |
| `photos/` | Where photos are filed by driver |
| `PHOTO-FILING-TEST-PLAN.md` | Testing guide (coming soon) |

---

## Next Steps

### To enable the photo workflow:

1. ✅ Workflow infrastructure: **READY**
2. ✅ AI filing agent: **READY**
3. ⏳ Configure ANTHROPIC_API_KEY: **ACTION NEEDED**
4. ⏳ Configure SLACK_BOT_TOKEN: **OPTIONAL**
5. ⏳ Test with sample photos: **PENDING API KEY**
6. ⏳ Run caption pipeline: **PENDING PHOTO TEST**

### Quick checklist:

- [ ] API key configured in GitHub Secrets
- [ ] Slack bot configured (optional)
- [ ] Test photo uploaded to `intake/photos/`
- [ ] Workflow runs without errors
- [ ] Photos filed correctly
- [ ] Captions generate successfully
- [ ] Social posts appear on schedule

---

## Questions?

- **Technical:** Check [`.github/copilot-instructions.md`](.github/copilot-instructions.md)
- **OIO Context:** See [`core/decisions-log.md`](core/decisions-log.md)
- **Social Strategy:** See [`brand/voice.md`](brand/voice.md)

---

**Last Updated:** April 2, 2026  
**Status:** PRODUCTION-READY (awaiting API key configuration)
