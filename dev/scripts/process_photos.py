#!/usr/bin/env python3
"""
OIO Racing - Unified Photo Pipeline

Polls the OIO Google Photos album, identifies vehicles via Claude Vision,
writes entries to car photo logs, generates captions, and creates PostBridge
drafts — all in a single run.

Workflow per new photo:
  1. Poll the OIO Google Photos album via the Library API
  2. Skip photos already present in any photo log (workflow_status: draft_created
     or any other terminal status)
  3. For new photos:
     a. Fetch baseUrl fresh from Google Photos (never stored — expires)
     b. Run Claude Vision to identify vehicle + generate visual notes
     c. confidence >= 0.8 and known vehicle →
          - Append entry to photos/{driver}/{slug}/photo-log.md (auto_identified)
          - Generate caption with brand voice + vehicle context
          - Create PostBridge draft with baseUrl + '=d' as media URL
          - Update workflow_status to draft_created
     d. confidence < 0.8 OR unknown/other →
          - Append entry to photos/unknown/photo-log.md (needs_identification)
  4. For photos already in photos/unknown/photo-log.md:
     - If the current Google Photos description differs from last_description,
       re-run Claude Vision with the new description as a hint
     - If confidence is now >= 0.8: promote to car log, generate caption,
       create PostBridge draft, remove from unknown log
     - Update last_description regardless of outcome

Environment variables:
  GOOGLE_PHOTOS_CREDENTIALS   JSON with OAuth2 credentials (client_id, client_secret,
                               refresh_token, token_uri)
  GOOGLE_PHOTOS_ALBUM_ID      Album ID from the Google Photos URL
  ANTHROPIC_API_KEY           Claude API key (Vision + caption generation)
  POSTBRIDGE_API_KEY          PostBridge API key
  POSTBRIDGE_ACCOUNT_IDS      Comma-separated social account IDs (optional)

Usage:
  python dev/scripts/process_photos.py
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Ensure the scripts directory is on the path so sibling modules can be imported
sys.path.insert(0, str(Path(__file__).parent))
import photo_log as pl

REPO_ROOT = Path(__file__).parent.parent.parent
AUTO_IDENTIFY_THRESHOLD = 0.8


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
        payload: dict = {"albumId": album_id, "pageSize": 100}
        if page_token:
            payload["pageToken"] = page_token

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as exc:
            log(f"Failed to fetch album photos: {exc}", "ERROR")
            if getattr(getattr(exc, "response", None), "status_code", None) == 403:
                log(
                    "Google Photos album search returned 403. "
                    "Check album sharing / API access policy. Skipping photo fetch.",
                    "WARN",
                )
            return items

        data = resp.json()
        items.extend(data.get("mediaItems", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break

    log(f"Fetched {len(items)} photos from Google Photos album")
    return items


def fetch_media_item(creds: Credentials, media_id: str) -> dict | None:
    """Fetch a single media item from Google Photos by ID (refreshes baseUrl)."""
    url = f"https://photoslibrary.googleapis.com/v1/mediaItems/{media_id}"
    headers = {"Authorization": f"Bearer {creds.token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        log(f"Failed to fetch media item {media_id}: {exc}", "ERROR")
        return None


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
    description_hint = (
        f"\nGoogle Photos description: {source_description}" if source_description else ""
    )

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
# Caption generation
# ---------------------------------------------------------------------------

def _read(path: Path, limit: int) -> str:
    if path.exists():
        return path.read_text()[:limit]
    return ""


def load_brand_voice() -> str:
    return _read(REPO_ROOT / "brand" / "voice-and-tone.md", 3000)


def load_vehicle_context(vehicle_key: str) -> str:
    match = pl.VEHICLE_FOLDERS.get(vehicle_key.lower())
    if not match or vehicle_key == "unknown":
        return ""
    driver, slug = match
    overview = REPO_ROOT / "cars" / driver / slug / "overview.md"
    if not overview.exists():
        overview = REPO_ROOT / "cars" / driver / slug / "Overview.md"
    return _read(overview, 3000)


def load_story_arcs() -> str:
    return _read(REPO_ROOT / "content" / "story-arcs.md", 2000)


def load_approved_captions(vehicle_key: str) -> list[str]:
    examples: list[str] = []
    log_path = pl.log_path_for_vehicle(vehicle_key)
    history_path = log_path.parent / "caption_history.md"
    if not history_path.exists():
        return examples
    for line in history_path.read_text().splitlines():
        line = line.strip()
        if line.startswith("- ") and len(line) > 10:
            examples.append(line[2:])
    return examples[:5]


def generate_caption(
    image_url: str,
    vehicle_key: str,
    source_description: str | None,
    visual_notes: str | None,
    google_id: str,
) -> str | None:
    """
    Generate a polished social caption for a photo using Claude.

    image_url: The fresh baseUrl + '=d' URL (not stored; passed in at runtime).
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        log("anthropic package not installed", "FATAL")
        sys.exit(1)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        log("Missing ANTHROPIC_API_KEY", "FATAL")
        sys.exit(1)

    rough = source_description or visual_notes or ""
    rough_block = (
        f"\nRough caption to improve upon:\n{rough}\n" if rough else ""
    )

    brand_voice = load_brand_voice()
    vehicle_context = load_vehicle_context(vehicle_key)
    story_arcs = load_story_arcs()
    examples = load_approved_captions(vehicle_key)

    examples_block = ""
    if examples:
        examples_block = "\n\nApproved past captions for style reference:\n"
        for i, ex in enumerate(examples, 1):
            examples_block += f"{i}. {ex}\n"

    prompt = f"""You are writing a social media caption for OIO Racing.

OIO Racing is a grassroots motorsports team run by Ian Jennings out of Kansas City, MO.
The brand voice is: practical, enthusiastic, hands-on, mildly irreverent, self-deprecating.
Cars are treated like characters with names and story arcs.

CAPTION RULES — follow these strictly:
- No emoji of any kind
- No em dashes (-- or —)
- Write like a real human, not marketing copy
- 1-4 sentences is ideal; do not pad or over-explain
- Ground every claim in the actual vehicle history and context below
- Improve on the rough caption — do not ignore it, do not just restate it word for word
- Do not invent facts not supported by the context provided
- No fake hype ("thrilling", "exciting", "incredible")

Vehicle: {vehicle_key or "unknown"}

--- Vehicle context ---
{vehicle_context or "No specific vehicle context available."}

--- Season story arcs ---
{story_arcs or "No story arc context available."}

--- Brand voice reference ---
{brand_voice or "See brand/voice-and-tone.md"}{rough_block}{examples_block}

Analyze the photo and write a single polished social media caption.
Output the caption text only — no quotes, no labels, no explanation."""

    client = Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=400,
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

        caption = response.content[0].text.strip()
        if not caption:
            log(f"Empty caption returned for {google_id}", "ERROR")
            return None
        if any(c in caption for c in ["—", "–"]):
            log(f"Caption for {google_id} contains em/en dash — check output", "WARN")
        if any(ord(c) > 127 for c in caption):
            log(f"Caption for {google_id} may contain emoji — check output", "WARN")
        return caption

    except Exception as exc:
        log(f"Caption generation failed for {google_id}: {exc}", "ERROR")
        return None


