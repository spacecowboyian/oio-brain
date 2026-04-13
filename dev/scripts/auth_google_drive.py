#!/usr/bin/env python3
"""
One-time Google Drive OAuth2 authentication helper.

Generates a refresh token that allows the brain sync scripts to read/write
files in a designated Google Drive folder without requiring user interaction.

Run this once locally:
  python dev/scripts/auth_google_drive.py

Then save the output JSON as a GitHub secret named GOOGLE_DRIVE_CREDENTIALS.
Also create a secret GOOGLE_DRIVE_BRAIN_FOLDER_ID containing the Drive folder ID
where brain docs should be synced.

To find the folder ID: open the folder in Google Drive and copy the ID from
the URL: https://drive.google.com/drive/folders/<FOLDER_ID>

Requirements (install before running):
  pip install google-auth-oauthlib
"""

import json
import os
import sys

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("ERROR: google-auth-oauthlib not installed")
    print("Install with: pip install google-auth-oauthlib")
    sys.exit(1)

SCOPES = [
    "https://www.googleapis.com/auth/drive",
]


def main() -> None:
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("ERROR: Missing required environment variables")
        print("Set these before running:")
        print("  export GOOGLE_CLIENT_ID=<your-client-id>")
        print("  export GOOGLE_CLIENT_SECRET=<your-client-secret>")
        print()
        print("To get these:")
        print("  1. Go to https://console.cloud.google.com/")
        print("  2. Create or select a project")
        print("  3. Enable the Google Drive API")
        print("  4. Create OAuth2 credentials (Desktop application type)")
        print("  5. Extract client_id and client_secret from the downloaded JSON")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8080/"],
            }
        },
        scopes=SCOPES,
    )

    print("Opening browser for Google Drive authorization...")
    print("If no browser opens, visit the URL printed below.\n")

    credentials = flow.run_local_server(
        host="localhost",
        port=8080,
        open_browser=False,
        access_type="offline",
        prompt="consent",
    )

    if not credentials.refresh_token:
        print("ERROR: No refresh token returned. Re-run with a fresh consent flow.")
        sys.exit(1)

    credentials_dict = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": list(credentials.scopes),
        "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
    }

    print("\n" + "=" * 70)
    print("SUCCESS! Save the JSON below as GitHub secret GOOGLE_DRIVE_CREDENTIALS:")
    print("=" * 70)
    print(json.dumps(credentials_dict, indent=2))
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Copy the JSON above")
    print("2. Go to GitHub → Settings → Secrets and variables → Actions")
    print("3. Create secret: GOOGLE_DRIVE_CREDENTIALS  (paste the JSON)")
    print("4. Create secret: GOOGLE_DRIVE_BRAIN_FOLDER_ID  (your Drive folder ID)")
    print()
    print("Find your folder ID:")
    print("  Open the Google Drive folder → copy ID from URL:")
    print("  https://drive.google.com/drive/folders/<FOLDER_ID>")


if __name__ == "__main__":
    main()
