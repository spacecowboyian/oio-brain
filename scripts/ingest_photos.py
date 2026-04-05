#!/usr/bin/env python3
"""
OIO Racing - Google Photos Ingestion Pipeline

Fetches photos from the configured Google Photos album, stores them in
Supabase, and runs Claude Vision to attempt automatic vehicle identification.

Workflow per photo:
  1. Fetch album contents from Google Photos Library API
  2. Skip photos already in Supabase (dedup on source_photo_id)
  3. Download full-res image, upload to Supabase oio-photos bucket
  4. Insert photo record with workflow_status='ingested'
  5. Run Claude Vision analysis
     - confidence >= 0.8 → workflow_status='auto_identified'
     - confidence <  0.8 → workflow_status='needs_triage', needs_triage=true

Environment variables (all required):
  GOOGLE_PHOTOS_CREDENTIALS   JSON blob: client_id, client_secret, refresh_token, token_uri
  GOOGLE_PHOTOS_ALBUM_ID      Album ID from the Google Photos URL
  ANTHROPIC_API_KEY           Claude API key
  SUPABASE_URL                Supabase project URL
  SUPABASE_SERVICE_ROLE_KEY   Supabase service-role key

Usage:
  python scripts/ingest_photos.py
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

REPO_ROOT = Path(__file__).parent.parent

# Vision confidence threshold for auto-identification
AUTO_IDENTIFY_THRESHOLD = 0.8

# Known OIO vehicles: display name → vehicle_key
VEHICLE_KEYS = {
    "goblin": "goblin",
    "mr2": "goblin",
    "aw11": "goblin",
    "dale": "dale",
    "celica": "dale",
    "fitty cent": "fittycent",
    "fittycent": "fittycent",
    "fit": "fittycent",
    "ge8": "fittycent",
    "tootie": "tootie",
    "suburban": "tootie",
    "nessie": "nessie",
    "cressida": "nessie",
    "killer corolla": "killer-corolla",
    "corolla": "killer-corolla",
    "geoffrey": "geoffrey",
    "dauphine": "geoffrey",
    "mgb": "mgb-gt",
    "mgb gt": "mgb-gt",
    "ae86": "ae86",
}


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def log(message: str, level: str = "INFO") -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {level}: {message}"
    print(line, flush=True)
    if level in ("ERROR", "FATAL"):
        print(line, file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# Google Photos helpers
# ---------------------------------------------------------------------------

def load_credentials() -> Credentials:
    """Load and refresh Google Photos OAuth2 credentials."""
    raw = os.getenv("GOOGLE_PHOTOS_CREDENTIALS")
    if not raw:
        log("Missing GOOGLE_PHOTOS_CREDENTIALS", "FATAL")
        sys.exit(1)

    try:
        creds_dict = json.loads(raw)
    except json.JSONDecodeError as exc:
        log(f"Invalid GOOGLE_PHOTOS_CREDENTIALS JSON: {exc}", "FATAL")
        sys.exit(1)

    creds = Credentials(
        token=None,
        refresh_token=creds_dict.get("refresh_token"),
        token_uri=creds_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=creds_dict.get("client_id"),
        client_secret=creds_dict.get("client_secret"),
    )

    try:
        creds.refresh(Request())
        log("Google Photos credentials refreshed")
    except Exception as exc:
        log(f"Failed to refresh credentials: {exc}", "FATAL")
        sys.exit(1)

    return creds


def fetch_album_photos(creds: Credentials) -> list:
    """Return all media items from the configured Google Photos album."""
    album_id = os.getenv("GOOGLE_PHOTOS_ALBUM_ID")
    if not album_id:
        log("Missing GOOGLE_PHOTOS_ALBUM_ID", "FATAL")
        sys.exit(1)

    items = []
    page_token = None
    url = "https://photoslibrary.googleapis.com/v1/mediaItems:search"
    headers = {"Authorization": f"Bearer {creds.token}"}

    while True:
        payload = {"albumId": album_id, "pageSize": 100}
        if page_token:
            payload["pageToken"] = page_token

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as exc:
            log(f"Failed to fetch album photos: {exc}", "ERROR")
            return items

        data = resp.json()
        items.extend(data.get("mediaItems", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break

    log(f"Fetched {len(items)} photos from Google Photos album")
    return items


def download_photo(base_url: str) -> bytes | None:
    """Download full-resolution photo bytes from a Google Photos base URL."""
    try:
        resp = requests.get(f"{base_url}=d", timeout=30)
        resp.raise_for_status()
        return resp.content
    except requests.RequestException as exc:
        log(f"Failed to download photo: {exc}", "ERROR")
        return None


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

def supabase(method: str, path: str, json_data=None, extra_headers=None) -> list | dict | None:
    """Make a request to the Supabase REST API."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        log("Missing Supabase environment variables", "FATAL")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {key}",
        "apikey": key,
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    if extra_headers:
        headers.update(extra_headers)

    full_url = f"{url}/rest/v1{path}"
    try:
        if method == "GET":
            resp = requests.get(full_url, headers=headers, timeout=30)
        elif method == "POST":
            resp = requests.post(full_url, json=json_data, headers=headers, timeout=30)
        elif method == "PATCH":
            resp = requests.patch(full_url, json=json_data, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        resp.raise_for_status()
        return resp.json() if resp.text else None
    except requests.RequestException as exc:
        log(f"Supabase {method} {path} failed: {exc}", "ERROR")
        return None


def upload_to_storage(photo_bytes: bytes, storage_path: str) -> bool:
    """Upload bytes to Supabase Storage bucket oio-photos."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    headers = {
        "Authorization": f"Bearer {key}",
        "x-upsert": "false",
        "Content-Type": "image/jpeg",
    }
    try:
        resp = requests.post(
            f"{url}/storage/v1/object/oio-photos/{storage_path}",
            data=photo_bytes,
            headers=headers,
            timeout=60,
        )
        resp.raise_for_status()
        return True
    except requests.RequestException as exc:
        log(f"Storage upload failed ({storage_path}): {exc}", "ERROR")
        return False


def storage_public_url(storage_path: str) -> str:
    url = os.getenv("SUPABASE_URL", "")
    return f"{url}/storage/v1/object/public/oio-photos/{storage_path}"


# ---------------------------------------------------------------------------
# Claude Vision identification
# ---------------------------------------------------------------------------

def identify_photo(photo_id: str, image_url: str, source_description: str | None) -> dict | None:
    """
    Run Claude Vision on a photo to identify the OIO vehicle.

    Returns a dict with keys:
      vehicle_key, confidence, event_context, reasoning, visual_notes
    or None on failure.
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        log("anthropic package not installed — skipping Vision analysis", "WARN")
        return None

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        log("Missing ANTHROPIC_API_KEY — skipping Vision analysis", "WARN")
        return None

    client = Anthropic(api_key=api_key)

    # Build OIO fleet context from repo files
    fleet_context = _build_fleet_context()

    description_hint = f"\nGoogle Photos description: {source_description}" if source_description else ""

    prompt = f"""You are analyzing a photo from the OIO Racing archive.

OIO Racing is a grassroots motorsports team based in Kansas City, MO run by Ian Jennings.
Events include KCRSCCA Rallycross (dirt/gravel) and Autocross (asphalt).{description_hint}

Known OIO fleet:
{fleet_context}

Your task:
1. Identify which vehicle is in the photo (if any)
2. Estimate the event context
3. Provide a confidence score 0.0–1.0

Be conservative. Only assign confidence >= 0.8 if you can clearly identify the specific vehicle
from the fleet list above using visible features (color, body shape, wheels, livery, decals, era).

Respond with JSON only — no prose:
{{
  "vehicle_key": "goblin|dale|fittycent|tootie|nessie|killer-corolla|geoffrey|mgb-gt|ae86|other|unknown",
  "confidence": 0.85,
  "event_context": "rallycross|autocross|shop|travel|street|portrait|unknown",
  "reasoning": "brief explanation of visual clues used",
  "visual_notes": "natural language description of what is visible — good as rough caption context"
}}"""

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "url", "url": image_url}},
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        text = response.content[0].text
        try:
            result = json.loads(text)
            return result
        except json.JSONDecodeError:
            log(f"Vision response not valid JSON for {photo_id}: {text[:80]}", "ERROR")
            return None

    except Exception as exc:
        log(f"Vision analysis failed for {photo_id}: {exc}", "ERROR")
        return None


