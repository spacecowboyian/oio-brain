---
title: OIO Open Loops
type: state
status: active
owner: Ian Jennings
updated: 2026-04-08
source_of_truth: false
summary: All pending decisions, unanswered questions, missing information, and things waiting on money, parts, time, people, or research. Update as loops open and close.
---

# Open Loops

Active as of March 2026. Mark items as resolved by adding `✅ [YYYY-MM-DD] — [resolution]` and moving them to the bottom of the section.

---

## Vehicles

- **Fitty Cent clutch hydraulics:** ✅ 2026-04-07 — Brake master replaced. Pressure bleed completed. Pedal functional — no longer sucks to floor. Clutch disc worn (~60k miles) but usable for 2026. Replace before 2027 season. See `cars/ian/fit-fittycent/Maintenance-Log.md`.
- **Goblin motor diagnosis:** ✅ 2026-03-28 — Two-stage diagnostic complete. Initial inspection confirmed bearing failure (lock-up), cyl 4 at 35 PSI, oil contamination across all cylinders, heavy valve carbon, loose cyl 1 plug wire. Follow-up wet compression test showed cyl 4 rising to ~60 PSI (partial recovery). Root cause not yet isolated. See `cars/ian/mr2-goblin/Maintenance-Log.md`.
- **Goblin — cyl 4 compression loss root cause:** Partially narrowed. Wet test (35→60 PSI) confirms ring sealing is a factor, but partial recovery means valve sealing may also be compromised. Heavy carbon on valve faces prevents visual confirmation of sealing surfaces.
- **Goblin — ring sealing vs. valve sealing contribution in cyl 4:** Wet compression test is consistent with partial ring failure, but cannot rule out carbon-fouled valve sealing. Both may be active failure modes.
- **Goblin — oil source in cylinder 4:** Upper area suspected but not confirmed. Valve seals? Head gasket? Rings? Oil reconfirmed present after follow-up inspection.
- **Goblin — top-end vs. bottom-end failure relationship:** Valve motion confirmed normal (no stuck valves). Carbon buildup significant but cannot visually confirm sealing. Relationship to bearing failure still unknown.
- **Goblin 4AG assessment status:** ✅ 2026-03-28 — Diagnostic complete. ✅ 2026-04-08 — Rebuild vs. replace decision made: replace. Sourcing 3-rib 4age from Henry for $350 + melted motor trade. ✅ 2026-04-08 — Pickup confirmed Friday April 9, 2026.
- **Goblin differential:** ✅ 2026-04-08 — No limited slip differential. Cost prohibitive and not needed to win locally. Not part of this rebuild.
- **Goblin rebuild timeline:** Target is the 3rd Kansas City rallycross event of 2026. KCRX E3 = May 25 (Thunder Valley). Is that confirmed on the family calendar?
- **Goblin rebuild budget:** Base motor cost is $350. Bearings TBD pending teardown sizing. Stock pistons confirmed. Slightly higher comp head gasket needed. Full rebuild kit + rings required. New clutch (spec TBD). Hot tank cost TBD. Oil flow mod cost TBD. Full parts list not yet finalized — research best value for dollar.
- **Goblin — 4age oiling system under rally G-forces:** Research needed before rebuild is buttoned up: oil pickup upgrade, better oil pump, possibly 20-valve pump upgrade. Confirm if 20v pump is the standard upgrade path or if better options exist. Cost-effective solutions prioritized.
- **Goblin motor condition (from Henry):** Main caps show light rust; no other visible wear; no signs of major damage. Bearings TBD after sizing — Henry pulled and inspected main caps. Await teardown findings.
- **Euro Speedworks swap weekend scheduling:** Arrange with Ryan — Ian helps Ryan on MGB rebuild in exchange for lift access. Estimated 1 day swap with lift. Timing TBD after motor pickup on Apr 9.
- **Mystery motor for Killer Corolla:** What is it? Does it run? Is it actually the right engine for the car? How long is the full rebuild?
- **Killer Corolla TRD parts inventory:** No documented inventory yet. What TRD parts are on the car?
- **Geoffrey (Dauphine) condition:** ✅ 2026-04-07 — Spark plugs removed after Free All soak. Distributor out. ~895 ccs Marvel Mystery Oil added through plug holes. Valve cover off (very rusty inside), MMO poured in. Engine still locked. Next: hand-crank attempt with plugs out; if fails, try transmission push method.
- **Geoffrey build direction:** "Rally car replica" is the stated goal but no details defined. What era? What spec? What rally?
- **Keegan's full collection — needs audit:** Keegan has roughly 8–9 cars total. The repo only covers the 1985 Tercel and Lincoln Town Car. The rest of his collection (Dustbuster vans and any other builds) need to be documented — which cars are active, which have appeared on OIO, and what years/models they are. Year confirmed for Tercel (1985); Lincoln Town Car year still unknown.

---

## Events

