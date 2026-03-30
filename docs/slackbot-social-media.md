# OIO Racing - Slackbot Social Media Interface

## Overview

The Slackbot Social Media Interface provides mobile-first social media management through Slack commands. It integrates with PostBridge for cross-platform posting, the Caption Generation Service for AI-powered captions, and local photo management.

## Features

1. **Photo Browsing** - List and filter recently synced photos from Google Photos
2. **AI Caption Generation** - Generate brand-voice captions using AI Copywriter
3. **Post Scheduling** - Schedule or publish posts to Instagram/Facebook
4. **Post Management** - View and manage scheduled posts

## Architecture

```
┌─────────────────┐
│  User in Slack  │
└────────┬────────┘
         │ Slash commands
         ▼
┌──────────────────────────────────┐
│  Slackbot Social Media Interface │
│  (Socket Mode)                   │
├──────────────────────────────────┤
│  Command Handlers:               │
│  • /photos - List photos         │
│  • /caption - Generate captions  │
│  • /post - Create posts          │
│  • /posts - List posts           │
└────┬─────────────────────────┬───┘
     │                         │
     │                         │ PostBridge API
     │ Caption Service         ▼
     ▼                    ┌─────────────────┐
┌─────────────────────┐  │  PostBridge     │
│  Caption Generation │  │  • Instagram    │
│  Service (Flask)    │  │  • Facebook     │
│  • AI Copywriter    │  │  • Scheduling   │
│  • Brand Voice      │  │  • Media        │
│  • OIO Brain Context│  └─────────────────┘
└─────────────────────┘
```

## Installation

### Prerequisites

1. **Python Dependencies:**
   ```bash
   pip install slack-bolt requests flask
   ```

2. **Slack App Setup:**
   - Create a Slack app at https://api.slack.com/apps
   - Enable Socket Mode
   - Add Bot Token Scopes: `commands`, `chat:write`
   - Create slash commands: `/photos`, `/caption`, `/post`, `/posts`
   - Install app to workspace

3. **Required Services:**
   - Caption Generation Service running on http://localhost:5000
   - PostBridge account with connected Instagram/Facebook accounts
   - Google Photos sync workflow (for photo uploads)

### Environment Variables

```bash
# Slack Configuration
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_APP_TOKEN="xapp-your-app-token"

# PostBridge Configuration
export POSTBRIDGE_API_KEY="your-postbridge-api-key"

# Caption Service (optional, defaults to localhost:5000)
export CAPTION_SERVICE_URL="http://localhost:5000"
```

### Running the Slackbot

```bash
# Start caption generation service first
python scripts/caption_generation_service.py &

# Start the Slackbot
python scripts/slackbot_social_media.py
```

The bot will connect to Slack via Socket Mode and listen for commands.

## Commands

### `/photos list [filter]`

Browse photos from the picdump directory (synced from Google Photos).

**Usage:**
```
/photos list              # List recent photos
/photos list 2026-03-30   # Filter by date
/photos list race         # Filter by keyword in filename
```

**Response:**
```
Found 5 photo(s):

1. `photo_race_001.jpg` — 2,456 KB — 2026-03-30 14:23
2. `photo_race_002.jpg` — 1,890 KB — 2026-03-30 14:25
3. `photo_trophy.jpg` — 3,120 KB — 2026-03-30 15:01
4. `photo_car_123.jpg` — 2,678 KB — 2026-03-29 18:45
5. `photo_pits.jpg` — 1,234 KB — 2026-03-29 17:30

Use `/caption <photo-names>` to generate captions
```

### `/caption <photo-names> [context: ...]`

Generate AI-powered captions for photos using the Caption Generation Service.

**Usage:**
```
/caption photo_race_001.jpg photo_race_002.jpg

/caption photo_trophy.jpg context: KCRX E1, Hudson won Novice class
```

