---
title: OIO Current State
type: state
status: active
owner: Ian Jennings
updated: 2026-04-05
tags: [state, current, season-2026]
source_of_truth: false
summary: Live snapshot of what OIO is focused on right now. Update this file whenever the state changes. AI agents should read this first before any other file.
---

# OIO Current State

> **AI agents: read this first.** This file is the current-state snapshot. It is not a permanent reference — it reflects reality as of the `updated` date above.

*As of: April 5, 2026 — content machine recovery*

---

## What OIO Is Focused On Right Now

The 2026 motorsport season is opening. The primary focus is:

1. **Content machine recovery** — Fit How-To pipeline and vlog cadence fell behind in March. April reset underway: Fit clutch video due Apr 10, catch-up vlog before Apr 20, COC season premiere on Apr 20.
2. **Getting the Goblin ready** — motor is shot, rebuild is in progress. Season-long question: will it make it?
3. **Fitty Cent dual-duty season** — kids (Miles, Hudson) are racing Ian's daily driver in both autocross and rallycross
4. **Dale's Lake Garnett pilgrimage** — Celica is active, season-long build arc toward October's cathedral moment

---

## Active Vehicles

| Nickname | Car | Driver | Status | Blocker |
|---|---|---|---|---|
| The Goblin | 1985 Toyota MR2 AW11 | Ian | **Non-operational** | Diagnostic complete — bearing failure + cyl 4 at 35 PSI. Rebuild vs. replace TBD. |
| Dale | 1972 Toyota Celica | Ian | Active | None currently |
| Fitty Cent | 2009 Honda Fit GE8 | Ian / Kids | Active | Dual-duty workload on one car |
| Nessie | 1982 Toyota Cressida Wagon | Ian | Building | Drag setup not complete |
| Killer Corolla | 1977 Toyota Corolla | Ian | **Down** | 6-year resurrection, $100 mystery motor |
| Geoffrey | 1962 Renault Dauphine | Ian | Just acquired | Build direction not yet defined |

---

## Active Content Efforts

| Format | Status | Notes |
|---|---|---|
| Honda Fit How-To | Active — must run monthly | Pipeline needs to stay stocked |
| Vlog | Active | Opens/closes at Project Board each episode |
| Church of Combustion | Pending first event | Season opener CoC episode not yet started |
| Kids racing documentary | Planning | Debut target: mid-2026 |

---

## What Is Blocked

| Item | Blocker | Notes |
|---|---|---|
| Goblin on track | Motor rebuild not complete — rebuild vs. replace decision pending | Diagnostic done: bearing failure, cyl 4 at 35 PSI |
| Nessie drag debut | Setup not complete | 2026 dragstrip appearance is goal |
| Killer Corolla | Mystery motor status unknown | Full rebuild required |
| Geoffrey build direction | Too new — no plan yet | First step: assess condition |
| Sponsorship revenue | No active sponsors | **Research complete** — media kit strategy + SEO keywords defined. Next: write outreach messages. |
| Website | **Built, pending deployment** | **Build complete** (Paperclip OUT-123, completed 2026-03-31) — Astro 5 + Tailwind CSS with YouTube/Instagram integration. Pending: API credentials, GitHub push, Vercel/Netlify setup, domain config. |
| Merch | Not launched | **Platform research complete** — Shopify + Printful print-on-demand recommended. Decision + design selection pending. |
| Parker racing | Awaiting driver's permit | Gets permit at 14; once he has it, he races |

---

## Recent Changes

