# OIO Racing - Social Media System Deployment Guide

**Version:** 1.0
**Last Updated:** 2026-03-30
**Status:** Production Ready

---

## Overview

This guide covers the complete setup and deployment of the OIO Racing Social Media System, from initial configuration to production operation.

## Prerequisites

### Hardware/Infrastructure

- GitHub repository with Actions enabled
- Server or local machine for running services (Mac/Linux recommended)
- Stable internet connection
- 2GB+ available RAM
- 10GB+ available storage (for photo storage)

### Accounts Required

1. **GitHub Account** - Repository access, Actions, Copilot
2. **Slack Workspace** - Admin access to create apps
3. **PostBridge Account** - With connected Instagram/Facebook
4. **Paperclip Instance** - Running with AI Copywriter agent
5. **Google Photos** - Access to shared album

### Skills Needed

- Basic command line knowledge
- Git operations
- Python environment management
- API key management

---

## Phase 1: Repository Setup

### Step 1: Clone Repository

```bash
cd ~
git clone https://github.com/spacecowboyian/oio-brain.git
cd oio-brain
```

### Step 2: Verify File Structure

```bash
# Check critical files exist
ls -la scripts/postbridge_client.py
ls -la scripts/slackbot_social_media.py
ls -la scripts/caption_generation_service.py
ls -la scripts/sync_google_photos.py
ls -la .github/workflows/sync-google-photos.yml
ls -la .github/workflows/process-picdump-photos.yml
```

All files should exist. If missing, restore from feature branch:
```bash
git show aacb21e:scripts/postbridge_client.py > scripts/postbridge_client.py
git show 0ba60ff:scripts/sync_google_photos.py > scripts/sync_google_photos.py
git show 0ba60ff:.github/workflows/sync-google-photos.yml > .github/workflows/sync-google-photos.yml
```

### Step 3: Create Required Directories

```bash
mkdir -p picdump
mkdir -p photos/unidentified
mkdir -p docs
```

### Step 4: Install Python Dependencies

```bash
# Upgrade pip
python3 -m pip install --upgrade pip

# Install core dependencies
pip install -r requirements.txt

# Install additional dependencies for social media system
pip install slack-bolt flask beautifulsoup4 pillow
```

Verify installation:
```bash
python3 -c "import slack_bolt, flask, requests; print('✓ All dependencies installed')"
```

---

## Phase 2: External Services Setup

### Google Photos Setup

**Objective:** Configure photo source album

1. **Verify Album Access:**
   - Open https://photos.app.goo.gl/W757cit6HfvKmCQh6
   - Should load without login
   - Verify photos are visible

2. **Album URL:**
   - No changes needed if using default URL
   - To use different album, update `.github/workflows/sync-google-photos.yml`:
   ```yaml
   ALBUM_URL="${ALBUM_URL:-https://photos.app.goo.gl/YOUR-NEW-ALBUM-URL}"
   ```

3. **Test Sync Script:**
   ```bash
   python3 scripts/sync_google_photos.py \
     --album-url "https://photos.app.goo.gl/W757cit6HfvKmCQh6" \
     --dry-run
   ```

---

### Slack App Setup

**Objective:** Create and configure Slack bot

#### Step 1: Create Slack App

1. Go to https://api.slack.com/apps
2. Click **"Create New App"**
3. Choose **"From scratch"**
4. App Name: `OIO Social Media Bot`
5. Workspace: Your workspace
6. Click **"Create App"**

#### Step 2: Enable Socket Mode

1. In app settings → **"Socket Mode"**
2. Toggle **"Enable Socket Mode"** → ON
3. **Generate Token:**
   - Token Name: `socket-token`
   - Scopes: `connections:write`
   - Click **"Generate"**
   - **SAVE THIS TOKEN** (starts with `xapp-`)

#### Step 3: Configure OAuth Scopes

1. In app settings → **"OAuth & Permissions"**
2. Scroll to **"Bot Token Scopes"**
3. Add these scopes:
   - `commands` - Required for slash commands
   - `chat:write` - Required for sending messages
4. Click **"Install to Workspace"**
5. Authorize the app
6. **SAVE THE BOT TOKEN** (starts with `xoxb-`)

#### Step 4: Create Slash Commands

