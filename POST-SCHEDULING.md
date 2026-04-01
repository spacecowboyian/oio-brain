---
title: Post Scheduling & Optimal Times
type: operations
status: active
owner: Social Media Engineer
updated: 2026-04-01
tags: [operations, scheduling, optimization, automation, social-media]
---

# Post Scheduling & Optimal Times

Automated system for scheduling social media posts at optimal times based on historical engagement patterns.

---

## Overview

The post scheduling system:

1. **Analyzes** historical posts from Instagram and Facebook
2. **Identifies** optimal posting times and days per platform
3. **Automatically** schedules new drafts to maximize engagement
4. **Logs** all scheduling decisions for future refinement

---

## How It Works

### 1. Historical Analysis

**Script:** `scripts/analyze_posting_times.py`

Examines all published posts in `OIO Brain/data/social-posts/`:
- Extracts posting date and time from each post file
- Aggregates by day of week (Monday-Sunday)
- Aggregates by hour of day (0-23)
- Identifies days and hours with most posts

**Output:** `OIO Brain/data/optimal-posting-schedule.json`

```json
{
  "instagram": {
    "best_time": "12:00",
    "best_day": "Tuesday",
    "recommended_times": ["12:00", "15:00", "18:00"],
    "recommended_days": ["Tuesday", "Thursday"],
    "timezone": "America/Chicago"
  },
  "facebook": {
    "best_time": "10:00",
    "best_day": "Wednesday",
    "recommended_times": ["10:00", "14:00", "17:00"],
    "recommended_days": ["Wednesday", "Saturday"],
    "timezone": "America/Chicago"
  }
}
```

### 2. Draft Detection

**Script:** `scripts/auto_schedule_posts.py`

Via PostBridge API, finds all drafts with `status: "draft"`:
- Queries PostBridge for unscheduled posts
- Extracts platform (Instagram, Facebook) for each draft
- Prepares for scheduling

### 3. Optimal Time Calculation

For each draft:
1. Look up platform in optimal schedule
2. Find next occurrence of recommended day
3. Schedule at recommended time
4. Ensure at least 1 hour in the future

**Example:**
- Today: Tuesday 2 PM
- Platform: Instagram
- Best day: Tuesday at 12 PM (already passed)
- Next occurrence: Next Tuesday at 12 PM
- Schedule: Next Tuesday at 12 PM

### 4. Scheduling via PostBridge

Uses PostBridge API `schedule_post()` method:
- POST `/posts/{post_id}/schedule`
- Specifies ISO 8601 timestamp
- Receives confirmation

### 5. Logging

**File:** `OIO Brain/data/post-scheduling-log.jsonl`

Each scheduling decision is logged:
```json
{
  "timestamp": "2026-04-01T07:15:30",
  "post_id": "post-123",
  "platform": "instagram",
  "scheduled": true,
  "scheduled_at": "2026-04-08T12:00:00"
}
```

---

## Automation Schedule

**GitHub Actions Workflow:** `.github/workflows/auto-schedule-posts.yml`

| Task | Schedule | Time |
|------|----------|------|
| Analyze posting times | Daily | 7 AM CDT |
| Auto-schedule drafts | Daily | 7 AM CDT |
| Update schedule file | Always | After analysis |
| Log decisions | Always | During scheduling |

---

## Configuration

### Optimal Posting Times

**Current Default** (if insufficient historical data):
```
Instagram:
  - Weekday: Tuesday at 12 PM CDT
  - Weekend: Saturday at 3 PM CDT
  - Best hours: 12-6 PM

Facebook:
  - Weekday: Wednesday at 10 AM CDT
  - Weekend: Sunday at 2 PM CDT
  - Best hours: 9 AM - 5 PM
```

**Note:** These defaults will be replaced with actual analysis once sufficient historical posts are available.

### PostBridge Integration

Required: `POSTBRIDGE_API_KEY` GitHub secret

The auto-scheduler uses PostBridge API to:
- List unscheduled drafts
- Schedule posts to specific times
- Track scheduling status

---

## Manual Scheduling

### Dry Run (Test Without Scheduling)

```bash
python scripts/auto_schedule_posts.py --dry-run
```

Shows what would be scheduled without committing changes to PostBridge.

### Manual Analysis

```bash
# Analyze all platforms
python scripts/analyze_posting_times.py

# Analyze specific platform
python scripts/analyze_posting_times.py --platform instagram

# Generate and save schedule
python scripts/analyze_posting_times.py --generate-schedule
```

