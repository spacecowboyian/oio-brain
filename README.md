# OIO Brain

The canonical operational brain for **Outside Inside Outside Racing (OIO)** — Ian Jennings' grassroots motorsports brand and YouTube channel out of Kansas City, MO.

---

## If you are an AI agent

Start with [`skill.md`](skill.md) — it explains how to use this brain. Then read [`active/current-state.md`](active/current-state.md) and [`active/next-actions.md`](active/next-actions.md). Full standing instructions in [`.github/copilot-instructions.md`](.github/copilot-instructions.md).

- Use the dedicated `paperclip` worktree based on `main` for repo edits.
- Leave the default repo worktree alone unless explicitly told otherwise.

## If you are a human

Start at [`core/README.md`](core/README.md) or [`INDEX.md`](INDEX.md) for navigation.

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

## Execution Reality (Planning Guardrail)

OIO execution is heavily DIY and bottlenecked by Ian's available hours.

- Assume only one major hands-on execution track can move at full speed at once.
- Treat additional parallel work as staggered, delegated, or lower confidence until named owner/time exists.
- Default planning to conservative throughput so recommendations stay runnable in real life.

---

## Repo Structure

```
/
├── README.md              ← Start here
├── INDEX.md               ← Full section navigation
├── skill.md               ← Agent onboarding guide (start here if you're an AI)
├── .github/
│   └── copilot-instructions.md   ← AI agent standing instructions
├── core/                  ← Governance, standards, templates, decisions log
├── active/                ← Live memory layer
├── brand/                 ← Mission, voice, audience, team bios
├── content/               ← Video pipeline, ideas, schedules, published log
├── cars/                  ← All vehicles by driver/car-slug
├── events/                ← Autocross, rallycross, schedules, results
├── production/            ← Camera/audio workflow, editing SOPs, shot lists
├── business/              ← Budget, sponsors, merch, website
├── ops/                   ← Contacts, accounts, policies, operating system
├── data/                  ← JSON data: social posts, racing results
├── transcripts/           ← YouTube video transcripts
├── photos/                ← Photo library by driver
├── intake/
│   ├── docs/              ← Drop documents here for processing
│   ├── photos/            ← Drop photos here for filing
│   └── dailies/           ← Drop raw daily transcripts here
└── docs/                  ← Technical pipeline documentation
```
