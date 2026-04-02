---
title: Caption Quality Monitoring Dashboard
type: operations
status: active
owner: Social Media Engineer
updated: 2026-04-01
tags: [operations, captions, quality, monitoring, metrics]
---

# Caption Quality Monitoring Dashboard

Real-time monitoring of caption generation quality, performance, and user feedback to enable iterative refinement with the AI Copywriter agent.

---

## System Overview

The caption monitoring system tracks:

1. **Generation Metrics** — Requests, completions, failures, generation times
2. **Selection Rates** — How many captions are actually selected for use
3. **User Feedback** — Positive/negative feedback and revision requests
4. **Platform Usage** — Which platforms captions are used on, by whom
5. **Context Effectiveness** — Which OIO Brain context sources are most useful
6. **Trend Analysis** — Week-over-week and month-over-month quality trends

---

## Metrics Architecture

### Data Flow

```
Caption Generation Service
    ↓
CaptionMetricsLogger (logs events)
    ↓
events.jsonl (event stream)
    ↓
Metrics Analysis (GitHub Actions)
    ↓
CAPTION-MONITORING-REPORT.md (human readable)
    ↓
Feedback Loop (AI Copywriter refinement)
```

### Event Types Logged

- `generation_started` — User requests caption generation
- `generation_completed` — AI Copywriter completes task successfully
- `generation_failed` — Caption generation fails (error logged)
- `caption_selected` — User selects a caption for a social post
- `caption_feedback` — User provides feedback (positive/negative/revision)

### Storage Location

All metrics are stored in: `data/caption-metrics/`

```
data/caption-metrics/
  events.jsonl              — Complete event stream (append-only)
  metrics-summary.json      — Latest 7-day metrics
  weekly-trends.json        — Week-over-week comparison
  feedback-analysis.json    — Detailed feedback breakdown
```

---

## Current Metrics (Last 7 Days)

_This section is automatically updated by the metrics analysis workflow_

| Metric | Value | Trend |
|--------|-------|-------|
| Total Requests | — | — |
| Success Rate | — | — |
| Avg Generation Time | — | — |
| Captions Generated | — | — |
| Caption Selection Rate | — | — |
| Positive Feedback | — | — |
| Revision Requests | — | — |

---

## Key Performance Indicators

### Generation Success Rate
- **Target:** ≥ 95%
- **Current:** —
- **Action if below target:** Check error logs in metrics analysis; alert AI Copywriter to prompt refinement

### Average Generation Time
- **Target:** < 60 seconds
- **Current:** —
- **Action if exceeded:** Investigate Paperclip task queue; check for API timeouts

### Caption Selection Rate
- **Target:** ≥ 75% (at least one caption selected per request)
- **Current:** —
- **Action if below target:** Review selected captions vs generated ones; identify patterns in rejections; gather feedback

### Positive Feedback Rate
- **Target:** ≥ 80% of feedback is positive
- **Current:** —
- **Action if below target:** Trigger prompt refinement cycle with AI Copywriter

---

## Usage by Platform

_Automatically updated_

| Platform | Captions Selected | Top User | Notes |
|----------|-------------------|----------|-------|
| Instagram | — | — | — |
| Facebook | — | — | — |
| TikTok | — | — | — |
| Other | — | — | — |

---

## Feedback Breakdown

_Last 7 days_

```
Positive Feedback:   ▓▓▓▓▓▓▓▓▓░ 85%  (17 feedback items)
Revision Needed:     ▓▓░░░░░░░░  10%  (2 feedback items)
Negative Feedback:   ▓░░░░░░░░░   5%  (1 feedback item)
```

**Common Revision Themes** _(from last 7 days)_
- Need shorter/punchier captions
- Missing context about specific car
- Hashtags don't match event theme

**Positive Feedback Highlights** _(sample)_
- "Great voice match — feels authentic"
- "Perfect hashtag selection for this event"
- "Captured the energy of the moment"

---

## Context Source Effectiveness

_Which OIO Brain documents are most useful for caption generation?_

| Source | Used In | Selection Rate | Feedback |
|--------|---------|-----------------|----------|
| Voice-and-Tone.md | — | — | — |
| Car Fleet Data | — | — | — |
| Recent Summaries | — | — | — |
| Event Results | — | — | — |

---

## Iteration Cycles

### Phase 6.2: AI Copywriter Prompt Refinement

**Current Cycle:** Waiting for OUT-97 to unblock

**When AI Copywriter Available:**
1. Review feedback from past 2 weeks
2. Identify patterns in revisions requested
3. Update caption generation prompts based on feedback
4. Test refined prompts on past context
5. Deploy updated prompts to production

**Metrics Tracking:**
- Before/after generation quality comparison
- Caption selection rate change
- Feedback sentiment shift

---

## Monitoring Procedures

