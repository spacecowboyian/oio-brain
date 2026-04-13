#!/usr/bin/env python3
"""
OIO Racing - PostBridge Draft Creation

Creates PostBridge draft posts for photos that have a generated caption,
reading workflow state from photo-log.md files in the OIO brain and writing
the PostBridge draft ID and tentative publish date back to those files.

A photo is eligible when workflow_status is 'caption_generated'.

Scheduling logic:
  - Default cadence: Tuesday and Friday at 10:00 AM CT (approximated as 16:00 UTC)
  - Skips any date already used by another tentative_publish_at in the brain
  - Looks ahead up to 30 weeks to find an open slot

After creating each draft, the script updates:
  - postbridge_draft_id
  - tentative_publish_at
  - workflow_status → 'draft_created'

The calling workflow commits and pushes the photo-log.md changes.

Environment variables:
  POSTBRIDGE_API_KEY      PostBridge API key
  POSTBRIDGE_ACCOUNT_IDS  Comma-separated social account IDs (optional)

Usage:
  python dev/scripts/create_postbridge_drafts.py
  python dev/scripts/create_postbridge_drafts.py --google-id <id>   # single photo
  python dev/scripts/create_postbridge_drafts.py --dry-run           # print, no create
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
import photo_log as pl

REPO_ROOT = Path(__file__).parent.parent.parent

# Default posting cadence: Tuesday (1) and Friday (4) at 10:00 AM CT.
# CT is UTC-6 during CDT (Mar-Nov) and UTC-5 during CST (Nov-Mar).
# 16:00 UTC approximates 10:00 AM CST. During CDT it will be 11:00 AM CT.
# Adjust POSTBRIDGE_POST_HOUR_UTC env var to override.
DEFAULT_POST_DAYS = [1, 4]
DEFAULT_POST_HOUR_UTC = int(os.environ.get("POSTBRIDGE_POST_HOUR_UTC", "16"))
MIN_LEAD_HOURS = 2


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
# Scheduling helpers
# ---------------------------------------------------------------------------

def get_booked_dates() -> set[str]:
    """Return the set of dates (YYYY-MM-DD) already booked in the brain."""
    booked: set[str] = set()
    for entry in pl.all_entries().values():
        raw = entry.get("tentative_publish_at", "none")
        if raw and raw != "none":
            try:
                date_part = raw.split("T")[0]
                booked.add(date_part)
            except Exception:
                pass
    return booked


def next_posting_slot(booked_dates: set[str]) -> datetime:
    """
    Return the next unbooked posting slot (Tue/Fri at DEFAULT_POST_HOUR_UTC UTC).
    """
    now = datetime.now(timezone.utc)
    candidate = now + timedelta(hours=MIN_LEAD_HOURS)

    for _ in range(365):  # safety cap — search up to ~1 year
        if candidate.weekday() in DEFAULT_POST_DAYS:
            slot = candidate.replace(
                hour=DEFAULT_POST_HOUR_UTC,
                minute=0,
                second=0,
                microsecond=0,
            )
            if slot >= now + timedelta(hours=MIN_LEAD_HOURS):
                date_str = slot.strftime("%Y-%m-%d")
                if date_str not in booked_dates:
                    return slot
        candidate += timedelta(days=1)

    # Fallback: 1 week from now
    return (now + timedelta(days=7)).replace(
        hour=DEFAULT_POST_HOUR_UTC, minute=0, second=0, microsecond=0
    )


# ---------------------------------------------------------------------------
# PostBridge draft creation
# ---------------------------------------------------------------------------

def create_draft(entry: dict[str, str], publish_at: datetime, account_ids: list[int], dry_run: bool) -> str | None:
    """
    Create a PostBridge draft for the given photo entry.

    Returns the PostBridge post ID string, or None on failure.
    """
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        from postbridge_client import PostBridgeClient, PostBridgeError, PostBridgeAuthError
    except ImportError as exc:
        log(f"Cannot import postbridge_client: {exc}", "FATAL")
        sys.exit(1)

    api_key = os.getenv("POSTBRIDGE_API_KEY")
    if not api_key:
        log("Missing POSTBRIDGE_API_KEY — skipping PostBridge draft creation", "WARN")
        return None

    caption = entry.get("final_caption", "")
    image_url = entry.get("supabase_url", "")
    filename = entry.get("_filename", entry.get("google_photos_id", "unknown"))

    if not caption or caption == "none":
        log(f"No final_caption for {filename} — skipping", "WARN")
        return None

    if dry_run:
        print(f"\n--- Draft for {filename} ---")
        print(f"Tentative publish: {publish_at.strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"Caption: {caption[:120]}...")
        print(f"Image URL: {image_url}")
        print(f"Accounts: {account_ids}")
        return "dry-run"

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
            media_urls=[image_url] if image_url and image_url != "none" else [],
        )

        draft_id = draft.get("id") or draft.get("data", {}).get("id")
        if not draft_id:
            log(f"PostBridge returned no draft ID for {filename}", "WARN")
            return None

        log(f"[DRAFT] {filename} → PostBridge draft {draft_id}")
        return str(draft_id)

    except PostBridgeAuthError as exc:
        log(f"PostBridge auth failed: {exc}", "ERROR")
        return None
    except Exception as exc:
        log(f"PostBridge draft creation failed for {filename}: {exc}", "ERROR")
        return None


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def process(google_id: Optional[str] = None, dry_run: bool = False) -> None:
    """Create PostBridge drafts for photos with captions."""

    if google_id:
        entry = pl.all_entries().get(google_id)
        if not entry:
            log(f"Photo with google_photos_id={google_id} not found in brain", "ERROR")
            return
        photos = [entry]
    else:
        photos = pl.entries_by_status("caption_generated")

    if not photos:
        log("No photos ready for draft creation")
        return

    log(f"Creating PostBridge drafts for {len(photos)} photo(s)")

    account_ids_raw = os.getenv("POSTBRIDGE_ACCOUNT_IDS", "")
    account_ids: list[int] = []
    if account_ids_raw:
        try:
            account_ids = [int(x.strip()) for x in account_ids_raw.split(",") if x.strip()]
        except ValueError:
            log("POSTBRIDGE_ACCOUNT_IDS must be comma-separated integers", "WARN")

    booked_dates = get_booked_dates() if not dry_run else set()

    success = 0
    failed = 0

    for entry in photos:
        filename = entry.get("_filename", entry.get("google_photos_id", "unknown"))
        vehicle = entry.get("vehicle_key", "unknown")
        gid = entry.get("google_photos_id", "unknown")
        log(f"[DRAFT] {filename} ({vehicle})")

        publish_at = next_posting_slot(booked_dates)
        if not dry_run:
            booked_dates.add(publish_at.strftime("%Y-%m-%d"))

        draft_id = create_draft(entry, publish_at, account_ids, dry_run)

        if dry_run:
            success += 1
            continue

        if draft_id:
            log_path = Path(entry["_log_path"])
            pl.update_entry(log_path, gid, {
                "postbridge_draft_id": draft_id,
                "tentative_publish_at": publish_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "workflow_status": "draft_created",
            })
            success += 1
        else:
            failed += 1

    log(f"Draft creation complete: {success} created, {failed} failed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create PostBridge drafts for captioned OIO photos")
    parser.add_argument("--google-id", help="Process a single photo by Google Photos ID")
    parser.add_argument("--dry-run", action="store_true", help="Print draft info without creating")
    args = parser.parse_args()

    log("=== OIO PostBridge Draft Creation ===")
    process(google_id=args.google_id, dry_run=args.dry_run)
    log("=== Done ===")


if __name__ == "__main__":
    main()