# ---------------------------------------------------------------------------
# PostBridge draft creation
# ---------------------------------------------------------------------------

def create_postbridge_draft(
    caption: str,
    media_url: str,
    filename: str,
) -> str | None:
    """
    Create a PostBridge draft post.

    media_url: The fresh baseUrl + '=d' download URL.
    Returns the PostBridge draft ID string, or None on failure.
    """
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from postbridge_client import PostBridgeClient, PostBridgeError, PostBridgeAuthError
    except ImportError as exc:
        log(f"Cannot import postbridge_client: {exc}", "FATAL")
        sys.exit(1)

    api_key = os.getenv("POSTBRIDGE_API_KEY")
    if not api_key:
        log("Missing POSTBRIDGE_API_KEY — skipping PostBridge draft creation", "WARN")
        return None

    account_ids_raw = os.getenv("POSTBRIDGE_ACCOUNT_IDS", "")
    account_ids: list[int] = []
    if account_ids_raw:
        try:
            account_ids = [int(x.strip()) for x in account_ids_raw.split(",") if x.strip()]
        except ValueError:
            log("POSTBRIDGE_ACCOUNT_IDS must be comma-separated integers", "WARN")

    try:
        client = PostBridgeClient(api_key=api_key)

        if not account_ids:
            accounts = client.list_accounts()
            account_ids = [a["id"] for a in accounts if "id" in a]
            if not account_ids:
                log("No PostBridge accounts found — cannot create draft", "WARN")
                return None

        draft = client.create_draft(
            caption=caption,
            account_ids=account_ids,
            media_urls=[media_url] if media_url else [],
        )

        draft_id = draft.get("id") or draft.get("data", {}).get("id")
        if not draft_id:
            log(f"PostBridge returned no draft ID for {filename}", "WARN")
            return None

        log(f"[DRAFT CREATED] {filename} → PostBridge draft {draft_id}")
        return str(draft_id)

    except PostBridgeAuthError as exc:
        log(f"PostBridge auth failed: {exc}", "ERROR")
        return None
    except Exception as exc:
        log(f"PostBridge draft creation failed for {filename}: {exc}", "ERROR")
        return None


