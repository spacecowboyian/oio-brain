# OIO Brain

The canonical operational brain for **Outside Inside Outside Racing (OIO)** — Ian Jennings' grassroots motorsports brand and YouTube channel out of Kansas City, MO.

---

## If you are an AI agent

Start with [`skill.md`](skill.md) — it explains how to use this brain. Then read [`active/current-state.md`](active/current-state.md) and [`active/next-actions.md`](active/next-actions.md). Full standing instructions in [`.github/copilot-instructions.md`](.github/copilot-instructions.md).

## If you are a human

Start at [`INDEX.md`](INDEX.md) for full navigation, or [`core/README.md`](core/README.md) for repo standards.

---

## What Is OIO

OIO makes grassroots motorsports feel accessible to regular people — autocross, rallycross, car builds, race prep, and YouTube content. The brand runs as "The Church of Combustion," with Ian as The Reverend, racing events as Sunday services, and the congregation as the audience.

- **Channel:** @oioracing | ~1.93K subscribers | 358 videos
- **Location:** Kansas City, MO

---

## Memory Layer (Read These First)

| File | What It Contains |
|---|---|
| [`active/current-state.md`](active/current-state.md) | What is happening right now |
| [`active/priorities.md`](active/priorities.md) | What matters most and why |
| [`active/open-loops.md`](active/open-loops.md) | Pending decisions and unknowns |
| [`active/next-actions.md`](active/next-actions.md) | Concrete next steps |
| [`core/decisions-log.md`](core/decisions-log.md) | Decision history |

---

## Repo Structure

```
/
├── README.md              ← Start here
├── INDEX.md               ← Full section navigation
├── skill.md               ← Agent onboarding guide (start here if you're an AI)
├── OIO-Master-Brief.md    ← Original source brief (archived reference — do not overwrite)
├── .github/
│   └── copilot-instructions.md   ← AI agent standing instructions
├── active/                ← Live memory layer (current state, priorities, loops, actions)
├── brand/                 ← Voice, tone, mission, audience, team bios
├── business/              ← Budget, expenses, sponsorships, merch, website
├── cars/                  ← Every build by driver (ian/, ryan/, keegan/, karen/, richard/)
├── content/               ← Video ideas, schedule, published log, summaries
├── core/                  ← Governance, standards, templates, decisions log
├── data/                  ← JSON data files (social posts, video catalog, race results)
├── docs/                  ← Technical pipeline documentation
├── events/                ← Rallycross, autocross, schedules, results
├── intake/                ← Drop docs/photos/dailies here for processing
├── ops/                   ← Contacts, accounts, policies, operating system
├── photos/                ← Filed photo library by driver
├── production/            ← Shot lists, camera/audio workflow, editing SOPs
└── transcripts/           ← YouTube transcript archives and video scripts
```
