# Photo Pipeline Testing Guide

Ready-to-execute testing procedures for the OIO photo automation pipeline.

---

## Pre-Test Checklist ✅

**Before you start, verify:**

- [ ] `ANTHROPIC_API_KEY` configured in GitHub Secrets
- [ ] Optional: `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID` configured
- [ ] Test photos ready (50 sample photos prepared)
- [ ] Git main branch clean and up-to-date
- [ ] `intake/photos/` directory ready (currently contains 3 test photos)

---

## Phase 1: Quick Validation (3 sample photos)

### Status: READY TO EXECUTE

**Purpose:** Verify full pipeline works end-to-end with small batch

**Duration:** 10-15 minutes

### Steps

1. **Trigger Initial Test**
   ```bash
   cd /Users/ian/repos/oio-brain
   git status  # Verify clean
   ```

2. **Verify Test Photos Present**
   ```bash
   ls -la intake/photos/
   # Should show: test_photo_1.png, test_photo_2.png, test_photo_3.png
   ```

3. **Trigger Workflow (Option A: GitHub UI)**
   - Go to: Repository → Actions → Process Picdump Photos
   - Click "Run workflow" → Run workflow
   - Wait for completion

4. **Trigger Workflow (Option B: Force Push)**
   ```bash
   # Touch a file to force a push (triggers photo detection)
   touch intake/photos/.trigger
   git add intake/photos/.trigger
   git commit -m "test: trigger photo processing"
   git push
   ```

5. **Monitor Execution**
   - Go to: Repository → Actions
   - Watch "Process Picdump Photos" workflow
   - Should complete in ~2-3 minutes

6. **Verify Results**
   ```bash
   git pull  # Get workflow results
   ls -la photos/
   # Should show filed photos in photos/{driver}/{car}/ structure
   ```

7. **Check Slack Notifications** (if configured)
   - Bot should post messages for uncertain/failed photos
   - Check channel for any low-confidence photo alerts

### Success Criteria

✅ Workflow triggered automatically  
✅ All 3 test photos processed  
✅ At least 2 photos filed correctly (filed to `photos/{driver}/{car}/`)  
✅ Results committed to repo  
✅ Slack notifications received (if configured)  

### If Test Fails

**Common issues and fixes:**

| Error | Cause | Fix |
|-------|-------|-----|
| Workflow doesn't trigger | Photo push not detected | Ensure photos committed and pushed to main |
| API authentication error | ANTHROPIC_API_KEY not set | Check GitHub Secrets configuration |
| Photos not filed | Confidence too low | Check Slack for uncertainty notifications |
| Git commit fails | Permission issues | Verify GitHub Actions has write access |

---

## Phase 2: Full Batch Test (50 photos)

### Status: READY AFTER PHASE 1 PASSES

**Purpose:** Validate system works at scale with realistic photo variety

**Duration:** 20-30 minutes

### Preparation

1. **Prepare 50 Test Photos**
   - Copy additional test photos from `picdump/` directory
   - Or use representative sample photos
   - Place in `intake/photos/`

   ```bash
   # Example: Copy more test photos
   cp picdump/test_photo_*.png intake/photos/
   
   # Should have ~50 photos total
   ls intake/photos/ | wc -l
   ```

2. **Commit Batch**
   ```bash
   git add intake/photos/
   git commit -m "test: prepare 50-photo validation batch"
   git push
   ```

### Execution

1. **Run Workflow**
   - Repository → Actions → File Picdump Photos
   - Click "Run workflow" → Run workflow
   - Monitor progress

2. **Processing Time**
   - ~1-2 seconds per photo
   - 50 photos = ~2-3 minutes total
   - Longer if API rate limits engaged

3. **Monitor Workflow**
   - GitHub Actions logs show real-time progress
   - Check for errors or stalled jobs
   - Slack notifications for uncertain photos

4. **Collect Results**
   ```bash
   git pull
   
   # Count filed photos
   find photos/ -type f \( -name "*.jpg" -o -name "*.png" \) | wc -l
   
   # Should be close to 50
   ```

### Success Criteria