def _build_fleet_context() -> str:
    """Load a compact fleet summary from car overview files."""
    lines = []
    cars_root = REPO_ROOT / "cars"
    if not cars_root.exists():
        return "Fleet context unavailable"

    for driver_dir in sorted(cars_root.iterdir()):
        if not driver_dir.is_dir():
            continue
        for car_dir in sorted(driver_dir.iterdir()):
            if not car_dir.is_dir():
                continue
            overview = car_dir / "overview.md"
            if not overview.exists():
                overview = car_dir / "Overview.md"
            if overview.exists():
                try:
                    text = overview.read_text()[:600]
                    lines.append(f"--- {driver_dir.name}/{car_dir.name} ---\n{text}")
                except Exception:
                    pass

    return "\n\n".join(lines) if lines else "Fleet context unavailable"


# ---------------------------------------------------------------------------
# Ingestion logic
# ---------------------------------------------------------------------------

def ingest_photos(media_items: list) -> dict:
    """
    Ingest new photos from Google Photos into Supabase.

    Returns summary counts.
    """
    log(f"Checking {len(media_items)} album photos for new items")

    # Fetch existing source_photo_ids to avoid duplicates
    existing = supabase("GET", "/photos?select=source_photo_id") or []
    known_ids = {r["source_photo_id"] for r in existing if r.get("source_photo_id")}

    new_count = 0
    skip_count = 0
    error_count = 0

    for item in media_items:
        photo_id = item.get("id")
        filename = item.get("filename", "photo.jpg")
        base_url = item.get("baseUrl")
        description = item.get("description") or None

        if not photo_id or not base_url:
            continue

        if photo_id in known_ids:
            # Check if description was added or changed since last sync
            _maybe_update_description(photo_id, description)
            skip_count += 1
            continue

        log(f"[NEW] {filename} ({photo_id[:12]}...)")

        # Download from Google Photos
        photo_bytes = download_photo(base_url)
        if not photo_bytes:
            error_count += 1
            continue

        # Upload to Supabase Storage
        storage_path = f"{photo_id}/{filename}"
        if not upload_to_storage(photo_bytes, storage_path):
            error_count += 1
            continue

        # Parse capture time from metadata if available
        meta = item.get("mediaMetadata", {})
        creation_time = meta.get("creationTime")
        captured_at = None
        if creation_time:
            try:
                captured_at = datetime.fromisoformat(creation_time.replace("Z", "+00:00")).isoformat()
            except ValueError:
                pass

        supabase_url = os.getenv("SUPABASE_URL", "")
        image_url = storage_public_url(storage_path)
        thumbnail_url = f"{base_url}=w400-h300-no"  # Google Photos thumbnail

        record = {
            "source_photo_id": photo_id,
            "source_album_id": os.getenv("GOOGLE_PHOTOS_ALBUM_ID"),
            "image_url": image_url,
            "thumbnail_url": thumbnail_url,
            "captured_at": captured_at,
            "source_description": description,
            "rough_caption": description,  # seed rough caption from Google description
            "workflow_status": "ingested",
            "needs_triage": True,
        }

        result = supabase("POST", "/photos", record)
        if result:
            new_count += 1
            known_ids.add(photo_id)
        else:
            error_count += 1

    log(f"Ingestion complete: {new_count} new, {skip_count} skipped, {error_count} errors")
    return {"new": new_count, "skipped": skip_count, "errors": error_count}


