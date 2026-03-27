# Copilot Instructions — OIO Brain

This repository is the **canonical operational brain for OIO (Outside Inside Outside Racing)**. Every AI agent working in this repo must read and follow these instructions before making any changes.

---

## What This Repo Is

This is not a project scaffold or a general knowledge base. It is the living, writable memory for a real grassroots motorsports brand and YouTube channel run by Ian Jennings out of Kansas City, MO. It covers racing operations, vehicle builds, content production, business, and team management.

The repo must remain useful to both **humans** and **AI agents** over time. Agents read it to understand context. Agents write to it to update state. Humans read it to operate the brand. Humans write to it when things change.

---

## Core Behavioral Rules

### Do
- **Read `01-active/` first.** These files hold the current state. Start there before reading anything else.
- **Update existing files instead of creating new ones** when the content logically belongs in an existing document.
- **Promote learnings properly.** Capture notes belong in `01-active/` or a dated working file. Durable facts belong in canonical docs in `OIO Brain/`.
- **Mark uncertainty with `TODO:` or `[unknown]` placeholders.** Never invent facts.
- **Add frontmatter** to any new file you create. See `00-core/repo-standards.md` for the required format.
- **Log significant decisions** in `00-core/decisions-log.md` with date and rationale.
- **Keep `01-active/` files concise and current.** These are the memory layer — they decay if they grow too long.
- **Archive, don't delete.** Mark outdated content as archived rather than removing it.

### Do Not
- Do not create near-duplicate files. If something similar exists, update it.
- Do not invent facts, stats, or details that are not confirmed. Use `TODO:` instead.
- Do not overwrite human-written content just to standardize tone.
- Do not let `01-active/` files grow stale — update them whenever the state changes.
- Do not treat capture notes or working docs as source of truth.
- Do not create files without frontmatter in folders that require it (all of `OIO Brain/`, `00-core/`, `01-active/`).
- Do not remove standing rules or canonical decisions without logging the change.

---

## Document Classes

Every document in this repo belongs to one of four classes. The class determines how it should be read, written, and treated.

### Canonical / Source of Truth
- **Definition:** Authoritative, durable reference. This is the official answer.
- **Marked by:** `source_of_truth: true` in frontmatter, `status: active` or `status: reference`
- **Examples:** Brand Guide, Team Bios, Voice and Tone, Car Overviews, Operating System, Policies
- **Agent behavior:** Read with high confidence. Update only when reality changes. Never silently overwrite — log the change if it's significant.

### Working
- **Definition:** Active, in-progress document. Accurate for now but expected to evolve.
- **Marked by:** `status: draft` or `status: active` without `source_of_truth: true`
- **Examples:** Video Ideas Backlog, Budget, Schedules, Sponsorship Leads, current-state.md
- **Agent behavior:** Read and update freely. These are meant to change. Flag stale entries rather than silently removing them.

### Capture
- **Definition:** Raw notes, quick logs, unprocessed information. Not yet validated or organized.
- **Marked by:** No frontmatter, or `type: notes`, or lives in a `capture/` or `notes/` path
- **Examples:** Quick notes typed during an event, rough ideas, unverified info
- **Agent behavior:** Treat with caution. Do not promote capture content to canonical docs without review. When promoting, clean up and validate first.

### Archive
- **Definition:** Outdated content that should not be treated as current. Preserved for reference only.
- **Marked by:** `status: archived` in frontmatter, or lives in an `archive/` subfolder
- **Examples:** Prior season priorities, outdated setup notes, old video logs
- **Agent behavior:** Do not treat as current. Do not update. Reference only if explicitly relevant.

---

## The Memory Layer

The files in `01-active/` are the short-term memory of this repo. They must be kept current.

| File | Purpose |
|---|---|
| `01-active/current-state.md` | What is happening right now |
| `01-active/active-priorities.md` | What matters most and why |
| `01-active/open-loops.md` | Unresolved questions, pending decisions, waiting-ons |
| `01-active/next-actions.md` | Concrete next steps, grouped by area |
| `00-core/decisions-log.md` | Log of significant decisions with rationale |

When you complete work, update the relevant `01-active/` file. Do not let the memory layer go stale.

---

## Frontmatter Requirements

All documents in `OIO Brain/`, `00-core/`, and `01-active/` must include a frontmatter block at the top:

```yaml
---
title: Human-readable title
type: core | state | sop | checklist | vehicle | content | event | finance | reference | notes | archive
status: active | draft | reference | archived
owner: Ian Jennings
updated: YYYY-MM-DD
tags: [tag1, tag2]
source_of_truth: true | false
summary: 1–3 sentences describing what this file contains and when to use it.
---
```

---

## Repo Navigation

- **`00-core/`** — Governance, standards, decisions log, templates
- **`01-active/`** — Live memory layer. Read this first.
- **`OIO Brain/`** — Canonical knowledge organized by domain
- **`INDEX.md`** — Root-level navigation table
- **`README.md`** — Human-facing entry point
- **`OIO-Master-Brief.md`** — Original source document (do not overwrite)