# ---------------------------------------------------------------------------
# Per-photo pipeline
# ---------------------------------------------------------------------------

def process_new_photo(item: dict, creds: Credentials) -> str:
    """
    Run the full pipeline for a single new album photo.

    Returns the workflow_status written to the log:
      'draft_created', 'auto_identified' (caption failed), or 'needs_identification'.
    """
    photo_id = item["id"]
    filename = item.get("filename", f"photo_{photo_id}.jpg")
    base_url = item.get("baseUrl", "")
    product_url = item.get("productUrl", "")
    description = item.get("description") or None

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

    image_url = f"{base_url}=d" if base_url else ""

    # Identify the vehicle
    vision = identify_photo(filename, image_url, description) if image_url else None
    confidence = float(vision.get("confidence", 0)) if vision else 0.0
    vehicle_key = (
        (vision.get("vehicle_key") or "unknown") if vision else "unknown"
    )
    visual_notes = (vision.get("visual_notes") or "") if vision else ""

    is_identified = (
        vision is not None
        and confidence >= AUTO_IDENTIFY_THRESHOLD
        and vehicle_key not in ("unknown", "other", "")
    )

    if is_identified:
        log_path = pl.log_path_for_vehicle(vehicle_key)
        entry: dict[str, str] = {
            "_filename": filename,
            "google_photos_id": photo_id,
            "google_photos_url": product_url or "none",
            "captured_at": captured_at,
            "source_description": description or "none",
            "last_description": description or "",
            "vehicle_key": vehicle_key,
            "auto_identified_vehicle_key": vehicle_key,
            "identification_confidence": str(round(confidence, 2)),
            "workflow_status": "auto_identified",
            "final_caption": "none",
            "postbridge_draft_id": "none",
            "posted_at": "none",
            "notes": visual_notes or "none",
        }
        pl.append_entry(log_path, entry)
        log(f"[LOGGED] {filename} → {log_path.relative_to(REPO_ROOT)} (auto_identified)")

        # Generate caption
        caption = generate_caption(image_url, vehicle_key, description, visual_notes, photo_id)
        if caption:
            pl.update_entry(log_path, photo_id, {"final_caption": caption})
            log(f"[CAPTION] {filename}")

            # Create PostBridge draft
            draft_id = create_postbridge_draft(caption, image_url, filename)
            if draft_id:
                pl.update_entry(log_path, photo_id, {
                    "postbridge_draft_id": draft_id,
                    "workflow_status": "draft_created",
                })
                log(f"[DRAFT] {filename} → draft_created")
                return "draft_created"
            else:
                # Caption done but draft failed — leave as auto_identified
                return "auto_identified"
        else:
            # Identification succeeded but caption failed — leave as auto_identified
            return "auto_identified"

    else:
        # Low confidence or unknown vehicle → unknown log
        unknown_log = pl.UNKNOWN_LOG
        reason = "Vision unavailable" if not vision else f"{vehicle_key} at {int(confidence * 100)}% confidence"
        log(f"[UNKNOWN] {filename} — {reason}")

        entry = {
            "_filename": filename,
            "google_photos_id": photo_id,
            "google_photos_url": product_url or "none",
            "captured_at": captured_at,
            "source_description": description or "none",
            "last_description": description or "",
            "auto_identified_vehicle_key": vehicle_key,
            "identification_confidence": str(round(confidence, 2)),
            "workflow_status": "needs_identification",
            "notes": visual_notes or "none",
        }
        pl.append_entry(unknown_log, entry)
        log(f"[LOGGED] {filename} → photos/unknown/photo-log.md (needs_identification)")
        return "needs_identification"


