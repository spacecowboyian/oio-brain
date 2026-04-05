#!/usr/bin/env python3
"""
OIO Racing - Transcript Cleaner
Generates clean, readable script versions from raw transcripts using Claude AI.

Usage:
  python dev/scripts/clean_transcripts.py                        # Clean all transcripts missing clean versions
  python dev/scripts/clean_transcripts.py --all                  # Re-clean ALL transcripts
  python dev/scripts/clean_transcripts.py --video-id VIDEO_ID    # Clean specific video

Requires:
  ANTHROPIC_API_KEY environment variable set
"""

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError:
    print("Error: anthropic package is not installed.")
    print("Run: pip install anthropic")
    sys.exit(1)

TRANSCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "transcripts")


def find_transcript_folders(transcripts_dir):
    """Find all folders containing transcript.md files."""
    folders = []
    if not os.path.isdir(transcripts_dir):
        return folders

    for item in os.listdir(transcripts_dir):
        folder_path = os.path.join(transcripts_dir, item)
        if os.path.isdir(folder_path):
            transcript_path = os.path.join(folder_path, "transcript.md")
            if os.path.isfile(transcript_path):
                folders.append(folder_path)

    return sorted(folders)


def read_transcript(transcript_path):
    """Read and extract the transcript content (without metadata header)."""
    with open(transcript_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip YAML frontmatter if present
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()

    return content


def clean_transcript_with_claude(transcript_text, video_title, client):
    """Use Claude to clean up the transcript into a readable script."""

    prompt = f"""You are cleaning up a raw YouTube transcript for the video titled "{video_title}".

Your task is to transform this raw transcript into a clean, readable script that reads like it was written beforehand.

Guidelines:
1. Remove filler words (um, uh, like, you know, etc.)
2. Fix incomplete sentences and thoughts
3. Correct obvious speech-to-text errors
4. Maintain the speaker's authentic voice and style
5. Keep the same content and meaning - don't add new information
6. Format as a flowing script with proper paragraphs
7. Keep the title and structure, but remove timestamp markers
8. Preserve any important technical terms or car-specific jargon

Here is the raw transcript:

{transcript_text}

Please output ONLY the cleaned script in markdown format, starting with the title."""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=16000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text


def write_clean_script(folder_path, clean_text, video_metadata):
    """Write the clean script to clean-script.md."""
    clean_script_path = os.path.join(folder_path, "clean-script.md")

    # Add frontmatter
    frontmatter = f"""---
title: "{video_metadata['title']} — Clean Script"
video_id: {video_metadata['video_id']}
date: {video_metadata['date']}
url: {video_metadata['url']}
type: clean_script
---

"""

    with open(clean_script_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter + clean_text)

    return clean_script_path


def get_video_metadata(folder_path):
    """Load metadata.json from the transcript folder."""
    metadata_path = os.path.join(folder_path, "metadata.json")
    if not os.path.isfile(metadata_path):
        return None

    with open(metadata_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Clean YouTube transcripts into readable scripts using Claude AI.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Re-clean all transcripts, including those with existing clean scripts.",
    )
    parser.add_argument(
        "--video-id",
        type=str,
        metavar="VIDEO_ID",
        help="Clean only the transcript for this specific video ID.",
    )
    args = parser.parse_args()

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Get your API key from: https://console.anthropic.com/")
        sys.exit(1)

    client = Anthropic(api_key=api_key)
    transcripts_dir = os.path.abspath(TRANSCRIPTS_DIR)

    print(f"Scanning for transcripts in: {transcripts_dir}")
    folders = find_transcript_folders(transcripts_dir)

    if not folders:
        print("No transcript folders found.")
        return

    print(f"Found {len(folders)} transcript folder(s)")

    # Filter by video_id if specified
    if args.video_id:
        folders = [f for f in folders if args.video_id in os.path.basename(f)]
        if not folders:
            print(f"No transcript found for video ID: {args.video_id}")
            return
        print(f"Filtering to video ID: {args.video_id}")

    # Filter out folders that already have clean scripts (unless --all)
    if not args.all:
        folders_needing_cleaning = []
        for folder in folders:
            clean_script_path = os.path.join(folder, "clean-script.md")
            if not os.path.isfile(clean_script_path):
                folders_needing_cleaning.append(folder)
        folders = folders_needing_cleaning
        print(f"{len(folders)} transcript(s) need cleaning")

    if not folders:
        print("All transcripts already have clean scripts. Use --all to re-clean.")
        return

    success = 0
    failed = []

    for i, folder in enumerate(folders, 1):
        folder_name = os.path.basename(folder)
        print(f"\n[{i}/{len(folders)}] Processing: {folder_name}")

        # Load metadata
        metadata = get_video_metadata(folder)
        if not metadata:
            print(f"    ⚠ No metadata.json found, skipping")
            failed.append(folder_name)
            continue

        # Read transcript
        transcript_path = os.path.join(folder, "transcript.md")
        try:
            transcript_text = read_transcript(transcript_path)
        except Exception as e:
            print(f"    ⚠ Failed to read transcript: {e}")
            failed.append(folder_name)
            continue

        # Clean with Claude
        try:
            print(f"    🤖 Cleaning transcript with Claude...")
            clean_text = clean_transcript_with_claude(
                transcript_text,
                metadata['title'],
                client
            )
        except Exception as e:
            print(f"    ⚠ Claude API error: {e}")
            failed.append(folder_name)
            continue

        # Write clean script
        try:
            clean_path = write_clean_script(folder, clean_text, metadata)
            print(f"    ✓ Saved → {os.path.relpath(clean_path)}")
            success += 1
        except Exception as e:
            print(f"    ⚠ Failed to write clean script: {e}")
            failed.append(folder_name)
            continue

    print(f"\nDone. {success} cleaned successfully.")
    if failed:
        print(f"Failed to clean {len(failed)} transcript(s):")
        for name in failed:
            print(f"  - {name}")


if __name__ == "__main__":
    main()
