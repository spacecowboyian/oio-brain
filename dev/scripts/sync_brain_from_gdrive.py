#!/usr/bin/env python3
"""
sync_brain_from_gdrive.py — Pull brain docs from Google Drive into the repo.

Downloads every .md file from the configured Google Drive folder (and its
subfolders) into the brain/ directory, preserving folder structure.
Files in the repo that are newer than Drive are NOT overwritten unless
--force is passed.

Intended to run on a cron schedule via GitHub Actions to keep the repo
up to date with edits made directly in Google Drive.

Usage:
  python dev/scripts/sync_brain_from_gdrive.py [--path active] [--force] [--dry-run]

  --path     Restrict sync to a subfolder name inside the Drive brain folder
  --force    Overwrite local files even if Drive version is not newer
  --dry-run  Print what would be downloaded without making changes

Required environment variables (or GitHub secrets):
  GOOGLE_DRIVE_CREDENTIALS       JSON blob from auth_google_drive.py
  GOOGLE_DRIVE_BRAIN_FOLDER_ID   Google Drive folder ID for brain/ root

Install deps:
  pip install google-auth google-auth-httplib2 google-api-python-client
"""

import argparse
import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
except ImportError:
    print("ERROR: Google API client not installed.")
    print("Run: pip install google-auth google-auth-httplib2 google-api-python-client")
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent.parent
BRAIN_DIR = REPO_ROOT / "brain"
MIME_FOLDER = "application/vnd.google-apps.folder"


def get_credentials() -> Credentials:
    raw = os.environ.get("GOOGLE_DRIVE_CREDENTIALS")
    if not raw:
        print("ERROR: GOOGLE_DRIVE_CREDENTIALS environment variable not set.")
        sys.exit(1)
    creds_data = json.loads(raw)
    creds = Credentials(
        token=creds_data.get("token"),
        refresh_token=creds_data["refresh_token"],
        token_uri=creds_data["token_uri"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=creds_data.get("scopes"),
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


def list_drive_items(service, folder_id: str) -> list:
    """List all files and folders inside a Drive folder (non-recursive)."""
    items = []
    page_token = None
    while True:
        params = {
            "q": f"'{folder_id}' in parents and trashed=false",
            "fields": "nextPageToken, files(id, name, mimeType, modifiedTime)",
            "pageSize": 200,
        }
        if page_token:
            params["pageToken"] = page_token
        result = service.files().list(**params).execute()
        items.extend(result.get("files", []))
        page_token = result.get("nextPageToken")
        if not page_token:
            break
    return items


def download_file(service, file_id: str) -> bytes:
    """Download a Drive file and return its content as bytes."""
    request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()


def parse_drive_time(ts: str) -> datetime:
    """Parse Google Drive RFC3339 timestamp to timezone-aware datetime."""
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def get_local_mtime(path: Path) -> datetime:
    """Return file mtime as timezone-aware datetime."""
    mtime = os.path.getmtime(path)
    return datetime.fromtimestamp(mtime, tz=timezone.utc)


def sync_folder(
    service,
    drive_folder_id: str,
    local_dir: Path,
    force: bool,
    dry_run: bool,
) -> int:
    """Recursively sync Drive folder to local_dir. Returns count of files written."""
    local_dir.mkdir(parents=True, exist_ok=True)
    items = list_drive_items(service, drive_folder_id)
    count = 0

    for item in items:
        name = item["name"]
        mime = item["mimeType"]

        if mime == MIME_FOLDER:
            # Recurse into subfolder
            count += sync_folder(
                service, item["id"], local_dir / name, force, dry_run
            )
        elif name.endswith(".md"):
            local_path = local_dir / name
            drive_mtime = parse_drive_time(item["modifiedTime"])

            should_download = force
            if not should_download:
                if not local_path.exists():
                    should_download = True
                else:
                    local_mtime = get_local_mtime(local_path)
                    should_download = drive_mtime > local_mtime

            if should_download:
                rel = local_path.relative_to(REPO_ROOT)
                if dry_run:
                    print(f"  [DRY RUN] Would download: {rel}")
                else:
                    content = download_file(service, item["id"])
                    local_path.write_bytes(content)
                    print(f"  Downloaded: {rel}")
                count += 1
            # else: local is up-to-date, skip silently

    return count


def find_subfolder(service, folder_id: str, name: str) -> str | None:
    """Find a named subfolder inside folder_id. Returns its ID or None."""
    query = (
        f"name='{name}' and mimeType='{MIME_FOLDER}' "
        f"and '{folder_id}' in parents and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    return files[0]["id"] if files else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync brain docs from Google Drive")
    parser.add_argument(
        "--path",
        default=None,
        help="Restrict to a named subfolder inside the Drive brain folder (e.g. active)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite local files even when they are newer than Drive",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be downloaded without making changes",
    )
    args = parser.parse_args()

    folder_id = os.environ.get("GOOGLE_DRIVE_BRAIN_FOLDER_ID")
    if not folder_id:
        print("ERROR: GOOGLE_DRIVE_BRAIN_FOLDER_ID environment variable not set.")
        sys.exit(1)

    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    drive_folder_id = folder_id
    local_target = BRAIN_DIR

    if args.path:
        drive_folder_id = find_subfolder(service, folder_id, args.path)
        if not drive_folder_id:
            print(f"ERROR: Subfolder '{args.path}' not found in Drive brain folder.")
            sys.exit(1)
        local_target = BRAIN_DIR / args.path

    label = f"brain/{args.path}" if args.path else "brain/"
    if args.dry_run:
        print(f"[DRY RUN] Syncing Google Drive → {label}")
    else:
        print(f"Syncing Google Drive → {label}")

    count = sync_folder(service, drive_folder_id, local_target, args.force, args.dry_run)
    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Done. {count} file(s) updated.")


if __name__ == "__main__":
    main()
