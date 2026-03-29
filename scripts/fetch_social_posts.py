#!/usr/bin/env python3
"""
OIO Racing - Social Media Post Fetcher

Fetches text posts from Facebook (Page) and Instagram (Business Account)
via the Meta Graph API and saves them to social-posts/ as markdown files.

These posts are used as a reference library to inform tone, content, and
voice when drafting new posts.

Usage:
  python scripts/fetch_social_posts.py                          # Sync both platforms (default)
  python scripts/fetch_social_posts.py --batch-size 25         # Max posts per platform per run
  python scripts/fetch_social_posts.py --platform facebook     # Facebook only
  python scripts/fetch_social_posts.py --platform instagram    # Instagram only

Batching strategy:
  Each run performs two phases per platform:
    1. Forward sync  — fetch the most recent page to pick up new posts
    2. Backfill      — continue paginating older posts using the saved cursor

  Run this on a daily schedule. Each run fetches --batch-size posts per platform
  and resumes from the saved cursor on the next run. After backfill completes,
  only forward sync runs (near-zero API cost).

Saves each post to:
  social-posts/facebook/YYYY-MM-DD_slug.md
  social-posts/instagram/YYYY-MM-DD_slug.md

Pagination state is stored in:
  social-posts/sync-state.json
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("Error: requests is not installed.")
    print("Run: pip install requests")
    raise

META_API_VERSION = "v21.0"
META_BASE_URL = f"https://graph.facebook.com/{META_API_VERSION}"

RATE_LIMIT_SECONDS = 0.5  # pause between API calls — well under Meta's 200 req/hr limit

SOCIAL_POSTS_DIR = os.path.join(os.path.dirname(__file__), "..", "social-posts")
STATE_FILE = os.path.join(SOCIAL_POSTS_DIR, "sync-state.json")


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state():
    """Load pagination state from disk, or return a fresh default state."""
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {
        "facebook": {
            "backfill_cursor": None,
            "backfill_complete": False,
            "latest_post_time": None,
        },
        "instagram": {
            "backfill_cursor": None,
            "backfill_complete": False,
            "latest_post_time": None,
        },
    }


def save_state(state):
    """Write pagination state to disk."""
    os.makedirs(SOCIAL_POSTS_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


# ---------------------------------------------------------------------------
# Existing post discovery
# ---------------------------------------------------------------------------

def get_existing_post_ids(platform):
    """Return the set of post IDs already saved to disk for a platform."""
    platform_dir = os.path.join(SOCIAL_POSTS_DIR, platform)
    if not os.path.isdir(platform_dir):
        return set()

    existing = set()
    id_pattern = re.compile(r'^post_id:\s*["\']?([^"\']+?)["\']?\s*$')
    for fname in os.listdir(platform_dir):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(platform_dir, fname)
        try:
            with open(fpath, encoding="utf-8") as f:
                for line in f:
                    m = id_pattern.match(line)
                    if m:
                        existing.add(m.group(1))
                        break
        except OSError:
            pass
    return existing


# ---------------------------------------------------------------------------
# File writing
# ---------------------------------------------------------------------------

def sanitize_slug(text, max_len=40):
    """Convert a string to a safe, lowercase, hyphenated filename segment."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text[:max_len].rstrip("-")


