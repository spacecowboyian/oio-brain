---
title: OIO Current State
type: state
status: active
owner: Ian Jennings
updated: 2026-04-13
source_of_truth: false
summary: Live snapshot of what OIO is focused on right now. Update this file whenever the state changes. AI agents should read this first before any other file.
---

# OIO Current State

> **AI agents: read this first.** This file is the current-state snapshot. It is not a permanent reference — it reflects reality as of the `updated` date above.

---

## ⚠️ Brain Sync Requirement

This is the authoritative current state of OIO.

Rules:
- Agents MUST re-read this file before answering
- Agents MUST NOT rely on memory when this file exists
- If today's date is later than the `updated` field in the frontmatter above:
  → Assume changes may have occurred
  → Re-read before answering

If you have not read all six startup files (`README.md`, `active/current-state.md`, `active/priorities.md`, `active/open-loops.md`, `active/next-actions.md`, `INDEX.md`), stop and read them now. Responding before syncing is not permitted.

---

*As of: April 13, 2026 — post-AX E1 / 4AG motor in hand*

---

## What OIO Is Focused On Right Now

The 2026 motorsport season is underway. KCR Autocross E1 completed April 12. Primary focus:

1. **4AG motor teardown** — Motor picked up from Henry April 9, now on stand. Miles assigned as teardown/assessment lead. Parts to be ordered from Battle Garage. Need a table in the garage first.
2. **Fitty Cent dry tire setup** — AX E1 confirmed strategy: 225 sticky on 7.5" front, 205 340 treadwear on rear. Need 2 wheels + 2 tires (secondhand wheels if possible) before next dry event.
3. **Content machine recovery** — Autocross E1 vlog needs editing. Fit clutch How-To still pending. COC season premiere target April 20.
4. **Rallycross this Sunday (Apr 19 KCRX E2)** — Ian hoping to drive Ryan's MGB. Miles driving Miata. Both unconfirmed. Close the loop before committing to the drive.
5. **Fergus co-driving relationship** — Ian to discuss car improvement with Doug directly. Outcome will determine level of commitment to national events.

## Execution Capacity Constraint (Planning Baseline)

- OIO remains a highly DIY operation with Ian as the primary hands-on executor across wrenching, filming, editing, and publishing.
- Default assumption: only one major execution lane can run at full pace at a time (example: Goblin rebuild **or** major web/sponsor buildout), with smaller supporting tasks around it.
- Any plan that assumes multiple simultaneous major lanes must identify explicit additional owners and protected time blocks, or it is treated as over-capacity risk.

---

## Active Vehicles

| Nickname | Car | Driver | Status | Blocker |
|---|---|---|---|---|
| The Goblin | 1985 Toyota MR2 AW11 | Ian | **Non-operational — motor on stand** | 4AG picked up from Henry April 9. On stand in garage. Plugs likely frozen, main caps loose. Miles leads teardown. Parts to order from Battle Garage. Target: KCRX E3 (May 25). |
| Dale | 1972 Toyota Celica | Ian | Active — out for work | Motor at Clay County Engine Rebuilders (high-comp rebuild); body at Gary Rod and Chassis (rockers + AW11 rack). Both targeting end of May / mid-June return. |
| Fitty Cent | 2009 Honda Fit GE8 | Ian / Kids | Active | Dual-duty workload on one car |
| Nessie | 1982 Toyota Cressida Wagon | Ian | Building | Drag setup not complete |
| Killer Corolla | 1977 Toyota Corolla | Ian | **Down** | 6-year resurrection, $100 mystery motor |
| Geoffrey | 1962 Renault Dauphine | Ian | Not running — MMO soaking, plugs out | Engine locked; next: hand-crank attempt |

---

## Active Content Efforts

| Format | Status | Notes |
|---|---|---|
| Honda Fit How-To | Active — must run monthly | Pipeline needs to stay stocked |
| Vlog | Active | Opens/closes at Project Board each episode |
| Church of Combustion | Pending first event | Season opener CoC episode not yet started |
| Kids racing documentary | Planning | Debut target: mid-2026 |
| **Fitty Cent EST Build Arc** | **Active — planning** | 4-episode arc: rulebook ep → rebuild/swap vlog → dyno How-To → COC payoff. Spare L15 triage is first step. See [`active/arcs/fitty-cent-est-build.md`](arcs/fitty-cent-est-build.md) |

---

## What Is Blocked

