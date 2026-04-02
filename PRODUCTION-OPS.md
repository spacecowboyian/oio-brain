# Production Operations Guide

Operations procedures for the live photo automation pipeline.

---

## Pre-Launch Checklist

**Before going live with production photos:**

- [ ] ANTHROPIC_API_KEY configured in GitHub Secrets
- [ ] SLACK_BOT_TOKEN configured (optional but recommended)
- [ ] SLACK_CHANNEL_ID configured (optional but recommended)
- [ ] 50-photo test batch completed successfully (≥80% accuracy)
- [ ] Caption validation passed (brand voice check)
- [ ] End-to-end social posting test successful
- [ ] Team trained on procedures
- [ ] Monitoring dashboard set up
- [ ] Runbooks reviewed

---

## Daily Operations

### Uploading Photos

**Typical workflow:**

1. **Take photos** at event or during shoot
2. **Export photos** with descriptive names (optional)
3. **Upload to intake folder**:
   ```bash
   # Option A: Via GitHub web UI
   # Go to: Repository → intake/photos → Add file → Upload files
   
   # Option B: Via git command
   cp photos/*.jpg ~/repos/oio-brain/intake/photos/
   cd ~/repos/oio-brain
   git add intake/photos/
   git commit -m "photos: add photos from [event name]"
   git push
   ```

4. **Workflow triggers automatically**
   - No manual action needed
   - Check Slack for status updates

5. **Photos filed within 2-3 minutes**
   - Check `photos/` directory for filed photos
   - Review in GitHub if needed

### Weekly Tasks

**Every Monday (or as needed):**

1. **Review filed photos**
   ```bash
   find photos/ -type f -mtime -7 | head -20
   # Shows recently filed photos
   ```

2. **Check filing accuracy**
   - Visual scan of `photos/{driver}/{car}/` structure
   - Verify photos in correct locations
   - Note any misfilings for feedback

3. **Monitor Slack notifications**
   - Review #photo-workflow for uncertainty alerts
   - Manually file any low-confidence photos
   - Identify patterns if any

4. **Review captions**
   - Check generated captions for quality
   - Verify brand voice compliance
   - Document any refinements needed

### Monthly Tasks

**First week of month:**

1. **Analyze metrics**
   ```bash
   # Count photos processed
   find photos/ -type f -mtime -30 | wc -l
   
   # Check filing success rate
   # Look for any patterns in misfiled photos
   ```

2. **Review system logs**
   - GitHub Actions workflow logs
   - API usage and costs
   - Error rates and types

3. **Validate captions**
   - Run validation tool on recent captions
   - Check quality benchmarks
   - Document any adjustments

4. **Update metrics dashboard**
   - Success rates
   - Filing accuracy
   - Caption quality scores

---

## Monitoring & Alerting

### Slack Notifications Setup

**The bot automatically notifies:**

- ✅ Photos successfully filed
- ⚠️ Low-confidence photos requiring review
- ❌ Failed analyses with error details
- 📊 Weekly summary reports

**Example notifications:**

```
✓ Filed 42 photos from [event]
  - ian-jennings/miata-nb: 12 photos
  - ian-jennings/civic: 8 photos
  - other drivers: 22 photos

⚠️ Uncertain filing (confidence 65-79%)
  - photo_123.jpg - Could be Miata or Civic
  - photo_456.jpg - Driver not visible
  Review these manually in intake/photos/
```

### GitHub Actions Monitoring

**Check workflow status:**

1. Repository → Actions tab
2. Filter by "Process Picdump Photos" workflow
3. Latest run shows:
   - Status (success/failed)
   - Duration (~2-3 min per photo)
   - Error details if any
   - Commit with results

### Key Metrics to Track

**Success rate:** Photos filed correctly / Photos processed
- Target: ≥90%
- Monitor: Weekly
- Alert threshold: <85%

**Processing time:** Time from upload to filing
- Target: <3 minutes
- Monitor: Per batch
- Alert threshold: >5 minutes

**API cost:** Anthropic API usage
- Monitor: Monthly
- Expected: ~$0.10-0.50 per 100 photos
- Budget: Discuss with team

**Caption quality:** Validation score
- Target: ≥90%
- Monitor: Weekly
- Alert threshold: <85%

---

## Common Operations

### Manually File a Low-Confidence Photo

**When Slack alerts you:**

1. **Check the photo**
   ```bash
   ls intake/photos/ | grep photo_123
   # Find the photo in intake/photos/
   ```

2. **Decide correct location**
   - What car is in the photo?
   - What driver owns it?
   - What event/context?

3. **File manually**
   ```bash
   # Copy to correct location
   cp intake/photos/photo_123.jpg photos/ian-jennings/miata-nb/
   
   # Remove from intake
   rm intake/photos/photo_123.jpg
   
   # Commit
   git add photos/ intake/
   git commit -m "photos: manually file photo_123.jpg to miata-nb"
   git push
   ```

### Re-process Failed Photos

**If a photo fails to analyze:**