- **2026-03-31:** Website build complete — OIO Racing website built and ready for deployment (Paperclip OUT-123). Tech stack: Astro 5 + Tailwind CSS 4 with TypeScript. Features: YouTube Data API v3 integration (with mock fallback), Instagram Basic Display API, auto-sitemap, SEO optimization (OpenGraph, Twitter Cards), mobile-first responsive design, Lighthouse 90+. Core pages ready: Homepage, Videos, Schedule, Sponsors, Merch (Ecwid-ready), Contact. Project location: `/Users/ian/.paperclip/instances/default/workspaces/8a3fa8e5-7267-4c99-8471-c89e355f6ffd/oio-racing/`. Deployment blockers: API credentials, GitHub setup, Vercel/Netlify config, domain DNS. Comprehensive README included with setup and deployment guides.
- **2026-03-30:** Racing brand voice document complete — OIO Racing Brand Voice Document finalized (Paperclip OUT-19). Defines tone, messaging, and content pillars for the channel.
- **2026-03-30:** Website + merch platform research complete — CMO completed comprehensive competitive analysis of 6 grassroots automotive YouTube channels (S/M/L/XL tiers). Key findings: Shopify dominates (95%+ market share), YouTube Merch Shelf integration critical, mobile-first UX required. Recommended stack: Shopify Basic ($39/mo) + Printful (print-on-demand) + YouTube Merch Shelf + automation (Zapier/RSS feeds). Sponsor strategy delivered: media kit components, SEO keywords, landing page structure. Full research filed in Paperclip task OUT-104. Next: platform decision + account setup.
- **2026-03-29:** Social media post indexing system launched — `scripts/fetch_social_posts.py` + `.github/workflows/fetch-social-posts.yml` created. Posts fetched from Facebook Page and Instagram Business Account via Meta Graph API. Runs daily at 9 AM CDT; 25 posts/platform/run for conservative initial import. Posts stored as markdown in `data/social-posts/facebook/` and `data/social-posts/instagram/`. Requires 3 secrets: `META_ACCESS_TOKEN`, `META_FACEBOOK_PAGE_ID`, `META_INSTAGRAM_ACCOUNT_ID`. See `data/social-posts/README.md` for setup.
- **2026-03-29:** KCRX 2026 Event 1 results logged (March 22, Ray Rocks). **Corrected results:** Ryan 2nd MR (trophy), Miles 3rd MR (trophy), Hudson wins Novice (trophy). Ian DNF'd run 7 — official Pronto display shows him 1st (318.321, 6 runs) but DNF penalty corrects to 7th (393.784). Goblin post-race failure confirmed. `2026-Season-Results.md` and `oio-racing-results.json` created.
- **2026-03-29:** 2025 season competition results processed — full KCR RallyCross (8 events) and KS Region RallyCross (5 events) results filed. New files: `events/results/2025-Season-Results.md` and `KSRX-Historical-2018-2024.md`. Notable: Hudson Smith debuted at KCRX E8 (Novice, 2nd place), Ian switched to Honda Fit for season finale (MR2 sidelined), Ryan won E9 driving the MGB GT. Source `oio_results.json` deleted from docdump.
- **2026-03-29:** Transcript system clarified — two types distinguished: (1) final YouTube video transcripts (`transcripts/` repo root, auto-fetched) and (2) raw dailies (`intake/dailies/`, manual intake). `intake/docs/transcripts/` renamed to `intake/dailies/`. `process-transcripts.yml` replaced with `process-dailies.yml`. Rogue daily `failedfit lutchbleeddrive.txt` processed and deleted — summary filed at `content/summaries/2026-03-29_failed-fit-clutch-bleed-drive.md`. Honda Fit Maintenance-Log.md created.
- **2026-03-29:** Racing result links processed — comprehensive KCRSCCA + KSRX URL reference (2017–2024, AX + RX) filed as `events/results/KCRSCCA-Results-Links.md`. All direct links to every individual event result page now in the brain. Source deleted from docdump.
- **2026-04-05:** April content reset — schedule updated: Fit clutch video moved to Apr 10 (replaces Apr 2 Fit How-To slot), flexible catch-up vlog inserted before Apr 20, COC season premiere unchanged. Focus shift to content machine recovery.
- **2026-04-01:** Legacy caption drafts cleaned up — 17 pre-generated caption drafts (OUT-48–OUT-64) for 2025 video backlog removed from `content/caption-drafts/`. Workflow shift: captions now generated on-demand as new videos are posted rather than pre-batched. README updated to document cleanup. Changes pushed to GitHub (Paperclip OUT-166).
- **2026-03-29:** MR2 quick rack recovery documented — Ian recovered the quick steering rack from the old rallycross MR2 at Alex's house on 2026-03-18 and installed it on the Goblin same day before KCRX E1 (Mar 22, Ray Rocks). Steering Rack Swap marked done in MR2 Overview.md. U-joint connector lesson logged in Setup-Notes.md. Video idea added to backlog. Source deleted from docdump.
- **2026-03-28:** Goblin engine diagnostic complete — post-rallycross inspection done. Confirmed bearing failure (lock-up), cylinder 4 at 35 PSI, oil contamination across all cylinders (heaviest cyl 1), heavy valve carbon, loose cyl 1 plug wire. Root cause not yet isolated. Rebuild vs. replace decision pending. See `cars/ian/mr2-goblin/Maintenance-Log.md`.
- **2026-03-28:** Photo library system launched — `photos/` folder created, organized by driver/car. `photos/README.md` created at repo root. GitHub Action `process-picdump-photos.yml` created to auto-spawn Copilot agent whenever images are pushed to `intake/photos/`.
- **2026-03-28:** First photo filed — `IMG_8181.png` (Goblin MR2 rallycross action shot) moved to `photos/Ian/1985-MR2-Goblin/`. MR2 Overview.md updated with Visual Identification section and photo reference.
- **2026-03-28:** Expanded KCRSCCA competition data processed — full AX + RX history 2021–2024 for Ian, Ryan, Miles, Keegan, Robyn, and Matthew. Updated 9 brain files: historical results, MR2, Honda Fit, Celica, MGB GT, Lincoln Continental, Tercel, Team-Bios, and current-state. Also corrected Ian = primary driver, Miles = co-driver framing throughout.
- **2026-03-28:** Miles Smith's rallycross history updated — confirmed as co-driver of MR2, KCRSCCA season trophy holder (3rd and 4th place). KCRSCCA results archive 2017–2024 processed and deleted from docdump. See Team-Bios.md and MR2 Overview.md.
- **2026-03-28:** Tootie added to brain — Karen's 1965 Chevrolet Suburban (blue). Ian and kids do occasional work on it; may appear in OIO content. Filed under `cars/karen/`.
- **2026-03-28:** Team project status updated — MGB GT (orange paint/rebuild), Goblin (mostly dead/4AG assessment), 2001 Car (slow build/Gambler 500), Richard Starlet Miata rear end consideration noted
- **2026-03-28:** 2026 content schedule rebooted — new schedule created in `content/schedule.md`. Full race calendar added to `events/schedules.md`.
- **2026-03-28:** Channel gap identified — no uploads since Mar 4. First priority: Fit How-To on Apr 2 (overdue by 4+ weeks).
- **2026-03-27:** OIO Brain repository established — canonical operational brain created
- **2026-03-27:** Fitty Cent nickname confirmed and corrected throughout
- **2026 (pre-season):** Geoffrey (1962 Renault Dauphine) recently acquired

---

## What Matters Right Now

1. Goblin rebuild — document every step, this is content
2. First Fit How-To of 2026 — don't let the pipeline gap
3. Season opener planning — which events, which cars, who's filming
4. Sponsorship outreach — costs are not covered

---

## Congregation Active Arcs

| Driver | Car | Arc | Status |
|---|---|---|---|
| Ryan | MGB GT | Stripped to bare metal, rebuilt with Bondo + new metal + new design cues. Orange paint imminent. Returns to rallycross after paint. | Nearly ready |
| Ryan | The 2001 Car | Gambler 500 Kansas run — slowly building, target later in 2026 | Building |
| Ryan | AE86 | 1UZ V8 swap — national rallycross push | In progress |
| Richard | ST205 | Bits and bobs; active SCCA competitor | Ongoing |
| Richard | Starlet | 4AG swap planned; also considering Miata rear end + subframe | Planning |
