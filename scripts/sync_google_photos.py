#!/usr/bin/env python3
"""
OIO Racing - Google Photos Sync

Automatically fetches photos from a shared Google Photos album
and stages them in intake/photos/ for AI filing.

The shared album URL must be public and accessible without authentication.

Usage:
  GOOGLE_PHOTOS_ALBUM_URL=https://photos.app.goo.gl/... python scripts/sync_google_photos.py

Environment Variables:
  GOOGLE_PHOTOS_ALBUM_URL - Required: Public Google Photos album URL
  DEBUG - Optional: Set to 'true' for verbose output
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Configuration
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
REPO_ROOT = Path(__file__).parent.parent
PICDUMP_DIR = REPO_ROOT / "intake" / "photos"
SYNC_STATE_DIR = REPO_ROOT / ".github" / "sync-state"
SYNC_STATE_FILE = SYNC_STATE_DIR / "google-photos.json"

# Create directories if needed
PICDUMP_DIR.mkdir(exist_ok=True)
SYNC_STATE_DIR.mkdir(parents=True, exist_ok=True)


def log(message, level="INFO"):
    """Print timestamped log message to stdout."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = f"[{timestamp}] {level}: {message}"
    print(output, flush=True)
    # Also print errors to stderr for better visibility in logs
    if level in ("ERROR", "FATAL"):
        print(output, file=sys.stderr, flush=True)


def debug(message):
    """Print debug message if DEBUG is enabled."""
    if DEBUG:
        log(message, "DEBUG")


def load_sync_state():
    """Load previously synced photo URLs to avoid duplicates."""
    if not SYNC_STATE_FILE.exists():
        debug("No previous sync state found")
        return {}

    try:
        with open(SYNC_STATE_FILE, "r") as f:
            state = json.load(f)
            debug(f"Loaded sync state: {len(state.get('synced_urls', []))} synced URLs")
            return state
    except json.JSONDecodeError as e:
        log(f"Warning: Could not parse sync state file: {e}", "WARN")
        return {}


def save_sync_state(state):
    """Save synced photos state."""
    with open(SYNC_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    debug(f"Saved sync state: {len(state.get('synced_urls', []))} URLs")


def get_album_url():
    """Get Google Photos album URL from environment."""
    url = os.getenv("GOOGLE_PHOTOS_ALBUM_URL")
    if not url:
        log("ERROR: GOOGLE_PHOTOS_ALBUM_URL environment variable not set", "ERROR")
        log("This is required for the sync workflow to run", "ERROR")
        log("Set it in GitHub Secrets → GOOGLE_PHOTOS_ALBUM_URL", "ERROR")
        return None

    debug(f"Album URL (first 50 chars): {url[:50]}...")

    # Handle short URLs: https://photos.app.goo.gl/...
    # Need to expand to full album URL if using short link
    if "photos.app.goo.gl" in url:
        try:
            debug("Resolving Google Photos short URL...")
            response = requests.head(url, allow_redirects=True, timeout=10)
            url = response.url
            debug(f"Resolved to: {url[:100]}...")
        except requests.RequestException as e:
            log(f"ERROR: Could not resolve Google Photos URL: {e}", "ERROR")
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

    except requests.Timeout:
        log(f"ERROR: Timeout downloading photo (>{timeout}s)", "ERROR")
        return False
    except requests.HTTPError as e:
        log(f"ERROR: HTTP {e.response.status_code} downloading photo", "ERROR")
        return False
    except requests.RequestException as e:
        log(f"ERROR: Network error downloading photo: {e}", "ERROR")
        return False
    except IOError as e:
        log(f"ERROR: Failed to save photo file: {e}", "ERROR")
        return False


def sync_google_photos():
    """Main sync function."""
    log("Starting Google Photos sync...")

    # Get album URL
    album_url = get_album_url()
    if not album_url:
        log("FATAL: No album URL configured", "ERROR")
        return -1

    log(f"Album URL configured (first 50 chars): {album_url[:50]}...")

    # Fetch album page
    try:
        log("Fetching album page...")
        response = requests.get(album_url, timeout=15)
        response.raise_for_status()
        album_html = response.text
        log(f"Album page fetched successfully ({len(album_html)} bytes)")
        debug(f"Response status: {response.status_code}")
    except requests.exceptions.Timeout:
        log("ERROR: Request timed out fetching album (15 seconds)", "ERROR")
        return -1
    except requests.exceptions.ConnectionError as e:
        log(f"ERROR: Network connection failed: {e}", "ERROR")
        return -1
    except requests.RequestException as e:
        log(f"ERROR: Failed to fetch album page: {e}", "ERROR")
        return -1

    # Extract photo URLs
    log("Extracting photo URLs from album HTML...")
    photo_list = extract_photo_urls(album_html)
    log(f"Found {len(photo_list)} photos in album")

    if not photo_list:
        log("WARNING: No photos found in album", "WARN")
        log("This could mean:", "WARN")
        log("  1. Album is empty", "WARN")
        log("  2. Album is not publicly accessible", "WARN")
        log("  3. Album URL is incorrect", "WARN")
        return 0

    # Load previous sync state
    log("Loading previous sync state...")
    state = load_sync_state()
    synced = state.get("synced_urls", [])
    synced_files = state.get("synced_files", [])
    log(f"Previous sync tracked {len(synced)} photos")

    # Download new photos
    log("Checking for new photos...")
    downloaded_count = 0

    for filename, url in photo_list:
        # Skip if already synced
        if url in synced or filename in synced_files:
            debug(f"Skipping {filename} (already synced)")
            continue

        # Download
        filepath = PICDUMP_DIR / filename
        log(f"Downloading: {filename}")

        if download_photo(url, filepath):
            log(f"✓ Saved to intake/photos/{filename}")
            synced.append(url)
            synced_files.append(filename)
            downloaded_count += 1
        else:
            log(f"✗ Failed to download {filename}", "WARN")

    # Save updated state
    state = {
        "synced_urls": synced,
        "synced_files": synced_files,
        "last_sync": datetime.now().isoformat(),
    }
    save_sync_state(state)

    # Summary
    already_synced = len(photo_list) - downloaded_count
    log(f"\n{'='*60}")
    log(f"Sync Summary:")
    log(f"  ✓ Downloaded: {downloaded_count}")
    log(f"  ⊘ Already synced: {already_synced}")
    log(f"  Total in state: {len(synced)}")
    log(f"{'='*60}")

    return downloaded_count


if __name__ == "__main__":
    log("=" * 60)
    log("OIO Racing - Google Photos Sync")
    log("=" * 60)

    if DEBUG:
        log("DEBUG MODE ENABLED", "DEBUG")
        log(f"GOOGLE_PHOTOS_ALBUM_URL set: {bool(os.getenv('GOOGLE_PHOTOS_ALBUM_URL'))}", "DEBUG")

    try:
        count = sync_google_photos()

        if count < 0:
            log("\nFATAL: Sync failed - check error messages above", "ERROR")
            sys.exit(1)
        else:
            log(f"\nSUCCESS: Sync completed (downloaded {count} new photos)", "INFO")
            sys.exit(0)

    except KeyboardInterrupt:
        log("\nInterrupted by user", "WARN")
        sys.exit(130)
    except Exception as e:
        log(f"\nUNEXPECTED ERROR: {type(e).__name__}: {e}", "ERROR")
        import traceback
        log("Traceback:", "ERROR")
        # Always log full traceback for visibility
        tb_lines = traceback.format_exc().split('\n')
        for line in tb_lines:
            if line.strip():
                log(line, "ERROR")
        sys.exit(1)
