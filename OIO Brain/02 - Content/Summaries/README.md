---
title: Video Summaries
type: content
status: active
owner: Ian Jennings
updated: 2026-03-29
tags: [content, transcripts, summaries, video]
source_of_truth: false
summary: AI-generated summaries of OIO Racing video transcripts. Each file summarizes one video — key topics, cars, people, events, and brain updates triggered. Populated by the process-transcripts workflow when Ian drops transcript files in docdump/transcripts/.
---

# Video Summaries

AI-generated summaries from raw video transcripts.

Each summary covers one video and follows the `transcript-summary` template from `00-core/templates/transcript-summary.md`.

## How Summaries Are Created

1. Ian drops a raw transcript file into `docdump/transcripts/`
2. The `process-transcripts` GitHub Actions workflow triggers automatically
3. A Copilot agent reads the transcript and generates a summary using the template
4. The summary is saved here as `YYYY-MM-DD_video-title.md`
5. The source transcript file is deleted from `docdump/transcripts/`

## Summary Files

| File | Video | Date |
|---|---|---|
| *(none yet — summaries will appear here as transcripts are processed)* | | |
