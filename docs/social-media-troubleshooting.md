# OIO Racing - Social Media System Troubleshooting Guide

**Version:** 1.0
**Last Updated:** 2026-03-30

---

## Quick Diagnostics

### System Health Check

Run this diagnostic script to check all components:

```bash
#!/bin/bash
echo "=== OIO Social Media System Health Check ==="
echo

# Check environment variables
echo "1. Environment Variables:"
[[ -n "$SLACK_BOT_TOKEN" ]] && echo "  ✓ SLACK_BOT_TOKEN set" || echo "  ✗ SLACK_BOT_TOKEN missing"
[[ -n "$SLACK_APP_TOKEN" ]] && echo "  ✓ SLACK_APP_TOKEN set" || echo "  ✗ SLACK_APP_TOKEN missing"
[[ -n "$POSTBRIDGE_API_KEY" ]] && echo "  ✓ POSTBRIDGE_API_KEY set" || echo "  ✗ POSTBRIDGE_API_KEY missing"
[[ -n "$PAPERCLIP_API_KEY" ]] && echo "  ✓ PAPERCLIP_API_KEY set" || echo "  ✗ PAPERCLIP_API_KEY missing"
echo

# Check Python dependencies
echo "2. Python Dependencies:"
python3 -c "import requests" 2>/dev/null && echo "  ✓ requests installed" || echo "  ✗ requests missing"
python3 -c "import flask" 2>/dev/null && echo "  ✓ flask installed" || echo "  ✗ flask missing"
python3 -c "import slack_bolt" 2>/dev/null && echo "  ✓ slack-bolt installed" || echo "  ✗ slack-bolt missing"
echo

# Check key files
echo "3. Required Files:"
[[ -f scripts/postbridge_client.py ]] && echo "  ✓ postbridge_client.py exists" || echo "  ✗ postbridge_client.py missing"
[[ -f scripts/slackbot_social_media.py ]] && echo "  ✓ slackbot_social_media.py exists" || echo "  ✗ slackbot_social_media.py missing"
[[ -f scripts/caption_generation_service.py ]] && echo "  ✓ caption_generation_service.py exists" || echo "  ✗ caption_generation_service.py missing"
[[ -f scripts/sync_google_photos.py ]] && echo "  ✓ sync_google_photos.py exists" || echo "  ✗ sync_google_photos.py missing"
echo

# Check directories
echo "4. Required Directories:"
[[ -d picdump ]] && echo "  ✓ picdump/ exists" || echo "  ✗ picdump/ missing"
[[ -d photos ]] && echo "  ✓ photos/ exists" || echo "  ✗ photos/ missing"
[[ -d "OIO Brain/01 - Brand" ]] && echo "  ✓ OIO Brain/01 - Brand/ exists" || echo "  ✗ Brand directory missing"
echo

# Check services
echo "5. Running Services:"
curl -s http://localhost:5000/health >/dev/null 2>&1 && echo "  ✓ Caption service running" || echo "  ✗ Caption service not running"
echo

echo "=== End Health Check ==="
```

---

## Common Issues

### PostBridge Client Issues

#### Issue: "POSTBRIDGE_API_KEY not set"

**Symptoms:**
- PostBridge client fails to initialize
- `/post` command returns error

**Causes:**
- Environment variable not set
- API key expired or invalid

**Solutions:**

1. Set the environment variable:
```bash
export POSTBRIDGE_API_KEY="your-api-key-here"
```

2. Verify the key is valid:
```bash
python3 << 'EOF'
from scripts.postbridge_client import PostBridgeClient
client = PostBridgeClient()
print(client.list_accounts())
EOF
```

3. Generate a new API key:
   - Log in to https://postbridge.app/settings/api
   - Create new API key
   - Update environment variable

---

#### Issue: "No connected social accounts found"

**Symptoms:**
- PostBridge client initializes but can't create posts
- `/post` command fails with account error

**Causes:**
- No Instagram/Facebook accounts connected to PostBridge
- Accounts disconnected or expired

**Solutions:**

1. Log in to PostBridge:
   - Visit https://postbridge.app/settings/accounts
   - Connect Instagram and/or Facebook accounts
   - Verify accounts show as "Connected"

2. Check account status via API:
```python
from scripts.postbridge_client import PostBridgeClient
client = PostBridgeClient()
accounts = client.list_accounts()
for account in accounts:
    print(f"{account['platform']}: {account['status']}")
```

3. Re-authorize accounts if expired:
   - Click "Reconnect" in PostBridge settings
   - Grant required permissions
   - Verify connection

---

#### Issue: "Rate limit exceeded"

**Symptoms:**
- PostBridge requests fail with 429 error
- Error message mentions rate limiting

