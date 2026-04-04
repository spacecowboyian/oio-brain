#!/usr/bin/env python3
"""
OIO Racing - Google Photos to Supabase Sync Pipeline

Syncs photos from a Google Photos album to Supabase storage and database,
runs Claude Vision analysis, and maintains photo metadata.

This replaces the old git-based photo ingest system with a cloud-native
architecture:
  Google Photos → Supabase storage + database → Claude Vision → Triage UI

Environment Variables (required):
  GOOGLE_PHOTOS_CREDENTIALS - JSON string with client_id, client_secret, refresh_token
  GOOGLE_PHOTOS_ALBUM_ID - Album ID from Google Photos URL
  ANTHROPIC_API_KEY - For Claude Vision analysis
  SUPABASE_URL - Project URL (https://zdjughkxryhabduhsdgg.supabase.co)
  SUPABASE_SERVICE_ROLE_KEY - Service role key (not anon key)

Usage:
  python scripts/sync_google_photos.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Ensure repo context is available
REPO_ROOT = Path(__file__).parent.parent


def log(message, level="INFO"):
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = f"[{timestamp}] {level}: {message}"
    print(output, flush=True)
    if level in ("ERROR", "FATAL"):
        print(output, file=sys.stderr, flush=True)


def load_credentials():
    """Load and refresh Google Photos credentials."""
    creds_json = os.getenv("GOOGLE_PHOTOS_CREDENTIALS")
    if not creds_json:
        log("Missing GOOGLE_PHOTOS_CREDENTIALS environment variable", "FATAL")
        sys.exit(1)

    try:
        creds_dict = json.loads(creds_json)
    except json.JSONDecodeError as e:
        log(f"Invalid GOOGLE_PHOTOS_CREDENTIALS JSON: {e}", "FATAL")
        sys.exit(1)

    # Create credentials object
    credentials = Credentials(
        token=None,  # Will be refreshed
        refresh_token=creds_dict.get("refresh_token"),
        token_uri=creds_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=creds_dict.get("client_id"),
        client_secret=creds_dict.get("client_secret"),
    )

    # Refresh to get a fresh access token
    try:
        credentials.refresh(Request())
        log("Google Photos credentials refreshed")
    except Exception as e:
        log(f"Failed to refresh Google Photos credentials: {e}", "FATAL")
        sys.exit(1)

    return credentials


def fetch_album_photos(credentials):
    """Fetch all photos from the configured Google Photos album."""
    album_id = os.getenv("GOOGLE_PHOTOS_ALBUM_ID")
    if not album_id:
        log("Missing GOOGLE_PHOTOS_ALBUM_ID environment variable", "FATAL")
        sys.exit(1)

    all_items = []
    next_page_token = None
    url = "https://photoslibrary.googleapis.com/v1/mediaItems:search"

    while True:
        payload = {"albumId": album_id, "pageSize": 100}
        if next_page_token:
            payload["pageToken"] = next_page_token

        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            log(f"Failed to fetch album photos: {e}", "ERROR")
            return []

        data = response.json()
        all_items.extend(data.get("mediaItems", []))

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    log(f"Fetched {len(all_items)} photos from Google Photos album")
    return all_items


def supabase_request(method, path, json_data=None, headers=None):
    """Make a request to Supabase REST API."""
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_role_key:
        log("Missing Supabase environment variables", "FATAL")
        sys.exit(1)

    url = f"{supabase_url}/rest/v1{path}"
    default_headers = {
        "Authorization": f"Bearer {service_role_key}",
        "apikey": service_role_key,
        "Content-Type": "application/json",
    }
    if headers:
        default_headers.update(headers)

    try:
        if method == "GET":
            response = requests.get(url, headers=default_headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=json_data, headers=default_headers, timeout=30)
        elif method == "PATCH":
            response = requests.patch(url, json=json_data, headers=default_headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json() if response.text else None
    except requests.RequestException as e:
        log(f"Supabase API error ({method} {path}): {e}", "ERROR")
        return None


def upload_to_storage(photo_bytes, path):
    """Upload photo bytes to Supabase Storage."""
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_role_key:
        log("Missing Supabase environment variables", "FATAL")
        sys.exit(1)

    url = f"{supabase_url}/storage/v1/object/oio-photos/{path}"
    headers = {
        "Authorization": f"Bearer {service_role_key}",
        "x-upsert": "false",
    }

    try:
        response = requests.post(url, data=photo_bytes, headers=headers, timeout=60)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        log(f"Failed to upload photo to storage: {e}", "ERROR")
        return False


def download_photo(base_url):
    """Download photo from Google Photos base URL."""
    url = f"{base_url}=d"  # =d flag gets full resolution
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        log(f"Failed to download photo: {e}", "ERROR")
        return None


def sync_photos(media_items):
    """Sync photos from Google Photos to Supabase."""
    log(f"Starting sync of {len(media_items)} photos")

    # Fetch existing photos to check for duplicates
    existing = supabase_request("GET", "/photos?select=id,google_photos_id,description,ai_status")
    if existing is None:
        existing = []

    existing_by_google_id = {p.get("google_photos_id"): p for p in existing if p.get("google_photos_id")}

    new_count = 0
    update_count = 0
    skip_count = 0

    for item in media_items:
        google_id = item.get("id")
        filename = item.get("filename", "photo.jpg")
        description = item.get("description")
        base_url = item.get("baseUrl")

        if not google_id or not base_url:
            continue

        if google_id in existing_by_google_id:
            # Case 2: Already in database
            existing_photo = existing_by_google_id[google_id]
            if existing_photo.get("ai_status") == "unknown":
                # Only update if description changed
                old_description = existing_photo.get("description")
                if description and description != old_description:
                    log(f"[UPDATE description] {filename}")
                    supabase_request(
                        "PATCH",
                        f"/photos?google_photos_id=eq.{google_id}",
                        {
                            "google_description": description,
                            # Only update description if it was null before
                            "description": description if old_description is None else old_description,
                        },
                    )
                    update_count += 1
                else:
                    log(f"[SKIP] {filename}")
                    skip_count += 1
            else:
                # Case 3: Already identified or skipped
                log(f"[SKIP] {filename} (already processed)")
                skip_count += 1
        else:
            # Case 1: New photo
            log(f"[NEW] {filename}")

            # Download photo
            photo_bytes = download_photo(base_url)
            if not photo_bytes:
                continue

            # Upload to Supabase Storage
            storage_path = f"{google_id}/{filename}"
            if not upload_to_storage(photo_bytes, storage_path):
                continue

            # Construct public URL
            supabase_url = os.getenv("SUPABASE_URL")
            public_url = f"{supabase_url}/storage/v1/object/public/oio-photos/{storage_path}"

            # Insert into database
            photo_record = {
                "filename": filename,
                "url": public_url,
                "size_bytes": len(photo_bytes),
                "google_photos_id": google_id,
                "google_description": description,
                "description": description,  # Use Google description as initial description
                "ai_status": "unknown",
            }

            result = supabase_request("POST", "/photos", photo_record)
            if result:
                new_count += 1
            else:
                skip_count += 1

    log(f"Sync complete: {new_count} new, {update_count} updated, {skip_count} skipped")
    return new_count, update_count, skip_count


def analyze_with_vision(photo_id, photo_url, description):
    """Run Claude Vision analysis on a photo."""
    try:
        from anthropic import Anthropic
    except ImportError:
        log("anthropic package not installed", "ERROR")
        return None

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        log("Missing ANTHROPIC_API_KEY", "ERROR")
        return None

    client = Anthropic(api_key=api_key)

    # Load OIO context from repo files
    context_parts = []

    # Load team bios
    team_bios_path = REPO_ROOT / "brand" / "Team-Bios.md"
    if team_bios_path.exists():
        try:
            context_parts.append(team_bios_path.read_text()[:1000])
        except Exception:
            pass

    # Load car overviews
    cars_dir = REPO_ROOT / "cars"
    if cars_dir.exists():
        for driver_dir in cars_dir.glob("*"):
            for car_dir in driver_dir.glob("*"):
                overview_path = car_dir / "Overview.md"
                if overview_path.exists():
                    try:
                        context_parts.append(overview_path.read_text()[:500])
                    except Exception:
                        pass

    context = "\n\n".join(context_parts) if context_parts else "OIO Racing fleet information not available"

    prompt = f"""Analyze this photo from an OIO Racing archive.

