#!/usr/bin/env python3
"""
OIO Racing - YouTube Transcript Fetcher
Fetches auto-generated YouTube transcripts for videos listed in OIO-Video-Catalog.md.

Usage:
  python scripts/fetch_transcripts.py           # Fetch only new (unprocessed) transcripts
  python scripts/fetch_transcripts.py --all     # Re-fetch all transcripts (full batch)

Saves each transcript to:
  transcripts/YYYY-MM-DD_video-title/transcript.md
  transcripts/YYYY-MM-DD_video-title/metadata.json
"""

import argparse
import json
import os
import re
import time
from datetime import datetime

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
except ImportError:
    print("Error: youtube-transcript-api is not installed.")
    print("Run: pip install youtube-transcript-api")
    raise

CATALOG_FILE = os.path.join(os.path.dirname(__file__), "..", "OIO-Video-Catalog.md")
TRANSCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "transcripts")
RATE_LIMIT_SECONDS = 1  # 1 request per second


def sanitize_folder_name(title):
    """Convert a video title to a safe folder name (lowercase, hyphens, max 50 chars)."""
    name = title.lower()
    name = re.sub(r"[^a-z0-9\s-]", "", name)
    name = re.sub(r"[\s]+", "-", name.strip())
    name = re.sub(r"-+", "-", name)
    return name[:50].rstrip("-")


def format_timestamp(seconds):
    """Format seconds as MM:SS or H:MM:SS."""
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def parse_catalog(catalog_path):
    """
    Parse OIO-Video-Catalog.md and extract video entries.

    Returns a list of dicts with keys: video_id, title, date, url
    """
    videos = []
    seen_ids = set()

    # Pattern matches markdown table rows with YouTube URLs
    # e.g.: | 2026-02-02 | [Road Noise - 002](https://www.youtube.com/watch?v=Scclz_OPo0U) | ...
    row_pattern = re.compile(
        r"\|\s*(\d{4}-\d{2}-\d{2})\s*\|"          # date column
        r"\s*\[([^\]]+)\]\(https://www\.youtube\.com/watch\?v=([A-Za-z0-9_-]{11})\)"  # title + video_id
    )

    with open(catalog_path, encoding="utf-8") as f:
        for line in f:
            match = row_pattern.search(line)
            if match:
                date = match.group(1)
                title = match.group(2).strip()
                video_id = match.group(3)
                if video_id not in seen_ids:
                    seen_ids.add(video_id)
                    videos.append({
                        "video_id": video_id,
                        "title": title,
                        "date": date,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                    })

    return videos


def get_processed_ids(transcripts_dir):
    """Return a set of video IDs that already have a transcript folder."""
    processed = set()
    if not os.path.isdir(transcripts_dir):
        return processed
    for folder in os.listdir(transcripts_dir):
        meta_path = os.path.join(transcripts_dir, folder, "metadata.json")
        if os.path.isfile(meta_path):
            try:
                with open(meta_path, encoding="utf-8") as f:
                    meta = json.load(f)
                vid_id = meta.get("video_id")
                if vid_id:
                    processed.add(vid_id)
            except (json.JSONDecodeError, KeyError):
                pass
    return processed


def fetch_transcript(video_id):
    """Fetch transcript for a video. Returns list of segment dicts or None on failure."""
    try:
        segments = YouTubeTranscriptApi.get_transcript(video_id)
        return segments
    except TranscriptsDisabled:
        print(f"    ⚠ Transcripts disabled for {video_id}")
        return None
    except NoTranscriptFound:
        print(f"    ⚠ No transcript found for {video_id}")
        return None
    except Exception as exc:
        print(f"    ✗ Error fetching {video_id}: {exc}")
        return None


def write_transcript(video, segments, transcripts_dir):
    """Write transcript.md and metadata.json for a video."""
    folder_name = f"{video['date']}_{sanitize_folder_name(video['title'])}"
    folder_path = os.path.join(transcripts_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Build transcript markdown
    transcript_title = f"{video['title']} — Transcript"
    lines = [
        "---",
        f'title: "{transcript_title}"',
        f"video_id: {video['video_id']}",
        f"date: {video['date']}",
        f"url: {video['url']}",
        "---",
        "",
        f"# {video['title']}",
        "",
        f"**Video:** [{video['video_id']}]({video['url']})  ",
        f"**Date:** {video['date']}",
        "",
        "---",
        "",
        "## Transcript",
        "",
    ]

    for segment in segments:
        ts = format_timestamp(segment["start"])
        text = segment["text"].replace("\n", " ").strip()
        lines.append(f"**[{ts}]** {text}")
        lines.append("")

    transcript_path = os.path.join(folder_path, "transcript.md")
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Build metadata JSON
    metadata = {
        "video_id": video["video_id"],
        "title": video["title"],
        "date": video["date"],
        "url": video["url"],
        "transcript_path": os.path.join("transcripts", folder_name, "transcript.md"),
        "segment_count": len(segments),
        "fetched_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    meta_path = os.path.join(folder_path, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return folder_path


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube transcripts for OIO Racing videos.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Re-fetch all transcripts (full batch mode). Default: only fetch new ones.",
    )
    args = parser.parse_args()

    catalog_path = os.path.abspath(CATALOG_FILE)
    transcripts_dir = os.path.abspath(TRANSCRIPTS_DIR)

    print(f"Parsing catalog: {catalog_path}")
    videos = parse_catalog(catalog_path)
    print(f"  Found {len(videos)} videos in catalog")

    if not videos:
        print("No videos found in catalog. Exiting.")
        return

    if args.all:
        targets = videos
        print("Mode: FULL BATCH — fetching all transcripts")
    else:
        processed = get_processed_ids(transcripts_dir)
        targets = [v for v in videos if v["video_id"] not in processed]
        print(f"Mode: INCREMENTAL — {len(targets)} new videos to fetch ({len(processed)} already processed)")

    if not targets:
        print("Nothing to fetch. All transcripts are up to date.")
        return

    os.makedirs(transcripts_dir, exist_ok=True)

    success = 0
    skipped = 0

    for i, video in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {video['date']} — {video['title'][:60]}")
        segments = fetch_transcript(video["video_id"])

        if segments:
            folder = write_transcript(video, segments, transcripts_dir)
            print(f"    ✓ Saved → {os.path.relpath(folder)}")
            success += 1
        else:
            skipped += 1

        if i < len(targets):
            time.sleep(RATE_LIMIT_SECONDS)

    print(f"\nDone. {success} fetched, {skipped} skipped (no transcript available).")


if __name__ == "__main__":
    main()
