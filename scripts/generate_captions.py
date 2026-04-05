#!/usr/bin/env python3
"""
OIO Racing - Caption Generation

Generates polished social media captions for photos that are ready.

A photo is ready for caption generation when:
  - workflow_status is 'auto_identified' or 'needs_triage' with vehicle_key set
  - OR workflow_status is 'metadata_complete'

Context used for each caption:
  - The photo itself (via Claude Vision)
  - Vehicle overview from cars/{driver}/{slug}/overview.md
  - Season story arcs from content/story-arcs.md
  - Brand voice from brand/voice-and-tone.md
  - Content schedule from content/schedule.md
  - Rough caption / source description if available
  - Recent approved captions from caption_history table (for style tuning)

Caption rules (enforced by prompt):
  - No emoji
  - No em dashes
  - Write like a real human
  - Grounded in vehicle history and current context
  - Improve on the rough caption rather than ignore it

Environment variables:
  ANTHROPIC_API_KEY           Claude API key
  SUPABASE_URL                Supabase project URL
  SUPABASE_SERVICE_ROLE_KEY   Supabase service-role key

Usage:
  python scripts/generate_captions.py
  python scripts/generate_captions.py --photo-id <uuid>   # single photo
  python scripts/generate_captions.py --dry-run            # print captions, no write
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).parent.parent

# Supabase statuses that are eligible for caption generation
CAPTION_ELIGIBLE_STATUSES = ["auto_identified", "metadata_complete"]


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
# OIO Brain context loaders
# ---------------------------------------------------------------------------

def load_brand_voice() -> str:
    path = REPO_ROOT / "brand" / "voice-and-tone.md"
    if path.exists():
        return path.read_text()[:3000]
    return ""


def load_vehicle_context(vehicle_key: str) -> str:
    """Return the overview text for the given vehicle_key."""
    if not vehicle_key:
        return ""

    # Map vehicle_key → car slug directory pattern
    key_to_slug = {
        "goblin": ("ian", "mr2-goblin"),
        "dale": ("ian", "celica-dale"),
        "fittycent": ("ian", "fit-fittycent"),
        "nessie": ("ian", "cressida-nessie"),
        "killer-corolla": ("ian", "corolla-killer"),
        "geoffrey": ("ian", "dauphine-geoffrey"),
        "tootie": ("karen", "tootie"),
        "mgb-gt": ("ryan", "mgb-gt"),
        "ae86": ("ryan", "ae86"),
    }

    match = key_to_slug.get(vehicle_key.lower())
    if not match:
        return ""

    driver, slug = match
    overview = REPO_ROOT / "cars" / driver / slug / "overview.md"
    if not overview.exists():
        overview = REPO_ROOT / "cars" / driver / slug / "Overview.md"
    if overview.exists():
        return overview.read_text()[:3000]
    return ""


def load_story_arcs() -> str:
    path = REPO_ROOT / "content" / "story-arcs.md"
    if path.exists():
        return path.read_text()[:2000]
    return ""


def load_content_schedule() -> str:
    path = REPO_ROOT / "content" / "schedule.md"
    if path.exists():
        return path.read_text()[:1500]
    return ""


def load_approved_caption_examples(vehicle_key: str | None, limit: int = 5) -> list[str]:
    """Pull recent approved captions from Supabase caption_history for style examples."""
    filter_part = ""
    if vehicle_key:
        filter_part = f"&photo_id=in.(select id from photos where vehicle_key=eq.{vehicle_key})"

    rows = supabase(
        "GET",
        f"/caption_history?approved=eq.true{filter_part}&order=created_at.desc&limit={limit}&select=caption",
    ) or []

    return [r["caption"] for r in rows if r.get("caption")]


# ---------------------------------------------------------------------------
# Caption generation
# ---------------------------------------------------------------------------

def generate_caption(photo: dict, dry_run: bool = False) -> str | None:
    """
    Generate a polished social caption for a single photo.

    Returns the generated caption text, or None on failure.
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

    photo_id = photo.get("id", "unknown")
    image_url = photo.get("image_url", "")
    vehicle_key = photo.get("vehicle_key") or photo.get("auto_identified_vehicle_key") or ""
    rough_caption = photo.get("rough_caption") or photo.get("source_description") or ""

    # Gather context
    brand_voice = load_brand_voice()
    vehicle_context = load_vehicle_context(vehicle_key)
    story_arcs = load_story_arcs()
    schedule = load_content_schedule()
    examples = load_approved_caption_examples(vehicle_key)

    # Build examples block
    examples_block = ""
    if examples:
        examples_block = "\n\nApproved caption examples (use for style reference only):\n"
        for i, ex in enumerate(examples, 1):
            examples_block += f"{i}. {ex}\n"

    rough_block = f"\nRough caption / description to improve upon:\n{rough_caption}\n" if rough_caption else ""

    prompt = f"""You are writing a social media caption for OIO Racing.

OIO Racing is a grassroots motorsports team run by Ian Jennings out of Kansas City, MO.
The brand voice is: practical, enthusiastic, hands-on, mildly irreverent, self-deprecating.
Cars are treated like characters with names and story arcs.

CAPTION RULES — follow these strictly:
- No emoji of any kind
- No em dashes (—)
- Write like a real human, not marketing copy
- Keep it concise and readable (1-4 sentences is ideal)
- Ground every claim in the actual vehicle history and current context below
- Improve upon the rough caption — do not ignore it, do not just restate it
- Do not invent facts that are not supported by the context provided
- No fake hype. No "thrilling" or "exciting" or "incredible"

Vehicle: {vehicle_key or "unknown"}

--- Vehicle context ---
{vehicle_context or "No specific vehicle context available."}

--- Season story arcs ---
{story_arcs or "No story arc context available."}

--- Content schedule ---
{schedule or "No schedule context available."}

--- Brand voice reference ---
{brand_voice or "See brand/voice-and-tone.md"}
{rough_block}{examples_block}

Analyze the photo and write a single polished social media caption. Output the caption text only — no quotes, no labels, no explanation."""

    client = Anthropic(api_key=api_key)

    try:
        if image_url:
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
        else:
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )

        caption = response.content[0].text.strip()

        # Basic validation
        if not caption:
            log(f"Empty caption returned for {photo_id}", "ERROR")
            return None

        # Warn if rules were violated (don't block, just flag)
        if any(c in caption for c in ["—", "–"]):
            log(f"Caption for {photo_id} contains em/en dash — check output", "WARN")
        if any(ord(c) > 127 for c in caption):
            log(f"Caption for {photo_id} may contain emoji — check output", "WARN")

        return caption

    except Exception as exc:
        log(f"Caption generation failed for {photo_id}: {exc}", "ERROR")
        return None


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def process_photos(photo_id: str | None = None, dry_run: bool = False) -> None:
    """Generate captions for eligible photos."""

    if photo_id:
        photos = supabase("GET", f"/photos?id=eq.{photo_id}&select=*") or []
        if not photos:
            log(f"Photo {photo_id} not found", "ERROR")
            return
    else:
        # Photos eligible for captioning:
        # - auto_identified (vehicle known, needs caption)
        # - metadata_complete (human has triaged and marked ready)
        # Also require vehicle_key to be set
        eligible_filter = "workflow_status=in.(auto_identified,metadata_complete)&caption_status=neq.generated&vehicle_key=not.is.null"
        photos = supabase("GET", f"/photos?{eligible_filter}&select=*") or []

    if not photos:
        log("No photos ready for caption generation")
        return

    log(f"Generating captions for {len(photos)} photo(s)")

    success = 0
    failed = 0

    for photo in photos:
        pid = photo.get("id", "unknown")
        vehicle = photo.get("vehicle_key", "unknown")
        log(f"[CAPTION] {pid[:12]}... ({vehicle})")

        caption = generate_caption(photo, dry_run=dry_run)

        if not caption:
            failed += 1
            continue

        if dry_run:
            print(f"\n--- Caption for {pid[:12]}... ---")
            print(caption)
            print()
            success += 1
            continue

        # Write final_caption to Supabase
        supabase("PATCH", f"/photos?id=eq.{pid}", {
            "final_caption": caption,
            "caption_status": "generated",
            "workflow_status": "caption_generated",
        })

        # Store in caption_history for future style tuning
        supabase("POST", "/caption_history", {
            "photo_id": pid,
            "caption": caption,
            "model": "claude-opus-4-6",
            "approved": False,
        })

        success += 1
        log(f"[DONE] {pid[:12]}... caption saved")

    log(f"Caption generation complete: {success} generated, {failed} failed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate OIO social media captions")
    parser.add_argument("--photo-id", help="Generate caption for a single photo by UUID")
    parser.add_argument("--dry-run", action="store_true", help="Print captions without saving")
    args = parser.parse_args()

    log("=== OIO Caption Generation ===")
    process_photos(photo_id=args.photo_id, dry_run=args.dry_run)
    log("=== Done ===")


if __name__ == "__main__":
    main()
