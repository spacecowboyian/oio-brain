---
title: OIO Brain — Entry Point
type: core
status: active
owner: Ian Jennings
updated: 2026-03-27
tags: [navigation, overview, onboarding]
source_of_truth: true
summary: Starting point for any human or AI agent entering this repo. Explains what OIO is, what this repo is for, where the memory layer lives, and how to navigate quickly.
---

# OIO Brain — Start Here

This repository is the canonical operational brain for **Outside Inside Outside Racing (OIO)** — Ian Jennings' grassroots motorsports brand and YouTube channel based in Kansas City, MO.

If you are an AI agent: read `01-active/current-state.md` first, then come back here.

If you are a human: the most important files are listed below.

---

## What OIO Is

OIO is a grassroots motorsports brand built around autocross, rallycross, car builds, race prep, and YouTube content — aimed at making motorsports feel accessible to regular people.

- **Channel:** @oioracing | ~1.93K subscribers | 358 videos
- **Brand voice:** Lonely Island meets Vice Grip Garage — absurdist comedy meets folksy Midwest "will it run" drama
- **The church bit:** OIO also operates as a Southern Baptist-style Church of Combustion. Call
it an alter ego of the team. Ian is The Reverend. Racing events are Sunday services.
- **Sign-off:** *"Until next time, remember to go out and find your own apex, because it's better late than never."*

---

## What This Repo Is For

This is the operating brain for all of OIO — racing operations, vehicle builds, content production, business, team, and strategy. It is designed to be:

- **Read** by AI agents to understand current state and context
- **Written** by AI agents to update state, log decisions, capture information
- **Used** by Ian and the OIO team to operate and plan

---

## Where the Memory Layer Lives

The `01-active/` folder holds the short-term memory of OIO. Start here for current context:

| File | What It Answers |
|---|---|
| [`01-active/current-state.md`](01-active/current-state.md) | What is happening right now |
| [`01-active/active-priorities.md`](01-active/active-priorities.md) | What matters most and why |
| [`01-active/open-loops.md`](01-active/open-loops.md) | Unresolved questions and pending decisions |
| [`01-active/next-actions.md`](01-active/next-actions.md) | Concrete next steps by area |
| [`00-core/decisions-log.md`](00-core/decisions-log.md) | Log of significant decisions with rationale |

---

## Most Important Files

| File | Why It Matters |
|---|---|
| [`OIO Brain/00 - Start Here/OIO-Brand-Guide.md`](OIO%20Brain/00%20-%20Start%20Here/OIO-Brand-Guide.md) | Voice, tone, Church of Combustion, message pillars |
| [`OIO Brain/00 - Start Here/OIO-Operating-System.md`](OIO%20Brain/00%20-%20Start%20Here/OIO-Operating-System.md) | Content schedule, standing rules, workflows |
| [`OIO Brain/01 - Brand/Team-Bios.md`](OIO%20Brain/01%20-%20Brand/Team-Bios.md) | Full team roster, cars, 2026 arcs |
| [`OIO Brain/01 - Brand/Voice-and-Tone.md`](OIO%20Brain/01%20-%20Brand/Voice-and-Tone.md) | How OIO writes and sounds |
| [`OIO Brain/02 - Content/Video-Ideas-Backlog.md`](OIO%20Brain/02%20-%20Content/Video-Ideas-Backlog.md) | All video ideas by content bucket |
| [`OIO Brain/03 - Cars/`](OIO%20Brain/03%20-%20Cars/) | Every vehicle — overview, setup, maintenance |

---

## How to Navigate

```
/
├── README.md                     ← You are here
├── INDEX.md                      ← Full section navigation
├── OIO-Master-Brief.md           ← Original source brief (read-only reference)
├── 00-core/                      ← Governance, standards, templates, decisions log
│   ├── README.md                 ← This file
│   ├── repo-standards.md         ← How this repo works
│   ├── decisions-log.md          ← Decision history
│   └── templates/                ← Reusable document templates
├── 01-active/                    ← LIVE MEMORY LAYER — update frequently
│   ├── current-state.md
│   ├── active-priorities.md
│   ├── open-loops.md
│   └── next-actions.md
└── OIO Brain/                    ← Canonical knowledge by domain
    ├── 00 - Start Here/          ← Brand identity, operating system
    ├── 01 - Brand/               ← Mission, audience, voice, team
    ├── 02 - Content/             ← Video pipeline, ideas, published log
    ├── 03 - Cars/                ← All vehicles
    ├── 04 - Events/              ← Schedules, results, event notes
    ├── 05 - Production/          ← Workflows, SOPs, assets
    ├── 06 - Business/            ← Budget, sponsors, merch, website
    └── 07 - Admin/               ← Contacts, accounts, policies, templates
```

---

## Source of Truth vs Working vs Notes

| Type | Where It Lives | Trust Level |
|---|---|---|
| **Canonical** | `OIO Brain/` — marked `source_of_truth: true` | High — official answer |
| **Working** | `01-active/` or `OIO Brain/` — `status: active` | Medium — accurate now, expect change |
| **Capture** | Anywhere without frontmatter, or `type: notes` | Low — unvalidated, do not promote without review |
| **Archive** | `status: archived` or in `archive/` subfolder | Reference only — not current |

See `00-core/repo-standards.md` for full rules.
