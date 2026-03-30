# OIO Racing - Social Media System Architecture

**Version:** 1.0
**Last Updated:** 2026-03-30
**Status:** Ready for Production Testing

---

## Overview

The OIO Racing Social Media System is an end-to-end automated pipeline for managing social media content from photo capture to publication. It integrates Google Photos, AI-powered filing and caption generation, Slack-based mobile interface, and PostBridge for multi-platform publishing.

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        OIO Social Media Pipeline                         │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Google Photos│────▶│  Sync Workflow   │────▶│   picdump/      │
│   Album      │     │ (GitHub Action)  │     │  (Staging Dir)  │
└──────────────┘     └──────────────────┘     └────────┬────────┘
                                                        │
                     ┌──────────────────────────────────┘
                     │
                     ▼
              ┌──────────────────┐
              │ Picdump Process  │
              │ (GitHub Action)  │
              │ + AI Filing Agent│
              └────────┬─────────┘
                       │
       ┌───────────────┴───────────────┐
       │                               │
       ▼                               ▼
┌─────────────┐              ┌──────────────────┐
│  photos/    │              │  Notification    │
│  {Driver}/  │              │  (Unidentified   │
│  {Car}/     │              │   photos)        │
└──────┬──────┘              └──────────────────┘
       │
       │ Photo filed and logged
       │
       ▼
┌──────────────────────────────────────────────────────┐
│              User Posts from Track/Event             │
│              (Mobile-First Workflow)                 │
└──────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────┐
│   Slack Interface   │
│   (Mobile App)      │
├─────────────────────┤
│ Commands:           │
│  /photos list       │◀────┐
│  /caption <photo>   │     │
│  /post <caption>    │     │
│  /posts list        │     │
└────────┬────────────┘     │
         │                  │
         ├──────────────────┘
         │
         ├─────────────────▶ Caption Generation Service
         │                         │
         │                         ├─▶ AI Copywriter Agent
         │                         │   (Paperclip API)
         │                         │
         │                         └─▶ OIO Brain Context
         │                             • Brand voice
         │                             • Car details
         │                             • Race history
         │
         └─────────────────▶ PostBridge API
                                   │
                                   ├─▶ Instagram
                                   └─▶ Facebook
```

## Components

### 1. Google Photos Sync (Automated)

**File:** `.github/workflows/sync-google-photos.yml`
**Script:** `scripts/sync_google_photos.py`
**Schedule:** Every 5 hours (4-6 hour requirement)
**Source Album:** https://photos.app.goo.gl/W757cit6HfvKmCQh6

**Function:**
- Monitors shared Google Photos album for new photos
- Downloads new photos that haven't been processed
- Commits photos to `picdump/` directory
- Triggers picdump processing workflow

**Authentication:** Public album (no auth required)

**Commit Message Format:**
```
chore: sync {N} photo(s) from Google Photos [skip ci]