**Causes:**
- Too many API requests in short time
- PostBridge API limits exceeded

**Solutions:**

1. Wait before retrying:
   - PostBridge client automatically waits 60 seconds
   - Check `Retry-After` header for exact wait time

2. Reduce request frequency:
   - Batch operations where possible
   - Add delays between requests

3. Check rate limit status:
```python
from scripts.postbridge_client import PostBridgeClient
client = PostBridgeClient()
# Check response headers for rate limit info
response = client._make_request('GET', '/accounts')
print(f"Rate limit remaining: {response.headers.get('X-RateLimit-Remaining')}")
```

---

### Caption Generation Service Issues

#### Issue: "Caption generation service not running"

**Symptoms:**
- `/caption` command fails
- Curl to localhost:5000 fails
- "Connection refused" errors

**Causes:**
- Service not started
- Port 5000 already in use
- Service crashed

**Solutions:**

1. Start the service:
```bash
cd /Users/ian/repos/oio-brain
python3 scripts/caption_generation_service.py &
```

2. Check if port is already in use:
```bash
lsof -i :5000
```

If port is in use, either:
- Kill the process: `kill $(lsof -t -i :5000)`
- Or use a different port: `export CAPTION_SERVICE_PORT=5001`

3. Check service logs:
```bash
# If service crashes immediately, run in foreground to see errors
python3 scripts/caption_generation_service.py
```

---

#### Issue: "Caption generation timeout"

**Symptoms:**
- `/caption` command takes > 2 minutes
- Service returns timeout error
- Paperclip task never completes

**Causes:**
- AI Copywriter agent is busy
- AI Copywriter agent is offline
- Paperclip API unreachable
- Network issues

**Solutions:**

1. Check AI Copywriter agent status:
```bash
curl -s "${PAPERCLIP_API_URL}/api/agents/a2859bcb-cb20-4429-916b-65401f66d96a" \
  -H "Authorization: Bearer ${PAPERCLIP_API_KEY}" | jq '.status'
```

Expected: `"running"`

2. Check Paperclip API connectivity:
```bash
curl -s "${PAPERCLIP_API_URL}/api/health"
```

3. Verify Paperclip agent has capacity:
   - Check agent budget (not over 100%)
   - Check agent is not paused
   - Review agent recent runs for issues

4. Increase timeout (if needed):
   - Edit `caption_generation_service.py`
   - Increase `POLL_TIMEOUT` from 120 to 180 seconds

---

#### Issue: "Brand voice context missing"

**Symptoms:**
- Captions don't match OIO brand voice
- Service logs show file not found errors
- Captions are generic

**Causes:**
- Brand voice files moved or deleted
- Incorrect path to OIO Brain directory

**Solutions:**

1. Verify brand voice files exist:
```bash
ls -la "OIO Brain/01 - Brand/Voice-and-Tone.md"
ls -la "OIO Brain/02 - Content/OIO-Brand-Voice-Guide.md"
```

2. Check service is reading files:
```python
from pathlib import Path
BRAIN_ROOT = Path(__file__).parent.parent / "OIO Brain"
print(f"Brain root exists: {BRAIN_ROOT.exists()}")
print(f"Brand dir exists: {(BRAIN_ROOT / '01 - Brand').exists()}")
```

3. Update paths if OIO Brain moved:
   - Edit `caption_generation_service.py`
   - Update `BRAIN_ROOT` path

---

### Slackbot Issues

#### Issue: "Slackbot won't start"

**Symptoms:**
- Script exits immediately
- "SLACK_BOT_TOKEN not set" error
- Import errors

**Causes:**
- Missing environment variables
- Missing dependencies
- Invalid tokens

**Solutions:**

1. Set required environment variables:
```bash
export SLACK_BOT_TOKEN="xoxb-your-token"
export SLACK_APP_TOKEN="xapp-your-token"
export POSTBRIDGE_API_KEY="your-key"
```

2. Install missing dependencies:
```bash
pip install slack-bolt requests
```

3. Verify tokens are valid:
   - Bot token should start with `xoxb-`
   - App token should start with `xapp-`
   - Check tokens in Slack app settings

---

#### Issue: "Commands not responding"

**Symptoms:**
- Slash commands return no response
- Commands time out
- Slackbot appears to be running

**Causes:**
- Socket Mode not enabled
- Commands not registered in Slack
- Bot token missing scopes
- Slackbot crashed after startup

**Solutions:**

1. Check Slackbot logs:
   - Look for "⚡️ Bolt app is running!" message
   - Check for error messages
   - Verify WebSocket connection established

2. Verify Socket Mode enabled:
   - Go to https://api.slack.com/apps
   - Select your app
   - Navigate to "Socket Mode"
   - Ensure it's enabled
   - Generate app token if needed

