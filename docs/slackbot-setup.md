---
title: OIO Slackbot Setup Guide
type: operations
status: active
owner: Ian Jennings
updated: 2026-04-02
tags: [operations, slackbot, social-media, setup, slack]
source_of_truth: false
summary: Setup guide for the OIO Racing Slackbot — mobile-first Slack interface for managing social media posts, approvals, and publishing via PostBridge.
---

# OIO Slackbot Setup Guide

Mobile-first Slack interface for managing OIO Racing social media posts.

## Prerequisites

- Python 3.11+
- Slack workspace admin access
- PostBridge account (for Instagram/Facebook posting)
- Anthropic API key (for Claude integration)
- Railway.app account (for hosting)

## Local Setup

### 1. Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "OIO Slackbot"
4. Select your workspace
5. Click "Create App"

### 2. Configure Bot Permissions

In "Bot Token Scopes," add:
- `commands` - Register slash commands
- `chat:write` - Send messages
- `files:read` - Access files
- `files:write` - Upload files
- `reactions:read` - Read reactions
- `reactions:write` - Add reactions

### 3. Get Tokens

1. **Bot Token**: "OAuth & Permissions" → Copy "Bot User OAuth Token" (starts with `xoxb-`)
2. **App Token**: "App-Level Tokens" → Create token with `socket.connect:write` and `events:read` scopes (starts with `xapp-`)

### 4. Enable Socket Mode

1. Go to "Socket Mode"
2. Toggle "Enable Socket Mode" ON
3. Your tokens are ready to use

### 5. Register Slash Commands

In "Slash Commands," create:

- **`/photos list`** - Browse synced photos
  - Request URL: (leave blank for local, use Railway URL for production)
  - Short Description: "Browse unfiled photos"

- **`/caption`** - Generate captions
  - Request URL: (leave blank for local)
  - Short Description: "Generate AI captions for photos"

- **`/post`** - Create posts
  - Request URL: (leave blank for local)
  - Short Description: "Create and schedule posts"

- **`/posts list`** - View posts
  - Request URL: (leave blank for local)
  - Short Description: "View scheduled and published posts"

### 6. Local Environment

Copy `.env.example` to `.env` and fill in your tokens:

```bash
cp .env.example .env
# Edit .env with your tokens
```

### 7. Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the bot (uses Socket Mode, no webhook needed)
python scripts/slackbot_social_media.py
```

Bot will connect to Slack via Socket Mode and be ready for commands.

## Production Deployment (Railway)

### 1. Connect Repository

1. Go to https://railway.app
2. Create new project
3. Deploy from GitHub
4. Connect `oio-brain` repository
5. Select branch: `main`

### 2. Set Environment Variables

In Railway project settings, add:

```
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
POSTBRIDGE_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...
SLACK_CHANNEL_ID=C...
```

### 3. Deploy

Railway automatically builds and deploys from `Dockerfile`. To redeploy:
- Push to main branch, or
- Manually trigger redeploy in Railway dashboard

### 4. Update Slack Commands

Once deployed, update slash command URLs in Slack to use Railway URL:
- Request URL: `https://your-railway-domain.railway.app/slack/events`
- (Or use Socket Mode - no URL needed)

## Available Commands

### `/photos list [filter]`
Browse recently synced photos from intake/photos.

**Example:**
```
/photos list recent
/photos list goblin
```

### `/caption <photo-ids>`
Generate AI captions for photos using Claude.

**Example:**
```
/caption photo_123.jpg photo_456.jpg
```

### `/post <photos> "<caption>" [schedule: YYYY-MM-DD HH:MM]`
Create a draft post and optionally schedule it.

**Example:**
```
/post photo_123.jpg "Great race day! #ChurchOfCombustion"
/post photo_123.jpg "Goblin rebuild" schedule: 2026-04-15 14:00
```

### `/posts list [status]`
View all posts or filter by status.

**Example:**
```
/posts list
/posts list scheduled
/posts list published
```

## Troubleshooting

### "Connection refused" error
- Make sure `SLACK_APP_TOKEN` is set correctly
- Check Socket Mode is enabled in Slack app settings
- Verify bot token has correct scopes

### Commands not appearing in Slack
- Reload Slack client (`Cmd+R` on Mac, `Ctrl+R` on Windows)
- Verify slash commands are registered in Slack app settings
- Check bot has `commands` scope

### PostBridge errors
- Verify `POSTBRIDGE_API_KEY` is set
- Check PostBridge API is accessible
- Ensure API key has correct permissions

### Local vs Production
- **Local**: Uses Socket Mode (no public URL needed)
- **Production**: Can use Socket Mode or webhooks (Railway provides public URL)

## Architecture

```
Slack (commands, events)
    ↓
Slackbot (scripts/slackbot_social_media.py)
    ├→ Claude API (captions)
    ├→ PostBridge API (posting)
    └→ Local file system (photos)
```

## Files

- `scripts/slackbot_social_media.py` - Main bot implementation
- `scripts/postbridge_client.py` - PostBridge API client
- `scripts/caption_generation_service.py` - Caption generation
- `Procfile` - Railway process configuration
- `railway.json` - Railway deployment config
- `Dockerfile` - Container definition
- `.env` - Environment variables (create from `.env.example`)

## Next Steps

1. Complete local testing with test photos
2. Deploy to Railway
3. Monitor logs for errors
4. Gather feedback from Ian
5. Iterate on command UX

## Support

For issues:
1. Check logs: `railway logs` (production) or console output (local)
2. Verify tokens in Slack app settings
3. Check that commands are registered
4. Test with simple commands first (`/photos list`)

---

Last updated: 2026-04-01
