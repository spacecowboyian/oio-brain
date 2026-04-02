# docs/

Technical pipeline documentation for OIO Brain automation systems.

These docs cover the operational details of the automated workflows that feed data into the brain. They are written for developers and agents who need to understand, debug, or extend the pipelines.

---

## Contents

| File | Covers |
|---|---|
| [transcript-pipeline.md](transcript-pipeline.md) | YouTube transcript fetch pipeline — `fetch_transcripts.py`, `clean_transcripts.py`, GitHub Actions workflow |
| [social-media-system-architecture.md](social-media-system-architecture.md) | Full social media pipeline — Google Photos → picdump → AI captions → PostBridge |
| [social-media-engineering.md](social-media-engineering.md) | Complete social media infrastructure status — all 6 phases, current deployment state |
| [caption-generation-service.md](caption-generation-service.md) | AI caption generation service — `caption_generation_service.py`, API interface |
| [caption-monitoring.md](caption-monitoring.md) | Caption quality monitoring dashboard — metrics, selection rates, feedback tracking |
| [catalog-maintenance.md](catalog-maintenance.md) | Ongoing maintenance status for photo and video catalogs |
| [slackbot-setup.md](slackbot-setup.md) | Setup guide for the OIO Slackbot (Slack app creation, bot permissions, Railway deployment) |
| [slackbot-social-media.md](slackbot-social-media.md) | Slack bot interface for mobile photo review and posting |
| [postbridge-integration.md](postbridge-integration.md) | PostBridge API integration — `postbridge_client.py`, draft creation, scheduling |
| [post-scheduling.md](post-scheduling.md) | Post scheduling and optimal times — historical analysis, automated scheduling |
| [social-media-deployment.md](social-media-deployment.md) | Deployment guide for the social media pipeline |
| [social-media-integration-testing.md](social-media-integration-testing.md) | Integration testing guide |
| [social-media-troubleshooting.md](social-media-troubleshooting.md) | Troubleshooting common issues |

---

*For brain content, data, and editorial docs, see [`active/`](../active/), [`brand/`](../brand/), [`cars/`](../cars/), and [`INDEX.md`](../INDEX.md).*
