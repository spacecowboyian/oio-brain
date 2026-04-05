# OIO Picker Intake Web UI

This directory provides a lightweight web UI to create and commit
`intake/selected-photos.json` for the Option B intake path.

## What it does

- Accepts selected Google Photos media IDs (paste JSON from your picker response)
- Builds a session payload using the repo schema
- Lets you download `selected-photos.json` locally
- Optionally commits `intake/selected-photos.json` to GitHub via API token

## Run locally

```bash
cd intake/web
python3 -m http.server 8000
# open http://localhost:8000
```

## Input format

Paste a JSON array of selected items in the UI:

```json
[
  {
    "id": "AMxabc123",
    "filename": "IMG_1234.JPG",
    "description": "RayRocks launch",
    "baseUrl": "https://lh3.googleusercontent.com/...",
    "creationTime": "2026-04-05T16:25:00Z"
  }
]
```

Only `id` is required.

## Commit flow

1. Set `owner/repo` (for example `spacecowboyian/oio-brain`)
2. Set a GitHub token with repo write permissions
3. Set branch (default `main`)
4. Click **Commit to GitHub**

The UI writes `intake/selected-photos.json` in the target branch.

## Notes

- This UI intentionally avoids build tooling to keep adoption simple.
- Ingestion is handled by `scripts/ingest_photos.py`.
- Marking items as processed happens during ingestion.
