#!/usr/bin/env python3
"""
AI Photo Filing Agent

Uses Claude vision API to analyze racing photos and automatically file them
into the OIO photo library with appropriate metadata and documentation updates.
"""

import os
import sys
import json
import shutil
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import anthropic


# Configuration
CONFIDENCE_THRESHOLD = 0.7
REPO_ROOT = Path(__file__).parent.parent
PICDUMP_DIR = REPO_ROOT / "picdump"
PHOTOS_DIR = REPO_ROOT / "photos"
CARS_DIR = REPO_ROOT / "OIO Brain" / "03 - Cars"
PHOTO_INDEX = REPO_ROOT / "PHOTO-INDEX.md"


class PhotoFilingAgent:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.fleet_context = self._load_fleet_context()

    def _load_fleet_context(self) -> str:
        """Load car fleet information for context."""
        context_parts = []

        # Load PHOTO-INDEX.md for visual ID markers
        if PHOTO_INDEX.exists():
            with open(PHOTO_INDEX) as f:
                context_parts.append(f.read())

        # Load car Overview.md files
        if CARS_DIR.exists():
            for overview in CARS_DIR.rglob("Overview.md"):
                with open(overview) as f:
                    content = f.read()
                    context_parts.append(f"\n\n=== {overview.parent.name} ===\n{content}")

        return "\n".join(context_parts)

    def analyze_photo(self, photo_path: Path) -> Dict:
        """Analyze a photo using Claude vision API."""

        # Read the image
        with open(photo_path, "rb") as f:
            image_data = f.read()

        # Determine media type
        ext = photo_path.suffix.lower()
        media_type_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp"
        }
        media_type = media_type_map.get(ext, "image/jpeg")

        # Create the prompt
        prompt = f"""Analyze this racing photo and identify the car, driver, event, and context.

You have access to the OIO Racing fleet information below. Use this to identify which specific car from the fleet is in the photo.

{self.fleet_context}

Provide your analysis in JSON format:
{{
    "car_model": "Full car name/model",
    "car_nickname": "Nickname if identifiable",
    "driver": "Driver name (Ian, Ryan, Keegan, Richard, or Karen)",
    "event": "Event name/type (e.g., 'KCRSCCA Rallycross', 'Gateway Track Day')",
    "context": "Detailed description of what's happening in the photo",
    "visual_details": "Detailed visual description for ID (color, body style, key features, graphics)",
    "confidence": 0.0-1.0,
    "reasoning": "Explanation of identification",
    "unidentified": false
}}

If you cannot confidently identify the car (confidence < 0.7), set "unidentified": true and still provide your best guess with reasoning.

Focus on:
- Visual ID markers (color, body style, door graphics, wheels, spoilers, etc.)
- Event context visible in the background
- Any visible numbers, livery, or graphics
- Car shape, era, and distinctive features"""

        # Encode image as base64
        image_base64 = base64.standard_b64encode(image_data).decode("utf-8")

        # Call Claude API
        message = self.client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        # Parse response
        response_text = message.content[0].text

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text.strip()

        analysis = json.loads(json_str)

        return analysis

    def file_photo(self, photo_path: Path, analysis: Dict) -> Tuple[bool, str]:
        """File the photo and update documentation."""

        filename = photo_path.name
        driver = analysis["driver"]
        car_name = analysis.get("car_nickname") or analysis["car_model"]

        # Sanitize car name for directory
        car_dir_name = car_name.replace("/", "-").replace(" ", "-")
        target_dir = PHOTOS_DIR / driver / car_dir_name
        target_dir.mkdir(parents=True, exist_ok=True)

        # Move the photo
        target_path = target_dir / filename
        shutil.move(str(photo_path), str(target_path))

        # Update photo-log.md
        photo_log = target_dir / "photo-log.md"
        self._update_photo_log(photo_log, filename, analysis)

        # Update PHOTO-INDEX.md
        self._update_photo_index(driver, car_name, filename, analysis, target_path)

        # Update car Overview.md
        self._update_car_overview(driver, car_name, filename, analysis)

        # Create analysis metadata file
        metadata_path = target_dir / f"{filename}.analysis.json"
        with open(metadata_path, "w") as f:
            json.dump({
                "analyzed_at": datetime.now().isoformat(),
                "analysis": analysis,
                "original_location": str(photo_path),
                "filed_location": str(target_path)
            }, f, indent=2)

        return True, f"Filed to {target_path.relative_to(REPO_ROOT)}"

    def _update_photo_log(self, log_path: Path, filename: str, analysis: Dict):
        """Create or update the per-car photo-log.md."""

        if log_path.exists():
            with open(log_path) as f:
                content = f.read()
        else:
            content = f"""---
title: Photo Log
type: reference
status: active
updated: {datetime.now().strftime('%Y-%m-%d')}
---

# Photo Log

| Filename | Date | Event | Context | Social Media Status |
|---|---|---|---|---|
"""

        # Add new entry
        entry = f"| {filename} | {datetime.now().strftime('%Y-%m-%d')} | {analysis.get('event', 'Unknown')} | {analysis['context'][:50]}... | Not posted |\n"
        content += entry

        with open(log_path, "w") as f:
            f.write(content)

    def _update_photo_index(self, driver: str, car: str, filename: str, analysis: Dict, photo_path: Path):
        """Update PHOTO-INDEX.md with the new photo."""

        if not PHOTO_INDEX.exists():
            return

        with open(PHOTO_INDEX) as f:
            lines = f.readlines()

        # Find the car section
        # This is a simplified update - in production, you'd want more robust parsing
        new_row = f"| {len([l for l in lines if '|' in l and filename not in l]) + 1} | [{filename}]({photo_path.relative_to(REPO_ROOT)}) | — | {datetime.now().strftime('%Y-%m-%d')} | {analysis.get('event', 'Unknown')} | {analysis['context'][:40]}... | No |\n"

        # Update the file (simplified - would need more robust section detection)
        with open(PHOTO_INDEX, "a") as f:
            f.write(f"\n{new_row}")

    def _update_car_overview(self, driver: str, car: str, filename: str, analysis: Dict):
        """Update the car's Overview.md with visual ID info and photo reference."""

        # Find the car's Overview.md
        # This would need to match car names to directory names
        # Simplified for now
        pass

    def process_picdump(self) -> List[Dict]:
        """Process all photos in picdump directory."""

        if not PICDUMP_DIR.exists():
            print("No picdump directory found")
            return []

        results = []
        photo_extensions = {".png", ".jpg", ".jpeg", ".heic", ".webp"}
        photos = [f for f in PICDUMP_DIR.iterdir()
                 if f.is_file() and f.suffix.lower() in photo_extensions]

        if not photos:
            print("No photos found in picdump")
            return []

        print(f"Found {len(photos)} photo(s) to process")

        for photo in photos:
            print(f"\nProcessing {photo.name}...")

            try:
                # Analyze the photo
                analysis = self.analyze_photo(photo)
                confidence = analysis.get("confidence", 0.0)

                print(f"  Identified: {analysis.get('car_model')} - {analysis.get('driver')}")
                print(f"  Confidence: {confidence:.2f}")
                print(f"  Event: {analysis.get('event')}")

                result = {
                    "filename": photo.name,
                    "status": "pending",
                    "analysis": analysis,
                    "confidence": confidence
                }

                # Check confidence threshold
                if confidence >= CONFIDENCE_THRESHOLD and not analysis.get("unidentified", False):
                    # File the photo automatically
                    success, message = self.file_photo(photo, analysis)
                    result["status"] = "filed" if success else "error"
                    result["message"] = message
                    print(f"  ✓ {message}")
                else:
                    # Flag for manual review
                    result["status"] = "flagged"
                    result["message"] = f"Low confidence ({confidence:.2f}) - needs manual review"
                    print(f"  ⚠ {result['message']}")

                    # Move to unidentified folder
                    unidentified_dir = PHOTOS_DIR / "unidentified"
                    unidentified_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(photo), str(unidentified_dir / photo.name))

                    # Save analysis for reference
                    metadata_path = unidentified_dir / f"{photo.name}.analysis.json"
                    with open(metadata_path, "w") as f:
                        json.dump(analysis, f, indent=2)

                results.append(result)

            except Exception as e:
                print(f"  ✗ Error: {e}")
                results.append({
                    "filename": photo.name,
                    "status": "error",
                    "message": str(e)
                })

        return results