3. Check slash commands registered:
   - In Slack app settings → "Slash Commands"
   - Verify all 4 commands exist:
     - `/photos`
     - `/caption`
     - `/post`
     - `/posts`

4. Verify bot scopes:
   - In Slack app settings → "OAuth & Permissions"
   - Required scopes:
     - `commands`
     - `chat:write`

5. Restart Slackbot:
```bash
# Kill existing process
pkill -f slackbot_social_media.py

# Start fresh
python3 scripts/slackbot_social_media.py
```

---

#### Issue: "/caption command times out"

**Symptoms:**
- `/caption` command never completes
- User sees "timeout" message after 2 minutes

**Causes:**
- Caption service not running
- Caption service unreachable
- AI Copywriter agent issues

**Solutions:**

1. Verify caption service is running:
```bash
curl http://localhost:5000/health
```

2. Check caption service URL in Slackbot:
```bash
echo $CAPTION_SERVICE_URL
```

If different from localhost:5000, update:
```bash
export CAPTION_SERVICE_URL="http://localhost:5000"
```

3. Test caption service directly:
```bash
curl -X POST http://localhost:5000/generate-caption \
  -H "Content-Type: application/json" \
  -d '{"media_urls": ["test.jpg"], "context": "test", "caption_count": 1}'
```

4. Check AI Copywriter agent (see Caption Generation Service issues above)

---

#### Issue: "/photos list shows no photos"

**Symptoms:**
- `/photos list` returns "No photos found"
- Photos exist in picdump directory

**Causes:**
- picdump directory empty
- Photos are hidden files
- Incorrect path to picdump

**Solutions:**

1. Check picdump directory:
```bash
ls -la picdump/
```

2. Move test photos to picdump:
```bash
cp photos/Ian/1985\ MR2/*.jpg picdump/
```

3. Check for hidden files (start with `.`):
```bash
ls -a picdump/ | grep "^\."
```

4. Verify Slackbot path:
```python
# In slackbot_social_media.py
PICDUMP_DIR = Path(__file__).parent.parent / "picdump"
print(f"Picdump path: {PICDUMP_DIR}")
print(f"Exists: {PICDUMP_DIR.exists()}")
```

---

### Google Photos Sync Issues

#### Issue: "Google Photos workflow fails"

**Symptoms:**
- GitHub Action fails
- No photos synced to picdump
- Workflow logs show errors

**Causes:**
- Album URL changed or invalid
- Album became private
- Network connectivity issues
- Google Photos HTML structure changed
- Rate limiting

**Solutions:**

1. Verify album URL is accessible:
   - Open https://photos.app.goo.gl/W757cit6HfvKmCQh6 in browser
   - Should load without login
   - Check photos are visible

2. Check GitHub Action logs:
```bash
gh run list --workflow=sync-google-photos.yml --limit=5
gh run view <run-id> --log
```

3. Test sync script locally:
```bash
python3 scripts/sync_google_photos.py \
  --album-url "https://photos.app.goo.gl/W757cit6HfvKmCQh6"
```

4. Check for rate limiting:
   - Wait 24 hours before retrying
   - Reduce sync frequency in workflow
   - Use workflow_dispatch for manual triggers only

5. Update script if Google Photos HTML changed:
   - Review script parsing logic
   - Update selectors if needed
   - Test with new HTML structure

---

#### Issue: "Synced photos not being processed"

**Symptoms:**
- Photos appear in picdump
- Picdump workflow doesn't trigger
- No GitHub issues created

**Causes:**
- Workflow disabled
- Workflow path filter incorrect
- Commit message includes `[skip ci]`

**Solutions:**

1. Check workflow is enabled:
```bash
gh workflow list
```

2. Manually trigger workflow:
```bash
gh workflow run process-picdump-photos.yml
```

3. Check workflow file path trigger:
```yaml
on:
  push:
    paths:
      - 'picdump/**'
```

4. Remove `[skip ci]` from commit messages if not intended:
   - Sync workflow includes `[skip ci]` by design
   - Picdump workflow should still trigger on the commit

---

### Picdump Processing Issues

#### Issue: "Photos not being identified"

**Symptoms:**
- All photos go to `photos/unidentified/`
- GitHub Copilot issues show "cannot identify"
- Photos never filed correctly

**Causes:**
- Photos don't match OIO fleet
- Visual markers insufficient
- Copilot agent not working properly

**Solutions:**

1. Provide more context in photo filename:
```bash
# Instead of: IMG_1234.jpg
# Use: 2026-03-30_KCRX_Hudson_Novice_Win.jpg
```

