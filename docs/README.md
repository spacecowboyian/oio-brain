# docs/

Technical pipeline documentation for OIO Brain automation systems.

These docs cover the operational details of the automated workflows that feed data into the brain. They are written for developers and agents who need to understand, debug, or extend the pipelines.

---

## Contents

| File | Covers |
|---|---|
| [transcript-pipeline.md](transcript-pipeline.md) | YouTube transcript fetch pipeline — `fetch_transcripts.py`, `clean_transcripts.py`, GitHub Actions workflow |
| [social-media-system-architecture.md](social-media-system-architecture.md) | Full social media pipeline — Google Photos → picdump → AI captions → PostBridge |
| [social-media-engineering.md](social-media-engineering.md) | Complete social media infrastructure status across all 6 build phases |
| [caption-generation-service.md](caption-generation-service.md) | AI caption generation service — `caption_generation_service.py`, API interface |
| [caption-monitoring.md](caption-monitoring.md) | Caption quality monitoring dashboard — metrics, performance, feedback |
| [slackbot-social-media.md](slackbot-social-media.md) | Slack bot interface for mobile photo review and posting |
| [slackbot-setup.md](slackbot-setup.md) | Slackbot setup and configuration guide |
| [post-scheduling.md](post-scheduling.md) | Post scheduling and optimal times — engagement analysis, automation |
| [postbridge-integration.md](postbridge-integration.md) | PostBridge API integration guide — drafts, scheduling, publishing |
| [catalog-maintenance.md](catalog-maintenance.md) | Ongoing maintenance status for photos and video catalogs |
| [social-media-deployment.md](social-media-deployment.md) | Deployment guide for the social media pipeline |
| [social-media-integration-testing.md](social-media-integration-testing.md) | Integration testing guide |
| [social-media-troubleshooting.md](social-media-troubleshooting.md) | Troubleshooting common issues |

---

*For brain content, data, and editorial docs, see [`brain/`](../brain/) and [`INDEX.md`](../INDEX.md).*
