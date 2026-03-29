---
title: Social Media Post Library
type: reference
status: active
owner: Ian Jennings
updated: 2026-03-29
tags: [social, facebook, instagram, content, reference]
source_of_truth: false
summary: Archive of OIO Racing Facebook and Instagram post text. Used as a reference library to inform tone, voice, and content when drafting new posts.
---

# Social Media Post Library

This folder contains an archive of OIO Racing's published Facebook and Instagram posts, stored as individual markdown files. The library is used as a reference when drafting new posts — to inform voice, tone, content themes, and what has already been covered.

---

## Structure

```
social-posts/
  README.md             — this file
  sync-state.json       — pagination cursors for the fetch script (do not edit manually)
  facebook/
    YYYY-MM-DD_slug.md  — one file per Facebook post
  instagram/
    YYYY-MM-DD_slug.md  — one file per Instagram post
```

Each post file contains YAML frontmatter (platform, post_id, date, tags) followed by the raw post text.

---

## How Posts Are Fetched

Posts are fetched by `scripts/fetch_social_posts.py` via the **Meta Graph API**, running as a GitHub Actions scheduled workflow (`.github/workflows/fetch-social-posts.yml`).

**Each run:**
1. **Forward sync** — fetches the most recent page of posts to pick up anything new published via PostBridge or directly.
2. **Backfill** — if historical backfill is not yet complete, fetches the next batch of older posts using the saved pagination cursor.

**Rate limiting:** Each run saves a maximum of 25 posts per platform (configurable). This keeps API usage well within Meta's 200 requests/hour limit. The workflow runs daily; the initial import completes gradually across multiple days.

---

## Required GitHub Secrets

The fetch workflow requires these three secrets in the repository settings:

| Secret | Description | Where to get it |
|--------|-------------|-----------------|
| `META_ACCESS_TOKEN` | Long-lived Page Access Token | See setup instructions below |
| `META_FACEBOOK_PAGE_ID` | Numeric ID of the OIO Facebook Page | Graph API Explorer or Page About section |
| `META_INSTAGRAM_ACCOUNT_ID` | Numeric ID of the Instagram Business Account | Graph API Explorer — query `/{page-id}?fields=instagram_business_account` |

---

## Token Setup Instructions

### Prerequisites
- A Meta (Facebook) Developer account
- The OIO Facebook Page (admin access)
- An Instagram Business or Creator account connected to the Facebook Page

### Steps

**1. Create a Meta App**
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create a new App → choose **Business** type
3. Add the **Facebook Login** and **Instagram Graph API** products to the app

**2. Get a User Access Token**
1. Open [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Request these permissions:
   - `pages_read_engagement`
   - `pages_show_list`
   - `instagram_basic`
4. Click **Generate Access Token** and authorize

**3. Exchange for a Long-Lived Token**
Short-lived tokens expire in 1 hour. Exchange for a 60-day token:
```
GET https://graph.facebook.com/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id={APP_ID}
  &client_secret={APP_SECRET}
  &fb_exchange_token={SHORT_LIVED_TOKEN}
```

**4. Get a Never-Expiring Page Access Token**
Page Access Tokens generated from a long-lived User Access Token do not expire:
```
GET https://graph.facebook.com/me/accounts?access_token={LONG_LIVED_USER_TOKEN}
```
Find your page in the response and copy its `access_token`. This is your `META_ACCESS_TOKEN`.

**5. Find Your Page ID**
```
GET https://graph.facebook.com/me/accounts?access_token={PAGE_ACCESS_TOKEN}
```
The `id` field for your page is `META_FACEBOOK_PAGE_ID`.

**6. Find Your Instagram Account ID**
```
GET https://graph.facebook.com/{PAGE_ID}?fields=instagram_business_account&access_token={PAGE_ACCESS_TOKEN}
```
The returned `id` is `META_INSTAGRAM_ACCOUNT_ID`.

**7. Add Secrets to the Repository**
Go to: **Repository Settings → Secrets and variables → Actions → New repository secret**
Add all three secrets listed in the table above.

---

## Running Manually

```bash
# Sync both platforms (25 posts each)
python scripts/fetch_social_posts.py

# Sync with a smaller batch (gentler on first run)
python scripts/fetch_social_posts.py --batch-size 10

# Facebook only
python scripts/fetch_social_posts.py --platform facebook

# Instagram only
python scripts/fetch_social_posts.py --platform instagram
```

Environment variables must be set:
```bash
export META_ACCESS_TOKEN=...
export META_FACEBOOK_PAGE_ID=...
export META_INSTAGRAM_ACCOUNT_ID=...
```

---

## Using the Library

When drafting new posts, review the archived posts in `facebook/` and `instagram/` to:
- Match the established voice and tone
- Avoid repeating content that was recently posted
- Identify themes and topics that have resonated
- Reference the language and hashtag patterns already in use

Posts are stored as plain markdown with frontmatter so they can be easily read by AI agents (Copilot, Claude) when generating new draft captions.