1. **Check error in Slack** or GitHub Actions logs
2. **Verify photo file**
   - Is it actually a valid image?
   - Is it readable?
   - File size reasonable?
3. **Re-upload to intake/photos/**
   - Workflow will try again
   - May fail for same reason, or succeed

### Add New Car/Driver Context

**When OIO Racing gets a new car or driver:**

1. **Update context files**
   - `cars/` directory - add car specs
   - `brand/team-bios.md` - add driver bio

2. **Test with sample photo**
   ```bash
   cp picdump/test_photo.png intake/photos/new_car_test.png
   git add intake/photos/
   git commit -m "test: validate new car filing"
   git push
   ```

3. **Verify filed to correct location**
   - Check `photos/{driver}/{car}/`
   - Adjust prompts if needed

### Update Filing Thresholds

**If accuracy is too low or high:**

1. **Check confidence threshold** in `ai_photo_filing_agent.py`
   - Line 51: `CONFIDENCE_THRESHOLD = 0.80`
   - Lower = more auto-filing (more misfiles)
   - Higher = more Slack alerts (more manual work)

2. **Test adjustment**
   ```bash
   # Edit the threshold
   vim scripts/ai_photo_filing_agent.py
   # Change line 51
   
   # Commit
   git add scripts/
   git commit -m "config: adjust confidence threshold to 0.75"
   git push
   ```

3. **Monitor results**
   - Watch next batch for accuracy change
   - Adjust further if needed

---

## Troubleshooting

### Workflow Doesn't Trigger

**Problem:** Photos uploaded but workflow doesn't run

**Solutions:**
1. Verify photos are actually pushed to GitHub
2. Check GitHub Actions is enabled (Settings → Actions)
3. Manually trigger: Actions → Process Picdump Photos → Run workflow
4. Check workflow logs for error messages

### Photos Not Filing Correctly

**Problem:** Photos filed to wrong car/driver

**Solutions:**
1. Check Slack for low-confidence alerts
2. Review photo quality (blurry/unclear = low confidence)
3. Verify car/driver info is in OIO context
4. Lower confidence threshold if consistently too strict
5. Manually file and provide feedback for prompt improvement

### API Authentication Errors

**Problem:** Workflow fails with auth error

**Solutions:**
1. Check ANTHROPIC_API_KEY is configured
2. Verify API key is still valid (console.anthropic.com)
3. Check account billing is active
4. Get fresh API key if needed and update secret

### Performance Issues

**Problem:** Workflow takes >5 minutes for small batch

**Solutions:**
1. Check GitHub Actions performance (may be slow queue)
2. Check Anthropic API performance (may be rate limited)
3. Review workflow logs for bottlenecks
4. Contact support if consistently slow

---

## Escalation Procedures

### When to Contact Support

**Anthropic API issues:**
- Consistent authentication failures
- API timeouts or slow responses
- Unexpected usage/costs
- Contact: support@anthropic.com

**GitHub Actions issues:**
- Workflows not triggering
- Persistent job failures
- Rate limiting
- Contact: GitHub Support

**OIO Racing team:**
- Filing accuracy below target
- Caption quality issues
- System doesn't meet needs
- Contact: Team discussion

---

## Disaster Recovery

### If Everything Breaks

**Quick recovery steps:**

1. **Stop new uploads**
   - Don't push more photos to intake/

2. **Check what went wrong**
   ```bash
   # View latest GitHub Actions logs
   # Check Slack for error messages
   # Review API usage at console.anthropic.com
   ```

3. **Recover from last known good state**
   ```bash
   # View git history
   git log --oneline photos/
   
   # Check which photos were filed last
   git diff HEAD~1 HEAD photos/
   ```

4. **Restore API key if needed**
   - Get fresh key from console.anthropic.com
   - Update GitHub Secret: ANTHROPIC_API_KEY
   - Re-run workflow

5. **Re-process failed photos**
   - Copy problem photos back to intake/photos/
   - Trigger workflow again
   - Monitor for success

---

## Documentation Reference

| Document | Purpose |
|----------|---------|
| QUICK-START.md | Setup guide (2 minutes) |
| PHOTO-WORKFLOW.md | Complete reference |
| TESTING-GUIDE.md | Testing procedures |
| PRODUCTION-OPS.md | This file - Daily ops |

---

## Success Indicators

**System is working well when:**

- ✅ Photos filed within 2-3 minutes
- ✅ ≥90% filing accuracy
- ✅ <5 Slack uncertainty alerts per 50 photos
- ✅ Captions pass validation ≥90%
- ✅ No API errors for 1+ week
- ✅ Team can upload and caption in <30 min

**System needs attention when:**

- ⚠️ Processing takes >5 minutes
- ⚠️ Filing accuracy <85%
- ⚠️ >10 uncertainty alerts per 50 photos
- ⚠️ Caption validation <80%
- ⚠️ Consistent API errors
- ⚠️ Manual work takes >1 hour for 50 photos

---

**System Status: PRODUCTION-READY**

Ready to launch once ANTHROPIC_API_KEY is configured.

See QUICK-START.md to activate.
