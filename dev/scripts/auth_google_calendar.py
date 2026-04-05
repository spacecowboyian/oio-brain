#!/usr/bin/env python3
"""
One-time Google Calendar OAuth2 helper.

This script generates a refresh token for Google Calendar access using the
existing GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.

Usage:
  ./venv/bin/python scripts/auth_google_calendar.py

Required environment:
  GOOGLE_CLIENT_ID
  GOOGLE_CLIENT_SECRET
"""

import json
import os
import sys

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("ERROR: google-auth-oauthlib not installed")
    print("Install with: ./venv/bin/pip install google-auth-oauthlib")
    sys.exit(1)


SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main() -> None:
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
      print("ERROR: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set")
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

    print("\nA browser flow will open on http://localhost:8080/ for the callback.")
    print("If Google rejects that redirect, add http://localhost:8080/ to the OAuth client's allowed redirect URIs.\n")
    credentials = flow.run_local_server(
        host="localhost",
        port=8080,
        open_browser=False,
        access_type="offline",
        prompt="consent",
    )

    if not credentials.refresh_token:
        print("ERROR: No refresh token returned")
        sys.exit(1)

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": credentials.refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    print("\nSuccess. Google Calendar credentials:\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
