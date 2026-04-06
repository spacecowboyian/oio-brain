#!/usr/bin/env python3
"""
OIO Racing - Google Photos Ingestion Pipeline

Fetches photos from the configured Google Photos album, uploads binaries to
Supabase Storage, runs Claude Vision for vehicle identification, and logs
all metadata into the appropriate photo-log.md file in the OIO brain.

Workflow per new photo:
  1. Fetch album contents from Google Photos Library API
  2. Scan all photos/{driver}/{vehicle}/photo-log.md files to find already-ingested IDs
  3. For new photos:
     a. Download full-res image from Google Photos
     b. Upload binary to Supabase oio-photos bucket
     c. Run Claude Vision to identify vehicle + generate visual notes
     d. Write a photo entry to the appropriate photo-log.md:
        - confidence >= 0.8  → photos/{driver}/{slug}/photo-log.md, status=auto_identified
        - confidence <  0.8  → photos/triage/photo-log.md, status=needs_triage

After the script runs, the calling workflow commits and pushes any changed
photo-log.md files back to the repo.

Environment variables:
  GOOGLE_PHOTOS_CREDENTIALS   JSON: client_id, client_secret, refresh_token, token_uri
  GOOGLE_PHOTOS_ALBUM_ID      Album ID from the Google Photos URL
  ANTHROPIC_API_KEY           Claude API key (for Vision analysis)
  SUPABASE_URL                Supabase project URL (storage only)
  SUPABASE_SERVICE_ROLE_KEY   Supabase service-role key (storage only)

Usage:
  python dev/scripts/ingest_photos.py
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Ensure the scripts directory is on the path so photo_log can be imported
sys.path.insert(0, str(Path(__file__).parent))
import photo_log as pl

REPO_ROOT = Path(__file__).parent.parent
AUTO_IDENTIFY_THRESHOLD = 0.8
SELECTED_PHOTOS_PATH = REPO_ROOT / "intake" / "selected-photos.json"
REQUIRED_SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]


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

    # Use scopes stored in the credentials JSON when available; otherwise fall
    # back to the required scopes so the intent is explicit.
    stored_scopes = creds_dict.get("scopes") or REQUIRED_SCOPES

    creds = Credentials(
        token=None,
        refresh_token=creds_dict.get("refresh_token"),
        token_uri=creds_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=creds_dict.get("client_id"),
        client_secret=creds_dict.get("client_secret"),
        scopes=stored_scopes,
    )

    try:
        creds.refresh(Request())
        log("Google Photos credentials refreshed")
    except Exception as exc:
        log(f"Failed to refresh credentials: {exc}", "FATAL")
        sys.exit(1)

    # Early scope validation — catch missing photoslibrary scope before the
    # first API call so the failure message is unambiguous.
    if creds.scopes:
        missing = [s for s in REQUIRED_SCOPES if s not in creds.scopes]
        if missing:
            log(
                f"OAuth token is missing required scope(s): {missing}. "
                "Re-generate GOOGLE_PHOTOS_CREDENTIALS by running "
                "'python dev/scripts/auth_google_photos.py' locally, "
                "then update the GitHub repository secret.",
                "FATAL",
            )
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
            # 403 indicates a policy/access constraint, not an empty album.
            if getattr(exc.response, "status_code", None) == 403:
                raise RuntimeError(
                    "Google Photos album search returned 403 (Forbidden). "
                    "The OAuth credentials are missing the 'photoslibrary.readonly' scope "
                    "or GOOGLE_PHOTOS_ALBUM_ID does not belong to the authenticated account. "
                    "Re-generate GOOGLE_PHOTOS_CREDENTIALS by running "
                    "'python dev/scripts/auth_google_photos.py' locally, "
                    "then update the GitHub repository secret."
                ) from exc
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
        resp = requests.get(f"{base_url}=d", timeout=60)
        resp.raise_for_status()
        return resp.content
    except requests.RequestException as exc:
        log(f"Failed to download photo: {exc}", "ERROR")
        return None


def load_selected_photos() -> list[dict]:
    """
    Load pending selected photo items from intake/selected-photos.json.
    """
    if not SELECTED_PHOTOS_PATH.exists():
        return []

    try:
        data = json.loads(SELECTED_PHOTOS_PATH.read_text())
    except Exception as exc:
        log(f"Failed to read {SELECTED_PHOTOS_PATH}: {exc}", "ERROR")
        return []

    sessions = data.get("sessions", [])
    pending: list[dict] = []
    for session in sessions:
        for item in session.get("items", []):
            if item.get("status") == "ingested" or item.get("processed_at"):
                continue
            if item.get("id"):
                pending.append(item)

    log(f"Loaded {len(pending)} pending selected photos from intake/selected-photos.json")
    return pending


def fetch_media_item_by_id(creds: Credentials, media_id: str) -> dict | None:
    """
    Fetch a single media item from Google Photos by media item id.
    """
    url = f"https://photoslibrary.googleapis.com/v1/mediaItems/{media_id}"
    headers = {"Authorization": f"Bearer {creds.token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        log(f"Failed to fetch selected media item {media_id}: {exc}", "ERROR")
        return None


def mark_selected_photos_processed(processed_ids: set[str]) -> None:
    """
    Mark selected photo items as ingested after successful processing.
    """
    if not processed_ids or not SELECTED_PHOTOS_PATH.exists():
        return

    try:
        data = json.loads(SELECTED_PHOTOS_PATH.read_text())
    except Exception as exc:
        log(f"Failed to update {SELECTED_PHOTOS_PATH}: {exc}", "ERROR")
        return

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    updated = 0
    for session in data.get("sessions", []):
        for item in session.get("items", []):
            item_id = item.get("id")
            if item_id in processed_ids:
                item["status"] = "ingested"
                item["processed_at"] = now
                updated += 1
        session_items = session.get("items", [])
        if session_items and all(
            i.get("status") == "ingested" or i.get("processed_at") for i in session_items
        ):
            session["processed"] = True

    data["last_updated"] = now
    SELECTED_PHOTOS_PATH.write_text(json.dumps(data, indent=2) + "\n")
    log(f"Marked {updated} selected photos as ingested in intake/selected-photos.json")


# ---------------------------------------------------------------------------
# Supabase Storage helpers (binaries only — no DB)
# ---------------------------------------------------------------------------

def upload_to_storage(photo_bytes: bytes, storage_path: str) -> bool:
    """Upload photo bytes to the Supabase oio-photos storage bucket."""
    supabase_url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not key:
        log("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY", "FATAL")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {key}",
        "x-upsert": "false",
        "Content-Type": "image/jpeg",
    }
    try:
        resp = requests.post(
            f"{supabase_url}/storage/v1/object/oio-photos/{storage_path}",
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
    """Return the public URL for a file in Supabase Storage."""
    url = os.getenv("SUPABASE_URL", "")
    return f"{url}/storage/v1/object/public/oio-photos/{storage_path}"


# ---------------------------------------------------------------------------
# Claude Vision identification
# ---------------------------------------------------------------------------

def identify_photo(
    filename: str,
    image_url: str,
    source_description: str | None,
) -> dict | None:
    """
    Run Claude Vision to identify the OIO vehicle in a photo.

    Returns a dict with keys: vehicle_key, confidence, event_context,
    reasoning, visual_notes — or None on failure.
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
    fleet_context = _build_fleet_context()
    description_hint = f"\nGoogle Photos description: {source_description}" if source_description else ""

    prompt = f"""You are analyzing a photo from the OIO Racing archive.

OIO Racing is a grassroots motorsports team based in Kansas City, MO run by Ian Jennings.
Events include KCRSCCA Rallycross (dirt/gravel) and Autocross (asphalt, cones).{description_hint}

Known OIO fleet:
{fleet_context}

Your task:
1. Identify which vehicle is in the photo (if any)
2. Estimate the event context
3. Provide a confidence score 0.0-1.0

Be conservative. Only assign confidence >= 0.8 if you can clearly identify the specific vehicle
from the fleet list above using visible features: color, body shape, wheels, livery, decals.

Respond with JSON only — no prose:
{{
  "vehicle_key": "goblin|dale|fittycent|tootie|nessie|killer-corolla|geoffrey|mgb-gt|ae86|other|unknown",
  "confidence": 0.85,
  "event_context": "rallycross|autocross|shop|travel|street|portrait|unknown",
  "reasoning": "brief explanation of visual clues used",
  "visual_notes": "natural language description suitable as a rough caption seed"
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

        text = response.content[0].text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            log(f"Vision response not valid JSON for {filename}: {text[:80]}", "ERROR")
            return None

    except Exception as exc:
        log(f"Vision analysis failed for {filename}: {exc}", "ERROR")
        return None


def _build_fleet_context() -> str:
    """Load a compact fleet summary from car overview files in the brain."""
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
# Main ingestion logic
# ---------------------------------------------------------------------------

def ingest(media_items: list) -> dict:
    """
    Ingest new photos from Google Photos into Supabase Storage + photo-log.md files.
    """
    log(f"Checking {len(media_items)} album photos")

    # Load all already-ingested google_photos_ids by scanning photo-log.md files
    known_ids = set(pl.all_entries().keys())
    log(f"Found {len(known_ids)} already-ingested photos in brain")

    new_count = 0
    skip_count = 0
    error_count = 0
    processed_ids: set[str] = set()

    for item in media_items:
        photo_id = item.get("id")
        filename = item.get("filename", f"photo_{photo_id}.jpg")
        base_url = item.get("baseUrl")
        description = item.get("description") or None

        if not photo_id or not base_url:
            continue

        if photo_id in known_ids:
            # Check if a description was added in Google Photos since last sync
            _maybe_update_description(photo_id, description)
            skip_count += 1
            continue

        log(f"[NEW] {filename}")

        # Download from Google Photos
        photo_bytes = download_photo(base_url)
        if not photo_bytes:
            error_count += 1
            continue

        # Upload binary to Supabase Storage
        storage_path = f"{photo_id}/{filename}"
        if not upload_to_storage(photo_bytes, storage_path):
            error_count += 1
            continue

        image_url = storage_public_url(storage_path)
        thumbnail_url = f"{base_url}=w400-h300-no"

        # Parse capture time
        meta = item.get("mediaMetadata", {})
        creation_time = meta.get("creationTime")
        captured_at = "none"
        if creation_time:
            try:
                captured_at = datetime.fromisoformat(
                    creation_time.replace("Z", "+00:00")
                ).strftime("%Y-%m-%d")
            except ValueError:
                pass

        # Run Claude Vision
        vision = identify_photo(filename, image_url, description)
        confidence = float(vision.get("confidence", 0)) if vision else 0.0
        vehicle_key = (vision.get("vehicle_key", "unknown") if vision else "unknown") or "unknown"
        visual_notes = (vision.get("visual_notes", "") if vision else "") or ""

        # Determine workflow status and log destination
        if vision and confidence >= AUTO_IDENTIFY_THRESHOLD and vehicle_key not in ("unknown", "other", ""):
            workflow_status = "auto_identified"
            log_path = pl.log_path_for_vehicle(vehicle_key)
        else:
            workflow_status = "needs_triage"
            log_path = pl.TRIAGE_LOG
            if vision:
                log(
                    f"[TRIAGE] {filename} — {vehicle_key} at {int(confidence*100)}% confidence",
                )
            else:
                log(f"[TRIAGE] {filename} — Vision unavailable")

        # Build the photo entry
        entry: dict[str, str] = {
            "_filename": filename,
            "google_photos_id": photo_id,
            "supabase_url": image_url,
            "thumbnail_url": thumbnail_url,
            "captured_at": captured_at,
            "source_description": description or "none",
            "rough_caption": description or "none",
            "vehicle_key": vehicle_key if workflow_status == "auto_identified" else "none",
            "auto_identified_vehicle_key": vehicle_key,
            "identification_confidence": str(round(confidence, 2)),
            "workflow_status": workflow_status,
            "final_caption": "none",
            "postbridge_draft_id": "none",
            "tentative_publish_at": "none",
            "posted_at": "none",
            "notes": visual_notes or "none",
        }

        pl.append_entry(log_path, entry)
        known_ids.add(photo_id)
        processed_ids.add(photo_id)
        new_count += 1
        log(f"[LOGGED] {filename} → {log_path.relative_to(REPO_ROOT)} ({workflow_status})")

    log(f"Ingestion complete: {new_count} new, {skip_count} skipped, {error_count} errors")
    mark_selected_photos_processed(processed_ids)
    return {"new": new_count, "skipped": skip_count, "errors": error_count}


def _maybe_update_description(google_photos_id: str, new_description: str | None) -> None:
    """
    If Google Photos has a description that differs from what's in the brain,
    update source_description in the photo-log.md entry.
    """
    if not new_description:
        return

    existing = pl.all_entries().get(google_photos_id, {})
    old_description = existing.get("source_description", "none")
    if old_description == new_description:
        return

    log_path_str = existing.get("_log_path")
    if not log_path_str:
        return

    updates = {"source_description": new_description}
    # Only seed rough_caption if it's still none
    if existing.get("rough_caption", "none") in ("none", ""):
        updates["rough_caption"] = new_description

    pl.update_entry(Path(log_path_str), google_photos_id, updates)
    log(f"[UPDATE description] {google_photos_id}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    log("=== OIO Racing Photo Ingestion ===")

    creds = load_credentials()
    selected_items = load_selected_photos()

    media_items: list[dict] = []
    if selected_items:
        for selected in selected_items:
            media = fetch_media_item_by_id(creds, selected["id"])
            if media:
                # Preserve any custom description captured during picker selection.
                if selected.get("description"):
                    media["description"] = selected["description"]
                media_items.append(media)
        log(f"Using {len(media_items)} selected photos for ingestion")
    else:
        media_items = fetch_album_photos(creds)
        if not media_items:
            log("No photos found from selected-photos.json or album polling")
            return

    ingest(media_items)
    log("=== Ingestion Complete ===")


if __name__ == "__main__":
    main()
