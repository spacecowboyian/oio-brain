# OIO Racing - Social Media System Integration Testing Guide

**Version:** 1.0
**Last Updated:** 2026-03-30
**Status:** Ready for Testing

---

## Overview

This document outlines the comprehensive integration testing procedure for the OIO Racing Social Media System. Follow these tests sequentially to validate the complete end-to-end pipeline.

## Prerequisites

### 1. Environment Setup

Ensure all required services are configured:

- [ ] GitHub Actions enabled in repository
- [ ] Google Photos album accessible
- [ ] Slack workspace with bot installed
- [ ] PostBridge account with connected Instagram/Facebook
- [ ] Paperclip instance running with AI Copywriter agent

### 2. Dependencies Installed

```bash
# Install Python dependencies
pip install -r requirements.txt
pip install slack-bolt flask beautifulsoup4 pillow

# Verify installations
python3 -c "import slack_bolt; import flask; import requests; print('✓ All dependencies installed')"
```

### 3. Environment Variables Set

```bash
# Caption Service
export PAPERCLIP_API_KEY="your-paperclip-api-key"
export PAPERCLIP_API_URL="http://127.0.0.1:3100"
export PAPERCLIP_COMPANY_ID="your-company-id"

# Slackbot
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_APP_TOKEN="xapp-your-app-token"

# PostBridge
export POSTBRIDGE_API_KEY="your-postbridge-api-key"

# Optional overrides
export CAPTION_SERVICE_URL="http://localhost:5000"
```

Verify:
```bash
env | grep -E '(SLACK|POSTBRIDGE|PAPERCLIP)' && echo "✓ Environment variables set"
```

---

## Test Suite

### Phase 1: Component Testing

Test each component independently before integration testing.

#### Test 1.1: PostBridge Client Library

**Objective:** Verify PostBridge API connectivity and authentication.

```bash
cd /Users/ian/repos/oio-brain
python3 << 'EOF'
from scripts.postbridge_client import PostBridgeClient

# Initialize client
client = PostBridgeClient()
print("✓ PostBridge client initialized")

# List connected accounts
try:
    accounts = client.list_accounts()
    print(f"✓ Connected accounts: {len(accounts)}")
    for account in accounts:
        print(f"  - {account.get('platform')}: {account.get('name')}")
except Exception as e:
    print(f"✗ Failed to list accounts: {e}")
    exit(1)

# List recent posts
try:
    posts = client.list_posts(limit=5)
    print(f"✓ Retrieved {len(posts)} recent posts")
except Exception as e:
    print(f"✗ Failed to list posts: {e}")
    exit(1)

print("\n✓ PostBridge client test PASSED")
EOF
```

**Expected Result:**
- Client initializes without errors
- Lists connected Instagram/Facebook accounts
- Retrieves recent posts

**Failure Actions:**
- Verify `POSTBRIDGE_API_KEY` is correct
- Check PostBridge account has connected social accounts
- Check API base URL is accessible

---

#### Test 1.2: Caption Generation Service

**Objective:** Verify caption service can generate AI captions.

**Step 1:** Start the caption service
```bash
cd /Users/ian/repos/oio-brain
python3 scripts/caption_generation_service.py &
CAPTION_PID=$!
echo "Caption service started (PID: $CAPTION_PID)"
sleep 5
```

**Step 2:** Test health endpoint
```bash
curl -s http://localhost:5000/health | jq '.'
```

Expected: `{"status": "ok"}`

**Step 3:** Test caption generation
```bash
curl -X POST http://localhost:5000/generate-caption \
  -H "Content-Type: application/json" \
  -d '{
    "media_urls": ["test_photo.jpg"],
    "context": "KCRX Event 1 test",
    "caption_count": 3
  }' | jq '.'
```

**Expected Result:**
- Service returns 200 OK
- Response contains 3 caption variations
- Each caption has text, hashtags, char_count
- `brand_voice_applied` is true

**Step 4:** Cleanup
```bash
kill $CAPTION_PID
```

**Failure Actions:**
- Check Paperclip API is accessible
- Verify AI Copywriter agent is running
- Check OIO Brain brand voice files exist
- Review Flask logs for errors

---

#### Test 1.3: Google Photos Sync

**Objective:** Verify Google Photos sync can download photos.

```bash
cd /Users/ian/repos/oio-brain

# Run sync script (dry run mode if available, or with test album)
python3 scripts/sync_google_photos.py \
  --album-url "https://photos.app.goo.gl/W757cit6HfvKmCQh6" \
  --dry-run

# Check for downloaded photos (if not dry run)
ls -lh picdump/ | head -10
```

**Expected Result:**
- Script connects to Google Photos album
- Lists available photos
- Downloads new photos to `picdump/`
- No errors or authentication issues

**Failure Actions:**
- Verify album URL is accessible
- Check network connectivity
- Verify album is still public
- Check for rate limiting

---

#### Test 1.4: Picdump Processing Workflow

**Objective:** Verify picdump workflow detects and processes new photos.

