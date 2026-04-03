#!/usr/bin/env python3
"""
OIO Racing - AI Photo Filing Agent

Analyzes photos from intake/photos/ using Claude Vision API to identify:
- Which car is in the photo
- Which driver owns it
- What event/context

Auto-files photos to photos/{Driver}/{Car}/ if confidence >= 80%.
Notifies Ian via Slack if uncertain.

Usage:
  python scripts/ai_photo_filing_agent.py

Set SLACK_BOT_TOKEN and SLACK_CHANNEL_ID environment variables for notifications.
"""

import argparse
import base64
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError:
    print("Error: anthropic SDK is not installed.")
    print("Run: pip install anthropic")
    raise


# Paths
REPO_ROOT = Path(__file__).parent.parent
PICDUMP_DIR = REPO_ROOT / "intake" / "photos"
PHOTOS_DIR = REPO_ROOT / "photos"
OIO_BRAIN_DIR = REPO_ROOT
PHOTO_INDEX_FILE = REPO_ROOT / "PHOTO-INDEX.md"
CARS_DIR = REPO_ROOT / "cars"
TEAM_BIOS_FILE = REPO_ROOT / "brand" / "team-bios.md"


# ---------------------------------------------------------------------------
# Context Loading
# ---------------------------------------------------------------------------

def load_team_bios():
    """Load team and fleet information from Team-Bios.md."""
    if not TEAM_BIOS_FILE.exists():
        return "Team bios not found."

    with open(TEAM_BIOS_FILE, "r", encoding="utf-8") as f:
        return f.read()


def load_car_descriptions():
    """Load car overview descriptions for visual identification."""
    car_descriptions = {}

    if not CARS_DIR.exists():
        return car_descriptions

    for driver_dir in CARS_DIR.iterdir():
        if not driver_dir.is_dir():
            continue

        driver_name = driver_dir.name
        car_descriptions[driver_name] = {}

        for car_dir in driver_dir.iterdir():
            if not car_dir.is_dir():
                continue

            overview_file = car_dir / "Overview.md"
            if overview_file.exists():
                with open(overview_file, "r", encoding="utf-8") as f:
                    car_descriptions[driver_name][car_dir.name] = f.read()

    return car_descriptions


def format_context(team_bios, car_descriptions):
    """Format context for the Claude Vision prompt."""
    car_context = ""

    for driver, cars in car_descriptions.items():
        car_context += f"\n## {driver}'s Cars\n"
        for car_name, description in cars.items():
            car_context += f"\n### {car_name}\n{description[:500]}...\n"

    return f"""
# OIO Racing Fleet and Team Context

## Team Information
{team_bios[:2000]}...

## Car Descriptions and Visual Markers
{car_context}
"""


# ---------------------------------------------------------------------------
# Photo Analysis
# ---------------------------------------------------------------------------

def encode_image_to_base64(image_path):
    """Encode image file to base64 for Claude Vision API."""
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def get_image_media_type(image_path):
    """Determine media type from file extension."""
    ext = Path(image_path).suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".heic": "image/heic",
        ".webp": "image/webp",
    }
    return media_types.get(ext, "image/jpeg")


def analyze_photo(client, image_path, context):
    """
    Analyze a photo using Claude Vision API.

    Returns a dict with:
    - car_driver: (Driver, Car) tuple
    - confidence: float 0-1
    - event_context: str (race, shop, travel, etc.)
    - reasoning: str
    - auto_file: bool (True if confidence >= 0.8)
    """

    # Encode image
    image_data = encode_image_to_base64(image_path)
    media_type = get_image_media_type(image_path)

    # Build prompt for photo identification
    prompt = f"""Analyze this photo from an OIO Racing archive.

{context}

**Your task:**
1. Identify which car is in the photo using visual cues (color, shape, livery, wheels, era, unique features)
2. Determine the driver who owns it
3. Estimate the event/context (KCRSCCA Rallycross, autocross, shop work, travel, street, unknown)
4. Provide confidence score (0-1) for your identification

**Response format (JSON):**
{{
  "car": "Car name or model (e.g., '1985 MR2 AW11' or 'unknown')",
  "driver": "Driver first name (Ian, Ryan, Keegan, Richard, Karen, or 'unknown')",
  "event_context": "Event type (rallycross/autocross/shop/travel/street/unknown)",
  "confidence": 0.85,
  "reasoning": "Brief explanation of visual clues used for identification",
  "visual_notes": "Detailed description of what's visible (car condition, angle, environment, etc.)"
}}

Be conservative with confidence. Only assign high confidence if you can clearly identify:
- The specific car model/year
- The driver from known fleet info
- The likely event from visual cues (dirt/asphalt, event setup, etc.)

If uncertain about any field, set lower confidence and note what's ambiguous."""

    # Call Claude API with vision
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ],
    )

    # Parse response
    response_text = response.content[0].text

    try:
        # Extract JSON from response
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            # Fallback: treat entire response as failure
            result = {
                "car": "unknown",
                "driver": "unknown",
                "event_context": "unknown",
                "confidence": 0.0,
                "reasoning": response_text,
                "visual_notes": "",
            }
    except json.JSONDecodeError:
        result = {
            "car": "unknown",
            "driver": "unknown",
            "event_context": "unknown",
            "confidence": 0.0,
            "reasoning": f"Failed to parse response: {response_text}",
            "visual_notes": "",
        }

    # Add auto_file decision
    result["auto_file"] = result.get("confidence", 0) >= 0.8
    result["image_path"] = str(image_path)

    return result


