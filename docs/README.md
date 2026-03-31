# docs/

Technical pipeline documentation for OIO Brain automation systems.

These docs cover the operational details of the automated workflows that feed data into the brain. They are written for developers and agents who need to understand, debug, or extend the pipelines.

---

## Contents

| File | Covers |
|---|---|
| [transcript-pipeline.md](transcript-pipeline.md) | YouTube transcript fetch pipeline — `fetch_transcripts.py`, `clean_transcripts.py`, GitHub Actions workflow |
| [social-media-system-architecture.md](social-media-system-architecture.md) | Full social media pipeline — Google Photos → picdump → AI captions → PostBridge |
| [caption-generation-service.md](caption-generation-service.md) | AI caption generation service — `caption_generation_service.py`, API interface |
| [slackbot-social-media.md](slackbot-social-media.md) | Slack bot interface for mobile photo review and posting |
| [social-media-deployment.md](social-media-deployment.md) | Deployment guide for the social media pipeline |
| [social-media-integration-testing.md](social-media-integration-testing.md) | Integration testing guide |
| [social-media-troubleshooting.md](social-media-troubleshooting.md) | Troubleshooting common issues |

---

*For brain content, data, and editorial docs, see [`OIO Brain/`](../OIO%20Brain/) and [`INDEX.md`](../INDEX.md).*