**Step 1:** Add test photo to picdump
```bash
# Copy a test photo to picdump
cp photos/Ian/1985\ MR2/mr2_test.jpg picdump/test_photo_$(date +%s).jpg
```

**Step 2:** Commit and push
```bash
git add picdump/
git commit -m "test: add test photo to trigger picdump workflow"
git push
```

**Step 3:** Monitor GitHub Actions
```bash
# List recent workflow runs
gh run list --workflow=process-picdump-photos.yml --limit=1

# Watch the latest run
gh run watch
```

**Expected Result:**
- Workflow detects new image
- Creates GitHub issue assigned to @copilot
- Issue contains photo list and processing instructions

**Failure Actions:**
- Check workflow file syntax
- Verify workflow is enabled in repository settings
- Check GitHub Actions logs for errors

---

#### Test 1.5: Slackbot Commands

**Objective:** Verify Slackbot connects and responds to commands.

**Step 1:** Start caption service (required for /caption command)
```bash
python3 scripts/caption_generation_service.py &
CAPTION_PID=$!
```

**Step 2:** Start Slackbot
```bash
python3 scripts/slackbot_social_media.py &
SLACKBOT_PID=$!
echo "Slackbot started (PID: $SLACKBOT_PID)"
sleep 5
```

Look for: `⚡️ Bolt app is running!`

**Step 3:** Test commands in Slack

Test each command manually in your Slack workspace:

1. `/photos list` - Should list photos from picdump
2. `/photos list race` - Should filter by keyword
3. `/caption <photo-name>` - Should generate captions (takes 30-120s)
4. `/posts list` - Should list PostBridge posts
5. `/post <photo-name> "Test caption"` - Should create draft

**Expected Results:**
- Each command responds within reasonable time
- `/photos` lists actual photos from picdump
- `/caption` returns 3 caption variations
- `/posts` lists PostBridge posts
- `/post` creates draft successfully

**Step 4:** Cleanup
```bash
kill $SLACKBOT_PID $CAPTION_PID
```

**Failure Actions:**
- Check Socket Mode is enabled in Slack app
- Verify bot token has correct scopes
- Check slash commands are registered
- Review Slackbot logs for errors

---

### Phase 2: Integration Testing

Test complete workflows end-to-end.

#### Test 2.1: Google Photos → Picdump Pipeline

**Objective:** Verify complete photo sync and filing workflow.

**Step 1:** Trigger Google Photos sync
```bash
# Manually trigger workflow via GitHub CLI
gh workflow run sync-google-photos.yml

# Monitor the run
gh run watch
```

**Step 2:** Verify photos synced to picdump
```bash
# Check for new photos
git pull
ls -lt picdump/ | head -5
```

**Step 3:** Wait for picdump processing
- Check GitHub issues for new @copilot assignments
- Monitor issue for photo identification and filing

**Step 4:** Verify photos filed
```bash
# Check that photos were moved from picdump to photos/
git pull
find photos/ -name "*.jpg" -mtime -1 | head -10
```

**Expected Result:**
- Photos sync from Google Photos to picdump
- Picdump workflow triggers automatically
- Photos are identified and filed to correct driver/car directories
- Photo logs and indexes are updated
- Original picdump files are removed

**Success Criteria:**
- Photo-to-filing time < 10 minutes
- All photos correctly identified (or flagged as unidentified)
- Metadata complete in photo logs

---

#### Test 2.2: Mobile Posting Workflow

**Objective:** Complete photo-to-post workflow from mobile (Slack).

**Prerequisites:**
- Caption service running
- Slackbot running
- Photos available in picdump/

**Workflow Steps:**

1. **Browse photos** (in Slack mobile app)
   ```
   /photos list
   ```

   Expected: List of recent photos with sizes and dates

2. **Generate caption**
   ```
   /caption photo_race_001.jpg context: KCRX E1 test run
   ```

   Expected: 3 caption variations within 2 minutes

3. **Create post**
   ```
   /post photo_race_001.jpg "Selected caption text here #ChurchOfCombustion"
   ```

   Expected: Draft created in PostBridge

4. **Verify in PostBridge**
   - Log in to PostBridge web interface
   - Check drafts section
   - Verify caption matches

5. **Complete manual steps**
   - Upload photo to PostBridge media library
   - Attach media to draft
   - Publish or schedule

**Success Criteria:**
- Complete workflow takes < 5 minutes
- Captions match OIO brand voice
- Posts created successfully in PostBridge
- No errors or timeouts

---

#### Test 2.3: End-to-End Pipeline

**Objective:** Test complete pipeline from camera to publication.

**Full Workflow:**

1. **Capture photo** - Take photo at event (or use test photo)
2. **Upload to Google Photos** - Add to OIO Racing album
3. **Wait for sync** - GitHub Action runs (up to 5 hours)
4. **Verify sync** - Photo appears in picdump/
5. **Wait for filing** - Picdump workflow identifies and files
6. **Browse in Slack** - `/photos list` shows filed photo
7. **Generate caption** - `/caption <photo>` with event context
8. **Create post** - `/post <photo> "<caption>"`
9. **Verify draft** - Check PostBridge web interface
10. **Publish** - Upload media and publish from PostBridge

