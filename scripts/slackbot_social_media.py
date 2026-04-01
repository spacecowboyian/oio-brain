#!/usr/bin/env python3
"""
OIO Racing - Slackbot Social Media Interface

Mobile-first Slack interface for managing social media posts.

Commands:
    /photos list [filter]    - Browse recently synced photos
    /caption <photo-ids>     - Generate AI captions for photos
    /post <photo-ids> <caption> [schedule] - Schedule or publish post
    /posts list              - View scheduled and published posts
    /feedback <type> <id> [msg] - Provide caption feedback (positive/negative/revise)

Environment Variables:
    SLACK_BOT_TOKEN: Slack bot token (xoxb-...)
    SLACK_APP_TOKEN: Slack app token for Socket Mode (xapp-...)
    POSTBRIDGE_API_KEY: PostBridge API key
    CAPTION_SERVICE_URL: Caption service URL (default: http://localhost:5000)

Usage:
    # Start the Slackbot
    python scripts/slackbot_social_media.py

    # In Slack, use the commands:
    /photos list recent
    /caption photo_123.jpg photo_456.jpg
    /post photo_123.jpg "Great race day! #ChurchOfCombustion"
    /posts list
"""

import os
import sys
import json
import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from slack_bolt import App
    from slack_bolt.adapter.socket_mode import SocketModeHandler
except ImportError:
    print("Error: slack-bolt is not installed.")
    print("Run: pip install slack-bolt")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Error: requests is not installed.")
    print("Run: pip install requests")
    sys.exit(1)

# Import PostBridge client and metrics logger
sys.path.append(str(Path(__file__).parent))
from postbridge_client import PostBridgeClient, PostBridgeError
from caption_metrics_logger import CaptionMetricsLogger

# Configuration
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "")
POSTBRIDGE_API_KEY = os.environ.get("POSTBRIDGE_API_KEY", "")
CAPTION_SERVICE_URL = os.environ.get("CAPTION_SERVICE_URL", "http://localhost:5000")

# Paths
PICDUMP_DIR = Path(__file__).parent.parent / "picdump"

# Initialize Slack app
app = App(token=SLACK_BOT_TOKEN)

# Initialize metrics logger
metrics_logger = CaptionMetricsLogger()


# ---------------------------------------------------------------------------
# Photo Management
# ---------------------------------------------------------------------------