def _maybe_update_description(photo_id: str, new_description: str | None) -> None:
    """Update source_description if Google Photos added one since last sync."""
    if not new_description:
        return

    existing = supabase("GET", f"/photos?source_photo_id=eq.{photo_id}&select=source_description,rough_caption")
    if not existing:
        return

    row = existing[0] if existing else {}
    if row.get("source_description") != new_description:
        update = {"source_description": new_description}
        # Only seed rough_caption if it hasn't been set by a human
        if not row.get("rough_caption"):
            update["rough_caption"] = new_description
        supabase("PATCH", f"/photos?source_photo_id=eq.{photo_id}", update)


def run_identification() -> dict:
    """
    Run Claude Vision on photos with workflow_status='ingested'.

    Promotes photos to 'auto_identified' or 'needs_triage'.
    """
    log("Running Claude Vision identification")

    photos = supabase("GET", "/photos?workflow_status=eq.ingested&select=id,image_url,source_description") or []

    if not photos:
        log("No photos awaiting identification")
        return {"identified": 0, "triage": 0}

    identified = 0
    triage = 0

    for photo in photos:
        photo_id = photo.get("id")
        image_url = photo.get("image_url")
        description = photo.get("source_description")

        if not photo_id or not image_url:
            continue

        result = identify_photo(photo_id, image_url, description)

        if result is None:
            # Cannot analyze — mark for triage
            supabase("PATCH", f"/photos?id=eq.{photo_id}", {
                "workflow_status": "needs_triage",
                "needs_triage": True,
                "needs_vehicle_assignment": True,
            })
            triage += 1
            continue

        confidence = float(result.get("confidence", 0))
        vehicle_key = result.get("vehicle_key", "unknown")
        visual_notes = result.get("visual_notes", "")

        log(
            f"[VISION] {photo_id[:12]}... → {vehicle_key} "
            f"({int(confidence * 100)}% confidence)"
        )

        if confidence >= AUTO_IDENTIFY_THRESHOLD and vehicle_key not in ("unknown", ""):
            supabase("PATCH", f"/photos?id=eq.{photo_id}", {
                "workflow_status": "auto_identified",
                "auto_identified_vehicle_key": vehicle_key,
                "vehicle_key": vehicle_key,
                "identification_confidence": confidence,
                "needs_triage": False,
                "needs_vehicle_assignment": False,
                # Enrich rough_caption with visual notes if none set
                **({"rough_caption": visual_notes} if visual_notes else {}),
            })
            identified += 1
        else:
            supabase("PATCH", f"/photos?id=eq.{photo_id}", {
                "workflow_status": "needs_triage",
                "auto_identified_vehicle_key": vehicle_key if vehicle_key != "unknown" else None,
                "identification_confidence": confidence,
                "needs_triage": True,
                "needs_vehicle_assignment": True,
                **({"rough_caption": visual_notes} if visual_notes else {}),
            })
            triage += 1

    log(f"Identification complete: {identified} auto-identified, {triage} flagged for triage")
    return {"identified": identified, "triage": triage}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    log("=== OIO Racing Photo Ingestion ===")

    creds = load_credentials()
    media_items = fetch_album_photos(creds)

    if not media_items:
        log("No photos found in album")
        return

    ingest_photos(media_items)
    run_identification()

    log("=== Ingestion Complete ===")


if __name__ == "__main__":
    main()