def save_post(platform, post_id, date_str, text):
    """
    Save a single post as a markdown file with YAML frontmatter.
    Returns the path to the written file.
    """
    platform_dir = os.path.join(SOCIAL_POSTS_DIR, platform)
    os.makedirs(platform_dir, exist_ok=True)

    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        date_prefix = dt.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        date_prefix = (date_str or "unknown")[:10]

    # Build filename from date + first few words of the post
    first_words = " ".join(text.split()[:5])
    slug = sanitize_slug(first_words) or sanitize_slug(post_id[-12:])
    filename = f"{date_prefix}_{slug}.md"
    filepath = os.path.join(platform_dir, filename)

    # Resolve collisions (same date + same first words, different post)
    if os.path.isfile(filepath):
        filename = f"{date_prefix}_{sanitize_slug(post_id[-12:])}.md"
        filepath = os.path.join(platform_dir, filename)

    safe_text = text.replace('"', "'")
    summary_preview = safe_text[:80].replace("\n", " ")

    frontmatter = (
        "---\n"
        f'title: "{platform.capitalize()} post — {date_prefix}"\n'
        f"platform: {platform}\n"
        f'post_id: "{post_id}"\n'
        f"date: {date_str}\n"
        "type: social-post\n"
        "status: reference\n"
        "owner: Ian Jennings\n"
        f"updated: {date_prefix}\n"
        f"tags: [social, {platform}]\n"
        "source_of_truth: false\n"
        f'summary: "{summary_preview}"\n'
        "---\n\n"
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.write(text.strip())
        f.write("\n")

    return filepath


# ---------------------------------------------------------------------------
# Meta Graph API fetchers
# ---------------------------------------------------------------------------

def _api_get(url, params, retries=3):
    """GET request with simple retry on transient errors."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 429:
                wait = 60 * (attempt + 1)
                print(f"  Rate limited — waiting {wait}s before retry...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            if attempt < retries - 1:
                time.sleep(5)
            else:
                raise RuntimeError(f"API request failed after {retries} attempts: {exc}") from exc
    return {}


def fetch_facebook_posts(access_token, page_id, cursor=None, limit=25):
    """
    Fetch one page of Facebook Page posts.
    Returns (posts: list, next_cursor: str|None).
    """
    url = f"{META_BASE_URL}/{page_id}/posts"
    params = {
        "fields": "id,message,story,created_time",
        "limit": limit,
        "access_token": access_token,
    }
    if cursor:
        params["after"] = cursor

    data = _api_get(url, params)
    posts = data.get("data", [])
    paging = data.get("paging", {})
    cursors = paging.get("cursors", {})
    has_next = "next" in paging
    next_cursor = cursors.get("after") if has_next else None
    return posts, next_cursor


def fetch_instagram_posts(access_token, ig_account_id, cursor=None, limit=25):
    """
    Fetch one page of Instagram Business Account media.
    Returns (posts: list, next_cursor: str|None).
    """
    url = f"{META_BASE_URL}/{ig_account_id}/media"
    params = {
        "fields": "id,caption,media_type,timestamp",
        "limit": limit,
        "access_token": access_token,
    }
    if cursor:
        params["after"] = cursor

    data = _api_get(url, params)
    posts = data.get("data", [])
    paging = data.get("paging", {})
    cursors = paging.get("cursors", {})
    has_next = "next" in paging
    next_cursor = cursors.get("after") if has_next else None
    return posts, next_cursor


def _get_fb_text(post):
    """Extract the text body from a Facebook post dict."""
    return (post.get("message") or "").strip()


def _get_fb_time(post):
    return post.get("created_time", "")


def _get_ig_text(post):
    """Extract the caption from an Instagram post dict."""
    return (post.get("caption") or "").strip()


def _get_ig_time(post):
    return post.get("timestamp", "")


# ---------------------------------------------------------------------------
# Core sync logic
# ---------------------------------------------------------------------------

def sync_platform(platform, fetch_fn, get_text_fn, get_time_fn,
                  access_token, account_id, state, batch_size):
    """
    Sync posts for one platform.

    Phase 1 — Forward sync:
      Fetch page 1 (most recent posts). Save any not already on disk. This
      picks up new posts published since the last run. When we hit a post
      that already exists, the rest of the page is known — stop the forward
      scan.

    Phase 2 — Backfill:
      If the batch still has capacity and backfill is not complete, fetch
      from the saved backfill_cursor to import older posts. Continue until
      the batch is full or we reach the end of history.

    Returns the number of new posts saved.
    """
    pstate = state[platform]
    existing = get_existing_post_ids(platform)
    saved = 0

    print(f"\n[{platform.capitalize()}]")

    # ---- Phase 1: Forward sync ----
    print("  Forward sync (checking for new posts)...")
    fwd_posts, fwd_cursor = fetch_fn(access_token, account_id, cursor=None, limit=25)
    time.sleep(RATE_LIMIT_SECONDS)

    new_from_fwd = 0
    for post in fwd_posts:
        pid = post.get("id")
        text = get_text_fn(post)
        dt = get_time_fn(post)

        if pid in existing:
            # Posts are newest-first; hitting a known post means the rest are known too
            break
        if not text:
            continue  # Skip image-only or text-free posts

        path = save_post(platform, pid, dt, text)
        existing.add(pid)
        saved += 1
        new_from_fwd += 1
        if not pstate.get("latest_post_time") or dt > pstate["latest_post_time"]:
            pstate["latest_post_time"] = dt
        print(f"    ✓ New:  {dt[:10]} → {os.path.basename(path)}")

    if new_from_fwd == 0:
        print("    (up to date — no new posts)")

    # Initialize backfill cursor from first forward sync page
    if not pstate.get("backfill_cursor") and not pstate.get("backfill_complete"):
        pstate["backfill_cursor"] = fwd_cursor
        if not fwd_cursor:
            pstate["backfill_complete"] = True
            print("  Backfill: complete (page is the full history)")

    # ---- Phase 2: Backfill ----
    remaining = batch_size - saved
    if pstate.get("backfill_complete"):
        print("  Backfill: already complete")
    elif remaining <= 0:
        print(f"  Backfill: batch full — will continue on next run")
    else:
        cursor_label = "continuing" if pstate.get("backfill_cursor") else "starting"
        print(f"  Backfill: {cursor_label} (up to {remaining} older posts)...")
        backfill_saved = 0

        while not pstate.get("backfill_complete") and remaining > 0:
            cursor = pstate["backfill_cursor"]
            page_limit = min(remaining, 25)
            posts, next_cursor = fetch_fn(access_token, account_id, cursor=cursor, limit=page_limit)
            time.sleep(RATE_LIMIT_SECONDS)

            if not posts:
                pstate["backfill_complete"] = True
                print("  Backfill: reached end of history")
                break

            for post in posts:
                pid = post.get("id")
                text = get_text_fn(post)
                dt = get_time_fn(post)

                if pid in existing:
                    continue  # Already saved in a previous run
                if not text:
                    continue  # No text content

                path = save_post(platform, pid, dt, text)
                existing.add(pid)
                saved += 1
                remaining -= 1
                backfill_saved += 1
                print(f"    ✓ Old:  {dt[:10]} → {os.path.basename(path)}")

            if next_cursor:
                pstate["backfill_cursor"] = next_cursor
            else:
                pstate["backfill_complete"] = True
                print("  Backfill: reached end of history")
                break

            if remaining <= 0:
                print(f"  Backfill: batch full ({backfill_saved} saved this run) — will continue on next run")
                break

    return saved


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Fetch OIO social media posts from Facebook and Instagram."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=25,
        help="Max posts to save per platform per run (default: 25). "
             "Keeps API usage well within Meta limits.",
    )
    parser.add_argument(
        "--platform",
        choices=["facebook", "instagram", "both"],
        default="both",
        help="Which platform(s) to sync (default: both).",
    )
    args = parser.parse_args()

    # Read credentials from environment
    access_token = os.environ.get("META_ACCESS_TOKEN", "").strip()
    facebook_page_id = os.environ.get("META_FACEBOOK_PAGE_ID", "").strip()
    instagram_account_id = os.environ.get("META_INSTAGRAM_ACCOUNT_ID", "").strip()

    missing = []
    if not access_token:
        missing.append("META_ACCESS_TOKEN")
    if args.platform in ("facebook", "both") and not facebook_page_id:
        missing.append("META_FACEBOOK_PAGE_ID")
    if args.platform in ("instagram", "both") and not instagram_account_id:
        missing.append("META_INSTAGRAM_ACCOUNT_ID")

    if missing:
        print("Error: the following required environment variables are not set:")
        for v in missing:
            print(f"  {v}")
        print("\nSee social-posts/README.md for setup instructions.")
        sys.exit(1)

    state = load_state()
    total_saved = 0

    print(f"OIO Social Post Fetcher — batch size: {args.batch_size} per platform")

    if args.platform in ("facebook", "both"):
        try:
            n = sync_platform(
                platform="facebook",
                fetch_fn=fetch_facebook_posts,
                get_text_fn=_get_fb_text,
                get_time_fn=_get_fb_time,
                access_token=access_token,
                account_id=facebook_page_id,
                state=state,
                batch_size=args.batch_size,
            )
            total_saved += n
        except RuntimeError as exc:
            print(f"\n[Facebook] ERROR: {exc}")
            print("Check META_ACCESS_TOKEN permissions and META_FACEBOOK_PAGE_ID.")

    if args.platform in ("instagram", "both"):
        try:
            n = sync_platform(
                platform="instagram",
                fetch_fn=fetch_instagram_posts,
                get_text_fn=_get_ig_text,
                get_time_fn=_get_ig_time,
                access_token=access_token,
                account_id=instagram_account_id,
                state=state,
                batch_size=args.batch_size,
            )
            total_saved += n
        except RuntimeError as exc:
            print(f"\n[Instagram] ERROR: {exc}")
            print("Check META_ACCESS_TOKEN permissions and META_INSTAGRAM_ACCOUNT_ID.")

    save_state(state)

    fb_complete = state["facebook"].get("backfill_complete", False)
    ig_complete = state["instagram"].get("backfill_complete", False)

    print(f"\nDone. {total_saved} new post(s) saved this run.")
    if args.platform in ("facebook", "both"):
        status = "complete" if fb_complete else "in progress — run again to continue"
        print(f"  Facebook backfill: {status}")
    if args.platform in ("instagram", "both"):
        status = "complete" if ig_complete else "in progress — run again to continue"
        print(f"  Instagram backfill: {status}")

    if total_saved == 0 and args.platform == "both" and fb_complete and ig_complete:
        print("  Everything is up to date.")


if __name__ == "__main__":
    main()
