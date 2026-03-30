#!/usr/bin/env python3
"""
OIO Racing - Catalog Transcript Linker
Updates OIO-Video-Catalog.md with links to available transcripts.

Usage:
  python scripts/update_catalog_transcripts.py

Process:
1. Parse OIO-Video-Catalog.md for video tables
2. Scan transcripts/ folder for available transcripts
3. Add "Transcript" column to tables (if not exists)
4. Insert links to available transcripts
5. Write updated catalog back to file

Output format in Transcript column:
  - Available: [📄](transcripts/YYYY-MM-DD_video-title/transcript.md)
  - Not available: (empty cell)
"""

import json
import os
import re
from pathlib import Path


CATALOG_FILE = Path(__file__).parent.parent / "OIO-Video-Catalog.md"
TRANSCRIPTS_DIR = Path(__file__).parent.parent / "transcripts"


def get_transcript_mapping():
    """
    Build a mapping of video_id -> relative transcript path.

    Returns:
        dict: {video_id: "transcripts/YYYY-MM-DD_title/transcript.md"}
    """
    mapping = {}

    if not TRANSCRIPTS_DIR.exists():
        return mapping

    for folder in TRANSCRIPTS_DIR.iterdir():
        if not folder.is_dir():
            continue

        meta_path = folder / "metadata.json"
        if not meta_path.exists():
            continue

        try:
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)

            video_id = meta.get("video_id")
            if video_id:
                transcript_path = f"transcripts/{folder.name}/transcript.md"
                mapping[video_id] = transcript_path
        except (json.JSONDecodeError, KeyError):
            continue

    return mapping


def extract_video_id(url):
    """
    Extract YouTube video ID from URL.

    Args:
        url: YouTube URL (e.g., https://www.youtube.com/watch?v=abc123)

    Returns:
        str or None: Video ID if found
    """
    match = re.search(r'watch\?v=([A-Za-z0-9_-]{11})', url)
    return match.group(1) if match else None


def process_table_line(line, transcript_map, has_transcript_col):
    """
    Process a single table row and add/update transcript link.

    Args:
        line: Markdown table row
        transcript_map: dict of video_id -> transcript_path
        has_transcript_col: bool, whether Transcript column already exists

    Returns:
        tuple: (updated_line, is_table_row)
    """
    # Check if this is a table row (starts with |)
    if not line.strip().startswith('|'):
        return line, False

    # Check if this is a separator row (contains only |, -, and spaces)
    if re.match(r'^\|\s*[-:]+\s*(\|\s*[-:]+\s*)+\|?\s*$', line):
        # This is a separator row
        if not has_transcript_col:
            # Add a separator cell for Transcript column
            line = line.rstrip()
            if not line.endswith('|'):
                line += ' |'
            # Insert before last |
            parts = line.rsplit('|', 1)
            return parts[0] + ' --- |' + parts[1] + '\n', True
        return line, True

    # This is a data row - extract video ID from YouTube URL
    cells = [cell.strip() for cell in line.split('|')]

    # Need at least 3 cells (empty, content columns, empty for proper table)
    if len(cells) < 3:
        return line, True

    # Look for YouTube URL in the Title column (usually second non-empty cell)
    video_id = None
    for cell in cells:
        match = re.search(r'https://www\.youtube\.com/watch\?v=([A-Za-z0-9_-]{11})', cell)
        if match:
            video_id = match.group(1)
            break

    if not video_id:
        # No video URL found, but still a table row
        if not has_transcript_col:
            # Add empty transcript cell
            line = line.rstrip()
            if not line.endswith('|'):
                line += ' |'
            parts = line.rsplit('|', 1)
            return parts[0] + ' |' + parts[1] + '\n', True
        return line, True

    # Check if transcript exists
    transcript_path = transcript_map.get(video_id)
    transcript_cell = f' [📄]({transcript_path})' if transcript_path else ''

    if has_transcript_col:
        # Replace existing transcript cell (last column)
        line = line.rstrip()
        if not line.endswith('|'):
            line += ' |'

        # Split and replace last data cell
        parts = line.rsplit('|', 2)
        if len(parts) >= 3:
            return parts[0] + '|' + transcript_cell + ' |' + parts[2] + '\n', True
        return line, True
    else:
        # Add new transcript cell
        line = line.rstrip()
        if not line.endswith('|'):
            line += ' |'

        # Insert before last |
        parts = line.rsplit('|', 1)
        return parts[0] + '|' + transcript_cell + ' |' + parts[1] + '\n', True


def update_catalog(catalog_path, transcript_map):
    """
    Update catalog file with transcript links.

    Args:
        catalog_path: Path to OIO-Video-Catalog.md
        transcript_map: dict of video_id -> transcript_path

    Returns:
        int: Number of tables updated
    """
    with open(catalog_path, encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = []
    in_table = False
    has_transcript_col = False
    tables_updated = 0
    header_processed = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect table start (header row)
        if line.strip().startswith('|') and not in_table:
            # Check if this is a video table (contains "Title" and "Date")
            if 'Title' in line and 'Date' in line:
                in_table = True
                header_processed = False
                has_transcript_col = 'Transcript' in line

                if not has_transcript_col:
                    # Add Transcript column to header
                    line = line.rstrip()
                    if not line.endswith('|'):
                        line += ' |'
                    parts = line.rsplit('|', 1)
                    line = parts[0] + ' Transcript |' + parts[1] + '\n'
                    tables_updated += 1

            updated_lines.append(line)
            i += 1
            continue

        # Process table rows
        if in_table:
            updated_line, is_table_row = process_table_line(line, transcript_map, has_transcript_col)
            updated_lines.append(updated_line)

            # Check if table ended
            if not is_table_row or (i + 1 < len(lines) and not lines[i + 1].strip().startswith('|')):
                in_table = False
                has_transcript_col = False

            i += 1
            continue

        # Not in table, just append
        updated_lines.append(line)
        i += 1

    # Write back
    with open(catalog_path, 'w', encoding="utf-8") as f:
        f.writelines(updated_lines)

    return tables_updated


def main():
    catalog_path = CATALOG_FILE.resolve()
    transcripts_dir = TRANSCRIPTS_DIR.resolve()

    print(f"Catalog: {catalog_path}")
    print(f"Transcripts: {transcripts_dir}")

    if not catalog_path.exists():
        print(f"Error: Catalog file not found: {catalog_path}")
        return 1

    # Build transcript mapping
    print("\nScanning transcripts folder...")
    transcript_map = get_transcript_mapping()
    print(f"  Found {len(transcript_map)} available transcripts")

    if not transcript_map:
        print("\n  No transcripts found. Nothing to update.")
        return 0

    # Update catalog
    print("\nUpdating catalog...")
    tables_updated = update_catalog(catalog_path, transcript_map)

    if tables_updated > 0:
        print(f"  ✓ Updated {tables_updated} table(s) with transcript links")
    else:
        print("  ✓ Transcript columns already exist, links updated")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    exit(main())