✅ All 50 photos processed  
✅ ≥80% accuracy in filing (40+ photos filed correctly)  
✅ Slack notifications for uncertain/failed photos  
✅ Results properly committed  
✅ No workflow timeouts or errors  
✅ Filing distribution across drivers/cars  

### Data Collection

**Capture these metrics:**

```bash
# Accuracy metrics
echo "=== Filing Results ==="
echo "Total photos processed: $(ls intake/photos/ | grep -E '\.(png|jpg|jpeg)$' | wc -l)"
echo "Photos filed: $(find photos/ -type f \( -name '*.jpg' -o -name '*.png' \) | wc -l)"
echo "Filing accuracy: X% (filed / processed)"

# Distribution
echo ""
echo "=== Distribution by Driver ==="
find photos/ -mindepth 1 -maxdepth 1 -type d | while read dir; do
  driver=$(basename "$dir")
  count=$(find "$dir" -type f | wc -l)
  echo "  $driver: $count photos"
done

# Issues
echo ""
echo "=== Issues Captured ==="
echo "Check Slack for failed/uncertain photos"
echo "Review GitHub Actions logs for API errors"
```

---

## Phase 3: Caption Pipeline Validation

### Status: READY AFTER PHASE 2 PASSES

**Purpose:** Validate caption generation and quality control

**Duration:** 15-20 minutes

### Setup

1. **Verify Caption Scripts Present**
   ```bash
   ls scripts/caption*.py
   # Should show:
   #   caption_generation_service.py
   #   validate_captions.py
   ```

2. **Run Caption Validation on Filed Photos**
   ```bash
   python3 scripts/validate_captions.py --photo-dir photos/
   ```

3. **Monitor Output**
   - Brand voice validation
   - Specificity checks
   - Tone appropriateness
   - Quality report generation

### Success Criteria

✅ Captions generate without errors  
✅ Brand voice validation passes  
✅ Specificity meets OIO standards  
✅ Tone matches photo context  
✅ Quality report generated  

### Review Results

```bash
# Check caption validation report
cat caption-validation-report.md

# Review any flagged captions
grep -i "failed\|low-confidence" caption-validation-report.md
```

---

## Phase 4: End-to-End Social Posting

### Status: READY AFTER PHASE 3 PASSES

**Purpose:** Validate complete pipeline from photo to social post

**Duration:** 10-15 minutes

### Execution

1. **Test Caption + Photo Composition**
   ```bash
   python3 scripts/caption_generation_service.py \
     --photo photos/ian-jennings/miata-nb/test_photo_1.jpg \
     --output test-caption.json
   ```

2. **Generate Sample Posts**
   - Use caption templates from CAPTION-TEMPLATES.md
   - Create 3-5 sample social posts
   - Review for accuracy and brand voice

3. **Test PostBridge Integration**
   - Verify PostBridge API credentials configured
   - Test photo + caption composition
   - Validate post formatting for each platform

### Success Criteria

✅ Captions align with photos  
✅ Posts formatted correctly for each platform  
✅ Brand voice consistent  
✅ No API errors on post composition  
✅ Ready for manual social posting  

---

## Complete Test Workflow Diagram

```
GitHub Secrets: ANTHROPIC_API_KEY
              ↓
Phase 1: 3-Photo Quick Test
  ├─ Trigger workflow
  ├─ Monitor execution
  └─ Verify results
              ↓ (success)
Phase 2: 50-Photo Batch Test
  ├─ Prepare batch
  ├─ Process and file
  ├─ Collect metrics
  └─ Validate accuracy
              ↓ (≥80% success)
Phase 3: Caption Validation
  ├─ Generate captions
  ├─ Validate quality
  └─ Review report
              ↓ (pass)
Phase 4: Social Posting
  ├─ Compose posts
  ├─ Test integration
  └─ Ready for posting
              ↓
PRODUCTION READY ✅
```

---

## Monitoring & Logging

### Real-Time Monitoring

**GitHub Actions:**
- Repository → Actions tab
- Filter by workflow name
- Watch logs for errors