2. Update car Visual Identification markers:
   - Add more distinctive visual features
   - Include color, body style, unique details
   - Reference example photos

3. Manually file photos and update markers:
   - Move photo to correct directory
   - Update car `Overview.md` with new visual details
   - Add photo to `PHOTO-INDEX.md`

4. Review Copilot issue for details:
   - Check what the agent tried
   - See what confused it
   - Add clarifying information

---

#### Issue: "Picdump workflow creates duplicate issues"

**Symptoms:**
- Multiple issues for same photos
- Workflow runs multiple times

**Causes:**
- Multiple commits to picdump quickly
- Workflow triggered on every commit
- Race condition

**Solutions:**

1. Batch commits:
```bash
# Add all photos at once
git add picdump/*.jpg
git commit -m "chore: add multiple photos"
```

2. Use workflow_dispatch for testing:
```bash
gh workflow run process-picdump-photos.yml
```

3. Close duplicate issues:
```bash
gh issue close <issue-number> --comment "Duplicate of #<other-issue>"
```

---

## Advanced Diagnostics

### Enable Debug Logging

#### PostBridge Client
```python
# In postbridge_client.py, add at the top:
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Caption Service
```python
# In caption_generation_service.py:
app = Flask(__name__)
app.debug = True
```

#### Slackbot
```python
# In slackbot_social_media.py:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Network Diagnostics

Test connectivity to external services:

```bash
# PostBridge API
curl -I https://api.postbridge.app/v1/accounts \
  -H "Authorization: Bearer ${POSTBRIDGE_API_KEY}"

# Paperclip API
curl -I ${PAPERCLIP_API_URL}/api/health \
  -H "Authorization: Bearer ${PAPERCLIP_API_KEY}"

# Google Photos
curl -I https://photos.app.goo.gl/W757cit6HfvKmCQh6
```

### Database/State Issues

Check Paperclip task states:

```bash
curl -s "${PAPERCLIP_API_URL}/api/companies/${PAPERCLIP_COMPANY_ID}/issues?assigneeAgentId=${AI_COPYWRITER_AGENT_ID}" \
  -H "Authorization: Bearer ${PAPERCLIP_API_KEY}" | jq '.[] | {id, title, status}'
```

### Clean Restart

Complete system restart:

```bash
# Kill all services
pkill -f caption_generation_service
pkill -f slackbot_social_media

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -name "*.pyc" -delete

# Restart services
python3 scripts/caption_generation_service.py &
sleep 5
python3 scripts/slackbot_social_media.py &
```

---

## Performance Issues

### Issue: "Slow caption generation"

**Solutions:**
- Check AI Copywriter agent budget usage
- Verify Paperclip server load
- Consider caching common captions
- Reduce caption_count from 3 to 2

### Issue: "Slack commands timing out"

**Solutions:**
- Increase Slack timeout (if possible)
- Optimize photo listing queries
- Add pagination for large photo sets
- Use threading for long operations

### Issue: "High memory usage"

**Solutions:**
- Limit photo batch sizes
- Clear Python cache regularly
- Monitor process memory:
```bash
ps aux | grep -E '(caption|slackbot)' | awk '{print $6, $11}'
```

---

## Getting Help

### Logs to Collect

When reporting issues, include:

1. **Service logs:**
```bash
python3 scripts/caption_generation_service.py > caption_service.log 2>&1
python3 scripts/slackbot_social_media.py > slackbot.log 2>&1
```

2. **GitHub Actions logs:**
```bash
gh run view <run-id> --log > workflow.log
```

3. **Environment info:**
```bash
python3 --version
pip list | grep -E '(slack|flask|requests)'
env | grep -E '(SLACK|POSTBRIDGE|PAPERCLIP)' > env_vars.txt
```

4. **System health check:** (see Quick Diagnostics section)

### Escalation

For unresolved issues:
1. Check system architecture documentation
2. Review GitHub Actions logs
3. Check Paperclip task history
4. Review integration testing guide
5. Create GitHub issue with logs attached

---

## Preventive Maintenance

### Daily Checks

- [ ] Verify GitHub Actions ran successfully
- [ ] Check picdump is empty (photos filed)
- [ ] Spot-check caption quality
- [ ] Monitor PostBridge API limits

### Weekly Checks

- [ ] Review Copilot issue resolution rate
- [ ] Check for unidentified photos backlog
- [ ] Verify all services running
- [ ] Review caption generation times
- [ ] Check Slack command usage

### Monthly Checks

- [ ] Rotate API keys if needed
- [ ] Update dependencies:
```bash
pip list --outdated
pip install --upgrade slack-bolt flask requests
```
- [ ] Review and archive old photos
- [ ] Check GitHub Actions usage/limits

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-30 | Initial troubleshooting guide |
