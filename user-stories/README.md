---
title: User Stories — Agent Work Queue
type: reference
status: active
owner: Ian Jennings
updated: 2026-04-05
tags: [agents, workflow, user-stories, backlog]
source_of_truth: true
summary: This folder is the primary work queue for AI agents. New work items are filed here as user stories. Agents should check backlog/ before taking action in any other repo context.
---

# User Stories — Agent Work Queue

This is where new work is defined and picked up. Every user story here represents a scoped, actionable unit of work for an AI agent to execute.

---

## How Agents Should Use This Folder

1. **Check `backlog/` first.** Before doing any work in this repo, scan this folder for user stories with `status: ready`.
2. **Pick up a story.** Read the full file — including acceptance criteria, technical notes, and out-of-scope boundaries — before starting.
3. **Execute against the acceptance criteria.** Every AC item should be satisfied before the story is considered done.
4. **Update the story status.** When work is complete, update frontmatter `status` to `done` and add `completed: YYYY-MM-DD`. Do not delete the file.
5. **Log the decision.** Add a brief entry to `core/decisions-log.md` noting what was done.

---

## Folder Structure

| Folder | Contents |
|---|---|
| `backlog/` | Stories ready to be picked up (`status: ready`) or under review (`status: draft`) |
| `done/` | Completed stories — archived for reference |

---

## Status Values

| Status | Meaning |
|---|---|
| `draft` | Story written but not yet reviewed — do not pick up |
| `ready` | Approved and ready for an agent to execute |
| `in-progress` | An agent is actively working on this story |
| `done` | Work is complete and verified |
| `blocked` | Cannot proceed — reason is documented in the story |

---

## Story File Naming

`US-{zero-padded-number}-{kebab-case-title}.md`

Example: `US-001-photo-pipeline-rebuild.md`

Increment the number for each new story. Do not reuse numbers.