In app settings → **"Slash Commands"** → **"Create New Command"**

Create these 4 commands:

**Command 1: /photos**
- Command: `/photos`
- Request URL: (leave blank - Socket Mode handles this)
- Short Description: `Browse recently synced photos`
- Usage Hint: `list [filter]`

**Command 2: /caption**
- Command: `/caption`
- Request URL: (leave blank)
- Short Description: `Generate AI captions for photos`
- Usage Hint: `<photo-names> [context: ...]`

**Command 3: /post**
- Command: `/post`
- Request URL: (leave blank)
- Short Description: `Create and schedule social media post`
- Usage Hint: `<photo-names> "<caption>" [schedule: ...]`

**Command 4: /posts**
- Command: `/posts`
- Request URL: (leave blank)
- Short Description: `List scheduled and published posts`
- Usage Hint: `list [status]`

#### Step 5: Verify Installation

1. Go to your Slack workspace
2. Try typing `/photos` in any channel
3. Should show autocomplete suggestion
4. Don't run yet (bot not started)

---

### PostBridge Setup

**Objective:** Configure social media publishing platform

#### Step 1: Create PostBridge Account

1. Go to https://postbridge.app
2. Sign up for account
3. Verify email

#### Step 2: Connect Social Accounts

1. Log in to PostBridge
2. Go to **Settings** → **Accounts**
3. Click **"Connect Account"**
4. Connect Instagram:
   - Choose Instagram
   - Log in with Instagram credentials
   - Grant permissions
   - Verify connection shows "Connected"
5. Connect Facebook (optional):
   - Choose Facebook
   - Log in and authorize
   - Select page to connect

#### Step 3: Generate API Key

1. In PostBridge → **Settings** → **API**
2. Click **"Generate API Key"**
3. **SAVE THIS KEY** securely
4. Test the key:
```bash
export POSTBRIDGE_API_KEY="your-key-here"
curl https://api.postbridge.app/v1/accounts \
  -H "Authorization: Bearer ${POSTBRIDGE_API_KEY}"
```

Should return list of connected accounts.

---

### Paperclip Setup

**Objective:** Configure AI agent orchestration

#### Step 1: Verify Paperclip Running

```bash
curl ${PAPERCLIP_API_URL:-http://127.0.0.1:3100}/api/health
```

Should return healthy status.

#### Step 2: Verify AI Copywriter Agent

```bash
export PAPERCLIP_API_KEY="your-paperclip-api-key"
export PAPERCLIP_API_URL="http://127.0.0.1:3100"
export PAPERCLIP_COMPANY_ID="your-company-id"

curl -s "${PAPERCLIP_API_URL}/api/agents/a2859bcb-cb20-4429-916b-65401f66d96a" \
  -H "Authorization: Bearer ${PAPERCLIP_API_KEY}" | jq '.status'
```

Should return `"running"`.

#### Step 3: Test Agent Assignment

Create a test task to verify agent responds:
```bash
curl -X POST "${PAPERCLIP_API_URL}/api/companies/${PAPERCLIP_COMPANY_ID}/issues" \
  -H "Authorization: Bearer ${PAPERCLIP_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test caption generation",
    "description": "Test task for AI Copywriter",
    "assigneeAgentId": "a2859bcb-cb20-4429-916b-65401f66d96a",
    "status": "todo"
  }'
```

Check that agent picks up and completes the task.

---

## Phase 3: Environment Configuration

### Step 1: Create Environment File

Create `.env` file (never commit this):

```bash
cat > .env << 'EOF'
# Slack Configuration
export SLACK_BOT_TOKEN="xoxb-your-bot-token-here"
export SLACK_APP_TOKEN="xapp-your-app-token-here"

# PostBridge Configuration
export POSTBRIDGE_API_KEY="your-postbridge-api-key-here"

# Paperclip Configuration
export PAPERCLIP_API_KEY="your-paperclip-api-key-here"
export PAPERCLIP_API_URL="http://127.0.0.1:3100"
export PAPERCLIP_COMPANY_ID="your-company-id-here"

# Service Configuration (optional)
export CAPTION_SERVICE_URL="http://localhost:5000"
export CAPTION_SERVICE_PORT="5000"
EOF

# Set permissions
chmod 600 .env
```

