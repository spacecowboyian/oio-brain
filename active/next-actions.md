---
title: OIO Next Actions
type: state
status: active
owner: Ian Jennings
updated: 2026-04-13
source_of_truth: false
summary: Concrete next actions organized by area. Short and actionable only — not a project plan. Update after completing actions and when new ones are identified.
---

# Next Actions

*As of April 13, 2026 — post-AX E1, 4AG on stand, rallycross Sunday TBD*

---

## 7-Day Cadence

*April 12–19, 2026 — autocross done, rallycross Sunday TBD*

- [x] Apr 12: KCR Autocross E1 — attended, raced, filmed (Parker on camera).
- [ ] Apr 13: Order 4AG parts from Battle Garage. Verify kit against prior research. Place order.
- [ ] Apr 13: Set up table in garage for 4AG teardown.
- [ ] Apr 13–14: Tell Miles to start 4AG teardown/assessment ASAP.
- [ ] **Confirm Sunday Apr 19 KCRX E2 driver status** — Is Ian driving Ryan's MGB? Is Miles driving the Miata? Confirm before committing to drive far south. Or skip.
- [ ] Edit and publish AX E1 vlog (action footage from Parker).
- [ ] Fit clutch How-To video — still pending.
- [ ] COC season premiere edit (Apr 20 target).

## Racing

- [x] Diagnose Goblin motor — ✅ 2026-03-28 diagnostic complete (see Maintenance-Log.md)
- [x] **Goblin: decide rebuild vs. replace** — ✅ 2026-04-08 Decision made: replace. Source 3-rib 4age from Henry for $350 + melted motor trade.
- [x] **Acquire Goblin motor from Henry** — ✅ 2026-04-09 Done. Motor on stand in garage.
- [ ] **Set up workbench/table in garage** — prerequisite for 4AG teardown
- [ ] **Order 4AG parts from Battle Garage** — use prior research kit; order ASAP
- [ ] **Tell Miles to start 4AG teardown** — assess, measure, spec bearings; Ian is support/grunt
- [ ] **Coordinate Euro Speedworks swap weekend** — Arrange with Ryan; Ian helps Ryan on MGB rebuild in exchange for lift access; ~1 day swap with lift
- [ ] **Schedule hot tank at C-TEC** — coordinate with Miles; block + head need to go through the automotive program at North Kansas City High School
- [ ] **Research: 4age oiling system upgrades** — oil pickup, better oil pump, 20-valve pump upgrade; confirm if 20v pump is standard path or if better options exist; cost-effective solutions prioritized
- [ ] **KCRX E2 Sunday Apr 19** — Confirm Ian's MGB ride with Ryan; confirm Miles's Miata ride. If not confirmed before Sunday, consider skipping.
- [ ] **Fergus — talk to Doug about mechanical issues** — one clear, research-backed conversation about brakes, shifter, and engine issues. If dismissed, reassess commitment to national events.
- [x] Film Apr 12 autocross — ✅ Parker filmed. Edit and publish vlog.
- [x] Lake Garnett Grand Prix Revival date — ✅ 2026-04-07 **Oct 9–11, 2026 (8 track sessions) confirmed**
- [ ] Assess Dale's current mechanical condition before first 2026 event (car is currently out for work — motor at Clay County, body at Gary Rod and Chassis; check in around end of May)
- [ ] Book Nessie's first dragstrip outing: Thunder Valley Friday Night Test & Tune on May 15, 2026; keep Mo-Kan Fun Drags on May 29, 2026 as fallback

---

## Vehicles