# ---------------------------------------------------------------------------
# File Operations
# ---------------------------------------------------------------------------

def file_photo(driver, car, source_path, analysis_result):
    """
    File a photo to the correct location.

    Creates photos/{Driver}/{Car}/ folder if needed.
    Returns (True, dest_path) on success, (False, error_msg) on failure.
    """

    try:
        # Create target directory
        target_dir = PHOTOS_DIR / driver.lower() / car.replace(" ", "-")
        target_dir.mkdir(parents=True, exist_ok=True)

        # Move file
        filename = Path(source_path).name
        target_path = target_dir / filename

        shutil.move(str(source_path), str(target_path))

        # Create/update photo-log.md
        photo_log = target_dir / "photo-log.md"
        log_entry = f"\n## {filename}\n- Date: {datetime.now().strftime('%Y-%m-%d')}\n- Event: {analysis_result.get('event_context', 'unknown')}\n- Notes: {analysis_result.get('visual_notes', 'Auto-filed by AI agent')}\n"

        with open(photo_log, "a", encoding="utf-8") as f:
            f.write(log_entry)

        return True, str(target_path)

    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Slack Notifications
# ---------------------------------------------------------------------------

def notify_slack(filename, analysis_result, reason="uncertain", image_path=None):
    """Send Slack notification about photo filing decision with optional image attachment."""

    slack_token = os.getenv("SLACK_BOT_TOKEN")
    slack_channel = os.getenv("SLACK_CHANNEL_ID")
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")

    if not slack_token and not slack_webhook:
        # No Slack config — skip notification
        print(f"  ℹ No Slack credentials configured (set SLACK_BOT_TOKEN or SLACK_WEBHOOK_URL)")
        return False

    if slack_token and not slack_channel:
        print(f"  ⚠ Slack bot token set but SLACK_CHANNEL_ID not configured")
        return False

    try:
        import requests

        emoji = "⚠️" if reason == "uncertain" else ("✅" if reason == "auto_filed" else "❌")
        confidence = analysis_result.get("confidence", 0)

        # Build message blocks for rich formatting
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Photo Filing Update",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*File:*\n`{filename}`",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{reason.upper()}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Car:*\n{analysis_result.get('car', 'unknown')}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Driver:*\n{analysis_result.get('driver', 'unknown')}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Event:*\n{analysis_result.get('event_context', 'unknown')}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Confidence:*\n{confidence:.0%}",
                    },
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Reasoning:*\n{analysis_result.get('reasoning', 'N/A')}",
                },
            },
        ]

        # Add image block if image path provided
        if image_path and Path(image_path).exists():
            # For webhook, we can include image_url in blocks
            # For bot token API, we'll add the image as an initial comment
            if slack_webhook:
                image_url = f"file://{image_path}"  # Local file URL for testing
                blocks.append(
                    {
                        "type": "image",
                        "image_url": image_url,
                        "alt_text": f"Photo: {filename}",
                    }
                )

        # Send via appropriate method
        if slack_webhook:
            # Use incoming webhook (simpler, works with basic auth)
            response = requests.post(
                slack_webhook,
                json={
                    "blocks": blocks,
                    "text": f"Photo Filing Update: {filename}",
                },
                timeout=10,
            )
            response.raise_for_status()
            print(f"  ✓ Slack notification sent via webhook")
            return True

        elif slack_token and slack_channel:
            # Use bot API with files.upload for images
            response = requests.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {slack_token}"},
                json={
                    "channel": slack_channel,
                    "blocks": blocks,
                    "text": f"Photo Filing Update: {filename}",
                },
                timeout=10,
            )
            response.raise_for_status()
            response_data = response.json()

            if not response_data.get("ok"):
                error = response_data.get("error", "Unknown error")
                print(f"  ⚠ Slack API error: {error}")
                return False

            # If we have an image, upload it as a comment
            if image_path and Path(image_path).exists():
                ts = response_data.get("ts")
                with open(image_path, "rb") as f:
                    files_response = requests.post(
                        "https://slack.com/api/files.upload",
                        headers={"Authorization": f"Bearer {slack_token}"},
                        files={"file": f},
                        data={
                            "channels": slack_channel,
                            "title": filename,
                            "initial_comment": f"Uncertain photo requiring manual review",
                        },
                        timeout=30,
                    )
                    files_response.raise_for_status()
                    files_data = files_response.json()
                    if files_data.get("ok"):
                        print(f"  ✓ Image uploaded to Slack")
                    else:
                        print(f"  ⚠ Failed to upload image: {files_data.get('error')}")

            print(f"  ✓ Slack notification sent via bot API")
            return True

    except requests.Timeout:
        print(f"  ⚠ Slack notification timed out")
        return False
    except requests.RequestException as e:
        print(f"  ⚠ Slack notification failed: {e}")
        return False
    except Exception as e:
        print(f"  ⚠ Unexpected error sending Slack notification: {e}")
        return False