**Timing Measurements:**

Record actual times for:
- Photo to picdump: ______ (target: < 5 hours)
- Picdump to filed: ______ (target: < 10 minutes)
- Filed to captioned: ______ (target: < 2 minutes)
- Captioned to draft: ______ (target: < 1 minute)
- Draft to published: ______ (manual, target: < 2 minutes)

**Total time:** ______ (target: < 5 hours 15 minutes)

---

### Phase 3: Error Handling and Edge Cases

#### Test 3.1: Unidentified Photos

Add a photo that cannot be identified to picdump.

**Expected:**
- Picdump workflow flags as unidentified
- Photo moved to `photos/unidentified/`
- Entry added to `01-active/open-loops.md`

#### Test 3.2: Caption Service Failure

Stop the caption service and try `/caption` command.

**Expected:**
- Slackbot returns timeout error after 2 minutes
- Clear error message to user
- No system crash

#### Test 3.3: PostBridge API Error

Use invalid API key or disconnect internet.

**Expected:**
- Clear error message in Slack
- Retry logic attempts 3 times
- User notified of failure

#### Test 3.4: Rate Limiting

Make rapid requests to trigger rate limits.

**Expected:**
- System respects rate limits
- Appropriate wait times
- Clear error messages

#### Test 3.5: Concurrent Operations

Have multiple users run `/caption` simultaneously.

**Expected:**
- All requests handled
- No race conditions
- Appropriate queueing

---

### Phase 4: Performance Testing

#### Test 4.1: Caption Generation Speed

Generate captions for 10 different photos, measure time.

**Target:** < 2 minutes per photo (average)

#### Test 4.2: Photo Sync Volume

Add 20 photos to Google Photos album at once.

**Expected:**
- All photos sync successfully
- No memory or timeout issues
- Picdump processes all photos

#### Test 4.3: Slackbot Responsiveness

Test command response times under various loads.

**Target:**
- `/photos list`: < 2 seconds
- `/caption`: < 120 seconds
- `/post`: < 5 seconds
- `/posts list`: < 3 seconds

---

## Test Results Template

```markdown
# Social Media System Integration Test Results

**Date:** 2026-03-30
**Tester:** [Your Name]
**Environment:** [Production/Staging/Local]

## Phase 1: Component Testing

- [ ] Test 1.1: PostBridge Client - PASS/FAIL
  - Notes: _____
- [ ] Test 1.2: Caption Generation - PASS/FAIL
  - Notes: _____
- [ ] Test 1.3: Google Photos Sync - PASS/FAIL
  - Notes: _____
- [ ] Test 1.4: Picdump Processing - PASS/FAIL
  - Notes: _____
- [ ] Test 1.5: Slackbot Commands - PASS/FAIL
  - Notes: _____

## Phase 2: Integration Testing

- [ ] Test 2.1: Google Photos → Picdump - PASS/FAIL
  - Time: _____ (target: < 5 hours 10 min)
  - Notes: _____
- [ ] Test 2.2: Mobile Posting Workflow - PASS/FAIL
  - Time: _____ (target: < 5 minutes)
  - Notes: _____
- [ ] Test 2.3: End-to-End Pipeline - PASS/FAIL
  - Time: _____ (target: < 5 hours 15 min)
  - Notes: _____

## Phase 3: Error Handling

- [ ] Test 3.1: Unidentified Photos - PASS/FAIL
- [ ] Test 3.2: Caption Service Failure - PASS/FAIL
- [ ] Test 3.3: PostBridge API Error - PASS/FAIL
- [ ] Test 3.4: Rate Limiting - PASS/FAIL
- [ ] Test 3.5: Concurrent Operations - PASS/FAIL

## Phase 4: Performance

- [ ] Test 4.1: Caption Generation Speed - PASS/FAIL
  - Average: _____ seconds (target: < 120s)
- [ ] Test 4.2: Photo Sync Volume - PASS/FAIL
- [ ] Test 4.3: Slackbot Responsiveness - PASS/FAIL
  - /photos: _____ s
  - /caption: _____ s
  - /post: _____ s
  - /posts: _____ s

## Overall Results

**Success Rate:** _____% (___/24 tests passed)

**Critical Issues:**
- _____

**Blockers:**
- _____

**Recommendations:**
- _____

**Ready for Production:** YES/NO
```

---

## Troubleshooting

See [Troubleshooting Guide](./social-media-troubleshooting.md) for common issues and solutions.

## Next Steps

After successful testing:

1. Document any issues found
2. Create tickets for bugs or enhancements
3. Update deployment documentation
4. Schedule user acceptance testing with board
5. Plan production rollout

---

## Support

For questions or issues during testing:
- Review GitHub Actions logs
- Check service logs (caption service, Slackbot)
- Verify all environment variables are set
- Consult architecture documentation