**Response:**
```
Generated 3 caption option(s):

Option 1 (125 chars):
Hudson won Novice at KCRX E1. First trophy of the season. The congregation is proud. #ChurchOfCombustion #RallyCross #KCRX
Hashtags: #ChurchOfCombustion, #RallyCross, #KCRX

Option 2 (150 chars):
The Goblin didn't survive E1. Bearing failure, cyl 4 at 35 PSI. But Hudson grabbed his first Novice win. Season's not over. #GrassrootsRacing #KCRX
Hashtags: #GrassrootsRacing, #KCRX

Option 3 (134 chars):
Sunday service at Ray Rocks. Hudson's first trophy. The Goblin's final sermon before the bearing failure. Amen. #ChurchOfCombustion
Hashtags: #ChurchOfCombustion

Use `/post <photo-names> <caption>` to schedule or publish
```

**Notes:**
- Caption generation takes 30-120 seconds
- Uses OIO Brain brand voice guidelines
- Includes context from car details and race history
- Returns 3 caption variations by default

### `/post <photo-names> "<caption>" [schedule: ...]`

Create a post via PostBridge (draft, scheduled, or immediate publish).

**Usage:**
```
# Create draft post (immediate)
/post photo_race_001.jpg "Hudson won Novice at KCRX E1! #ChurchOfCombustion"

# Schedule for future (not yet implemented)
/post photo_trophy.jpg "First trophy!" schedule: 2026-04-01 09:00
```

**Response:**
```
✓ Post created as draft (ID: abc123-def456-ghi789)
Caption: Hudson won Novice at KCRX E1! #ChurchOfCombustion
Note: Photos need to be uploaded to PostBridge manually for now.
```

**Current Limitations:**
- Creates posts as drafts in PostBridge
- Photos must be uploaded to PostBridge media library manually
- Scheduling syntax not yet implemented

**Future Enhancements:**
- Automatic photo upload to PostBridge
- Proper scheduling with datetime parsing
- Preview before publishing
- Multi-platform caption customization

### `/posts list [status]`

View scheduled and published posts from PostBridge.

**Usage:**
```
/posts list              # List all recent posts
/posts list scheduled    # Show only scheduled posts
/posts list posted       # Show only published posts
```

**Response:**
```
Found 3 post(s):

1. SCHEDULED [DRAFT] — Scheduled: 2026-04-01T09:00:00Z
   Hudson won Novice at KCRX E1! #ChurchOfCombustion...
   ID: abc123-def456-ghi789

2. POSTED
   Great race day at Ray Rocks! The congregation is strong...
   ID: def456-ghi789-jkl012

3. SCHEDULED
   Track day prep starts now. Getting Fitty Cent ready...
   ID: ghi789-jkl012-mno345
```

## Integration with Caption Generation Service

The Slackbot calls the Caption Generation Service API to generate captions:

```python
POST http://localhost:5000/generate-caption
{
  "media_urls": ["photo_race_001.jpg", "photo_race_002.jpg"],
  "context": "KCRX E1, Hudson won Novice class",
  "caption_count": 3
}
```

The service:
1. Reads OIO Brain brand voice guidelines
2. Queries OIO Brain for relevant context (car details, race history)
3. Creates a Paperclip task for the AI Copywriter agent
4. Polls for caption generation completion (up to 2 minutes)
5. Returns 3 caption variations with hashtags

## Integration with PostBridge

The Slackbot uses the PostBridge client library to:
- List connected social accounts (Instagram, Facebook)
- Create draft posts
- Schedule posts for future publishing
- List scheduled and published posts

**Current Flow:**
1. User requests post creation via `/post`
2. Slackbot creates draft in PostBridge with caption
3. User manually uploads photos to PostBridge UI
4. User publishes draft from PostBridge

**Future Flow:**
1. User requests post creation via `/post`
2. Slackbot uploads photos to PostBridge media library
3. Slackbot creates post with media attached
4. Post publishes immediately or at scheduled time

## Workflow Example

### Complete Mobile Workflow

```
1. Take photos at track (phone camera)
   ↓
2. Google Photos auto-syncs photos
   ↓
3. GitHub Action syncs photos to picdump/
   ↓
4. In Slack: /photos list recent
   → See newly synced photos
   ↓
5. In Slack: /caption photo_race_001.jpg context: KCRX E1 results
   → Get 3 AI-generated caption options
   ↓
6. In Slack: /post photo_race_001.jpg "Selected caption text"
   → Create PostBridge draft
   ↓
7. Manually upload photo to PostBridge (for now)
   ↓
8. Publish from PostBridge
```

