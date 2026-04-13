#!/usr/bin/env python3
"""
sync_brain_to_gdrive.py — Push brain/ docs to Google Drive.

Walks the brain/ directory tree and uploads every markdown file to the
corresponding path inside the configured Google Drive folder, preserving
the subfolder structure. Existing files are updated (not duplicated).

Usage:
  python dev/scripts/sync_brain_to_gdrive.py [--path brain/active]

  --path   Restrict sync to a specific subdirectory (default: entire brain/)
  --dry-run  Print what would be uploaded without making changes

Required environment variables (or GitHub secrets):
  GOOGLE_DRIVE_CREDENTIALS       JSON blob from auth_google_drive.py
  GOOGLE_DRIVE_BRAIN_FOLDER_ID   Google Drive folder ID for brain/ root

Install deps:
  pip install google-auth google-auth-httplib2 google-api-python-client
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except ImportError:
    print("ERROR: Google API client not installed.")
    print("Run: pip install google-auth google-auth-httplib2 google-api-python-client")
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent.parent
BRAIN_DIR = REPO_ROOT / "brain"
MIME_MARKDOWN = "text/markdown"
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


def get_or_create_folder(service, name: str, parent_id: str) -> str:
    """Return the Drive folder ID for `name` inside `parent_id`, creating it if needed."""
    query = (
        f"name='{name}' and mimeType='{MIME_FOLDER}' "
        f"and '{parent_id}' in parents and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]
    # Create the folder
    metadata = {
        "name": name,
        "mimeType": MIME_FOLDER,
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def get_existing_file(service, name: str, parent_id: str):
    """Return existing file metadata dict or None."""
    query = (
        f"name='{name}' and mimeType!='{MIME_FOLDER}' "
        f"and '{parent_id}' in parents and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id, name, modifiedTime)").execute()
    files = results.get("files", [])
    return files[0] if files else None


def upload_file(service, local_path: Path, parent_id: str, dry_run: bool) -> str:
    """Upload or update a file in Drive. Returns the file ID."""
    name = local_path.name
    existing = get_existing_file(service, name, parent_id)
    media = MediaFileUpload(str(local_path), mimetype=MIME_MARKDOWN, resumable=False)

    if existing:
        if dry_run:
            return f"[DRY RUN] Would update: {name} (id={existing['id']})"
        updated = service.files().update(
            fileId=existing["id"],
            media_body=media,
        ).execute()
        return f"Updated: {name} (id={updated['id']})"
    else:
        if dry_run:
            return f"[DRY RUN] Would create: {name}"
        metadata = {"name": name, "parents": [parent_id]}
        created = service.files().create(
            body=metadata, media_body=media, fields="id"
        ).execute()
        return f"Created: {name} (id={created['id']})"


def ensure_drive_path(service, rel_parts: list, root_folder_id: str) -> str:
    """Walk/create Drive folder hierarchy for rel_parts, return leaf folder ID."""
    current_id = root_folder_id
    for part in rel_parts:
        current_id = get_or_create_folder(service, part, current_id)
    return current_id


def sync_directory(service, local_dir: Path, root_folder_id: str, dry_run: bool) -> int:
    """Recursively sync local_dir to Drive under root_folder_id. Returns file count."""
    count = 0
    for md_file in sorted(local_dir.rglob("*.md")):
        rel = md_file.relative_to(local_dir)
        folder_parts = list(rel.parts[:-1])  # dirs between local_dir and file
        parent_id = ensure_drive_path(service, folder_parts, root_folder_id)
        result = upload_file(service, md_file, parent_id, dry_run)
        print(f"  {result}")
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync brain/ docs to Google Drive")
    parser.add_argument(
        "--path",
        default=None,
        help="Restrict sync to a subdirectory of brain/ (e.g. brain/active)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be synced without making changes",
    )
    args = parser.parse_args()

    folder_id = os.environ.get("GOOGLE_DRIVE_BRAIN_FOLDER_ID")
    if not folder_id:
        print("ERROR: GOOGLE_DRIVE_BRAIN_FOLDER_ID environment variable not set.")
        sys.exit(1)

    sync_root = BRAIN_DIR
    if args.path:
        candidate = REPO_ROOT / args.path
        if not candidate.exists():
            print(f"ERROR: Path does not exist: {candidate}")
            sys.exit(1)
        sync_root = candidate

    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    if args.dry_run:
        print(f"[DRY RUN] Syncing {sync_root.relative_to(REPO_ROOT)} → Google Drive folder {folder_id}")
    else:
        print(f"Syncing {sync_root.relative_to(REPO_ROOT)} → Google Drive folder {folder_id}")

    # If syncing a subdirectory, create/find matching subfolder in Drive
    if sync_root != BRAIN_DIR:
        rel_parts = list(sync_root.relative_to(BRAIN_DIR).parts)
        target_folder_id = ensure_drive_path(service, rel_parts, folder_id)
    else:
        target_folder_id = folder_id

    count = sync_directory(service, sync_root, target_folder_id, args.dry_run)
    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Done. {count} file(s) processed.")


if __name__ == "__main__":
    main()
