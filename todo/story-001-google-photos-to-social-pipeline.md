---
title: "Story 001 — Google Photos → Picdump → Social Media Pipeline"
type: notes
status: draft
owner: Ian Jennings
updated: 2026-03-28
tags: [todo, automation, photos, social-media, google-photos, picdump, postbridge]
source_of_truth: false
summary: User story for building an automated pipeline that syncs photos from a Google Photos album into the picdump, uses an AI agent to file and caption them, and exposes a lightweight interface for reviewing and scheduling posts to PostBridge.
---

# Story 001 — Google Photos → Picdump → Social Media Pipeline

**Status:** Not started — parked for future development  
**Priority:** TODO  
**Area:** Tooling / Automation

---

## User Story

**As Ian,** I want to connect a Google Photos album to the picdump so that new race and event photos are automatically picked up, filed, captioned, and queued for social media — with minimal manual effort on my end — so I can stay consistent on social without spending hours writing captions or scheduling posts.

---

## Background

The picdump already exists as an intake queue for images. The goal here is to extend that system end-to-end: from camera roll → Google Photos → picdump → AI filing → caption drafting → PostBridge draft → my approval → published post.

---

## Acceptance Criteria

### 1. Google Photos Sync

- A specific public Google Photos shared album serves as the source folder. No API auth required — use the public shared album URL.
- A GitHub Action runs on a schedule (multiple times per day — e.g., every 4–6 hours) and checks for new photos in that album.
- Any new photos that haven't already been processed are downloaded and dropped into the `picdump/` folder.
- The action commits the new images to the repo so the existing picdump processing workflow can pick them up.

### 2. AI Filing Agent

- The existing picdump processing agent attempts to identify each photo: what car, what event, what driver, what context.
- If the agent can determine enough context, it files the photo to the correct location in the `photos/` library and logs it.
- **If the agent cannot confidently identify what it's looking at**, it notifies Ian via GitHub Actions — the action run result or a follow-up job surfaces a summary prompting Ian to review. A Slackbot integration is a secondary option worth evaluating if GitHub notifications prove insufficient.

### 3. Caption Generation Interface

- A lightweight React web app (as minimal as possible — no heavy framework overhead) allows Ian to view photos that have been filed but not yet posted.
- For each photo, Ian can type a short, rough description (a few words or a sentence).
- That description is sent to Claude, which generates a polished, on-brand caption in OIO voice.
- The generated caption can be reviewed inline and accepted, adjusted, or regenerated.

### 4. PostBridge Draft Integration

- Once a caption is approved (or adjusted), the interface automatically submits a draft post to PostBridge via the PostBridge API.
- PostBridge API credentials are stored as GitHub repository secrets and injected at runtime — never hardcoded.
- The draft includes the image and the approved caption.
- Ian does **not** need to leave the interface to push to PostBridge.

### 5. Inline Post Review and Scheduling

- The interface also shows all current PostBridge drafts.
- Ian can approve a draft for publishing, adjust the caption inline, or set a scheduled post time — all from within the same interface.
- No context-switching between tools to go from photo → caption → scheduled post.

---

## Out of Scope (for this story)

- Multi-platform cross-posting logic (handle that separately)
- Automatic posting without approval (Ian always approves before publish)
- Video handling (photos only for now)

---

## Decisions Made

| Question | Decision | Date |
|---|---|---|
| Google Photos auth | No auth required — use a public shared album URL | 2026-03-28 |
| Notification channel | GitHub Actions run results/summaries as primary; Slackbot as secondary option | 2026-03-28 |
| Interface stack | Lightweight React app | 2026-03-28 |
| PostBridge API auth | Credentials stored in GitHub repo secrets | 2026-03-28 |

## Open Questions

- Which specific Google Photos shared album URL(s) should be watched?

---

## Notes

- The existing `.github/workflows/process-picdump-photos.yml` GitHub Action is the right integration point for filing — extend it, don't replace it.
- Caption voice must follow the OIO Brand Guide (see `OIO Brain/01 - Brand/`).
- This story is parked — **do not start implementation** until Ian says go.