# ---------------------------------------------------------------------------
# Main Processing
# ---------------------------------------------------------------------------

def process_picdump():
    """Process all photos in picdump directory."""

    if not PICDUMP_DIR.exists():
        print(f"Error: picdump directory not found at {PICDUMP_DIR}")
        return 0

    # Find image files
    image_files = list(PICDUMP_DIR.glob("*.*"))
    image_files = [f for f in image_files if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".heic", ".webp"]]

    if not image_files:
        print("No image files found in intake/photos/")
        return 0

    print(f"Found {len(image_files)} image(s) in intake/photos/\n")

    # Initialize Anthropic client
    client = Anthropic()

    # Load context
    print("Loading OIO context...")
    team_bios = load_team_bios()
    car_descriptions = load_car_descriptions()
    context = format_context(team_bios, car_descriptions)

    # Process each photo
    filed_count = 0
    uncertain_count = 0
    failed_count = 0

    for image_path in image_files:
        print(f"\nAnalyzing: {image_path.name}")

        try:
            # Analyze photo
            result = analyze_photo(client, image_path, context)

            confidence = result.get("confidence", 0)
            driver = result.get("driver", "unknown")
            car = result.get("car", "unknown")

            print(f"  → {driver}'s {car}")
            print(f"  → Confidence: {confidence:.0%}")
            print(f"  → {result.get('reasoning', '')}")

            # Auto-file if confident
            if result["auto_file"] and driver != "unknown" and car != "unknown":
                success, dest = file_photo(driver, car, image_path, result)
                if success:
                    print(f"  ✓ Filed to {dest}")
                    filed_count += 1
                    notify_slack(image_path.name, result, "auto_filed", image_path=image_path)
                else:
                    print(f"  ✗ Filing failed: {dest}")
                    failed_count += 1
                    notify_slack(image_path.name, result, "failed", image_path=image_path)
            else:
                print(f"  ⚠ Uncertain — flagging for manual review")
                uncertain_count += 1
                notify_slack(image_path.name, result, "uncertain", image_path=image_path)

        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed_count += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"Processing complete:")
    print(f"  ✓ Filed: {filed_count}")
    print(f"  ⚠ Uncertain: {uncertain_count}")
    print(f"  ✗ Failed: {failed_count}")
    print(f"{'='*60}")

    return filed_count


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Analyze and auto-file photos from picdump using Claude Vision."
    )
    args = parser.parse_args()

    print("OIO Racing - AI Photo Filing Agent\n")

    try:
        filed = process_picdump()
        sys.exit(0)

    except RuntimeError as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