**Slack Notifications:**
- #photo-workflow channel
- Uncertainty alerts
- Error reports
- Completion summaries

### Log Files

```bash
# GitHub Actions logs (automatically captured)
# Check: Repository → Actions → Workflow run → Job logs

# Local testing logs (if running locally)
tail -f photo-processing.log
tail -f caption-validation.log
```

### Collecting Metrics

```bash
# Create test results summary
cat > test-results.md << 'EOF'
# Test Results - [Date]

## Phase 1: Quick Validation
- Photos processed: 3
- Photos filed: X
- Success rate: X%

## Phase 2: Batch Test
- Photos processed: 50
- Photos filed: X
- Success rate: X%
- Distribution: [by driver]

## Phase 3: Caption Validation
- Captions generated: X
- Quality score: X%
- Brand voice compliance: X%

## Phase 4: Social Posting
- Post composition: Success
- Platform formatting: Success

## Overall Status
[PASSED / NEEDS REFINEMENT]

## Next Steps
[List any adjustments needed]
EOF
```

---

## Troubleshooting Reference

### Issue: Workflow doesn't start

**Symptoms:** No workflow runs in Actions tab

**Solutions:**
1. Check ANTHROPIC_API_KEY is actually configured (not just present)
2. Verify photos are committed and pushed (not just on local)
3. Try manual workflow dispatch: Actions → Workflow name → Run workflow
4. Check GitHub Actions is enabled in repository settings

### Issue: Photos not filing (low confidence)

**Symptoms:** Photos stay in `intake/photos/`, Slack notifications of uncertainty

**Solutions:**
1. Review confidence scores in Slack notifications
2. Lower confidence threshold in `ai_photo_filing_agent.py` if consistently low (line 51)
3. Review photo quality - blurry/unclear photos get low scores
4. Check if cars/drivers in photo are recognized in OIO context

### Issue: API authentication fails

**Symptoms:** Error: "Could not resolve authentication method"

**Solutions:**
1. Verify API key in GitHub Secrets is valid
2. Check Anthropic account has active billing
3. Verify Claude 3.5 Sonnet (Vision) is enabled
4. Get fresh API key from console.anthropic.com

### Issue: Workflow times out

**Symptoms:** GitHub Actions job runs >30 minutes then fails

**Solutions:**
1. Reduce batch size (test with fewer photos)
2. Check for API rate limiting - add delays between photos
3. Verify network connectivity to Anthropic API
4. Split large batches into multiple workflow runs

### Issue: Git push fails in workflow

**Symptoms:** Workflow runs but results not committed

**Solutions:**
1. Check GitHub Actions has write permissions
2. Verify branch protection rules allow workflow commits
3. Check for merge conflicts before committing
4. Review git config in workflow (user.name, user.email)

---

## Rollback Procedures

### If Testing Breaks Something

**Quick recovery:**

```bash
# Option 1: Revert last commit
git revert HEAD
git push

# Option 2: Clean up test photos
rm intake/photos/*.png
git add intake/photos/
git commit -m "test: clean up test photos"
git push

# Option 3: Reset to known good state
git reset --hard origin/main
```

---

## Success Path Summary

| Phase | Duration | Passes? | Next Step |
|-------|----------|---------|-----------|
| Phase 1 (3 photos) | 10-15 min | ✓ | → Phase 2 |
| Phase 2 (50 photos) | 20-30 min | ✓ (≥80% accuracy) | → Phase 3 |
| Phase 3 (Captions) | 15-20 min | ✓ | → Phase 4 |
| Phase 4 (Social) | 10-15 min | ✓ | ✅ READY |
| **Total** | **55-80 min** | **All pass** | **Production** |

---

## Contacts & Resources

- **Technical Issues:** Check PHOTO-WORKFLOW.md troubleshooting
- **OIO Context:** See `core/decisions-log.md`
- **Brand Voice:** See `brand/voice.md`
- **API Docs:** https://docs.anthropic.com/

---

**Test Guide Version:** 1.0  
**Last Updated:** April 2, 2026  
**Status:** READY TO EXECUTE (awaiting API key configuration)