{context}

The OIO Racing fleet consists of grassroots motorsport vehicles driven by Ian Jennings and his crew in Kansas City, MO. Events include KCRSCCA Rallycross (dirt/gravel, cones, jumps) and Autocross (asphalt, tight cones).

Your task:
1. Identify which car is in the photo using visual cues (color, body shape, wheels, livery, decals, era, unique features)
2. Determine the driver
3. Estimate the event/context (rallycross, autocross, shop, travel, street, portrait, unknown)
4. Provide a confidence score 0.0–1.0

Respond with JSON only, no prose:
{{
  "car": "car name/model or unknown",
  "driver": "first name or unknown",
  "event_context": "rallycross|autocross|shop|travel|street|portrait|unknown",
  "confidence": 0.85,
  "reasoning": "brief explanation of visual clues",
  "visual_notes": "detailed natural language description of what is visible — suitable as an Instagram caption context"
}}

Be conservative. Only assign confidence >= 0.8 if you can clearly identify the specific car and driver from the fleet above."""

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "url",
                                "url": photo_url,
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

        result_text = response.content[0].text
        # Extract JSON from response
        try:
            result = json.loads(result_text)
            return result
        except json.JSONDecodeError:
            log(f"Failed to parse Vision response as JSON: {result_text[:100]}", "ERROR")
            return None

    except Exception as e:
        log(f"Vision analysis failed for {photo_id}: {e}", "ERROR")
        return None


def run_vision_analysis():
    """Run Claude Vision analysis on photos without descriptions."""
    log("Running Claude Vision analysis")

    # Fetch photos needing analysis
    photos_to_analyze = supabase_request(
        "GET",
        "/photos?ai_status=eq.unknown&description=is.null&select=id,url,description",
    )

    if not photos_to_analyze:
        log("No photos needing Vision analysis")
        return

    analyzed_count = 0
    uncertain_count = 0

    for photo in photos_to_analyze:
        photo_id = photo.get("id")
        photo_url = photo.get("url")

        if not photo_id or not photo_url:
            continue

        result = analyze_with_vision(photo_id, photo_url, photo.get("description"))
        if not result:
            continue

        confidence = result.get("confidence", 0)
        if confidence >= 0.8:
            # Update with analysis results
            log(f"[VISION identified {int(confidence*100)}%] {photo_id}")
            supabase_request(
                "PATCH",
                f"/photos?id=eq.{photo_id}",
                {
                    "car": result.get("car"),
                    "description": result.get("visual_notes"),
                    "ai_raw": result,
                    "ai_status": "identified",
                },
            )
            analyzed_count += 1
        else:
            # Keep as unknown but save analysis
            log(f"[VISION uncertain {int(confidence*100)}%] {photo_id}")
            supabase_request(
                "PATCH",
                f"/photos?id=eq.{photo_id}",
                {
                    "ai_raw": result,
                },
            )
            uncertain_count += 1

    log(f"Vision analysis complete: {analyzed_count} identified, {uncertain_count} uncertain")

    # Also mark photos with existing descriptions as identified
    photos_with_desc = supabase_request(
        "GET",
        "/photos?ai_status=eq.unknown&description=not.is.null&select=id",
    )
    if photos_with_desc:
        for photo in photos_with_desc:
            supabase_request(
                "PATCH",
                f"/photos?id=eq.{photo.get('id')}",
                {"ai_status": "identified"},
            )
        log(f"Marked {len(photos_with_desc)} photos with descriptions as identified")


def main():
    """Main sync workflow."""
    log("=== OIO Racing Photo Sync ===")

    # Load credentials
    credentials = load_credentials()

    # Fetch photos from Google Photos
    media_items = fetch_album_photos(credentials)
    if not media_items:
        log("No photos to sync", "WARN")
        return

    # Sync to Supabase
    sync_photos(media_items)

    # Run Vision analysis
    run_vision_analysis()

    log("=== Sync Complete ===")


if __name__ == "__main__":
    main()
