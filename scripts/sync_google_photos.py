#!/usr/bin/env python3
"""
OIO Racing - Google Photos Album Sync

Downloads photos from a public Google Photos album to intake/photos/.
Tracks downloaded photos to avoid duplicates.

Usage:
  python scripts/sync_google_photos.py --album-url https://photos.app.goo.gl/W757cit6HfvKmCQh6

The script maintains a state file (.github/sync-state/google-photos.json) to track which
photos have already been downloaded by their URL hash.

When new photos are found, they are downloaded to intake/photos/ and the state
file is updated. The GitHub Action will then commit these files, triggering
the photo processing workflow.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs

try:
    import requests
except ImportError:
    print("Error: requests is not installed.")
    print("Run: pip install requests")
    raise

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: beautifulsoup4 is not installed.")
    print("Run: pip install beautifulsoup4")
    raise


PICDUMP_DIR = os.path.join(os.path.dirname(__file__), "..", "intake", "photos")
SYNC_STATE_DIR = os.path.join(os.path.dirname(__file__), "..", ".github", "sync-state")
STATE_FILE = os.path.join(SYNC_STATE_DIR, "google-photos.json")
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state():
    """Load sync state from disk, or return a fresh default state."""
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {
        "downloaded_hashes": [],
        "last_sync": None,
        "total_downloaded": 0
    }


def save_state(state):
    """Write sync state to disk."""
    os.makedirs(SYNC_STATE_DIR, exist_ok=True)
    state["last_sync"] = datetime.utcnow().isoformat() + "Z"
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def photo_hash(url):
    """Generate a stable hash for a photo URL to track downloads."""
    # Use the photo ID from the URL if available, otherwise hash the full URL
    parsed = urlparse(url)
    # Google Photos URLs often have the photo ID in the path
    photo_id = parsed.path.split("/")[-1] if parsed.path else url
    return hashlib.sha256(photo_id.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Google Photos scraping
# ---------------------------------------------------------------------------

def fetch_album_page(album_url):
    """
    Fetch the HTML of a public Google Photos album.
    Returns the response object.
    """
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(album_url, headers=headers, timeout=30, allow_redirects=True)
        resp.raise_for_status()
        return resp
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch album page: {exc}") from exc


def extract_photo_urls(html_content):
    """
    Extract photo URLs from the Google Photos album HTML.

    Google Photos embeds photo data in the page source. This function
    uses multiple strategies to extract photo URLs:
    1. Look for JSON data in script tags
    2. Parse img tags with high-resolution photo URLs
    3. Find data attributes that contain photo URLs

    Returns a list of (photo_url, filename) tuples.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    photo_urls = []

    # Strategy 1: Extract from script tags containing JSON data
    # Google Photos often embeds photo data in script tags with AF_initDataCallback
    scripts = soup.find_all("script")
    for script in scripts:
        if script.string and "AF_initDataCallback" in script.string:
            # Look for URLs that match Google's user content pattern
            matches = re.findall(r'https://lh3\.googleusercontent\.com/[^"]+', script.string)
            for match in matches:
                # Google Photos URLs often have size parameters - get the largest size
                # Replace size parameters with =d to get original size
                photo_url = re.sub(r'=w\d+-h\d+', '=d', match)
                photo_url = re.sub(r'=s\d+', '=d', photo_url)

                # Extract a filename from the URL or generate one
                url_parts = urlparse(photo_url)
                path_parts = url_parts.path.split("/")
                filename = path_parts[-1] if path_parts[-1] else f"photo_{photo_hash(photo_url)}"

                # Ensure it has an image extension
                if not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.heic', '.webp']):
                    filename += ".jpg"

                photo_urls.append((photo_url, filename))

    # Strategy 2: Look for img tags (fallback)
    if not photo_urls:
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if "googleusercontent.com" in src:
                # Upgrade to full size
                photo_url = re.sub(r'=w\d+-h\d+', '=d', src)
                photo_url = re.sub(r'=s\d+', '=d', photo_url)

                filename = f"photo_{photo_hash(photo_url)}.jpg"
                photo_urls.append((photo_url, filename))

    # Remove duplicates by URL
    seen = set()
    unique_photos = []
    for url, filename in photo_urls:
        url_hash = photo_hash(url)
        if url_hash not in seen:
            seen.add(url_hash)
            unique_photos.append((url, filename))

    return unique_photos


def download_photo(photo_url, filename, output_dir):
    """
    Download a photo from a URL to the output directory.
    Returns True if successful, False otherwise.
    """
    output_path = os.path.join(output_dir, filename)

    # Skip if file already exists
    if os.path.isfile(output_path):
        print(f"  ⊙ Exists: {filename}")
        return False

    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(photo_url, headers=headers, timeout=60, stream=True)
        resp.raise_for_status()

        # Write the file
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"  ✓ Downloaded: {filename} ({len(resp.content) // 1024} KB)")
        return True

    except requests.RequestException as exc:
        print(f"  ✗ Failed: {filename} — {exc}")
        return False


# ---------------------------------------------------------------------------
# Main sync logic
# ---------------------------------------------------------------------------

def sync_album(album_url):
    """
    Sync photos from a public Google Photos album to intake/photos/.
    Returns the number of new photos downloaded.
    """
    print(f"Fetching album: {album_url}")

    # Fetch the album page
    resp = fetch_album_page(album_url)
    print(f"Album loaded (status: {resp.status_code})")

    # Extract photo URLs
    photo_urls = extract_photo_urls(resp.text)
    print(f"Found {len(photo_urls)} photo(s) in album")

    if not photo_urls:
        print("\nWarning: No photos found in album.")
        print("This could mean:")
        print("  - The album is empty")
        print("  - The album URL is incorrect")
        print("  - Google Photos changed their HTML structure")
        print("  - The album requires authentication")
        return 0

    # Load state to check for duplicates
    state = load_state()
    downloaded_hashes = set(state.get("downloaded_hashes", []))

    # Download new photos
    new_downloads = 0
    print(f"\nDownloading new photos to {PICDUMP_DIR}/")

    for photo_url, filename in photo_urls:
        url_hash = photo_hash(photo_url)

        # Skip if already downloaded
        if url_hash in downloaded_hashes:
            continue

        # Download the photo
        if download_photo(photo_url, filename, PICDUMP_DIR):
            downloaded_hashes.add(url_hash)
            new_downloads += 1
            time.sleep(0.5)  # Rate limiting

    # Update state
    state["downloaded_hashes"] = list(downloaded_hashes)
    state["total_downloaded"] = state.get("total_downloaded", 0) + new_downloads
    save_state(state)

    return new_downloads


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Sync photos from a public Google Photos album to intake/photos/."
    )
    parser.add_argument(
        "--album-url",
        required=True,
        help="Public Google Photos album URL (e.g., https://photos.app.goo.gl/...)",
    )
    args = parser.parse_args()

    print("OIO Racing - Google Photos Album Sync\n")

    try:
        new_count = sync_album(args.album_url)
        print(f"\nDone. {new_count} new photo(s) downloaded.")

        if new_count > 0:
            print("\nNext steps:")
            print("  1. Commit and push these photos to main")
            print("  2. The process-picdump-photos workflow will automatically trigger")
            print("  3. A Copilot agent will identify and file each photo")

        sys.exit(0)

    except RuntimeError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
