---
title: OIO Brain — Entry Point
type: core
status: active
owner: Ian Jennings
updated: 2026-03-28
tags: [navigation, overview, onboarding]
source_of_truth: true
summary: Starting point for any human or AI agent entering this repo. Explains what OIO is, what this repo is for, where the memory layer lives, and how to navigate quickly.
---

# OIO Brain — Start Here

This repository is the canonical operational brain for **Outside Inside Outside Racing (OIO)** — Ian Jennings' grassroots motorsports brand and YouTube channel based in Kansas City, MO.

If you are an AI agent: read `active/current-state.md` first, then come back here.

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

The `active/` folder holds the short-term memory of OIO. Start here for current context:

| File | What It Answers |
|---|---|
| [`active/current-state.md`](../active/current-state.md) | What is happening right now |
| [`active/priorities.md`](../active/priorities.md) | What matters most and why |
| [`active/open-loops.md`](../active/open-loops.md) | Unresolved questions and pending decisions |
| [`active/next-actions.md`](../active/next-actions.md) | Concrete next steps by area |
| [`core/decisions-log.md`](decisions-log.md) | Log of significant decisions with rationale |

---

## Most Important Files

| File | Why It Matters |
|---|---|
| [`brand/voice-and-tone.md`](../brand/voice-and-tone.md) | Voice, tone, Church of Combustion, message pillars |
| [`ops/operating-system.md`](../ops/operating-system.md) | Content schedule, standing rules, workflows |
| [`brand/team-bios.md`](../brand/team-bios.md) | Full team roster, cars, 2026 arcs |
| [`brand/voice-and-tone.md`](../brand/voice-and-tone.md) | How OIO writes and sounds |
| [`content/video-backlog.md`](../content/video-backlog.md) | All video ideas by content bucket |
| [`cars/`](../cars/) | Every vehicle — overview, setup, maintenance |

---

## How to Navigate

```
/
├── README.md                     ← You are here
├── INDEX.md                      ← Full section navigation
├── OIO-Master-Brief.md           ← Original source brief (read-only reference)
├── core/                         ← Governance, standards, templates, decisions log
│   ├── README.md                 ← This file
│   ├── repo-standards.md         ← How this repo works
│   ├── decisions-log.md          ← Decision history
│   └── templates/                ← Reusable document templates
├── active/                       ← LIVE MEMORY LAYER — update frequently
│   ├── current-state.md
│   ├── active-priorities.md
│   ├── open-loops.md
│   └── next-actions.md
└── brand/, cars/, content/, etc. ← Canonical knowledge by domain
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
| **Canonical** | domain folders (`brand/`, `cars/`, etc.) — marked `source_of_truth: true` | High — official answer |
| **Working** | `active/` or a domain folder — `status: active` | Medium — accurate now, expect change |
| **Capture** | Anywhere without frontmatter, or `type: notes` | Low — unvalidated, do not promote without review |
| **Archive** | `status: archived` or in `archive/` subfolder | Reference only — not current |

See `core/repo-standards.md` for full rules.