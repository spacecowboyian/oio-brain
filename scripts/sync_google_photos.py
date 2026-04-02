#!/usr/bin/env python3
"""
OIO Racing - Google Photos Sync

Automatically fetches photos from a shared Google Photos album
and stages them in picdump/ for AI filing.

The shared album URL must be public and accessible without authentication.

Usage:
  GOOGLE_PHOTOS_ALBUM_URL=https://photos.app.goo.gl/... python scripts/sync_google_photos.py
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Paths
REPO_ROOT = Path(__file__).parent.parent
PICDUMP_DIR = REPO_ROOT / "picdump"
SYNC_STATE_DIR = REPO_ROOT / ".github" / "sync-state"
SYNC_STATE_FILE = SYNC_STATE_DIR / "google-photos.json"

# Create directories if needed
PICDUMP_DIR.mkdir(exist_ok=True)
SYNC_STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_sync_state():
    """Load previously synced photo URLs to avoid duplicates."""
    if not SYNC_STATE_FILE.exists():
        return {}

    try:
        with open(SYNC_STATE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_sync_state(state):
    """Save synced photos state."""
    with open(SYNC_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_album_url():
    """Get Google Photos album URL from environment."""
    url = os.getenv("GOOGLE_PHOTOS_ALBUM_URL")
    if not url:
        print("Error: GOOGLE_PHOTOS_ALBUM_URL environment variable not set")
        return None

    # Handle short URLs: https://photos.app.goo.gl/...
    # Need to expand to full album URL if using short link
    if "photos.app.goo.gl" in url:
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            url = response.url
        except requests.RequestException as e:
            print(f"Error resolving Google Photos URL: {e}")
            return None

    return url


def extract_photo_urls(album_html):
    """
    Extract photo download URLs from Google Photos album HTML.

    Returns list of (filename, url) tuples.
    """
    soup = BeautifulSoup(album_html, "html.parser")
    photos = []

    # Google Photos uses data-src attributes for images
    # Look for image elements with srcset or data attributes
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""

        # Filter to photos only (not thumbnails, UI elements)
        if "/photo/" in src or "/image/" in src or "/media/" in src:
            # Try to extract filename from URL
            filename = extract_filename_from_url(src)
            if filename:
                photos.append((filename, src))

    # Alternative: Look for download links
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if "/photo/" in href or "download" in href.lower():
            filename = extract_filename_from_url(href)
            if filename and (filename, href) not in photos:
                photos.append((filename, href))

    return photos


def extract_filename_from_url(url):
    """Extract a reasonable filename from a URL."""
    # Try to get filename from URL parameters
    if "filename=" in url:
        match = re.search(r"filename=([^&]+)", url)
        if match:
            return match.group(1).strip('"\'')

    # Extract from path
    path = url.split("?")[0].split("#")[0]
    name = path.split("/")[-1]

    # Sanitize
    if name and "." in name:
        return name

    # Generate a name if we can't extract one
    ext = ".jpg"
    if ".png" in url:
        ext = ".png"
    elif ".heic" in url:
        ext = ".heic"
    elif ".webp" in url:
        ext = ".webp"

    return f"photo_{int(datetime.now().timestamp())}{ext}"


def download_photo(url, filepath, timeout=30):
    """Download a photo from URL to filepath."""
    try:
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return True

    except requests.RequestException as e:
        print(f"  ✗ Failed to download {url}: {e}")
        return False


def sync_google_photos():
    """Main sync function."""
    print("OIO Racing - Google Photos Sync\n")

    # Get album URL
    album_url = get_album_url()
    if not album_url:
        return 0

    print(f"Syncing from: {album_url}\n")

    # Fetch album page
    try:
        response = requests.get(album_url, timeout=15)
        response.raise_for_status()
        album_html = response.text
    except requests.RequestException as e:
        print(f"Error fetching album: {e}")
        return 0

    # Extract photo URLs
    photo_list = extract_photo_urls(album_html)
    print(f"Found {len(photo_list)} photos in album")

    if not photo_list:
        print("No photos found or album is not publicly accessible.")
        return 0

    # Load previous sync state
    state = load_sync_state()
    synced = state.get("synced_urls", [])
    synced_files = state.get("synced_files", [])

    # Download new photos
    downloaded_count = 0

    for filename, url in photo_list:
        # Skip if already synced
        if url in synced or filename in synced_files:
            print(f"  ⊘ Skipping {filename} (already synced)")
            continue

        # Download
        filepath = PICDUMP_DIR / filename
        print(f"  Downloading: {filename}")

        if download_photo(url, filepath):
            print(f"  ✓ Saved to picdump/{filename}")
            synced.append(url)
            synced_files.append(filename)
            downloaded_count += 1
        else:
            print(f"  ✗ Failed to download {filename}")

    # Save updated state
    state = {
        "synced_urls": synced,
        "synced_files": synced_files,
        "last_sync": datetime.now().isoformat(),
    }
    save_sync_state(state)

    # Summary
    print(f"\n{'='*60}")
    print(f"Sync complete:")
    print(f"  ✓ Downloaded: {downloaded_count}")
    print(f"  ⊘ Already synced: {len(photo_list) - downloaded_count}")
    print(f"  Total in state: {len(synced)}")
    print(f"{'='*60}")

    return downloaded_count


if __name__ == "__main__":
    import sys

    try:
        count = sync_google_photos()
        sys.exit(0 if count >= 0 else 1)

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
