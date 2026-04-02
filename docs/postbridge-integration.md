---
title: PostBridge API Integration Guide
type: operations
status: active
owner: Ian Jennings
updated: 2026-04-02
tags: [operations, postbridge, social-media, api, integration]
source_of_truth: false
summary: Complete integration guide for PostBridge API — draft creation, scheduling, and publishing to Instagram and Facebook via the postbridge_client.py library.
---

# PostBridge API Integration Guide

Complete integration with PostBridge API for draft creation, scheduling, and publishing to Instagram and Facebook.

## Overview

The PostBridge client library (`scripts/postbridge_client.py`) provides a Python interface to the PostBridge API with:
- Full authentication and error handling
- Automatic retry logic for transient errors
- Rate limiting support (60s backoff)
- Support for all major platforms (Instagram, Facebook)
- Status tracking (draft → scheduled → published)

## Setup

### 1. Get PostBridge API Key

1. Go to https://postbridge.app/settings/api
2. Generate a new API key
3. Copy the key (starts with `pb_...`)

### 2. Set Environment Variable

```bash
export POSTBRIDGE_API_KEY="pb_your_key_here"
```

Or add to `.env` file:
```
POSTBRIDGE_API_KEY=pb_your_key_here
```

### 3. Connect Social Accounts

1. Go to https://postbridge.app/settings/accounts
2. Connect your Instagram account
3. Connect your Facebook account
4. Note the account IDs (needed for posting)

## Basic Usage

### Initialize Client

```python
from postbridge_client import PostBridgeClient, PostBridgeError

client = PostBridgeClient()  # Reads POSTBRIDGE_API_KEY from env
```

### List Connected Accounts

```python
accounts = client.list_accounts()
for account in accounts:
    print(f"{account['platform']}: {account['username']} (ID: {account['id']})")
```

### Create a Draft Post

```python
draft = client.create_draft(
    caption="Check out our latest race! 🏁 #OIORacing",
    account_ids=[12345],  # Your Instagram account ID
    media_urls=["https://example.com/photo.jpg"]
)
print(f"Draft created: {draft['id']}")
```

### Schedule a Post

```python
scheduled = client.schedule_post(
    caption="Race day is here! 🏁",
    account_ids=[12345],
    scheduled_at="2026-04-15T14:00:00Z"  # ISO 8601 format
)
print(f"Post scheduled for {scheduled['scheduled_at']}")
```

### Publish Immediately

```python
published = client.publish_post(
    caption="We won! 🏆",
    account_ids=[12345]
)
print(f"Published: {published['id']}")
```

### List Posts

```python
# Get all posts
posts = client.list_posts(limit=10)

# Get only scheduled posts
scheduled = client.list_posts(status="scheduled")

# Get posts by platform
instagram = client.list_posts(platform="instagram")
```

### Update a Draft

```python
updated = client.update_draft(
    draft_id="draft_123",
    caption="Updated caption",
    account_ids=[12345, 67890]  # Add Facebook account
)
```

### Get Post Details

```python
post = client.get_post("post_123")
print(f"Status: {post['status']}")
print(f"Posted: {post['posted_at']}")
```

### Delete a Post

```python
client.delete_post("draft_123")  # Can delete drafts
# Note: Cannot delete published posts, only drafts and scheduled
```

## Integration with Slackbot

The PostBridge client is integrated into the Slackbot via the `/post` command:

```python
# From slackbot_social_media.py
@app.command("/post")
def handle_post_command(ack, command, respond):
    # Parse command: /post <photos> "<caption>" [schedule: YYYY-MM-DD HH:MM]
    # Creates draft via PostBridge
    # Optionally schedules for future publish
```

**User Flow:**
1. Ian types `/post photo_123.jpg "Great race!"`
2. Slackbot creates draft via PostBridge
3. Ian receives confirmation with post ID
4. Can later schedule with `/post ... schedule: 2026-04-15 14:00`

## Error Handling

The client raises specific exceptions for different error types:

```python
from postbridge_client import (
    PostBridgeError,      # Base error
    PostBridgeAuthError,  # Auth/credentials issue
    PostBridgeRateLimitError  # Rate limit exceeded
)

try:
    draft = client.create_draft(...)
except PostBridgeAuthError as e:
    print(f"Auth failed: {e}")
except PostBridgeRateLimitError as e:
    print(f"Rate limited, retrying in 60s...")
except PostBridgeError as e:
    print(f"API error: {e}")
```

## API Endpoints

The client wraps these PostBridge API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/accounts` | GET | List connected accounts |
| `/posts` | POST | Create draft post |
| `/posts` | GET | List posts |
| `/posts/{id}` | GET | Get post details |
| `/posts/{id}` | PATCH | Update post (draft only) |
| `/posts/{id}/schedule` | POST | Schedule post publish |
| `/posts/{id}/publish` | POST | Publish immediately |
| `/posts/{id}` | DELETE | Delete post (draft only) |

## Status Tracking

Posts have these statuses:

- **draft** - Created but not scheduled or published
- **scheduled** - Scheduled for future publish
- **processing** - Currently being published
- **posted** - Successfully published
- **failed** - Publishing failed

## Retry Logic

The client automatically retries transient errors (5xx, timeouts, connection errors):

```python
# Configurable per client instance:
client = PostBridgeClient(
    retries=3,      # Number of retry attempts
    timeout=30      # Request timeout (seconds)
)
```

## Rate Limiting

PostBridge enforces rate limits (typically 100 requests/minute):

- The client detects rate limit responses (429 status)
- Automatically waits 60 seconds before retrying
- Logs the wait time

To handle rate limits in your code:

```python
from postbridge_client import PostBridgeRateLimitError

try:
    result = client.create_draft(...)
except PostBridgeRateLimitError:
    print("Rate limited - will retry in 60s")
    # Client handles retries automatically
```

## Testing

### Run CLI Example

```bash
python scripts/postbridge_client.py
```

This displays:
- Connected accounts
- Recent posts
- Account IDs (needed for API calls)

### Test with Real Credentials

```python
# test_postbridge.py
from postbridge_client import PostBridgeClient

client = PostBridgeClient()
accounts = client.list_accounts()
assert len(accounts) > 0, "No accounts connected"
print(f"✓ Connected to {len(accounts)} account(s)")

# Create draft
draft = client.create_draft(
    caption="Test post from OIO",
    account_ids=[accounts[0]['id']],
    media_urls=[]
)
print(f"✓ Draft created: {draft['id']}")

# Clean up
client.delete_post(draft['id'])
print("✓ Test complete")
```

## Integration with Photo Workflow

The full workflow:

1. **Photo Sync** (Phase 1) - New photos arrive in picdump/
2. **Photo Filing** (Phase 2) - AI agent auto-files photos
3. **Caption Generation** - Claude generates caption
4. **PostBridge Draft** (Phase 4) - Create draft with photo + caption
5. **Slack Review** (Phase 5) - Ian approves in Slackbot
6. **Schedule/Publish** - PostBridge handles publishing

## Troubleshooting

### "POSTBRIDGE_API_KEY not set"
```
Solution: Export environment variable or add to .env
export POSTBRIDGE_API_KEY="pb_..."
```

### "No connected social accounts found"
```
Solution: Connect accounts at https://postbridge.app/settings/accounts
```

### "Rate limit exceeded"
```
Solution: Client automatically retries after 60s. This is normal with heavy usage.
```

### "Media upload failed"
```
Solution: Ensure media URLs are publicly accessible and image format is supported.
Supported: JPG, PNG, HEIC, WebP
```

## Development Notes

- Client uses `requests` library (standard HTTP)
- Automatic retry with exponential backoff
- Session-based for connection reuse
- Comprehensive error handling
- Full type hints for IDE support

## Reference

- PostBridge API: https://postbridge.app/api/docs
- Settings: https://postbridge.app/settings/api
- Accounts: https://postbridge.app/settings/accounts
- Status Dashboard: https://postbridge.app/dashboard

---

Last updated: 2026-04-01
