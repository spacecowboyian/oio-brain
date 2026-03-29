# Transcripts

Auto-generated YouTube transcripts for OIO Racing videos.

Each video gets its own folder named `YYYY-MM-DD_video-title/` containing:
- `transcript.md` — Full transcript with timestamps and YAML frontmatter
- `metadata.json` — Structured metadata for automation

## How transcripts are fetched

The `fetch-youtube-transcripts` workflow runs **automatically every 2 hours** on a cron schedule.
Each run fetches up to 25 new videos (configurable), commits them, and stops.
The next run automatically picks up where the last one left off (already-processed videos are skipped).
This batched approach avoids YouTube rate limiting that caused bulk fetch attempts to fail.

### Manual dispatch options

Trigger the workflow manually from the Actions tab with these optional inputs:

| Input | Default | Description |
|---|---|---|
| `batch_size` | `25` | Max videos to fetch in this run (set `0` for no limit) |
| `fetch_all` | `false` | Re-fetch all transcripts, including already-processed ones |

### Adding transcripts for all existing videos

The cron schedule will process all videos automatically over time (360 videos ÷ 25 per run = ~15 runs, ~30 hours total). To speed this up, trigger the workflow manually multiple times or increase `batch_size`.