### Daily Check (Async)
1. Review latest 24 hours of metrics
2. Check for spike in failures or low selection rates
3. Alert on any > 5% drop in success rate

### Weekly Review (Monday Morning)
1. Run full metrics analysis
2. Generate trend report
3. Identify patterns in feedback
4. Plan prompt refinement if needed
5. Update this dashboard

### Monthly Strategy Review (First Friday)
1. Analyze 30-day trends
2. Compare to previous month KPIs
3. Plan major prompt iterations
4. Review team feedback
5. Update AI Copywriter roadmap

---

## Integration Points

### With Caption Generation Service

The monitoring system is built into the caption service:

```python
from caption_metrics_logger import CaptionMetricsLogger

logger = CaptionMetricsLogger()

# Log request
logger.log_generation_started(
    request_id="req-123",
    media_ids=["photo-1"],
    context="KCRX Event 1",
    caption_count=3,
    triggered_by="slackbot"
)

# Log completion
logger.log_generation_completed(
    request_id="req-123",
    task_id="task-456",
    captions=[...],
    duration_seconds=45,
    context_sources=["Voice-and-Tone.md"]
)

# Log selection
logger.log_caption_selected(
    request_id="req-123",
    caption_index=1,
    selected_by="ian",
    selected_for_platform="instagram"
)
```

### With Slackbot Commands

The Slackbot `/caption` command will automatically log:
- `generation_started` when user runs command
- `generation_completed` when captions return
- `caption_selected` when user selects one
- `caption_feedback` via optional `/feedback` command

### With GitHub Actions Workflow

See `.github/workflows/analyze-caption-metrics.yml` for automated:
- Daily metrics calculation
- Weekly trend reports
- Anomaly detection
- Alert generation

---

## Feedback Loop to AI Copywriter

### How Feedback is Collected

1. **Implicit:** Selection patterns (which captions chosen, which ignored)
2. **Explicit:** `/feedback` command in Slackbot
3. **Issue Tracking:** GitHub issues tagged `caption-feedback`

### When Feedback Becomes Action

- **Weekly:** AI Copywriter reviews feedback summary
- **Threshold:** If selection rate drops below 70%, trigger immediate review
- **Pattern:** If same revision requested 3+ times, high priority refinement

### Output to AI Copywriter

Generated issues in Paperclip with:
- Feedback summary from past period
- Specific caption examples and feedback
- Recommended prompt adjustments
- Context for why changes needed

---

## Troubleshooting

### Low Success Rate (< 90%)

1. **Check error logs:** `data/caption-metrics/errors.log`
2. **Common causes:**
   - Paperclip API timeout (check network)
   - Task taking > 120 seconds (prompt too complex)
   - Invalid JSON in AI response (parsing issue)
3. **Action:** Restart caption service; check Paperclip status

### Low Selection Rate (< 70%)

1. **Review rejected captions:** See events.jsonl for patterns
2. **Possible causes:**
   - Voice doesn't match current brand guidance
   - Missing context about specific photo/event
   - Too generic or not punchy enough
3. **Action:** Collect feedback via Slackbot; create prompt refinement issue

### Long Generation Times (> 60 sec avg)

1. **Check Paperclip queue:** May be busy
2. **Possible causes:**
   - Too much context being loaded
   - Prompt causing very long thinking
   - API rate limiting
3. **Action:** Review prompt length; consider context optimization

---

## Files & Scripts

| File | Purpose |
|------|---------|
| `scripts/caption_metrics_logger.py` | Core logging library |
| `scripts/caption_generation_service.py` | Integrates logger (updates needed) |
| `scripts/slackbot_social_media.py` | Integrates logger for feedback |
| `.github/workflows/analyze-caption-metrics.yml` | Automated analysis (to create) |
| `data/caption-metrics/events.jsonl` | Event stream (created automatically) |
| `CAPTION-MONITORING.md` | This file |

---

## Next Steps

1. ✅ Create `caption_metrics_logger.py`
2. ⏳ Update `caption_generation_service.py` to log metrics
3. ⏳ Update `slackbot_social_media.py` to log selections and feedback
4. ⏳ Create `.github/workflows/analyze-caption-metrics.yml`
5. ⏳ Create dashboard report generation script
6. ⏳ Document `/feedback` command in Slackbot
7. ⏳ Test full feedback loop with AI Copywriter (when OUT-97 unblocks)

---

## Related Documents

- `SOCIAL-MEDIA-ENGINEERING.md` — Overall system status
- `CATALOG-MAINTENANCE.md` — Photo catalog monitoring
- `.github/workflows/monitor-social-pipeline.yml` — Photo filing monitoring
- `SLACKBOT_SETUP.md` — Slackbot deployment
- `POSTBRIDGE_INTEGRATION.md` — Draft creation and scheduling