- [ ] **Source 2 wheels (7.5" wide) + 2 tires (225 ~200 treadwear) for Fitty Cent EST dry setup** — secondhand wheels preferred; sticky compound for front only
- [ ] Fully document Goblin rebuild — film every step for content
- [ ] Identify and document the $100 mystery motor for Killer Corolla
- [ ] Complete TRD parts inventory on Killer Corolla
- [x] Assess Geoffrey (Dauphine) — ✅ 2026-04-05 engine is not running; plugs rusted in place; motor locked by hand crank
- [x] Free Geoffrey's spark plugs — ✅ 2026-04-07 plugs removed after Free All soak; ~895 ccs MMO soaking in cylinders + valve cover
- [ ] Attempt hand crank on Geoffrey with plugs out — if locked, try putting in gear and pushing back and forth to use transmission to help break it loose
- [ ] Define Geoffrey build direction — what kind of rally replica and to what spec

---

## Content

- [ ] **AX E1 vlog** — edit Parker's footage from April 12 (rain, splashing, Hudson 57.4, Fergus chaos). Publish soon while fresh.
- [ ] Fit clutch video (overdue — was Apr 10)
- [ ] COC edit (Apr 20 target)
- [ ] Catch-up vlog before Apr 20
- [ ] **Fitty Cent EST dry tire setup** — document and post when wheels/tires arrive: 225 sticky front + 205 340 rear. Could be short video or social content.

---

## Business

- [x] Research website + merch platforms — ✅ 2026-03-30 CMO research complete (Paperclip OUT-104)
- [x] Confirm domains owned — ✅ outsideinsideoutside.com + oioracing.com confirmed
- [x] Build OIO Racing website — ✅ 2026-03-31 Website built with Astro 5 + Tailwind (Paperclip OUT-123)
- [ ] **Deploy website to production** — Get YouTube API key + Channel ID, Instagram API token, push to GitHub, deploy to Vercel/Netlify, configure domain. See `/oio-racing/` README for deployment steps.
- [ ] **Decide: approve Shopify recommendation** — CMO research shows Shopify dominates (Vice Grip Garage, Hoonigan confirmed). Alternative: Squarespace/Webflow if simpler CMS preferred.
- [ ] **If Shopify approved:** Create Shopify Basic account ($39/mo), configure domains
- [ ] **If Shopify approved:** Choose automotive theme (Motion, Impulse, Streamline recommended)
- [ ] Enable YouTube Merch Shelf — requires 1K+ subs + YouTube Partner Program (current: 1.93K subs ✓, YPP status TBD)
- [ ] Pick first 3–5 merch designs (print-on-demand via Printful = zero inventory risk)
- [ ] Write first 5 targeted sponsorship outreach messages (use CMO media kit strategy)
- [ ] Create sponsor landing page `/sponsors` with media kit (web + PDF versions)
- [ ] Update Sponsorship Leads doc with first round of prospects

---

## Repo / Admin

- [x] **Photo pipeline rebuilt (US-001)** — ✅ 2026-04-06: unified `process_photos.py` + new workflow live
- [ ] **Add GitHub repo secret:** `GOOGLE_PHOTOS_ALBUM_ID` = `AF1QipMW1KCdIEBo2rMA--SpBF2pOt3pf0LkJp5X51DLN21brlvqmYanlJ1_YB11IEKnmA` — needed for new photo pipeline workflow
- [ ] **Remove stale secrets** (no longer needed): `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- [ ] **Add 3 GitHub repo secrets for social media indexing:** `META_ACCESS_TOKEN`, `META_FACEBOOK_PAGE_ID`, `META_INSTAGRAM_ACCOUNT_ID` — see `data/social-posts/README.md` for step-by-step setup
- [x] Fill in confirmed 2026 event dates in `events/schedules.md` — ✅ 2026-04-07 KCR E2/E3/E5 + Lake Garnett confirmed. Remaining: KCR E6 + E8-9 verify.
- [ ] Add specific 2026 Fit How-To topics to the Video Ideas Backlog as they're confirmed
- [ ] Fill in real data in Budget.md once racing costs are known
- [ ] Add contact info to `ops/contacts.md` for key people
- [ ] Upload more car photos to `intake/photos/` — agent will auto-file and index them
- [ ] Add social media post history to `photos/README.md` as photos get posted
