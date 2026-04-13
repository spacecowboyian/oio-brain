---
title: OIO Brain — Repo Standards
type: core
status: active
owner: Ian Jennings
updated: 2026-04-05
tags: [standards, governance, repo, agents]
source_of_truth: true
summary: The operational manual for this repository. Defines purpose, folder roles, document classes, frontmatter requirements, naming conventions, and how to decide whether to update an existing file or create a new one.
---

# OIO Brain — Repo Standards

This document is the operational manual for the OIO Brain repository. Read it before making structural changes or adding new files.

---

## Repo Purpose

This repository is the canonical operating brain for OIO Racing. It is designed to be read and written by both humans and AI agents over time. Its job is to hold durable knowledge, track current state, and support decision-making — not to be a pile of notes.

**Primary users:**
- Ian Jennings (owner, operator)
- AI agents acting on Ian's behalf
- OIO team members (Ryan, Richard, Keegan, the kids)

---

## Folder Roles

| Folder | Role | Mutability |
|---|---|---|
| `core/` | Governance, standards, decisions log, shared templates | Low — change deliberately |
| `active/` | Live memory layer — current state, priorities, loops, actions | High — update constantly |
| `00 - Start Here/` | Brand identity, operating system, standing rules | Low — stable reference |
| `brand/` | Mission, audience, voice, team | Low — update when reality changes |
| `content/` | Video pipeline, ideas, published log | Medium — ideas grow, log is append-only |
| `cars/` | All vehicles — overview, setup, maintenance | Medium — evolves with builds |
| `events/` | Schedules, results, event notes | Medium to High — append each season |
| `production/` | SOPs, workflows, camera, assets | Low — update when process changes |
| `business/` | Budget, sponsors, merch, website | Medium — active during season |
| `ops/` | Contacts, accounts, policies, templates | Low to Medium |
| `.github/` | AI agent instructions | Low — change only when governance changes |

---

## Document Classes

### Canonical / Source of Truth
Authoritative, durable reference documents. The official answer for their topic.

- Marked: `source_of_truth: true`
- Lives in: `` (primary), `core/`
- Examples: Brand Guide, Team Bios, Voice and Tone, Car Overviews, Operating System, Policies
- **Rules:** Update when reality changes. Log significant changes in `decisions-log.md`. Never silently overwrite without reason.

### Working
Active, in-progress documents. Accurate now but expected to evolve.

- Marked: `status: active` or `status: draft`, without `source_of_truth: true`
- Lives in: `active/`, or `` for longer-lived working docs
- Examples: Video Ideas Backlog, Budget, Schedules, current-state.md, Sponsorship Leads
- **Rules:** Update freely. Flag stale entries. Do not treat as permanent reference.

### Capture
Raw notes, quick logs, unprocessed information. Not yet validated.

- Marked: `type: notes`, no frontmatter, or lives in a `notes/` subfolder
- **Rules:** Treat with caution. Promote to canonical or working only after validation. Do not cite capture notes as facts.

### Archive
Outdated content preserved for reference. Not current.

- Marked: `status: archived` or lives in `archive/` subfolder
- **Rules:** Do not update. Do not treat as current. Reference only if explicitly needed.

---

## Frontmatter Requirements

All documents in ``, `core/`, and `active/` must include this frontmatter block:

```yaml
---
title: Human-readable title
type: core | state | sop | checklist | vehicle | content | event | finance | reference | notes | archive
status: active | draft | reference | archived
owner: Ian Jennings
updated: YYYY-MM-DD
tags: [tag1, tag2, tag3]
source_of_truth: true | false
summary: 1–3 sentences. What this file contains and when it should be used.
---
```

**Type values:**
| Value | Use for |
|---|---|
| `core` | Brand identity, standards, governance |
| `state` | Live state files (current-state, priorities) |
| `sop` | Standing operating procedures |
| `checklist` | Action checklists |
| `vehicle` | Car overviews and status |
| `content` | Video pipeline, ideas, scripts |
| `event` | Event notes, results, schedules |
| `finance` | Budget, expenses, sponsorships |
| `reference` | Stable reference material |
| `notes` | Capture and raw notes |
| `archive` | Archived content |

---

## Quick-Read Expectations

Every important document should be readable in under 2 minutes for the key facts. Achieve this by:

1. Frontmatter summary tells you what the file is and when to use it
2. First section after the heading answers the most important question
3. Tables for structured data (not prose)
4. Status fields on things that have states

---

## File Naming Conventions

- Use kebab-case for all filenames: `video-ideas-backlog.md`
- Dates in filenames use `YYYY-MM-DD`: `2026-04-12-lake-garnett-recap.md`
- Car folders use: `[Make-Model] - [Nickname]/`
- Event notes: `YYYY-MM-DD-[EventName].md`
- Scripts: `YYYY-MM-[Format]-[Short-Title].md`

---

## Promotion Path: Capture → Durable Memory

```
Raw capture note
       ↓
Validate: is this fact confirmed?
       ↓ yes
Working document (in `active/` or working section of relevant domain folder)
       ↓
Has it stabilized? Is it durable?
       ↓ yes
Canonical document in  with frontmatter
       ↓
If it's a significant decision: log in core/decisions-log.md
```

When in doubt, use a `TODO:` placeholder and note the gap rather than inventing content.

---

## Archive Behavior

When content becomes outdated:

1. **Within a file:** Add `> ⚠️ Archived [YYYY-MM-DD] — [reason]` above the section and mark it clearly.
2. **For a whole file:** Change frontmatter to `status: archived` and move to an `archive/` subfolder if appropriate.
3. **Never delete** content that might be historically relevant — archive it instead.

---

## Update vs Create Decision

**Update an existing file when:**
- The new content logically belongs to the same topic as an existing file
- You are correcting, clarifying, or extending existing information
- The existing file is the source of truth for this type of content

**Create a new file when:**
- This is a genuinely new document type (e.g., a new event's recap)
- The existing file has a clearly different scope
- You are starting a new dated entry (event notes, decisions log entries)

**Never create:**
- A near-duplicate of an existing file with slightly different content
- A file without frontmatter (in governed folders)
- A file that makes an existing source-of-truth doc ambiguous

---

## Standing Rules (Never Break)

These apply to any agent or human making changes to this repo:

1. Do not invent facts. Use `TODO:` or `[unknown]` instead.
2. Do not create near-duplicate files.
3. Do not delete content — archive it.
4. Do not treat capture notes as source of truth.
5. Do not skip frontmatter on new files.
6. Do not let `active/` files grow stale — they are the memory layer.
7. Log significant decisions in `core/decisions-log.md`.
8. For planning guidance, assume DIY capacity constraints by default: Ian is the primary hands-on execution bottleneck unless explicit additional owners/time are documented.
