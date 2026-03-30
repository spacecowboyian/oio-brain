---
title: Google Calendar Integration Setup
type: reference
status: active
owner: Ian Jennings
updated: 2026-03-30
tags: [admin, google-calendar, integration, setup]
source_of_truth: true
summary: Step-by-step setup guide for adding Google Calendar access to the OIO Brain agent system. Covers service account creation, secret configuration, and calendar IDs.
---

# Google Calendar Integration Setup

> This guide explains what you need to set up so that AI agents can read and update your Google Calendars — specifically the **video release calendar** and **car work / garage schedule**.

---

## What You'll Need

Three GitHub repository secrets:

| Secret Name | What It Is |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | The full JSON key for a Google Cloud service account |
| `GOOGLE_CALENDAR_VIDEO_RELEASE_ID` | The Calendar ID for the video release schedule |
| `GOOGLE_CALENDAR_CAR_WORK_ID` | The Calendar ID for car work / garage sessions |

---

## Step 1: Create a Google Cloud Project + Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one) — name it something like `oio-brain`
3. Enable the **Google Calendar API**:
   - In the left nav, go to **APIs & Services → Library**
   - Search for "Google Calendar API" and click **Enable**
4. Create a Service Account:
   - Go to **APIs & Services → Credentials**
   - Click **Create Credentials → Service Account**
   - Name it something like `oio-brain-agent`
   - Skip optional role assignment (click Continue → Done)
5. Generate a JSON key:
   - Click on the service account you just created
   - Go to the **Keys** tab → **Add Key → Create New Key → JSON**
   - Save the downloaded `.json` file — this is your `GOOGLE_SERVICE_ACCOUNT_JSON` value

---

## Step 2: Share Your Calendars with the Service Account

The service account has its own email address (looks like `oio-brain-agent@your-project-id.iam.gserviceaccount.com`). You need to share each calendar with it.

1. Open **Google Calendar** → find the calendar you want to share
2. Click the three dots next to the calendar → **Settings and sharing**
3. Under **Share with specific people**, add the service account email
4. Set the permission to **Make changes to events** (so the agent can both read and write)
5. Repeat for both calendars (video release + car work)

---

## Step 3: Get Calendar IDs

For each calendar:
1. In Google Calendar, click the three dots → **Settings and sharing**
2. Scroll down to **Integrate calendar**
3. Copy the **Calendar ID** (looks like `c_abc123...@group.calendar.google.com` or just your Gmail address for the primary calendar)

---

## Step 4: Add Secrets to GitHub

Go to your GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**

Add these three secrets:

| Secret Name | Value |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Paste the entire contents of the downloaded JSON key file |
| `GOOGLE_CALENDAR_VIDEO_RELEASE_ID` | The Calendar ID from Step 3 for video releases |
| `GOOGLE_CALENDAR_CAR_WORK_ID` | The Calendar ID from Step 3 for car work sessions |

---

## Step 5: Let the Agent Know

Once secrets are added, tell the agent:

> "Google Calendar secrets are set up. Add the calendar tool."

The agent will then create:
- `scripts/google_calendar.py` — a reusable helper for reading/writing calendar events
- A GitHub Actions workflow that exposes calendar read/write to agent tasks

---

## What the Agent Will Be Able to Do

Once set up:
- **Read** the video release calendar to check upcoming publish dates
- **Add or update** video release events when content is scheduled
- **Read** the car work calendar to see what garage sessions are planned
- **Add** maintenance events (like the Tundra oil change on 4/3/26) directly to the calendar
- **Cross-reference** calendar data with brain docs for scheduling conflicts and planning

---

## Security Note

- The service account only has access to calendars you explicitly share with it
- The JSON key is stored as a GitHub secret and never exposed in code or logs
- Rotate the key periodically via Google Cloud Console (Keys tab → delete old, create new)