This entire workflow can be done from a phone, making it ideal for on-the-go posting from race events.

## Configuration

### Slack App Configuration

**Bot Token Scopes:**
- `commands` - Required for slash commands
- `chat:write` - Required for sending messages

**Slash Commands:**
Create these commands in your Slack app:
- `/photos` - "Browse recently synced photos"
- `/caption` - "Generate AI captions for photos"
- `/post` - "Create and schedule social media post"
- `/posts` - "List scheduled and published posts"

**Socket Mode:**
Enable Socket Mode and generate an App-Level Token with `connections:write` scope.

### PostBridge Configuration

1. Connect Instagram and Facebook accounts at https://postbridge.app/settings/accounts
2. Generate API key at https://postbridge.app/settings/api
3. Set `POSTBRIDGE_API_KEY` environment variable

### Caption Service Configuration

The Caption Generation Service must be running and accessible:
- Default URL: http://localhost:5000
- Override with `CAPTION_SERVICE_URL` environment variable
- Requires Paperclip API access for AI Copywriter agent

## Troubleshooting

### Slackbot won't start

**Error:** `SLACK_BOT_TOKEN not set`

**Solution:**
```bash
export SLACK_BOT_TOKEN="xoxb-your-token"
export SLACK_APP_TOKEN="xapp-your-token"
```

### Commands not responding

**Issue:** Slash commands return no response

**Causes:**
1. Slackbot not running or crashed
2. Socket Mode not enabled
3. Incorrect token scopes

**Solution:**
- Check Slackbot logs for errors
- Verify Socket Mode is enabled in Slack app settings
- Verify bot token has `commands` and `chat:write` scopes

### Caption generation times out

**Error:** `Caption generation failed: timeout`

**Causes:**
1. Caption Generation Service not running
2. AI Copywriter agent busy or offline
3. Paperclip API unreachable

**Solution:**
```bash
# Check if caption service is running
curl http://localhost:5000/health

# Start caption service if needed
python scripts/caption_generation_service.py

# Check AI Copywriter agent status in Paperclip
```

### PostBridge errors

**Error:** `No connected social accounts found`

**Solution:**
- Log in to https://postbridge.app/settings/accounts
- Connect Instagram and/or Facebook accounts
- Verify accounts are active and authorized

**Error:** `POSTBRIDGE_API_KEY not set`

**Solution:**
```bash
export POSTBRIDGE_API_KEY="your-api-key"
```

### Photos not found

**Issue:** `/photos list` returns "No photos found"

**Causes:**
1. picdump/ directory is empty
2. Google Photos sync hasn't run
3. Photos are hidden (start with `.`)

**Solution:**
- Manually add photos to `picdump/` directory
- Run Google Photos sync: `python scripts/sync_google_photos.py --album-url <url>`
- Check for hidden files: `ls -la picdump/`

## Future Enhancements

### High Priority

- [ ] Automatic photo upload to PostBridge media library
- [ ] Proper datetime parsing for scheduling
- [ ] Caption editing before publishing
- [ ] Photo preview in Slack (inline images)

### Medium Priority

- [ ] Multi-select photos with checkboxes (Slack Block Kit)
- [ ] Platform-specific caption customization (Instagram vs Facebook)
- [ ] Post analytics viewing in Slack
- [ ] Draft management (edit, delete drafts)

### Low Priority

- [ ] Batch operations (post multiple at once)
- [ ] Caption history and favorites
- [ ] A/B testing for captions
- [ ] Integration with Google Photos API (direct listing)
- [ ] Slack interactive buttons for caption selection

## Related Documentation

- [Caption Generation Service](./caption-generation-service.md)
- [PostBridge Client Library](../scripts/postbridge_client.py)
- [Google Photos Sync Workflow](../.github/workflows/sync-google-photos.yml)
- [OIO Brand Voice Guide](../OIO%20Brain/02%20-%20Content/OIO-Brand-Voice-Guide.md)

## Support

For issues or questions:
1. Check Slackbot logs for errors
2. Verify all environment variables are set
3. Test Caption Generation Service independently
4. Test PostBridge API with client library directly
5. Review Paperclip task logs for AI Copywriter agent
