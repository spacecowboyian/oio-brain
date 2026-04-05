#!/usr/bin/env python3
"""
One-time Google Photos API OAuth2 authentication helper.

This script runs locally once to generate a refresh token that enables
the sync_google_photos.py script to access your Google Photos library
without requiring user interaction.

Run this once:
  python dev/scripts/auth_google_photos.py

Then save the output credentials as a GitHub secret named GOOGLE_PHOTOS_CREDENTIALS.

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


def main():
    # Load credentials from environment
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("ERROR: Missing required environment variables")
        print("Set these before running this script:")
        print("  export GOOGLE_CLIENT_ID=<your-client-id>")
        print("  export GOOGLE_CLIENT_SECRET=<your-client-secret>")
        print("\nTo get these:")
        print("  1. Go to https://console.cloud.google.com/")
        print("  2. Create a new project or select an existing one")
        print("  3. Enable the Google Photos Library API")
        print("  4. Create OAuth2 credentials (Desktop application)")
        print("  5. Download the JSON and extract client_id and client_secret")
        sys.exit(1)

    # Create the OAuth2 flow
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
        scopes=["https://www.googleapis.com/auth/photoslibrary.readonly"],
    )

    # Run the local server flow (opens browser for consent)
    print("Opening browser for Google Photos authorization...")
    print("If no browser opens, visit the URL printed below.\n")
    credentials = flow.run_local_server(port=8080)

    # Extract the refresh token and credentials
    credentials_dict = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": credentials.refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    # Print the JSON blob for saving
    print("\n" + "=" * 70)
    print("SUCCESS! Copy the JSON below and follow the setup instructions:")
    print("=" * 70)
    print(json.dumps(credentials_dict, indent=2))
    print("=" * 70)
    print("\nNext steps:")
    print("1. Copy the JSON above (all of it)")
    print("2. Go to GitHub repository settings → Secrets and variables → Actions")
    print("3. Create a new repository secret named: GOOGLE_PHOTOS_CREDENTIALS")
    print("4. Paste the JSON into the secret value")
    print("5. Also create a secret named: GOOGLE_PHOTOS_ALBUM_ID")
    print("   (Find this in the Google Photos URL when viewing the album)")
    print("\nExample album ID: 'AL9nkcK...' from https://photos.app.goo.gl/AL9nkcK...")


if __name__ == "__main__":
    main()
