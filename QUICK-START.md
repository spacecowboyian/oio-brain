# Quick Start: Photo Automation Pipeline

**For: Board Users**  
**Duration: 2 minutes to activate** | **30 minutes to verify working**

---

## What Is This?

Automated photo filing and caption generation for OIO Racing social media.

**What it does:**
- 📸 You upload photos → `intake/photos/`
- 🤖 AI analyzes them (car, driver, event)
- 📁 Files them automatically to `photos/{Driver}/{Car}/`
- ✍️ Generates social media captions
- 📱 Posts to Instagram, TikTok, Twitter, etc.

---

## Activate in 2 Minutes

### Step 1: Get API Key (1 minute)

1. Go to: https://console.anthropic.com/account/keys
2. Copy your **API Key** (starts with `sk-ant-...`)
3. Keep this tab open

### Step 2: Configure GitHub Secret (1 minute)

1. Go to your repo: **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. **Name:** `ANTHROPIC_API_KEY` (exactly)
4. **Value:** Paste your API key from step 1
5. Click **Add secret**

**Done!** The system is now active.

---

## Test It Works (5 minutes)

### Option A: Manual Test via GitHub UI

1. Go to: **Actions → Process Picdump Photos**
2. Click **Run workflow** → **Run workflow**
3. Wait 2-3 minutes for completion
4. Check: **Actions tab** to see results

### Option B: Push a Photo to Trigger Automatically

1. Copy a photo: `cp picdump/test_photo_1.png intake/photos/`
2. Commit and push:
   ```bash
   git add intake/photos/
   git commit -m "test: trigger workflow"
   git push
   ```
3. Watch: **Actions tab** for workflow execution (auto-triggers)

### What to Expect

✅ **Workflow runs**  
✅ **Photos analyzed** (~1 sec per photo)  
✅ **Photos filed** to `photos/{driver}/{car}/`  
✅ **Slack notification** (if configured)  
✅ **Results committed** back to repo  

---

## Full Testing (30 minutes)

### Phase 1: Verify Basic Function (10 min)

See TESTING-GUIDE.md → "Phase 1: Quick Validation"

**Success criteria:** 2/3 test photos filed correctly

### Phase 2: Validate at Scale (20 min)

See TESTING-GUIDE.md → "Phase 2: Full Batch Test"

**Need:** 50 test photos  
**Success criteria:** ≥80% filing accuracy

### Phase 3 & 4: Captions & Social Posts (10 min)

See TESTING-GUIDE.md → "Phase 3 & 4"

---

## How It Works (30 seconds)

```
You push photos
       ↓
GitHub detects new files
       ↓
Workflow triggers automatically
       ↓
Claude AI analyzes: "What car? What driver? What event?"
       ↓
Photos filed: photos/ian-jennings/miata-nb/photo.jpg
       ↓
Caption generated + posted to social
```

---

## Common Issues

### Q: "I configured the key but workflow still fails"
**A:** GitHub might not have picked up the secret yet. 
- Wait 1 minute after configuring secret
- Push a new photo to trigger fresh workflow
- Check GitHub Actions logs for actual error

### Q: "Photos aren't getting filed"
**A:** Check Slack for error messages. Common issues:
- Photo is blurry/unclear → low confidence
- Car/driver not recognized → check OIO context
- File format not supported → use .jpg or .png

### Q: "How do I get more help?"
**A:** See the full guides:
- **Setup:** Read `PHOTO-WORKFLOW.md`
- **Testing:** Read `TESTING-GUIDE.md`
- **Troubleshooting:** See `PHOTO-WORKFLOW.md` → "Troubleshooting"

---

## What Happens Next

### Timeline After Configuration

| Time | What | Status |
|------|------|--------|
| **Now** | Configure API key | ← You are here |
| **+2 min** | System active | API calls work |
| **+5 min** | Test workflow | Verifies working |
| **+30 min** | Full validation | 50-photo test |
| **+1 hour** | Production ready | Go live |

---

## Production Setup (Optional)

### Enable Slack Notifications

1. Create Slack bot in your workspace
2. Configure **SLACK_BOT_TOKEN** and **SLACK_CHANNEL_ID** GitHub secrets
3. Uncertain photos → Auto-notified in Slack

See `PHOTO-WORKFLOW.md` for detailed steps.

---

## Files Reference

| File | Purpose |
|---|---|
| `PHOTO-WORKFLOW.md` | Complete setup + troubleshooting |
| `TESTING-GUIDE.md` | Testing procedures (4 phases) |
| `QUICK-START.md` | This file (you are here) |
| `intake/photos/` | Where you upload photos |
| `photos/` | Where photos get filed |

---

## Success Checklist

- [ ] API key configured in GitHub Secrets
- [ ] Workflow runs without errors
- [ ] Test photos processed and filed
- [ ] Slack notifications working (optional)
- [ ] Ready for production photos

---

## One-Line Summary

Configure `ANTHROPIC_API_KEY` in GitHub Secrets → Upload photos to `intake/photos/` → Workflow runs automatically → Photos filed + captions generated → Posted to social

---

**Need more details?** See the full guides in the repo.  
**Questions?** Check the troubleshooting sections in PHOTO-WORKFLOW.md.

Ready? Start with **Step 1** above! ⬆️
