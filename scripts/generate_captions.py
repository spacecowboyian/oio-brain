#!/usr/bin/env python3
"""
OIO Racing - Caption Generation

Generates polished social media captions for photos that are ready, reading
workflow state from photo-log.md files in the OIO brain and writing results
back to those same files.

A photo is eligible for caption generation when:
  - workflow_status is 'auto_identified' (vehicle already known)
  - OR workflow_status is 'metadata_complete' (human triaged, vehicle_key set)

Context used per caption:
  - The photo (via Claude Vision/URL)
  - Vehicle overview from cars/{driver}/{slug}/overview.md
  - Season story arcs from content/story-arcs.md
  - Brand voice from brand/voice-and-tone.md
  - Content schedule from content/schedule.md
  - rough_caption / source_description from the photo-log entry
  - Recent approved captions from caption_history.md for style tuning

Caption rules (enforced by prompt):
  - No emoji
  - No em dashes
  - Write like a real human
  - Grounded in vehicle history and current context
  - Improve on the rough caption rather than ignore it

After generation, the script writes final_caption and updates workflow_status
to 'caption_generated' in the photo-log.md. The calling workflow commits and
pushes the changes.

Environment variables:
  ANTHROPIC_API_KEY   Claude API key

Usage:
  python scripts/generate_captions.py
  python scripts/generate_captions.py --google-id <google_photos_id>  # single photo
  python scripts/generate_captions.py --dry-run                         # print, no save
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import photo_log as pl

REPO_ROOT = Path(__file__).parent.parent

ELIGIBLE_STATUSES = ("auto_identified", "metadata_complete")

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
# OIO Brain context loaders
# ---------------------------------------------------------------------------

def _read(path: Path, limit: int) -> str:
    if path.exists():
        return path.read_text()[:limit]
    return ""


def load_brand_voice() -> str:
    return _read(REPO_ROOT / "brand" / "voice-and-tone.md", 3000)


def load_vehicle_context(vehicle_key: str) -> str:
    key_to_path = {
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
    match = key_to_path.get(vehicle_key.lower(), ())
    if not match:
        return ""
    driver, slug = match
    overview = REPO_ROOT / "cars" / driver / slug / "overview.md"
    if not overview.exists():
        overview = REPO_ROOT / "cars" / driver / slug / "Overview.md"
    return _read(overview, 3000)


def load_story_arcs() -> str:
    return _read(REPO_ROOT / "content" / "story-arcs.md", 2000)


def load_content_schedule() -> str:
    return _read(REPO_ROOT / "content" / "schedule.md", 1500)


def load_approved_captions(vehicle_key: str) -> list[str]:
    """
    Read approved captions from caption_history.md for style examples.

    The caption_history.md file lives at photos/{driver}/{slug}/caption_history.md
    and contains past approved captions as a simple bulleted list.
    """
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


# ---------------------------------------------------------------------------
# Caption generation
# ---------------------------------------------------------------------------

def generate_caption(entry: dict[str, str]) -> str | None:
    """
    Generate a polished social caption for a single photo entry.

    Returns the caption text, or None on failure.
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

    google_id = entry.get("google_photos_id", "unknown")
    image_url = entry.get("supabase_url", "")
    vehicle_key = (entry.get("vehicle_key") or "").strip()
    if vehicle_key in ("none", ""):
        vehicle_key = entry.get("auto_identified_vehicle_key", "unknown") or "unknown"

    rough_caption = entry.get("rough_caption", "none")
    if rough_caption in ("none", ""):
        rough_caption = entry.get("source_description", "none")
    rough_block = (
        f"\nRough caption to improve upon:\n{rough_caption}\n"
        if rough_caption not in ("none", "")
        else ""
    )

    brand_voice = load_brand_voice()
    vehicle_context = load_vehicle_context(vehicle_key)
    story_arcs = load_story_arcs()
    schedule = load_content_schedule()
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

--- Content schedule ---
{schedule or "No schedule context available."}

--- Brand voice reference ---
{brand_voice or "See brand/voice-and-tone.md"}{rough_block}{examples_block}

Analyze the photo and write a single polished social media caption.
Output the caption text only — no quotes, no labels, no explanation."""

    client = Anthropic(api_key=api_key)

    try:
        if image_url and image_url != "none":
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
# Main workflow
# ---------------------------------------------------------------------------

def process(google_id: str | None = None, dry_run: bool = False) -> None:
    """Generate captions for eligible photos and update photo-log.md files."""

    if google_id:
        entry = pl.all_entries().get(google_id)
        if not entry:
            log(f"Photo with google_photos_id={google_id} not found in brain", "ERROR")
            return
        photos = [entry]
    else:
        photos = pl.entries_by_status(*ELIGIBLE_STATUSES)

    if not photos:
        log("No photos ready for caption generation")
        return

    log(f"Generating captions for {len(photos)} photo(s)")
    success = 0
    failed = 0

    for entry in photos:
        gid = entry.get("google_photos_id", "unknown")
        vehicle = entry.get("vehicle_key", "unknown")
        filename = entry.get("_filename", gid)
        log(f"[CAPTION] {filename} ({vehicle})")

        caption = generate_caption(entry)
        if not caption:
            failed += 1
            continue

        if dry_run:
            print(f"\n--- Caption for {filename} ---")
            print(caption)
            print()
            success += 1
            continue

        # Update photo-log.md
        log_path = Path(entry["_log_path"])
        updated = pl.update_entry(log_path, gid, {
            "final_caption": caption,
            "workflow_status": "caption_generated",
        })
        if updated:
            success += 1
            log(f"[DONE] {filename} — caption saved to {log_path.relative_to(REPO_ROOT)}")
        else:
            log(f"Failed to update photo-log for {gid}", "ERROR")
            failed += 1

    log(f"Caption generation complete: {success} generated, {failed} failed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate OIO social media captions")
    parser.add_argument(
        "--google-id",
        help="Process a single photo by Google Photos ID",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print captions without saving",
    )
    args = parser.parse_args()

    log("=== OIO Caption Generation ===")
    process(google_id=args.google_id, dry_run=args.dry_run)
    log("=== Done ===")


if __name__ == "__main__":
    main()
