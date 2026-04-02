---
title: OIO Photo Index
type: reference
status: active
owner: Ian Jennings
updated: 2026-03-28
tags: [photos, index, library, social-media]
source_of_truth: true
summary: Master index of every photo in the OIO photo library. Organized by driver and car. Tracks social media post history per photo. Updated automatically when new photos are processed from picdump.
---

# OIO Photo Index

> Every photo that has ever been filed into the OIO photo library — organized by driver and car, with posting history.
>
> **How to add photos:** Drop image files into the `picdump/` folder and push to main. A GitHub Action will spawn a Copilot agent to identify the car, file the photo in the right folder, update this index, and update the car's description.

---

## Quick Stats

| Driver | Cars | Photos |
|---|---|---|
| Ian | 1985 MR2 (Goblin), 1972 Celica, 1977 Corolla, 1982 Cressida Wagon, 2009 Honda Fit, 2014 Tundra, 1962 Dauphine | 1 |
| Ryan | AE86, MGB GT, 2001 Camry | 0 |
| Keegan | 1981 Tercel, 1982 Honda Prelude, 1985 Tercel 4WD, 1996 Lumina APV, 2003 Tundra, 1979 Lincoln Continental | 0 |
| Richard | ST205 Celica | 0 |
| Karen | 1965 Suburban (Tootie) | 0 |

**Total photos: 1**

---

## Ian Jennings

### 1985 Toyota MR2 AW11 — The Goblin

📁 [photos/Ian/1985-MR2-Goblin/](photos/Ian/1985-MR2-Goblin/)

| # | Filename | Thumbnail | Date | Event | Subject | Posted |
|---|---|---|---|---|---|---|
| 1 | [IMG_8181.png](photos/Ian/1985-MR2-Goblin/IMG_8181.png) | — | Unknown | KCRSCCA Rallycross | Action shot — sliding on dirt, dust rooster tail, marshal in bg, "2MR" door graphics | No |

**Visual ID markers for The Goblin:**
Steel/medium blue AW11 coupe. T-top roof. Pop-up headlights. Black door vents. 4-spoke cross alloys. "2MR" red/white door number. Slatted rear engine cover. Rear spoiler.

---

### 1972 Toyota Celica — Dale's Dragon

📁 [photos/Ian/1972-Celica-Dales-Dragon/](photos/Ian/1972-Celica-Dales-Dragon/)

*No photos yet.*

---

### 1977 Toyota Corolla

📁 [photos/Ian/1977-Corolla/](photos/Ian/1977-Corolla/)

*No photos yet.*

---

### 1982 Toyota Cressida Wagon

📁 [photos/Ian/1982-Cressida-Wagon/](photos/Ian/1982-Cressida-Wagon/)

*No photos yet.*

---

### 2009 Honda Fit — Fitty Cent

📁 [photos/Ian/2009-Honda-Fit/](photos/Ian/2009-Honda-Fit/)

*No photos yet.*

---

### 2014 Toyota Tundra

📁 [photos/Ian/2014-Tundra/](photos/Ian/2014-Tundra/)

*No photos yet.*

---

### 1962 Renault Dauphine

📁 [photos/Ian/1962-Dauphine/](photos/Ian/1962-Dauphine/)

*No photos yet.*

---

## Ryan

📁 [photos/Ryan/](photos/Ryan/)

*No photos yet.*

---

## Keegan

📁 [photos/Keegan/](photos/Keegan/)

*No photos yet.*

---

## Richard

📁 [photos/Richard/](photos/Richard/)

*No photos yet.*

---

## Karen

📁 [photos/Karen/](photos/Karen/)

*No photos yet.*

---

## Social Media Post Tracker

> Track which photos have been used in posts. One photo can be posted multiple times.

| Filename | Platform | Post Date | Caption / Link | Notes |
|---|---|---|---|---|
| — | — | — | — | — |

---

## How This Index Is Maintained

This file is updated automatically by the Copilot agent whenever new photos are processed from `picdump/`. The agent:

1. Identifies the car in each photo using visual AI and cross-references it against known OIO fleet data
2. Moves the photo to the correct `photos/{Driver}/{Car}/` folder
3. Creates or updates the per-car `photo-log.md`
4. Adds the photo to this master index
5. Updates the car's `Overview.md` in `OIO Brain/03 - Cars/` with visual description data
6. Clears the processed image from `picdump/`

To manually update: edit the relevant section above and update the Quick Stats table.
