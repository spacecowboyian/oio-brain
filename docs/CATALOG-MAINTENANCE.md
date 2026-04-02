---
title: Catalog Maintenance Status
type: operations
status: active
owner: Social Media Engineer
updated: 2026-04-01
tags: [operations, catalog, maintenance, monitoring]
---

# Catalog Maintenance

Ongoing maintenance of OIO Racing's media catalogs (photos and videos).

## Current Status (April 1, 2026)

### Photos
- **PHOTO-INDEX.md**: Last updated March 29, 2026
- **Total photos in library**: 1 (IMG_8181.png in photos/Ian/1985-MR2-Goblin/)
- **picdump/ queue**: Empty (cleaned up after processing)
- **Status**: All photos properly filed and indexed

### Videos
- **OIO-Video-Catalog.md**: Last updated March 30, 2026 (360 videos)
- **Published-Videos.md**: Last updated March 28, 2026
- **Latest video**: March 4, 2026 (Headlight replacement - IkR0eHr1TfU)
- **Total views (all-time)**: 1.2M+
- **Status**: All videos fetched and cataloged. No pending items in docdump/

## Monitoring Procedures

### Video Monitoring (Automated)
1. **YouTube API Fetcher** (`scripts/oio-video-fetcher.js`) runs automatically after each PR merge to main
2. Fetcher detects new videos from the YouTube uploads playlist (UCA6AlnPQNu5u3Clq_hEmBKQ)
3. New videos are written to `docdump/oio_videos_raw.json`
4. Copilot agent automatically processes new video data into:
   - `OIO Brain/02 - Content/Published-Videos.md`
   - `OIO Brain/02 - Content/oio-videos-master.json`
   - `OIO-Video-Catalog.md`

**What to watch for:** Check if `docdump/oio_videos_raw.json` appears after PR merges. If it does, a Copilot issue will be created to process the new videos.

### Photo Monitoring (Manual)
1. New photos are placed in `picdump/` folder
2. AI Photo Filing Agent (`scripts/ai_photo_filing_agent.py`) automatically:
   - Identifies the car in each photo
   - Files photo to `photos/{Driver}/{Car}/`
   - Creates or updates `photo-log.md` for the car
   - Updates `PHOTO-INDEX.md`
3. Once processed, photos should be removed from picdump/

**What to watch for:** 
- Check `picdump/` folder is empty (it's a queue, not storage)
- Verify new photos appear in `PHOTO-INDEX.md` within 24 hours of being added
- If a photo cannot be identified, check `OIO Brain/01-active/open-loops.md`

## Files to Monitor

| File | Purpose | Update Frequency | Last Updated |
|------|---------|------------------|--------------|
| `PHOTO-INDEX.md` | Master photo index | When photos are filed | Mar 29, 2026 |
| `OIO-Video-Catalog.md` | Video index by car and performance | When new videos published | Mar 30, 2026 |
| `OIO Brain/02 - Content/Published-Videos.md` | Complete video catalog | When new videos published | Mar 28, 2026 |
| `OIO Brain/02 - Content/oio-videos-master.json` | Video metadata (source of truth) | Auto-refreshed by fetcher | Mar 4, 2026 (latest video) |
| `docdump/oio_videos_raw.json` | Staging area for new videos | Temporary (deleted after processing) | — |
| `picdump/` | Photo intake queue | Should stay empty | Empty (as of Apr 1) |

## Infrastructure

### Photo Pipeline
```
Raw photo (picdump/)
    ↓
AI Photo Filing Agent
    ↓
Identify car + file photo
    ↓
Create photo-log.md for car
    ↓
Update PHOTO-INDEX.md
```

### Video Pipeline
```
YouTube uploads
    ↓
YouTube API (after PR merge)
    ↓
oio-video-fetcher.js
    ↓
Update oio-videos-master.json
    ↓
New videos → docdump/oio_videos_raw.json
    ↓
Copilot agent processes
    ↓
Update Published-Videos.md, OIO-Video-Catalog.md
```

## Maintenance Checklist

- [x] picdump/ queue is empty
- [x] PHOTO-INDEX.md is current
- [x] OIO-Video-Catalog.md is current
- [x] Published-Videos.md is current
- [x] No videos pending in docdump/
- [x] All automation workflows are configured

## Next Steps

1. **Monitor for new uploads**: Check after each PR merge for `docdump/oio_videos_raw.json`
2. **Monitor for new photos**: Ensure photos added to picdump/ are processed within 24 hours
3. **Track stats**: Update view counts and engagement metrics as videos accumulate
4. **Maintain indexes**: Keep PHOTO-INDEX.md and OIO-Video-Catalog.md synchronized with source data

## Contact

For issues with:
- **Photo filing**: Check AI Photo Filing Agent logs in GitHub Actions
- **Video fetching**: Verify YOUTUBE_API_KEY is set in GitHub secrets
- **Copilot processing**: Check Issues for stuck tasks or errors