### Manual Scheduling

```bash
# Requires POSTBRIDGE_API_KEY environment variable
export POSTBRIDGE_API_KEY=...
python scripts/auto_schedule_posts.py
```

---

## Data Files

| File | Purpose | Format |
|------|---------|--------|
| `OIO Brain/data/social-posts/instagram/` | Historical Instagram posts | Markdown with frontmatter |
| `OIO Brain/data/social-posts/facebook/` | Historical Facebook posts | Markdown with frontmatter |
| `OIO Brain/data/optimal-posting-schedule.json` | Current optimal schedule | JSON |
| `OIO Brain/data/post-scheduling-log.jsonl` | Scheduling decisions log | JSONL (append-only) |

---

## Understanding Results

### Optimal Schedule Output

The analysis produces:

- **best_time** — Most recommended hour (24-hour format)
- **best_day** — Most recommended day of week
- **recommended_times** — Top 3 hours ranked by engagement
- **recommended_days** — Top 2 days ranked by engagement
- **day_distribution** — Posts per day with engagement scores
- **hour_distribution** — Posts per hour with engagement scores

### Scheduling Log

Each entry shows:
- **timestamp** — When scheduling occurred
- **post_id** — PostBridge post ID
- **platform** — Instagram or Facebook
- **scheduled** — True if successful
- **scheduled_at** — ISO 8601 timestamp of scheduled post time
- **error** — If failed, reason for failure
- **skipped** — If not applicable, reason for skip

---

## Limitations & Future Improvements

### Current Limitations

1. **Engagement Data Missing** — Currently uses post frequency as proxy
   - Real engagement metrics (likes, comments, shares) would improve accuracy
   - Would require additional Meta API integration
   
2. **Simple Time Bucketing** — Groups by hour, ignores time zones of audience
   - More sophisticated analysis could use timezone data

3. **No Audience Segmentation** — Single schedule for entire audience
   - Different audience segments may prefer different times
   - Could segment by demographics or post content type

### Future Improvements

1. **Engagement API Integration** — Fetch actual like/comment/share data from Meta
   - Would provide more accurate optimal times
   - Could track trends over time

2. **Content-Type Variation** — Different optimal times for different post types
   - Photos vs videos may perform better at different times
   - Event posts vs product announcements

3. **Timezone Awareness** — Account for audience timezone distribution
   - Peak engagement may vary by audience location

4. **A/B Testing** — Compare performance of posts scheduled at different times
   - Automatically adjust schedule based on actual results

---

## Troubleshooting

### Schedule Not Generated

1. Check if historical posts exist:
   ```bash
   ls OIO Brain/data/social-posts/instagram/
   ls OIO Brain/data/social-posts/facebook/
   ```

2. Ensure `fetch_social_posts.py` has been run (requires GitHub secrets configured)

3. Manually generate schedule:
   ```bash
   python scripts/analyze_posting_times.py --generate-schedule
   ```

### Posts Not Scheduled

1. Check PostBridge API key is configured as GitHub secret
2. Verify PostBridge API status
3. Check `post-scheduling-log.jsonl` for specific errors
4. Run dry-run to diagnose:
   ```bash
   python scripts/auto_schedule_posts.py --dry-run
   ```

### Scheduled at Wrong Time

1. Verify optimal schedule in `optimal-posting-schedule.json`
2. Check timezone setting (should be "America/Chicago")
3. Analyze historical posts to ensure accuracy:
   ```bash
   python scripts/analyze_posting_times.py
   ```

---

## Integration Points

### With Caption Generation

Scheduled posts automatically receive captions from caption generation service:
1. Draft is created with caption via `/post` command
2. Auto-scheduler finds unscheduled draft
3. Schedules to optimal time
4. PostBridge handles posting at scheduled time

### With Metrics System

Scheduling decisions are logged to `post-scheduling-log.jsonl`:
- Can be analyzed to track scheduling accuracy
- Compare scheduled vs actual post time
- Adjust schedule based on discrepancies

---

## See Also

- `SOCIAL-MEDIA-ENGINEERING.md` — Overall system architecture
- `CAPTION-MONITORING.md` — Caption quality monitoring
- `CATALOG-MAINTENANCE.md` — Photo and video catalog management
- `POSTBRIDGE_INTEGRATION.md` — PostBridge API details