### Step 2: Add to .gitignore

```bash
echo ".env" >> .gitignore
```

### Step 3: Load Environment

```bash
source .env
```

Add to your shell profile for persistence:
```bash
echo "source ~/oio-brain/.env" >> ~/.zshrc  # or ~/.bashrc
```

### Step 4: Verify Variables

```bash
env | grep -E '(SLACK|POSTBRIDGE|PAPERCLIP)'
```

Should show all required variables.

---

## Phase 4: GitHub Actions Setup

### Step 1: Configure Repository Secrets

1. Go to GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `POSTBRIDGE_API_KEY` | Your PostBridge API key | For post creation |
| `SLACK_BOT_TOKEN` | Your Slack bot token (xoxb-...) | For Slack integration (if needed) |
| `PAPERCLIP_API_KEY` | Your Paperclip API key | For AI agents |
| `PAPERCLIP_API_URL` | http://127.0.0.1:3100 | Paperclip server URL |
| `PAPERCLIP_COMPANY_ID` | Your company ID | Paperclip company context |

### Step 2: Enable GitHub Actions

1. Go to repository → **Actions** tab
2. If prompted, click **"I understand my workflows, go ahead and enable them"**

### Step 3: Verify Workflows

```bash
gh workflow list
```

Should show:
- `Sync Google Photos`
- `Process Picdump Photos`
- Other existing workflows

### Step 4: Test Google Photos Sync

Manually trigger the workflow:
```bash
gh workflow run sync-google-photos.yml
```

Monitor:
```bash
gh run watch
```

Should complete successfully and commit photos to picdump.

---

## Phase 5: Service Deployment

### Option A: Development (Local/Manual)

#### Start Caption Generation Service

```bash
cd ~/oio-brain
source .env
python3 scripts/caption_generation_service.py > logs/caption_service.log 2>&1 &
echo $! > logs/caption_service.pid
```

Verify:
```bash
curl http://localhost:5000/health
```

#### Start Slackbot

```bash
python3 scripts/slackbot_social_media.py > logs/slackbot.log 2>&1 &
echo $! > logs/slackbot.pid
```

Look for: `⚡️ Bolt app is running!` in logs.

---

### Option B: Production (systemd services)

#### Create Caption Service Unit

```bash
sudo tee /etc/systemd/system/oio-caption-service.service << 'EOF'
[Unit]
Description=OIO Racing Caption Generation Service
After=network.target

[Service]
Type=simple
User=ian
WorkingDirectory=/Users/ian/oio-brain
EnvironmentFile=/Users/ian/oio-brain/.env
ExecStart=/usr/bin/python3 /Users/ian/oio-brain/scripts/caption_generation_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

#### Create Slackbot Service Unit

```bash
sudo tee /etc/systemd/system/oio-slackbot.service << 'EOF'
[Unit]
Description=OIO Racing Slackbot Social Media Interface
After=network.target oio-caption-service.service
Requires=oio-caption-service.service

[Service]
Type=simple
User=ian
WorkingDirectory=/Users/ian/oio-brain
EnvironmentFile=/Users/ian/oio-brain/.env
ExecStart=/usr/bin/python3 /Users/ian/oio-brain/scripts/slackbot_social_media.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

#### Enable and Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable oio-caption-service
sudo systemctl enable oio-slackbot
sudo systemctl start oio-caption-service
sudo systemctl start oio-slackbot
```

#### Verify Services

```bash
sudo systemctl status oio-caption-service
sudo systemctl status oio-slackbot
```

#### View Logs

```bash
sudo journalctl -u oio-caption-service -f
sudo journalctl -u oio-slackbot -f
```

---

## Phase 6: Verification

### Test Complete Pipeline

#### 1. Test Photo Listing

In Slack:
```
/photos list
```

Expected: List of photos from picdump

#### 2. Test Caption Generation

```
/caption test_photo.jpg context: test caption generation
```

Expected: 3 caption variations within 2 minutes

#### 3. Test Post Creation

```
/post test_photo.jpg "Test post caption #ChurchOfCombustion"
```

Expected: Draft created in PostBridge

#### 4. Verify in PostBridge

- Log in to https://postbridge.app
- Go to Drafts
- See your test post

#### 5. Test Google Photos Sync

- Add photo to Google Photos album
- Wait up to 5 hours, or trigger manually:
```bash
gh workflow run sync-google-photos.yml
```
- Verify photo appears in picdump/

#### 6. Test Picdump Processing

- Add test photo to picdump/
- Commit and push
- Verify GitHub issue created
- Verify Copilot processes and files photo

---

## Phase 7: Monitoring Setup

### Log Rotation

```bash
# Create logrotate config
sudo tee /etc/logrotate.d/oio-social << 'EOF'
/Users/ian/oio-brain/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