def retry_unknown_photo(entry: dict[str, str], creds: Credentials) -> bool:
    """
    Re-evaluate a photo in the unknown log when its description has changed.

    Returns True if the photo was promoted to a car log.
    """
    photo_id = entry["google_photos_id"]
    filename = entry.get("_filename", photo_id)
    old_description = entry.get("last_description", "")

    # Fetch a fresh media item to get current description and a fresh baseUrl
    fresh = fetch_media_item(creds, photo_id)
    if not fresh:
        log(f"[RETRY] Could not fetch fresh item for {photo_id}", "WARN")
        return False

    new_description = fresh.get("description") or ""
    base_url = fresh.get("baseUrl", "")
    product_url = fresh.get("productUrl", "")
    image_url = f"{base_url}=d" if base_url else ""

    if new_description == old_description:
        return False  # No change — nothing to do

    log(f"[RETRY] {filename} — description changed, re-running Vision")

    vision = identify_photo(filename, image_url, new_description) if image_url else None
    confidence = float(vision.get("confidence", 0)) if vision else 0.0
    vehicle_key = (
        (vision.get("vehicle_key") or "unknown") if vision else "unknown"
    )
    visual_notes = (vision.get("visual_notes") or "") if vision else ""

    # Always update last_description in the unknown log, regardless of outcome
    pl.update_entry(pl.UNKNOWN_LOG, photo_id, {"last_description": new_description})

    is_identified = (
        vision is not None
        and confidence >= AUTO_IDENTIFY_THRESHOLD
        and vehicle_key not in ("unknown", "other", "")
    )

    if not is_identified:
        log(f"[RETRY] {filename} — still unidentified ({vehicle_key} at {int(confidence * 100)}%)")
        return False

    # Promoted — append to car log
    log_path = pl.log_path_for_vehicle(vehicle_key)
    meta = fresh.get("mediaMetadata", {})
    creation_time = meta.get("creationTime")
    captured_at = entry.get("captured_at", "none")
    if creation_time:
        try:
            captured_at = datetime.fromisoformat(
                creation_time.replace("Z", "+00:00")
            ).strftime("%Y-%m-%d")
        except ValueError:
            pass

    new_entry: dict[str, str] = {
        "_filename": filename,
        "google_photos_id": photo_id,
        "google_photos_url": product_url or entry.get("google_photos_url", "none"),
        "captured_at": captured_at,
        "source_description": new_description or "none",
        "last_description": new_description,
        "vehicle_key": vehicle_key,
        "auto_identified_vehicle_key": vehicle_key,
        "identification_confidence": str(round(confidence, 2)),
        "workflow_status": "auto_identified",
        "final_caption": "none",
        "postbridge_draft_id": "none",
        "posted_at": "none",
        "notes": visual_notes or "none",
    }
    pl.append_entry(log_path, new_entry)
    log(f"[PROMOTED] {filename} → {log_path.relative_to(REPO_ROOT)} (auto_identified)")

    # Generate caption
    caption = generate_caption(image_url, vehicle_key, new_description, visual_notes, photo_id)
    if caption:
        pl.update_entry(log_path, photo_id, {"final_caption": caption})
        log(f"[CAPTION] {filename}")

        draft_id = create_postbridge_draft(caption, image_url, filename)
        if draft_id:
            pl.update_entry(log_path, photo_id, {
                "postbridge_draft_id": draft_id,
                "workflow_status": "draft_created",
            })
            log(f"[DRAFT] {filename} → draft_created")

    # Remove from unknown log
    pl.remove_entry(pl.UNKNOWN_LOG, photo_id)
    log(f"[REMOVED] {filename} removed from photos/unknown/photo-log.md")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    log("=== OIO Racing Photo Pipeline ===")

    creds = load_credentials()

    # Step 1: Fetch all photos from the OIO album
    media_items = fetch_album_photos(creds)
    if not media_items:
        log("No photos found in the album")
    else:
        # Step 2: Determine which photos are already processed
        known_ids = set(pl.all_entries().keys())
        log(f"Found {len(known_ids)} already-logged photos in brain")

        new_count = 0
        skip_count = 0
        error_count = 0

        for item in media_items:
            photo_id = item.get("id")
            if not photo_id:
                continue

            if photo_id in known_ids:
                skip_count += 1
                continue

            if not item.get("baseUrl"):
                log(f"No baseUrl for {item.get('filename', photo_id)} — skipping", "WARN")
                error_count += 1
                continue

            log(f"[NEW] {item.get('filename', photo_id)}")
            try:
                status = process_new_photo(item, creds)
                known_ids.add(photo_id)
                new_count += 1
                log(f"[DONE] {item.get('filename', photo_id)} → {status}")
            except Exception as exc:
                log(f"Error processing {item.get('filename', photo_id)}: {exc}", "ERROR")
                error_count += 1

        log(f"New photos: {new_count} processed, {skip_count} skipped, {error_count} errors")

    # Step 3: Retry unknown photos whose descriptions have changed
    unknown_entries = pl.entries_by_status("needs_identification")
    if unknown_entries:
        log(f"Checking {len(unknown_entries)} unknown photo(s) for description updates")
        promoted = 0
        for entry in unknown_entries:
            try:
                if retry_unknown_photo(entry, creds):
                    promoted += 1
            except Exception as exc:
                log(f"Error retrying {entry.get('google_photos_id', '?')}: {exc}", "ERROR")
        log(f"Unknown retry: {promoted} promoted")
    else:
        log("No unknown photos to retry")

    log("=== Photo Pipeline Complete ===")


if __name__ == "__main__":
    main()