| Item | Blocker | Notes |
|---|---|---|
| Goblin on track | Motor swap not yet complete | Motor confirmed: 3-rib 4AGE from Henry (pickup Apr 9, $350 + melted motor trade). Swap at Euro Speedworks (lift, ~1 day). New motor tear down + rebuild + hot tank at C-TEC required before install. |
| Nessie drag debut | Setup not complete | 2026 dragstrip appearance is goal |
| Killer Corolla | Mystery motor status unknown | Full rebuild required |
| Geoffrey build direction | Too new — no plan yet | First step: assess condition |
| Sponsorship revenue | No active sponsors | **Research complete** — media kit strategy + SEO keywords defined. Next: write outreach messages. |
| Website | **Built, pending deployment** | **Build complete** (Paperclip OUT-123, completed 2026-03-31) — Astro 5 + Tailwind CSS with YouTube/Instagram integration. Pending: API credentials, GitHub push, Vercel/Netlify setup, domain config. |
| Merch | Not launched | **Platform research complete** — Shopify + Printful print-on-demand recommended. Decision + design selection pending. |
| Parker racing | Awaiting driver's permit | Gets permit at 14; once he has it, he races |

---

## Recent Changes

- **2026-04-13:** Fitty Cent EST Build Arc imported into brain. Car profile updated (`cars/ian/fit-fittycent/Overview.md`), EST rules reference created (`resources/scca-est-rules-reference.md`), and full 4-episode arc document created (`active/arcs/fitty-cent-est-build.md`). Triage of spare L15 long block is first action.
- **2026-04-13:** KCR Autocross E1 (April 12) results processed. Hudson Smith 3rd EST in Fitty Cent (57.4 best, rain). Miles Smith ~5–7th EST (59.1 best, steady improvement). Ian co-drove Douglas Hitchcock's 1976 BMW 2002 "Fergus" in FSP — Douglas won at 58.477, Ian ran 61.872 (2nd/2). Ian's first-ever drive of Fergus revealed: spongy brakes, dead shifter, engine misfiring, heavy white smoke late in event. Doug dismissive of mechanical issues. Results in `events/results/2026-Season-Results.md`.
- **2026-04-13:** 4AG motor pickup confirmed complete. Motor arrived Friday April 9 from Henry. Now on engine stand in garage. Plugs likely frozen, main caps loose — minimal rotation. Parts to be ordered from Battle Garage per prior research kit. Miles Smith assigned as teardown lead. Work to begin ASAP. Log in `cars/ian/mr2-goblin/Maintenance-Log.md`.
- **2026-04-13:** Fitty Cent dry tire strategy finalized — 225 sticky (~200 treadwear) on 7.5" front wheel, 205 340 treadwear on rear. Budget: 2 wheels + 2 tires. Secondhand wheels if possible. Updated in `cars/ian/fit-fittycent/Overview.md`.
- **2026-04-13:** Upcoming rallycross Sunday April 19 (KCRX E2 Holsworth Farm) — Ian may drive Ryan's MGB; Miles may drive Miata. Both unconfirmed. Open loop added to `active/open-loops.md`.

- **2026-04-08:** Goblin 4AGE sourcing confirmed — motor pickup from Henry locked in for Friday, April 9. Motor is a 3-rib 4AGE (1st gen, 16-valve), set outside for a while; main caps show light rust but no other visible wear and no signs of major damage. Henry pulled and inspected main caps; bearings TBD after sizing. Rebuild requirements updated: stock-sized pistons confirmed, slightly higher compression head gasket, full rebuild kit, rings for standard-sized pistons, bearings TBD, new clutch (spec TBD). Research needed: best value for dollar on all components + oiling system (oil pickup, better oil pump, possibly 20-valve pump upgrade). Motor swap at Euro Speedworks — Ian helping Ryan on MGB rebuild in exchange for lift access; estimated 1 day with lift. See `cars/ian/mr2-goblin/Maintenance-Log.md`.
- **2026-04-08:** KCRX E2 (Apr 19, Holsworth Farm) driver lineup confirmed — Ian driving MGB GTS (Ryan's car, prepped with Ian's help); Miles driving red bomber Miata with Larry as co-driver. MGB prep underway at Euro Speedworks. See `events/schedules.md`.

