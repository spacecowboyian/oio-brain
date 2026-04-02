#!/usr/bin/env python3
"""
OIO Racing - Social Media Caption Generation Service

Generates AI-powered social media captions using:
- Photo selection from PostBridge-indexed media
- Brand voice documents from OIO Brain
- OIO Brain context (past posts, racing events, car details)
- AI Copywriter agent via Paperclip API

Usage:
    # Start the Flask API server
    python scripts/caption_generation_service.py

    # API endpoint
    POST /generate-caption
    {
        "media_ids": ["photo_id_1", "photo_id_2"],
        "media_urls": ["https://example.com/photo.jpg"],
        "context": "KCRX Event 1, Hudson won Novice class",
        "caption_count": 3
    }

    Response:
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

Environment:
    POSTBRIDGE_API_KEY: PostBridge API key
    PAPERCLIP_API_KEY: Paperclip API key
    PAPERCLIP_API_URL: Paperclip API URL
    PAPERCLIP_COMPANY_ID: Paperclip company ID
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from flask import Flask, request, jsonify
    import requests
except ImportError:
    print("Error: Missing dependencies.")
    print("Run: pip install flask requests")
    sys.exit(1)

# Service configuration
CAPTION_SERVICE_PORT = int(os.environ.get("CAPTION_SERVICE_PORT", "5000"))
AI_COPYWRITER_AGENT_ID = "a2859bcb-cb20-4429-916b-65401f66d96a"
PAPERCLIP_API_URL = os.environ.get("PAPERCLIP_API_URL", "http://127.0.0.1:3100")
PAPERCLIP_API_KEY = os.environ.get("PAPERCLIP_API_KEY", "")
PAPERCLIP_COMPANY_ID = os.environ.get("PAPERCLIP_COMPANY_ID", "")

# OIO Brain paths
BRAIN_ROOT = Path(__file__).parent.parent
BRAND_VOICE_PATH = BRAIN_ROOT / "01 - Brand" / "Voice-and-Tone.md"
BRAND_VOICE_GUIDE_PATH = BRAIN_ROOT / "02 - Content" / "OIO-Brand-Voice-Guide.md"
CARS_PATH = BRAIN_ROOT / "03 - Cars"
CONTENT_PATH = BRAIN_ROOT / "02 - Content"

# Flask app
app = Flask(__name__)


class CaptionGenerationError(Exception):
    """Base exception for caption generation errors."""
    pass


def read_brand_voice_context() -> str:
    """
    Read brand voice documents to provide context for caption generation.

    Returns:
        Combined brand voice context as a string.
    """
    context_parts = []

    # Read core voice and tone guide
    if BRAND_VOICE_PATH.exists():
        with open(BRAND_VOICE_PATH, 'r') as f:
            context_parts.append(f"## Core Brand Voice\n{f.read()}")

    # Read comprehensive brand voice guide
    if BRAND_VOICE_GUIDE_PATH.exists():
        with open(BRAND_VOICE_GUIDE_PATH, 'r') as f:
            context_parts.append(f"## Social Media Brand Voice Guide\n{f.read()}")

    return "\n\n".join(context_parts)


def query_oio_brain_context(user_context: str) -> Dict[str, Any]:
    """
    Query OIO Brain for relevant context based on user input.

    Searches for relevant information in:
    - Car details (fleet nicknames, current status)
    - Recent race events
    - Team member information

    Args:
        user_context: User-provided context string

    Returns:
        Dictionary with relevant OIO Brain context
    """
    context = {
        "cars": {},
        "recent_events": [],
        "team_members": [],
        "relevant_files": []
    }

    # Extract car mentions from user context
    car_keywords = ["goblin", "fitty cent", "dale", "nessie", "killer corolla",
                    "geoffrey", "mr2", "fit", "celica", "cressida", "corolla",
                    "dauphine", "mgb"]

    mentioned_cars = [car for car in car_keywords if car.lower() in user_context.lower()]

    # Search for car information
    if mentioned_cars and CARS_PATH.exists():
        for car_file in CARS_PATH.rglob("*.md"):
            if any(car in car_file.stem.lower() for car in mentioned_cars):
                try:
                    with open(car_file, 'r') as f:
                        content = f.read()
                        # Extract first 500 chars as summary
                        context["cars"][car_file.stem] = content[:500]
                        context["relevant_files"].append(str(car_file.relative_to(BRAIN_ROOT)))
                except Exception:
                    pass

    # Search for recent race event summaries
    if CONTENT_PATH.exists():
        summaries_path = CONTENT_PATH / "Summaries"
        if summaries_path.exists():
            # Get most recent 3 summaries
            summary_files = sorted(summaries_path.glob("*.md"), reverse=True)[:3]
            for summary_file in summary_files:
                try:
                    with open(summary_file, 'r') as f:
                        context["recent_events"].append({
                            "file": summary_file.name,
                            "summary": f.read()[:500]
                        })
                        context["relevant_files"].append(str(summary_file.relative_to(BRAIN_ROOT)))
                except Exception:
                    pass

    return context


def create_copywriter_task(
    media_info: Dict[str, Any],
    user_context: str,
    oio_brain_context: Dict[str, Any],
    brand_voice: str,
    caption_count: int = 3
) -> str:
    """
    Create a Paperclip task for the AI Copywriter agent.

    Args:
        media_info: Information about the media (IDs, URLs)
        user_context: User-provided context
        oio_brain_context: Context from OIO Brain
        brand_voice: Brand voice guidelines
        caption_count: Number of caption variations to generate

    Returns:
        Task ID for the created Paperclip task

    Raises:
        CaptionGenerationError: If task creation fails
    """
    if not PAPERCLIP_API_KEY:
        raise CaptionGenerationError("PAPERCLIP_API_KEY not set")

    # Build task description
    task_description = f"""Generate {caption_count} social media caption variations for OIO Racing post.