def post_to_slack(results: List[Dict], webhook_url: Optional[str] = None):
    """Post results to Slack for flagged photos."""

    if not webhook_url:
        print("\nNo Slack webhook configured - skipping Slack notification")
        return

    flagged = [r for r in results if r["status"] == "flagged"]

    if not flagged:
        return

    # Build Slack message
    import requests

    message = {
        "text": f"⚠️ {len(flagged)} photo(s) need manual review",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*AI Photo Filing Alert*\n{len(flagged)} photo(s) could not be confidently identified and need manual review."
                }
            }
        ]
    }

    for item in flagged:
        analysis = item["analysis"]
        message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{item['filename']}*\n" +
                       f"Best guess: {analysis.get('car_model')} - {analysis.get('driver')}\n" +
                       f"Confidence: {item['confidence']:.0%}\n" +
                       f"Reasoning: {analysis.get('reasoning', 'N/A')}"
            }
        })

    requests.post(webhook_url, json=message)
    print(f"\n✓ Sent Slack notification for {len(flagged)} flagged photo(s)")


def main():
    """Main entry point."""

    # Get API key from environment
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    # Get optional Slack webhook
    slack_webhook = os.environ.get("SLACK_WEBHOOK_URL")

    # Create agent and process picdump
    agent = PhotoFilingAgent(api_key)
    results = agent.process_picdump()

    # Print summary
    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)

    filed = len([r for r in results if r["status"] == "filed"])
    flagged = len([r for r in results if r["status"] == "flagged"])
    errors = len([r for r in results if r["status"] == "error"])

    print(f"Total photos: {len(results)}")
    print(f"  ✓ Filed: {filed}")
    print(f"  ⚠ Flagged for review: {flagged}")
    print(f"  ✗ Errors: {errors}")

    # Post to Slack if configured
    if slack_webhook:
        post_to_slack(results, slack_webhook)

    # Output results as JSON for GitHub Actions
    output_file = REPO_ROOT / ".photo-filing-results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_file.relative_to(REPO_ROOT)}")

    # Exit with error if any photos failed
    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