### Health Check Script

Create `scripts/health_check.sh`:

```bash
#!/bin/bash
set -e

# Check caption service
curl -f http://localhost:5000/health || exit 1

# Check PostBridge
curl -f https://api.postbridge.app/v1/accounts \
  -H "Authorization: Bearer ${POSTBRIDGE_API_KEY}" || exit 1

# Check Paperclip
curl -f "${PAPERCLIP_API_URL}/api/health" || exit 1

echo "✓ All services healthy"
```

### Cron Job for Health Checks

```bash
crontab -e
```

Add:
```
*/15 * * * * /Users/ian/oio-brain/scripts/health_check.sh || echo "Health check failed" | mail -s "OIO Social Media Alert" your@email.com
```

---

## Phase 8: Documentation

### Create Operations Runbook

Document for team:
- Service start/stop procedures
- Where to find logs
- Common issues and solutions
- Emergency contacts
- Escalation procedures

### Update README

Add section about social media system:
- Link to architecture docs
- Link to troubleshooting guide
- Link to deployment guide
- Quick start commands

---

## Maintenance

### Daily Tasks

- [ ] Check GitHub Actions ran successfully
- [ ] Verify picdump is empty (processed)
- [ ] Monitor service logs for errors

### Weekly Tasks

- [ ] Review caption quality
- [ ] Check PostBridge draft queue
- [ ] Verify Google Photos sync working
- [ ] Review unidentified photos

### Monthly Tasks

- [ ] Update dependencies
- [ ] Rotate API keys (if policy requires)
- [ ] Review and archive old photos
- [ ] Check service resource usage

---

## Rollback Procedure

If issues occur after deployment:

### Stop Services

```bash
# systemd
sudo systemctl stop oio-slackbot
sudo systemctl stop oio-caption-service

# or manual
kill $(cat logs/slackbot.pid)
kill $(cat logs/caption_service.pid)
```

### Restore Previous Version

```bash
git log --oneline -10
git checkout <previous-commit>
```

### Restart Services

```bash
sudo systemctl start oio-caption-service
sudo systemctl start oio-slackbot
```

---

## Security Checklist

- [ ] All API keys in environment variables, not code
- [ ] `.env` file has 600 permissions
- [ ] `.env` in .gitignore
- [ ] GitHub secrets configured correctly
- [ ] Service users have minimal required permissions
- [ ] Logs don't contain sensitive data
- [ ] API keys rotated regularly
- [ ] HTTPS used for all external API calls

---

## Support

For deployment issues:
1. Check [Troubleshooting Guide](./social-media-troubleshooting.md)
2. Review [Architecture Documentation](./social-media-system-architecture.md)
3. Check service logs
4. Run health check script
5. Create GitHub issue with logs

---

## Appendix

### Service Management Commands

```bash
# Start services
sudo systemctl start oio-caption-service
sudo systemctl start oio-slackbot

# Stop services
sudo systemctl stop oio-slackbot
sudo systemctl stop oio-caption-service

# Restart services
sudo systemctl restart oio-caption-service
sudo systemctl restart oio-slackbot

# View status
sudo systemctl status oio-caption-service
sudo systemctl status oio-slackbot

# View logs
sudo journalctl -u oio-caption-service -f
sudo journalctl -u oio-slackbot -f
```

### Quick Reference URLs

- PostBridge: https://postbridge.app
- PostBridge API: https://api.postbridge.app/v1
- Slack Apps: https://api.slack.com/apps
- Google Photos Album: https://photos.app.goo.gl/W757cit6HfvKmCQh6
- GitHub Actions: https://github.com/spacecowboyian/oio-brain/actions

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-30 | Initial deployment guide |