Synced from OIO Racing Google Photos album.
Photos will be processed by the picdump workflow.
```

### 2. Picdump Processing (Automated)

**File:** `.github/workflows/process-picdump-photos.yml`
**Trigger:** New files in `picdump/` directory
**Agent:** GitHub Copilot (via issue creation)

**Function:**
- Detects new images in picdump
- Creates GitHub issue assigned to @copilot
- Agent identifies car from visual cues
- Files photo to `photos/{Driver}/{Car}/`
- Updates photo logs and index
- Moves unidentified photos to open-loops

**Visual Identification:**
- Cross-references OIO fleet in `OIO Brain/03 - Cars/`
- Uses PHOTO-INDEX.md visual markers
- Applies automotive knowledge for make/model recognition

**Output:**
- Filed photos in driver/car directories
- Updated `photo-log.md` per car
- Updated `PHOTO-INDEX.md`
- Updated car `Overview.md` Visual Identification sections

### 3. Caption Generation Service

**File:** `scripts/caption_generation_service.py`
**Type:** Flask REST API
**Port:** 5000 (default)
**Dependencies:** Flask, requests, Paperclip SDK

**Endpoints:**

#### POST /generate-caption
Generate AI-powered captions using OIO Brain context.

**Request:**
```json
{
  "media_urls": ["photo_race_001.jpg", "photo_race_002.jpg"],
  "context": "KCRX Event 1, Hudson won Novice class",
  "caption_count": 3
}
```

**Response:**
```json
{
  "captions": [
    {
      "text": "Hudson won Novice at KCRX E1...",
      "hashtags": ["#ChurchOfCombustion", "#RallyCross", "#KCRX"],
      "char_count": 150
    }
  ],
  "brand_voice_applied": true,
  "context_sources": ["Voice-and-Tone.md", "Recent race results"]
}
```

**Process:**
1. Reads brand voice documents from OIO Brain
2. Creates Paperclip task for AI Copywriter agent
3. Polls for completion (up to 2 minutes)
4. Returns 3 caption variations with hashtags

**Context Sources:**
- `OIO Brain/01 - Brand/Voice-and-Tone.md`
- `OIO Brain/02 - Content/OIO-Brand-Voice-Guide.md`
- Car details from `OIO Brain/03 - Cars/`
- Recent social posts and race results

### 4. Slackbot Social Media Interface

**File:** `scripts/slackbot_social_media.py`
**Type:** Slack Bolt (Socket Mode)
**Dependencies:** slack-bolt, requests

**Commands:**

#### /photos list [filter]
Browse photos from picdump directory.

**Examples:**
- `/photos list` - List recent photos
- `/photos list 2026-03-30` - Filter by date
- `/photos list race` - Filter by keyword

#### /caption <photo-names> [context: ...]
Generate AI captions using Caption Generation Service.

**Examples:**
- `/caption photo_race_001.jpg`
- `/caption photo_trophy.jpg context: KCRX E1, Hudson won Novice`

**Response Time:** 30-120 seconds (AI generation)

#### /post <photo-names> "<caption>" [schedule: ...]
Create post via PostBridge (draft or scheduled).

**Examples:**
- `/post photo_race_001.jpg "Great race day! #ChurchOfCombustion"`
- `/post photo_trophy.jpg "First win!" schedule: 2026-04-01 09:00`

**Current Behavior:** Creates drafts; manual photo upload to PostBridge required

#### /posts list [status]
View scheduled and published posts from PostBridge.

**Examples:**
- `/posts list` - All recent posts
- `/posts list scheduled` - Scheduled only
- `/posts list posted` - Published only

**Configuration:**
- Slack Bot Token: `SLACK_BOT_TOKEN`
- Slack App Token: `SLACK_APP_TOKEN` (Socket Mode)
- PostBridge API Key: `POSTBRIDGE_API_KEY`
- Caption Service URL: `CAPTION_SERVICE_URL` (default: localhost:5000)

### 5. PostBridge API Client

**File:** `scripts/postbridge_client.py`
**Type:** Python library
**API Base:** https://api.postbridge.app/v1

**Features:**
- List connected social accounts (Instagram, Facebook)
- Create draft posts
- Schedule posts for future publishing
- Publish posts immediately
- List posts by status
- Error handling with retry logic
- Rate limit handling

**Authentication:** API key via `POSTBRIDGE_API_KEY` env var

**Example Usage:**
```python
from postbridge_client import PostBridgeClient

client = PostBridgeClient()

# List accounts
accounts = client.list_accounts()

# Create draft
draft = client.create_draft(
    caption="Great race day!",
    account_ids=[12345],
    media_urls=["https://example.com/photo.jpg"]
)

# Schedule post
scheduled = client.schedule_post(
    caption="Race day prep!",
    account_ids=[12345],
    scheduled_at="2026-04-01T09:00:00Z"
)
```

## Data Flow

### Photo Capture to Filing

1. **Camera** → Google Photos (auto-sync)
2. **Google Photos** → GitHub Action (every 5 hours)
3. **GitHub Action** → `picdump/` directory (git commit)
4. **Picdump Workflow** → GitHub issue for Copilot
5. **Copilot Agent** → Identifies car, files photo
6. **Filed Photo** → `photos/{Driver}/{Car}/` with metadata

### Mobile Posting Workflow

1. **User** → Slack `/photos list` (browse synced photos)
2. **User** → Slack `/caption <photo>` (generate captions)
3. **Caption Service** → AI Copywriter agent (Paperclip)
4. **AI Copywriter** → 3 caption variations returned
5. **User** → Selects caption, `/post <photo> "<caption>"`
6. **Slackbot** → PostBridge API (create draft)
7. **User** → PostBridge UI (manual photo upload, publish)

**Target Time:** Photo-to-post in < 5 minutes

### Future Flow (Automated Photo Upload)

1. **User** → Slack `/photos list`
2. **User** → Slack `/caption <photo>`
3. **User** → Slack `/post <photo> "<caption>"`
4. **Slackbot** → Upload photo to PostBridge media library
5. **Slackbot** → Create post with media attached
6. **PostBridge** → Publish to Instagram/Facebook

## Environment Variables

### Required for Full System

```bash
# Google Photos Sync
# (None required - uses public album URL)