- **2026 rallycross schedule:** Which events is the OIO crew attending this season? Dates and locations not yet confirmed in the repo.
- **2026 autocross schedule:** KCR E2 (Sat Apr 25), E3 (Sun Apr 26), E5 (Sat Aug 16), E8 (Sun Sep 27), E9 (Sat Oct 24) confirmed. ⚠️ E6 date TBD (between May 17 and Sep 26).
- **KCRX E2 (Apr 19, Holsworth Farm) — driver lineup confirmed:** Ian driving MGB GTS (Ryan's car, prepped with Ian's help at Euro Speedworks); Miles driving red bomber Miata with Larry as co-driver. Event status: ❓ Questionable — verify before committing.
- **Lake Garnett Grand Prix Revival date:** ✅ 2026-04-07 — Oct 9–11, 2026 confirmed (8 track sessions). Updated in `events/schedules.md`.
- **KCRX E3 May 25:** Not yet on family calendar — add when confirmed.
- **Dragstrip for Nessie:** ✅ 2026-04-04 — Primary target set to Thunder Valley Friday Night Test & Tune on Friday, May 15, 2026. Fallback is Mo-Kan Fun Drags on Friday, May 29, 2026. Tech requirements captured in `cars/ian/cressida-nessie/Setup-Notes.md`.
- **FIT OFF timing:** "Mid-season" is noted but no specific date or format details are defined.

---

## Content

- **Q2 Fit How-To topics:** April and May How-To topics not yet identified and queued.
- **Season opener Church of Combustion:** No script or planning has started. Which event will it cover?
- **Kids racing documentary approach:** How will this be framed? Which event is the "debut" episode? What's the narrative?
- **Ryan's AE86 V8 filming:** When is the swap progressing to a filmable stage? Coordination needed.
- **Geoffrey origin story video:** New acquisition could be an episode — has this been decided?
- **2001 Car Gambler 500 video arc:** Ryan is slowly building the car for a Gambler event. Ian needs to start developing video ideas — what's the format, the narrative, the story arc? The potential here is significant.

---

## Business

- **Website deployment:** Website built (Astro 5 + Tailwind) but not yet deployed. Pending: YouTube API key + Channel ID, Instagram API token, GitHub push, Vercel/Netlify setup, domain DNS config. Comprehensive deployment guide in `/oio-racing/` README.
- **Merch platform:** Printful/Printify, Fourthwall, or local print run? Decision not made.
- **First merch designs:** Which 3–5 designs will launch with? Not decided.
- **Sponsorship targets:** Beyond the categories in the pitch doc, which specific companies are being contacted first?
- **OIO legal/business structure:** Is OIO operating as a sole proprietor, LLC, or other? Relevant for contracts and taxes. Not documented.

---

## Team / People

- **Parker's permit status:** When does he turn 14 and become eligible to race? Confirmed he needs it before he competes.
- **Hudson's adult ride-along requirement:** Which events require this and which don't? Rules clarification needed.
- **Doug's Spring Nationals prep:** Is OIO filming Doug's Spring Nationals run? If so, coordination needed.

---

## Repo / Operations

- ~~**Repo structure proposal awaiting review:**~~ ✅ **RESOLVED 2026-05-30** — Full restructuring implemented. See `core/decisions-log.md` for details.
- **Who else has access to this repo?** Beyond Ian, who can read and write?
- **Update cadence:** How often should `active/` files be reviewed and updated? Weekly? After each event?
- **process-dailies false-positive trigger:** The `process-dailies` workflow triggers on any push to `intake/dailies/` — including the permanent `intake/dailies/README.md`. When that README was pushed as infrastructure, the automation opened a processing issue. The workflow should be scoped to ignore README.md files in the dailies folder to prevent future false-positives.
- **2025 autocross results missing:** The `oio_results.json` file did not include 2025 KCRSCCA autocross data. No 2025 AX results are in the brain. Confirm whether Ian, Ryan, or others competed in 2025 AX and source that data.
- **KSRX BDR 2025 — Ian's car listed as "1985 Toyota Celica":** Source data shows Ian racing a "1985 Toyota Celica" in the O4 class at the December 2025 BDR event. Ian's known Celica is Dale (1972, HCS). This may be a source data error, or Ian drove a different car at this event. Needs confirmation. See `events/results/2025-Season-Results.md`.
- **GOOGLE_PHOTOS_CREDENTIALS scope issue — action required:** The `process-photos` workflow fails with a 403 Forbidden error because the OAuth refresh_token in `GOOGLE_PHOTOS_CREDENTIALS` was generated without the `photoslibrary.readonly` scope. The secret IS present but the scope is wrong. Fix: run `python dev/scripts/auth_google_photos.py` locally (requires `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` env vars), complete the browser OAuth consent flow, copy the output JSON, and update the `GOOGLE_PHOTOS_CREDENTIALS` GitHub repository secret. See [workflow run](https://github.com/spacecowboyian/oio-brain/actions/runs/24018183898/job/70041588984).

---

## Resolved Loops

<!-- Move resolved items here with ✅ [YYYY-MM-DD] — resolution note -->

✅ 2026-03-31 — Website platform decided and built. Astro 5 + Tailwind CSS 4 chosen. Website completed and ready for deployment (Paperclip OUT-123). Deployment pending: API credentials and GitHub/Vercel setup.
✅ 2026-03-30 — Brand voice document completed. OIO Racing Brand Voice Document finalized, defining tone, messaging, and content pillars (Paperclip OUT-19).
✅ 2026-03-27 — Fitty Cent nickname confirmed ("Fitty Cent" not "Fittty Scent"). Corrected throughout repo.