**Media:**
{json.dumps(media_info, indent=2)}

**User Context:**
{user_context}

**OIO Brain Context:**
{json.dumps(oio_brain_context, indent=2)}

**Requirements:**
1. Follow the brand voice guidelines exactly
2. Generate {caption_count} caption variations
3. Include appropriate hashtags (#ChurchOfCombustion, #GrassrootsRacing, etc.)
4. Keep captions punchy and authentic (1-3 sentences ideal)
5. Return captions in JSON format:
   {{
       "captions": [
           {{"text": "caption text", "hashtags": ["#tag1", "#tag2"], "char_count": 150}}
       ]
   }}

**Brand Voice Guidelines:**
{brand_voice[:2000]}

[See full brand voice guidelines in OIO Brain]
"""

    # Create task via Paperclip API
    try:
        response = requests.post(
            f"{PAPERCLIP_API_URL}/api/companies/{PAPERCLIP_COMPANY_ID}/issues",
            headers={
                "Authorization": f"Bearer {PAPERCLIP_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "title": f"Generate social media captions ({caption_count} variations)",
                "description": task_description,
                "status": "todo",
                "priority": "high",
                "assigneeAgentId": AI_COPYWRITER_AGENT_ID
            },
            timeout=30
        )
        response.raise_for_status()

        task_data = response.json()
        return task_data.get("id", "")

    except requests.RequestException as e:
        raise CaptionGenerationError(f"Failed to create Paperclip task: {e}")


def wait_for_caption_generation(task_id: str, timeout: int = 120) -> Dict[str, Any]:
    """
    Poll Paperclip task until caption generation is complete.

    Args:
        task_id: Paperclip task ID
        timeout: Maximum wait time in seconds

    Returns:
        Generated captions and metadata

    Raises:
        CaptionGenerationError: If task fails or times out
    """
    start_time = time.time()
    poll_interval = 5  # seconds

    while time.time() - start_time < timeout:
        try:
            # Get task status
            response = requests.get(
                f"{PAPERCLIP_API_URL}/api/issues/{task_id}",
                headers={"Authorization": f"Bearer {PAPERCLIP_API_KEY}"},
                timeout=10
            )
            response.raise_for_status()

            task = response.json()
            status = task.get("status", "")

            if status == "done":
                # Get task comments to extract captions
                comments_response = requests.get(
                    f"{PAPERCLIP_API_URL}/api/issues/{task_id}/comments",
                    headers={"Authorization": f"Bearer {PAPERCLIP_API_KEY}"},
                    timeout=10
                )
                comments_response.raise_for_status()

                comments = comments_response.json()

                # Look for JSON caption response in comments
                for comment in reversed(comments):
                    body = comment.get("body", "")
                    # Try to extract JSON from comment
                    try:
                        # Look for JSON code block
                        if "```json" in body:
                            json_start = body.find("```json") + 7
                            json_end = body.find("```", json_start)
                            json_str = body[json_start:json_end].strip()
                            return json.loads(json_str)
                        # Try to parse entire comment as JSON
                        elif body.strip().startswith("{"):
                            return json.loads(body)
                    except json.JSONDecodeError:
                        continue

                # If no JSON found, return text captions from description
                return {
                    "captions": [{
                        "text": task.get("description", "Caption generation completed but no captions found"),
                        "hashtags": [],
                        "char_count": len(task.get("description", ""))
                    }],
                    "note": "Captions extracted from task description (no JSON found)"
                }

            elif status in ["blocked", "cancelled"]:
                raise CaptionGenerationError(f"Caption generation task {status}: {task.get('description', '')}")

            # Still in progress, wait before next poll
            time.sleep(poll_interval)

        except requests.RequestException as e:
            raise CaptionGenerationError(f"Failed to check task status: {e}")

    raise CaptionGenerationError(f"Caption generation timed out after {timeout} seconds")


@app.route("/generate-caption", methods=["POST"])
def generate_caption():
    """
    Generate social media captions via AI Copywriter agent.

    Request body:
        {
            "media_ids": ["id1", "id2"],  # Optional: PostBridge media IDs
            "media_urls": ["url1"],        # Optional: Public media URLs
            "context": "Event context",    # Optional: Additional context
            "caption_count": 3             # Optional: Number of variations (default: 3)
        }

    Response:
        {
            "captions": [...],
            "brand_voice_applied": true,
            "context_sources": [...],
            "task_id": "paperclip-task-id"
        }
    """
    try:
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        media_ids = data.get("media_ids", [])
        media_urls = data.get("media_urls", [])
        user_context = data.get("context", "")
        caption_count = data.get("caption_count", 3)

        if not media_ids and not media_urls:
            return jsonify({"error": "Either media_ids or media_urls must be provided"}), 400

        # Read brand voice context
        brand_voice = read_brand_voice_context()

        # Query OIO Brain for relevant context
        oio_brain_context = query_oio_brain_context(user_context)

        # Prepare media info
        media_info = {
            "media_ids": media_ids,
            "media_urls": media_urls
        }

        # Create Paperclip task for AI Copywriter
        task_id = create_copywriter_task(
            media_info=media_info,
            user_context=user_context,
            oio_brain_context=oio_brain_context,
            brand_voice=brand_voice,
            caption_count=caption_count
        )

        # Wait for caption generation (with timeout)
        captions_result = wait_for_caption_generation(task_id, timeout=120)

        # Return response
        return jsonify({
            "captions": captions_result.get("captions", []),
            "brand_voice_applied": True,
            "context_sources": oio_brain_context.get("relevant_files", []),
            "task_id": task_id,
            "note": captions_result.get("note")
        })

    except CaptionGenerationError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "OIO Racing Caption Generation Service",
        "ai_copywriter_agent_id": AI_COPYWRITER_AGENT_ID
    })


def main():
    """Start the Flask API server."""
    print("=" * 60)
    print("OIO Racing - Caption Generation Service")
    print("=" * 60)
    print(f"API URL: http://localhost:{CAPTION_SERVICE_PORT}")
    print(f"Paperclip API: {PAPERCLIP_API_URL}")
    print(f"AI Copywriter Agent: {AI_COPYWRITER_AGENT_ID}")
    print()
    print("Endpoints:")
    print(f"  POST /generate-caption - Generate captions")
    print(f"  GET  /health          - Health check")
    print("=" * 60)

    app.run(host="0.0.0.0", port=CAPTION_SERVICE_PORT, debug=True)


if __name__ == "__main__":
    main()
