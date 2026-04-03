# Slack Integration Setup for OIO Photo Filing

The AI Photo Filing Agent can send notifications to Slack when uncertain about photo categorization. This guide covers how to configure the Slack integration.

## Option 1: Using Slack Webhook (Recommended for Simple Setup)

### Create an Incoming Webhook

1. Go to https://api.slack.com/apps
2. Create a new app or select an existing one
3. Under "Incoming Webhooks", click "Add New Webhook to Workspace"
4. Select the channel where notifications should be posted
5. Click "Allow"
6. Copy the webhook URL

### Configure Environment Variables

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

That's it! The photo filing agent will now send notifications to your channel.

## Option 2: Using Slack Bot Token (For File Uploads & Advanced Features)

### Create a Slack Bot

1. Go to https://api.slack.com/apps
2. Create a new app
3. Go to "OAuth & Permissions"
4. Under "Scopes", add these bot token scopes:
   - `chat:write` - Post messages
   - `files:write` - Upload files/images
5. Install the app to your workspace
6. Copy the "Bot User OAuth Token" (starts with `xoxb-`)
7. Add the bot to your notification channel

### Configure Environment Variables

```bash
export SLACK_BOT_TOKEN="xoxb-YOUR-TOKEN-HERE"
export SLACK_CHANNEL_ID="C1234567890"  # Channel ID (starts with C)
```

#### Finding Your Channel ID

1. Open Slack
2. Right-click on the channel → "View channel details"
3. Copy the Channel ID from the URL or details panel

## How It Works

### When Photos Are Uncertain

When the AI cannot confidently categorize a photo (confidence < 80%), it:

1. **Sends a Slack message** with:
   - Photo filename
   - AI analysis (driver, car, event, confidence)
   - Reasoning behind the analysis

2. **Optionally uploads the image** (bot token only):
   - Image is uploaded as a file to Slack
   - You can review the actual photo to decide where to file it

### Example Notifications

**Webhook mode:**
```
⚠️ Photo Filing Update

File: IMG_1234.jpg
Status: UNCERTAIN

Car: 1985 MR2 AW11
Driver: ian
Event: AUTOCROSS
Confidence: 72%

Reasoning: Color and wheels match, but image angle makes identification uncertain
```

**Bot token mode** (same as above, plus the image is uploaded as a file attachment)

## Troubleshooting

### "No Slack credentials configured"

**Problem:** Notifications aren't being sent
**Solution:** 
- Set either `SLACK_WEBHOOK_URL` OR `SLACK_BOT_TOKEN` + `SLACK_CHANNEL_ID`
- Verify the values are not empty: `echo $SLACK_WEBHOOK_URL`

### "Slack notification failed"

**Problem:** Notifications fail with an error
**Webhook mode:**
- Verify webhook URL is valid and not expired
- Test manually: `curl -X POST -H 'Content-Type: application/json' -d '{"text":"test"}' $SLACK_WEBHOOK_URL`

**Bot token mode:**
- Verify bot is in the channel: `@photobot` or check channel members
- Verify token is valid: `echo $SLACK_BOT_TOKEN`
- Check Slack API logs at https://api.slack.com/apps/YOUR-APP-ID/logs

### Images not uploading

**Problem:** Photos are posted as text only, not uploaded
**Solution:**
- This requires bot token mode (not webhook)
- Ensure `files:write` scope is added to bot token
- Reinstall the app after adding scopes

## Testing the Integration

### Quick Test with Webhook

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

# Send a test message
curl -X POST -H 'Content-Type: application/json' \
  -d '{"text":"Test notification from photo filing agent"}' \
  $SLACK_WEBHOOK_URL
```

### Full Test with Photo Agent

```bash
# Process one test photo
python scripts/ai_photo_filing_agent.py

# Check intake/photos/ - there should be test images
# You should receive a Slack notification within 5-10 seconds
```

## Production Deployment

### Using with CI/CD

If running photo filing as a scheduled job:

```yaml
# Example GitHub Actions workflow
- name: Sync Google Photos and File
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    python scripts/sync_google_photos.py
    python scripts/ai_photo_filing_agent.py
```

### Monitoring & Alerts

Set up Slack notification filters in your workspace:
1. Go to channel settings
2. Set up notification rules for messages containing "⚠️" (uncertain)
3. Get desktop alerts for hard-to-categorize photos

## Disabling Slack Notifications

If you want to disable notifications temporarily:

```bash
# Unset the environment variable
unset SLACK_WEBHOOK_URL
# or
unset SLACK_BOT_TOKEN
unset SLACK_CHANNEL_ID
```

The agent will log that Slack is not configured but continue processing photos.

## Reference

- Slack API Docs: https://api.slack.com/
- Incoming Webhooks: https://api.slack.com/messaging/webhooks
- Bot Token Scopes: https://api.slack.com/scopes