- **2026-04-07:** Fitty Cent clutch hydraulics **RESOLVED** — pressure bleed performed at Ryan's shop. Pedal is functional; clutch no longer sucks to the floor. Clutch disc worn (~60k miles) but usable for 2026 season. Replacement required before 2027. Log updated in `cars/ian/fit-fittycent/Maintenance-Log.md`.
- **2026-04-07:** 2026 event dates confirmed — Lake Garnett Grand Prix Revival: **Oct 9–11, 2026 (8 track sessions)**. KCR Autocross: E2 Sat Apr 25, E3 Sun Apr 26, E5 Sat Aug 16 all confirmed. Remaining open: KCR E6 (TBD), E8-9 (verify Sep 27/Oct 24), KCRX E3 May 25 (not on family calendar), FIT OFF (mid-season TBD). Updated in `events/schedules.md`.
- **2026-04-08:** Goblin motor swap decision made — rebuild vs. replace resolved. Ian will source a 3-rib 4age from Henry for $350 + melted motor in trade. New motor will be torn down, refreshed, and hot-tanked at C-TEC (Miles's automotive program at North Kansas City High School) before installation. New clutch required. Stock pistons assumed; bearings TBD pending inspection. Research needed on cheap oil flow improvements for the 4age under G-forces. Target: Goblin on track by the 3rd Kansas City rallycross event of 2026. Decision logged in `core/decisions-log.md`; build plan in `cars/ian/mr2-goblin/Modifications.md`.
- **2026-04-08:** Dale April 2026 update entered — (1) **Motor rebuild:** 18RG from Hilux at Clay County Engine Rebuilders. Block wallowed out; new block sourced. All parts (nearly) ordered from Kameri (Japan). Custom stainless valves cut by Clay County. Target: end of May / mid-June. Post-rebuild config: dual 45mm Weber DCOE. (2) **Body work:** at Gary Rod and Chassis (Thomas Gary) — KlassicFab inner + outer rockers being installed; AW11 manual steering rack conversion with custom bracket. Both targeting end of May / mid-June. Fiberglass + paint to follow. Historical note: Thomas Gary previously installed the Ford 8.8 rear end in Dale. (3) **Lake Garnett:** confirmed second weekend of October 2026. Both workstreams coordinated to complete together as a full package.
- **2026-04-07:** Geoffrey (1962 Renault Dauphine) — Free All soak worked. All four spark plugs removed (with coaxing). Distributor pulled. ~895 ccs Marvel Mystery Oil poured into spark plug holes via old 1960s metal funnel. Valve cover removed — interior very rusty. MMO also poured into valve cover to seep past seals. Engine is still locked but next attempt is hand crank with plugs out; if that fails, put in gear and push back and forth to use transmission to help break it loose. Goal: get motor running for first time in ~40 years.
- **2026-04-06:** Photo pipeline rebuilt (US-001) — unified `dev/scripts/process_photos.py` replaces three separate scripts and the picker intake step. Polls OIO Google Photos album directly, runs Claude Vision for vehicle identification, generates captions, and creates PostBridge drafts in one run. Supabase dependency removed. Low-confidence photos route to `photos/unknown/photo-log.md` and are automatically retried when their descriptions change. Old workflows deprecated. New workflow: `.github/workflows/process-photos.yml` (every 6 hours).
- **2026-04-04:** Content cadence re-established for Apr 4-10.
- **2026-03-31:** Website build complete — OIO Racing website built and ready for deployment (Paperclip OUT-123). Tech stack: Astro 5 + Tailwind CSS 4 with TypeScript. Features: YouTube Data API v3 integration (with mock fallback), Instagram Basic Display API, auto-sitemap, SEO optimization (OpenGraph, Twitter Cards), mobile-first responsive design, Lighthouse 90+. Core pages ready: Homepage, Videos, Schedule, Sponsors, Merch (Ecwid-ready), Contact. Project location: `/Users/ian/.paperclip/instances/default/workspaces/8a3fa8e5-7267-4c99-8471-c89e355f6ffd/oio-racing/`. Deployment blockers: API credentials, GitHub setup, Vercel/Netlify config, domain DNS. Comprehensive README included with setup and deployment guides.
- **2026-03-30:** Racing brand voice document complete — OIO Racing Brand Voice Document finalized (Paperclip OUT-19). Defines tone, messaging, and content pillars for the channel.
- **2026-04-05:** Added explicit DIY execution-capacity guardrails across the brain (`README.md`, `INDEX.md`, `active/`, `core/`, and operating instructions) so agents default to conservative, runnable planning assumptions instead of multi-track optimistic plans.
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
- **2026-04-05:** Geoffrey (1962 Renault Dauphine) initial assessment — spark plugs rusted in place, hand crank would not turn the motor, and the cover had blown off onto the boat next to it. Next attempt: Free All soak and retry.

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
| Ryan | MGB GT | Stripped to bare metal, rebuilt with Bondo + new metal + new design cues. Orange paint imminent. **Ian helping Ryan finish prep for KCRX E2 (Apr 19). Ian will drive at that event.** | Prepping for Apr 19 |
| Ryan | The 2001 Car | Gambler 500 Kansas run — slowly building, target later in 2026 | Building |
| Ryan | AE86 | 1UZ V8 swap — national rallycross push | In progress |
| Richard | ST205 | Bits and bobs; active SCCA competitor | Ongoing |
| Richard | Starlet | 4AG swap planned; also considering Miata rear end + subframe | Planning |
