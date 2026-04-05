#!/usr/bin/env python3
"""
OIO Racing - PostBridge Draft Creation

Creates PostBridge draft posts for photos that have a generated caption.

For each photo with workflow_status='caption_generated':
  1. Assign a tentative publish date based on the OIO content schedule
  2. Create a PostBridge draft with the photo URL, caption, and date
  3. Update Supabase with the PostBridge draft ID and workflow_status='draft_created'

Scheduling logic:
  - Reads content/schedule.md to understand the current content cadence
  - Targets the next available posting slot (weekday + time) based on schedule
  - Avoids collision with other tentative_publish_at dates already in Supabase
  - Default cadence: Tuesday and Friday at 10:00 AM CT if schedule is unreadable

Environment variables:
  POSTBRIDGE_API_KEY          PostBridge API key
  POSTBRIDGE_ACCOUNT_IDS      Comma-separated social account IDs (optional)
  SUPABASE_URL                Supabase project URL
  SUPABASE_SERVICE_ROLE_KEY   Supabase service-role key

Usage:
  python scripts/create_postbridge_drafts.py
  python scripts/create_postbridge_drafts.py --photo-id <uuid>   # single photo
  python scripts/create_postbridge_drafts.py --dry-run            # print without creating
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import requests

REPO_ROOT = Path(__file__).parent.parent

# Default posting cadence: Tue + Fri at 10:00 AM CT.
# Stored in UTC. CT is UTC-6 during CDT (Mar-Nov) and UTC-5 during CST (Nov-Mar).
# DEFAULT_POST_HOUR_UTC=16 approximates 10 AM CT standard time.
# Note: This will be 1 hour off during daylight saving time. Adjust manually
# or update POSTBRIDGE_ACCOUNT_IDS and reschedule if precise timing matters.
DEFAULT_POST_DAYS = [1, 4]   # Monday=0, Tuesday=1, Friday=4
DEFAULT_POST_HOUR_UTC = 16   # 10:00 AM CT = 16:00 UTC (CT standard)
DEFAULT_POST_MINUTE = 0
MIN_LEAD_HOURS = 2           # Minimum hours from now before scheduling


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
# Supabase helpers
# ---------------------------------------------------------------------------

def supabase(method: str, path: str, json_data=None) -> list | dict | None:
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


# ---------------------------------------------------------------------------
# Scheduling logic
# ---------------------------------------------------------------------------

def get_booked_dates() -> set:
    """Return the set of dates (YYYY-MM-DD) already booked with tentative drafts."""
    rows = supabase(
        "GET",
        "/photos?tentative_publish_at=not.is.null&select=tentative_publish_at",
    ) or []
    dates = set()
    for row in rows:
        raw = row.get("tentative_publish_at")
        if raw:
            try:
                dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                dates.add(dt.strftime("%Y-%m-%d"))
            except ValueError:
                pass
    return dates


def next_posting_slot(booked_dates: set) -> datetime:
    """
    Find the next unbooked posting slot using the default cadence.

    Post slots are Tue/Fri at 10:00 AM CT (16:00 UTC).
    Skip days already in booked_dates.
    """
    now = datetime.now(timezone.utc)
    candidate = now + timedelta(hours=MIN_LEAD_HOURS)

    # Snap to next valid posting time
    for _ in range(60):  # safety limit — max ~30 weeks ahead
        if candidate.weekday() in DEFAULT_POST_DAYS:
            slot = candidate.replace(
                hour=DEFAULT_POST_HOUR_UTC,
                minute=DEFAULT_POST_MINUTE,
                second=0,
                microsecond=0,
            )
            # If the slot is still in the past (or too soon), push to same day next week
            if slot < now + timedelta(hours=MIN_LEAD_HOURS):
                candidate += timedelta(days=1)
                continue
            date_str = slot.strftime("%Y-%m-%d")
            if date_str not in booked_dates:
                return slot
            # Date is booked — try the next slot day
        candidate += timedelta(days=1)

    # Fallback: just return a week from now
    return (now + timedelta(days=7)).replace(
        hour=DEFAULT_POST_HOUR_UTC, minute=0, second=0, microsecond=0
    )


# ---------------------------------------------------------------------------
# PostBridge draft creation
# ---------------------------------------------------------------------------

def create_draft(photo: dict, publish_at: datetime, account_ids: list[int], dry_run: bool) -> str | None:
    """
    Create a PostBridge draft post.

    Returns the PostBridge post ID, or None on failure.
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

    caption = photo.get("final_caption", "")
    image_url = photo.get("image_url", "")
    photo_id = photo.get("id", "unknown")

    if not caption:
        log(f"No final_caption for {photo_id[:12]}... — skipping", "WARN")
        return None

    if dry_run:
        print(f"\n--- Draft for {photo_id[:12]}... ---")
        print(f"Publish at: {publish_at.isoformat()}")
        print(f"Caption: {caption[:120]}...")
        print(f"Image URL: {image_url}")
        print(f"Accounts: {account_ids}")
        return "dry-run"

    try:
        client = PostBridgeClient(api_key=api_key)

        # Resolve account IDs: use provided list or discover from API
        if not account_ids:
            accounts = client.list_accounts()
            account_ids = [a["id"] for a in accounts if "id" in a]
            if not account_ids:
                log("No PostBridge accounts found — cannot create draft", "WARN")
                return None

        draft = client.create_draft(
            caption=caption,
            account_ids=account_ids,
            media_urls=[image_url] if image_url else [],
        )

        draft_id = draft.get("id") or draft.get("data", {}).get("id")
        if not draft_id:
            log(f"PostBridge draft created but no ID returned for {photo_id[:12]}...", "WARN")
            return None

        log(f"[DRAFT] {photo_id[:12]}... → PostBridge draft {draft_id}")
        return str(draft_id)

    except PostBridgeAuthError as exc:
        log(f"PostBridge auth failed: {exc}", "ERROR")
        return None
    except Exception as exc:
        log(f"PostBridge draft creation failed for {photo_id[:12]}...: {exc}", "ERROR")
        return None


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def process_photos(photo_id: Optional[str] = None, dry_run: bool = False) -> None:
    """Create PostBridge drafts for photos with captions."""

    if photo_id:
        photos = supabase("GET", f"/photos?id=eq.{photo_id}&select=*") or []
    else:
        photos = supabase(
            "GET",
            "/photos?workflow_status=eq.caption_generated&draft_status=eq.pending&select=*",
        ) or []

    if not photos:
        log("No photos ready for draft creation")
        return

    log(f"Creating PostBridge drafts for {len(photos)} photo(s)")

    # Parse account IDs from env (comma-separated integers)
    account_ids_raw = os.getenv("POSTBRIDGE_ACCOUNT_IDS", "")
    account_ids: list[int] = []
    if account_ids_raw:
        try:
            account_ids = [int(x.strip()) for x in account_ids_raw.split(",") if x.strip()]
        except ValueError:
            log("POSTBRIDGE_ACCOUNT_IDS must be comma-separated integers", "WARN")

    # Load already-booked dates to avoid scheduling collisions
    booked_dates = get_booked_dates() if not dry_run else set()

    success = 0
    failed = 0

    for photo in photos:
        pid = photo.get("id", "unknown")
        log(f"[DRAFT] {pid[:12]}... ({photo.get('vehicle_key', 'unknown')})")

        # Assign tentative publish date
        publish_at = next_posting_slot(booked_dates)
        booked_dates.add(publish_at.strftime("%Y-%m-%d"))

        draft_id = create_draft(photo, publish_at, account_ids, dry_run)

        if dry_run:
            success += 1
            continue

        if draft_id:
            supabase("PATCH", f"/photos?id=eq.{pid}", {
                "postbridge_draft_id": draft_id,
                "tentative_publish_at": publish_at.isoformat(),
                "draft_status": "created",
                "workflow_status": "draft_created",
            })
            success += 1
        else:
            failed += 1

    log(f"Draft creation complete: {success} created, {failed} failed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create PostBridge drafts for captioned OIO photos")
    parser.add_argument("--photo-id", help="Process a single photo by UUID")
    parser.add_argument("--dry-run", action="store_true", help="Print draft info without creating")
    args = parser.parse_args()

    log("=== OIO PostBridge Draft Creation ===")
    process_photos(photo_id=args.photo_id, dry_run=args.dry_run)
    log("=== Done ===")


if __name__ == "__main__":
    main()