# Caption Generation Service
PAPERCLIP_API_KEY="your-paperclip-api-key"
PAPERCLIP_API_URL="http://127.0.0.1:3100"
PAPERCLIP_COMPANY_ID="your-company-id"
AI_COPYWRITER_AGENT_ID="a2859bcb-cb20-4429-916b-65401f66d96a"

# Slackbot
SLACK_BOT_TOKEN="xoxb-your-bot-token"
SLACK_APP_TOKEN="xapp-your-app-token"
POSTBRIDGE_API_KEY="your-postbridge-api-key"
CAPTION_SERVICE_URL="http://localhost:5000"  # Optional, defaults to localhost

# PostBridge Client
POSTBRIDGE_API_KEY="your-postbridge-api-key"
```

## Dependencies

### Python Packages

```bash
# Core dependencies (requirements.txt)
requests>=2.31.0
anthropic>=0.39.0

# Slackbot dependencies
slack-bolt>=1.18.0

# Caption service dependencies
flask>=3.0.0

# Google Photos sync dependencies
beautifulsoup4>=4.12.0
pillow>=10.0.0
```

### External Services

1. **Google Photos** - Photo source (public album)
2. **GitHub Actions** - Automation workflows
3. **Slack Workspace** - Mobile interface
4. **PostBridge** - Social media publishing platform
5. **Paperclip** - AI agent orchestration
6. **GitHub Copilot** - Photo identification agent

## Security Considerations

### Secrets Management

- All API keys stored as GitHub repository secrets
- Never commit credentials to git
- Use environment variables for all sensitive data

### GitHub Secrets Required

```
POSTBRIDGE_API_KEY
SLACK_BOT_TOKEN
SLACK_APP_TOKEN
PAPERCLIP_API_KEY
PAPERCLIP_COMPANY_ID
```

### Access Control

- Google Photos album is public (read-only)
- GitHub Actions run with `contents: write` permission only
- Slack commands restricted to workspace members
- PostBridge API key has account-level access
- Paperclip API key scoped to AI Copywriter agent

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Photo sync frequency | 4-6 hours | 5 hours |
| Photo-to-post time | < 5 minutes | Manual steps required |
| Caption generation | < 2 minutes | 30-120 seconds |
| Photo filing | < 5 minutes | Depends on agent availability |

## Known Limitations

### Current Limitations

1. **Manual Photo Upload** - Photos must be manually uploaded to PostBridge UI
2. **No Scheduling UI** - Schedule syntax not implemented in Slackbot
3. **Single Album** - Only syncs from one Google Photos album
4. **No Video Support** - Photos only, no video handling
5. **Manual Approval** - All posts require manual review before publishing

### Future Enhancements

- Automatic photo upload to PostBridge
- Inline photo preview in Slack
- Multi-platform caption customization
- A/B testing for captions
- Post analytics viewing in Slack
- Video support
- Multi-album support

## Monitoring and Logs

### GitHub Actions

- **Sync Google Photos** - Check Actions tab for sync failures
- **Process Picdump Photos** - Check Copilot issue activity

### Service Logs

- **Caption Service** - Flask debug output (stdout)
- **Slackbot** - Socket mode connection logs (stdout)
- **PostBridge Client** - Requests/responses logged to stderr

### Health Checks

```bash
# Check caption service
curl http://localhost:5000/health

# Check Slackbot connection
# Look for "⚡️ Bolt app is running!" in logs

# Check PostBridge connectivity
python3 -c "from postbridge_client import PostBridgeClient; print(PostBridgeClient().list_accounts())"
```

## Support and Troubleshooting

See:
- [Slackbot Documentation](./slackbot-social-media.md)
- [Troubleshooting Guide](./social-media-troubleshooting.md) (to be created)
- [Deployment Guide](./social-media-deployment.md) (to be created)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-30 | Initial architecture documentation for Phase 5 testing |