def list_local_photos(filter_term: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """
    List photos from picdump directory.

    Args:
        filter_term: Optional filter (e.g., "recent", date, or keyword)
        limit: Maximum number of photos to return

    Returns:
        List of photo dictionaries with name, path, size, and modified date
    """
    if not PICDUMP_DIR.exists():
        return []

    photos = []

    # Get all image files from picdump
    image_extensions = {".jpg", ".jpeg", ".png", ".heic", ".webp"}
    for photo_path in PICDUMP_DIR.iterdir():
        if photo_path.is_file() and photo_path.suffix.lower() in image_extensions:
            # Skip hidden files
            if photo_path.name.startswith("."):
                continue

            stat = photo_path.stat()
            photos.append({
                "name": photo_path.name,
                "path": str(photo_path),
                "size_kb": stat.st_size // 1024,
                "modified": datetime.fromtimestamp(stat.st_mtime)
            })

    # Sort by modified date (most recent first)
    photos.sort(key=lambda p: p["modified"], reverse=True)

    # Apply filter
    if filter_term and filter_term.lower() != "recent":
        filtered = []
        for photo in photos:
            # Match against filename or date
            if filter_term.lower() in photo["name"].lower():
                filtered.append(photo)
            elif filter_term in photo["modified"].strftime("%Y-%m-%d"):
                filtered.append(photo)
        photos = filtered

    return photos[:limit]


def format_photos_message(photos: List[Dict[str, Any]]) -> str:
    """
    Format a list of photos into a Slack message.

    Args:
        photos: List of photo dictionaries

    Returns:
        Formatted Slack message string
    """
    if not photos:
        return "No photos found. Upload photos to the `picdump/` directory or sync from Google Photos."

    lines = [f"*Found {len(photos)} photo(s):*\n"]

    for i, photo in enumerate(photos, 1):
        modified_str = photo["modified"].strftime("%Y-%m-%d %H:%M")
        size_str = f"{photo['size_kb']} KB"
        lines.append(f"{i}. `{photo['name']}` — {size_str} — {modified_str}")

    lines.append(f"\n_Use `/caption <photo-names>` to generate captions_")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Caption Generation
# ---------------------------------------------------------------------------

def generate_captions(
    photo_names: List[str],
    context: Optional[str] = None,
    caption_count: int = 3
) -> Dict[str, Any]:
    """
    Generate captions for photos using the caption generation service.

    Args:
        photo_names: List of photo filenames
        context: Optional context about the photos
        caption_count: Number of caption variations to generate

    Returns:
        Caption generation result dictionary

    Raises:
        Exception: If caption generation fails
    """
    # Build media URLs (for now, use local file paths as identifiers)
    # In production, these would be uploaded to PostBridge first
    media_info = {
        "media_ids": [],
        "media_urls": photo_names  # Using filenames as identifiers
    }

    # Call caption generation service
    try:
        response = requests.post(
            f"{CAPTION_SERVICE_URL}/generate-caption",
            json={
                "media_urls": photo_names,
                "context": context or "",
                "caption_count": caption_count
            },
            timeout=180  # 3 minutes timeout
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        raise Exception(f"Caption generation failed: {e}")


def format_captions_message(result: Dict[str, Any]) -> str:
    """
    Format caption generation results into a Slack message.

    Args:
        result: Caption generation result dictionary

    Returns:
        Formatted Slack message string
    """
    captions = result.get("captions", [])

    if not captions:
        return "No captions generated. Please try again."

    lines = [f"*Generated {len(captions)} caption option(s):*\n"]

    for i, caption_obj in enumerate(captions, 1):
        caption_text = caption_obj.get("text", "")
        hashtags = caption_obj.get("hashtags", [])
        char_count = caption_obj.get("char_count", len(caption_text))

        lines.append(f"*Option {i}* ({char_count} chars):")
        lines.append(f"{caption_text}")
        if hashtags:
            lines.append(f"_Hashtags: {', '.join(hashtags)}_")
        lines.append("")

    lines.append("_Use `/post <photo-names> <caption>` to schedule or publish_")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Post Management
# ---------------------------------------------------------------------------

def create_post(
    photo_names: List[str],
    caption: str,
    schedule: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a post via PostBridge (draft, scheduled, or immediate).

    Args:
        photo_names: List of photo filenames
        caption: Post caption text
        schedule: Optional schedule datetime (ISO 8601 format)

    Returns:
        Post creation result dictionary

    Raises:
        PostBridgeError: If post creation fails
    """
    # Initialize PostBridge client
    client = PostBridgeClient()

    # Get connected accounts
    accounts = client.list_accounts()
    if not accounts:
        raise PostBridgeError("No connected social accounts found")

    # Use all connected accounts (or filter for Instagram/Facebook)
    account_ids = [acc["id"] for acc in accounts if acc.get("platform") in ["instagram", "facebook"]]

    if not account_ids:
        raise PostBridgeError("No Instagram or Facebook accounts connected")

    # For now, we'll create as a draft since we need to upload media first
    # In production, photos would be uploaded to PostBridge media library
    result = client.create_draft(
        caption=caption,
        account_ids=account_ids,
        media_urls=[]  # TODO: Upload photos to PostBridge first
    )

    return result


def list_posts(status: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    List posts from PostBridge.

    Args:
        status: Optional status filter (scheduled, posted, etc.)
        limit: Maximum number of posts to return

    Returns:
        List of post dictionaries

    Raises:
        PostBridgeError: If listing fails
    """
    client = PostBridgeClient()
    posts = client.list_posts(status=status, limit=limit)
    return posts


def format_posts_message(posts: List[Dict[str, Any]]) -> str:
    """
    Format a list of posts into a Slack message.

    Args:
        posts: List of post dictionaries

    Returns:
        Formatted Slack message string
    """
    if not posts:
        return "No posts found."

    lines = [f"*Found {len(posts)} post(s):*\n"]

    for i, post in enumerate(posts, 1):
        post_id = post.get("id", "unknown")
        status = post.get("status", "unknown")
        is_draft = post.get("is_draft", False)
        caption = post.get("caption", "")[:80]
        scheduled_at = post.get("scheduled_at", "")

        draft_label = " [DRAFT]" if is_draft else ""
        schedule_label = f" — Scheduled: {scheduled_at}" if scheduled_at else ""

        lines.append(f"{i}. *{status.upper()}{draft_label}*{schedule_label}")
        lines.append(f"   {caption}...")
        lines.append(f"   _ID: {post_id}_")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Slack Command Handlers
# ---------------------------------------------------------------------------

@app.command("/photos")
def handle_photos_command(ack, command, respond):
    """
    Handle /photos list command.

    Usage: /photos list [filter]
    """
    ack()

    try:
        # Parse command text
        text = command.get("text", "").strip()
        parts = text.split()

        # Default to "list recent"
        if not parts or parts[0] != "list":
            respond("Usage: `/photos list [filter]`\nExample: `/photos list recent`")
            return

        # Get filter term
        filter_term = parts[1] if len(parts) > 1 else "recent"

        # List photos
        photos = list_local_photos(filter_term=filter_term, limit=20)
        message = format_photos_message(photos)

        respond(message)

    except Exception as e:
        respond(f"Error listing photos: {e}")


@app.command("/caption")
def handle_caption_command(ack, command, respond):
    """
    Handle /caption command.

    Usage: /caption <photo-names> [context: ...]
    """
    ack()

    # Generate request ID for tracking
    user_id = command.get("user_id", "unknown")
    request_id = f"slack-{user_id}-{uuid.uuid4().hex[:8]}"

    try:
        # Parse command text
        text = command.get("text", "").strip()

        if not text:
            respond("Usage: `/caption <photo-names> [context: additional context]`\n"
                   "Example: `/caption photo_123.jpg photo_456.jpg context: KCRX E1 results`")
            return

        # Extract context if provided
        context = None
        if "context:" in text.lower():
            parts = text.split("context:", 1)
            photo_text = parts[0].strip()
            context = parts[1].strip()
        else:
            photo_text = text

        # Parse photo names (space-separated)
        photo_names = [name.strip() for name in photo_text.split() if name.strip()]

        if not photo_names:
            respond("Please provide at least one photo name.")
            return

        # Log generation start
        metrics_logger.log_generation_started(
            request_id=request_id,
            media_ids=[],
            media_urls=photo_names,
            context=context or "",
            caption_count=3,
            triggered_by="slackbot"
        )

        # Acknowledge the request
        respond(f"Generating captions for {len(photo_names)} photo(s)... This may take up to 2 minutes.")

        # Generate captions
        start_time = datetime.utcnow()
        result = generate_captions(photo_names, context=context, caption_count=3)
        duration = (datetime.utcnow() - start_time).total_seconds()

        # Log generation completion
        captions = result.get("captions", [])
        metrics_logger.log_generation_completed(
            request_id=request_id,
            task_id=result.get("task_id", ""),
            captions=captions,
            duration_seconds=duration,
            context_sources=result.get("context_sources", []),
            status="success"
        )

        # Format and send response
        message = format_captions_message(result)
        respond(message)

    except Exception as e:
        # Log generation failure
        duration = (datetime.utcnow() - start_time).total_seconds() if 'start_time' in locals() else 0
        metrics_logger.log_generation_failed(
            request_id=request_id,
            task_id="",
            error_message=str(e),
            duration_seconds=duration
        )
        respond(f"Error generating captions: {e}")


@app.command("/post")
def handle_post_command(ack, command, respond):
    """
    Handle /post command.

    Usage: /post <photo-names> "<caption>" [schedule: YYYY-MM-DD HH:MM]
    """
    ack()

    user_id = command.get("user_id", "unknown")

    try:
        # Parse command text
        text = command.get("text", "").strip()

        if not text:
            respond("Usage: `/post <photo-names> \"<caption>\" [schedule: YYYY-MM-DD HH:MM]`\n"
                   "Example: `/post photo_123.jpg \"Great race day! #ChurchOfCombustion\"`")
            return

        # Extract caption (quoted text)
        caption_match = re.search(r'"([^"]+)"', text)
        if not caption_match:
            respond("Please provide a caption in quotes. Example: `/post photo_123.jpg \"Caption text\"`")
            return

        caption = caption_match.group(1)

        # Remove caption from text to get photo names and schedule
        remaining_text = text.replace(caption_match.group(0), "").strip()

        # Extract schedule if provided
        schedule = None
        if "schedule:" in remaining_text.lower():
            parts = remaining_text.split("schedule:", 1)
            photo_text = parts[0].strip()
            schedule_str = parts[1].strip()
            # TODO: Parse schedule string to ISO 8601 format
            schedule = schedule_str
        else:
            photo_text = remaining_text

        # Parse photo names
        photo_names = [name.strip() for name in photo_text.split() if name.strip()]

        if not photo_names:
            respond("Please provide at least one photo name.")
            return

        # Create post (as draft for now)
        respond(f"Creating post for {len(photo_names)} photo(s)...")

        result = create_post(photo_names, caption, schedule=schedule)

        post_id = result.get("id", "unknown")

        # Log caption selection (assuming Instagram for now)
        metrics_logger.log_caption_selected(
            request_id=f"slack-post-{post_id}",
            caption_index=0,  # Custom caption, not from options
            caption_text=caption,
            selected_by=user_id,
            selected_for_platform="instagram"
        )

        respond(f"✓ Post created as draft (ID: {post_id})\n"
                f"Caption: {caption}\n"
                f"_Note: Photos need to be uploaded to PostBridge manually for now._")

    except PostBridgeError as e:
        respond(f"PostBridge error: {e}")
    except Exception as e:
        respond(f"Error creating post: {e}")


@app.command("/posts")
def handle_posts_command(ack, command, respond):
    """
    Handle /posts list command.

    Usage: /posts list [status]
    """
    ack()

    try:
        # Parse command text
        text = command.get("text", "").strip()
        parts = text.split()

        # Default to "list"
        if not parts or parts[0] != "list":
            respond("Usage: `/posts list [status]`\nExample: `/posts list scheduled`")
            return

        # Get status filter
        status = parts[1] if len(parts) > 1 else None

        # List posts
        posts = list_posts(status=status, limit=10)
        message = format_posts_message(posts)

        respond(message)

    except PostBridgeError as e:
        respond(f"PostBridge error: {e}")
    except Exception as e:
        respond(f"Error listing posts: {e}")


@app.command("/feedback")
def handle_feedback_command(ack, command, respond):
    """
    Handle /feedback command for caption quality feedback.

    Usage: /feedback <positive|negative|revise> <request-id> [message]
    """
    ack()

    user_id = command.get("user_id", "unknown")

    try:
        # Parse command text
        text = command.get("text", "").strip()

        if not text:
            respond("Usage: `/feedback <positive|negative|revise> <request-id> [message]`\n"
                   "Example: `/feedback positive slack-ian-1234567890 Great voice match!`\n"
                   "Example: `/feedback revise slack-ian-1234567890 Need shorter captions`")
            return

        parts = text.split(maxsplit=2)

        if len(parts) < 2:
            respond("Please provide: `/feedback <positive|negative|revise> <request-id> [message]`")
            return

        feedback_type = parts[0].lower()
        request_id = parts[1]
        message = parts[2] if len(parts) > 2 else ""

        # Validate feedback type
        if feedback_type not in ["positive", "negative", "revise"]:
            respond("Feedback type must be: positive, negative, or revise")
            return

        # Map "revise" to "revision_needed" for consistency with logger
        logger_feedback_type = "revision_needed" if feedback_type == "revise" else feedback_type

        # Log feedback
        metrics_logger.log_caption_feedback(
            request_id=request_id,
            caption_index=0,  # Generic feedback on all captions from request
            feedback_type=logger_feedback_type,
            feedback_text=message,
            feedback_by=user_id
        )

        emoji = "✅" if feedback_type == "positive" else ("⚠️" if feedback_type == "revise" else "❌")
        respond(f"{emoji} Feedback logged: {feedback_type}\n"
               f"Request ID: {request_id}\n"
               f"_This helps improve future captions_")

    except Exception as e:
        respond(f"Error logging feedback: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Start the Slackbot in Socket Mode."""
    print("=" * 60)
    print("OIO Racing - Slackbot Social Media Interface")
    print("=" * 60)
    print()

    # Validate configuration
    if not SLACK_BOT_TOKEN:
        print("Error: SLACK_BOT_TOKEN not set")
        print("Get your bot token from: https://api.slack.com/apps")
        sys.exit(1)

    if not SLACK_APP_TOKEN:
        print("Error: SLACK_APP_TOKEN not set")
        print("Get your app token from: https://api.slack.com/apps")
        sys.exit(1)

    if not POSTBRIDGE_API_KEY:
        print("Warning: POSTBRIDGE_API_KEY not set")
        print("Post creation will fail without PostBridge credentials")

    print("Configuration:")
    print(f"  Caption Service: {CAPTION_SERVICE_URL}")
    print(f"  Photos Directory: {PICDUMP_DIR}")
    print(f"  PostBridge: {'Configured' if POSTBRIDGE_API_KEY else 'Not configured'}")
    print()
    print("Available commands:")
    print("  /photos list [filter]    - Browse photos")
    print("  /caption <photo-names>   - Generate captions")
    print("  /post <photos> \"<caption>\" - Create post")
    print("  /posts list [status]     - View posts")
    print()
    print("Starting Slackbot in Socket Mode...")
    print("=" * 60)
    print()

    # Start the bot
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()


if __name__ == "__main__":
    main()
