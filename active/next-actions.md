---
title: OIO Next Actions
type: state
status: active
owner: Ian Jennings
updated: 2026-04-01
tags: [actions, tasks, next-steps]
source_of_truth: false
summary: Concrete next actions organized by area. Short and actionable only — not a project plan. Update after completing actions and when new ones are identified.
---

# Next Actions

*As of April 1, 2026 — keep this list short and current. Done items get removed, not accumulated.*

---

## Racing

- [x] Diagnose Goblin motor — ✅ 2026-03-28 diagnostic complete (see Maintenance-Log.md)
- [ ] **Goblin: decide rebuild vs. replace** — diagnostic confirms bearing failure + cyl 4 at 35 PSI. Is the 4AG worth rebuilding or does it need a replacement?
- [ ] Get a parts cost estimate for Goblin rebuild (or source a replacement 4AG if rebuild not viable)
- [ ] Confirm 2026 rallycross event schedule — which events, which dates
- [ ] Confirm 2026 autocross event schedule
- [ ] Confirm Lake Garnett Grand Prix Revival date for October
- [ ] Assess Dale's current mechanical condition before first 2026 event
- [ ] Identify which track Nessie will make her dragstrip debut at, and get tech requirements

---

## Vehicles

- [ ] Fully document Goblin rebuild — film every step for content
- [ ] Identify and document the $100 mystery motor for Killer Corolla
- [ ] Assess Geoffrey (Dauphine) — running or not, what's the condition
- [ ] Complete TRD parts inventory on Killer Corolla
- [ ] Define Geoffrey build direction — what kind of rally replica and to what spec

---

## Content

- [ ] **IMMEDIATE: Film and publish Fit How-To for Apr 2** — Home Alignment / Gyraline. Overdue by 4+ weeks. This is job one.
- [ ] **IMMEDIATE: Edit KCRX E1 footage (Mar 22 RayRocks)** — Season premiere COC due Apr 20
- [ ] Plan and film Apr 10 Vlog — season reboot, what happened in March, kids autocross prep
- [ ] Film Kids' First Autocross (Apr 12) for Apr 24 vlog
- [ ] Line up May Fit How-To topic: Kids prep the GE8
- [ ] Capture shorts at every event and garage session — minimum 2–3 per month
- [ ] See full schedule: `content/schedule.md`

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

- [ ] **Add 3 GitHub repo secrets for social media indexing:** `META_ACCESS_TOKEN`, `META_FACEBOOK_PAGE_ID`, `META_INSTAGRAM_ACCOUNT_ID` — see `data/social-posts/README.md` for step-by-step setup (requires Meta Developer account + connecting Instagram Business account to Facebook Page)
- [ ] Fill in confirmed 2026 event dates in `events/schedules.md`
- [ ] Add specific 2026 Fit How-To topics to the Video Ideas Backlog as they're confirmed
- [ ] Fill in real data in Budget.md once racing costs are known
- [ ] Add contact info to `ops/contacts.md` for key people
- [ ] Upload more car photos to `intake/photos/` — agent will auto-file and index them
- [ ] Add social media post history to `photos/README.md` as photos get posted
