#!/usr/bin/env python3
"""
OIO Racing - Auto Post Scheduler

Automatically schedules social media posts at optimal times based on
historical engagement analysis.

Workflow:
1. Load optimal posting schedule (from analyze_posting_times.py)
2. Find unscheduled drafts via PostBridge API
3. Schedule each draft to the best upcoming time for its platform
4. Log scheduling decisions

Usage:
    python scripts/auto_schedule_posts.py [--dry-run]
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys

# Import PostBridge client
sys.path.append(str(Path(__file__).parent))
from postbridge_client import PostBridgeClient, PostBridgeError


class PostScheduler:
    """Automatically schedule posts based on optimal times."""

    def __init__(self, postbridge_api_key: Optional[str] = None, dry_run: bool = False):
        """
        Initialize scheduler.

        Args:
            postbridge_api_key: API key for PostBridge
            dry_run: If True, don't actually schedule posts
        """
        import os
        self.api_key = postbridge_api_key or os.environ.get("POSTBRIDGE_API_KEY", "")
        self.dry_run = dry_run
        self.client = PostBridgeClient(api_key=self.api_key) if self.api_key else None
        self.schedule_file = (
            Path(__file__).parent.parent / "OIO Brain" / "data" / "optimal-posting-schedule.json"
        )
        self.scheduling_log = (
            Path(__file__).parent.parent / "OIO Brain" / "data" / "post-scheduling-log.jsonl"
        )

    def schedule_posts(self) -> Dict:
        """
        Schedule unscheduled drafts.

        Returns:
            Dictionary with scheduling results
        """
        if not self.client:
            return {"error": "PostBridge API key not configured", "scheduled": 0}

        # Load optimal schedule
        schedule = self._load_schedule()
        if not schedule:
            return {"error": "No optimal schedule available", "scheduled": 0}

        # Get unscheduled drafts
        try:
            posts = self.client.list_posts(status="draft")
        except PostBridgeError as e:
            return {"error": f"Failed to list posts: {e}", "scheduled": 0}

        results = {
            "scheduled": 0,
            "skipped": 0,
            "errors": 0,
            "scheduled_posts": []
        }

        # Schedule each draft
        for post in posts:
            result = self._schedule_post(post, schedule)
            if result.get("scheduled"):
                results["scheduled"] += 1
                results["scheduled_posts"].append(result)
            elif result.get("error"):
                results["errors"] += 1
            else:
                results["skipped"] += 1

            # Log decision
            self._log_scheduling_decision(result)

        return results

    def _schedule_post(self, post: Dict, schedule: Dict) -> Dict:
        """
        Schedule a single post.

        Args:
            post: Post dictionary from PostBridge API
            schedule: Optimal posting schedule

        Returns:
            Result dictionary
        """
        post_id = post.get("id", "unknown")
        platform = post.get("platform", "instagram")

        # Get optimal time for this platform
        platform_schedule = schedule.get(platform)
        if not platform_schedule:
            return {
                "post_id": post_id,
                "platform": platform,
                "skipped": True,
                "reason": f"No schedule for {platform}"
            }

        # Calculate next optimal posting time
        try:
            scheduled_time = self._next_optimal_time(platform_schedule)
        except Exception as e:
            return {
                "post_id": post_id,
                "platform": platform,
                "error": True,
                "reason": str(e)
            }

        # Schedule via PostBridge
        if self.dry_run:
            return {
                "post_id": post_id,
                "platform": platform,
                "scheduled": True,
                "scheduled_at": scheduled_time.isoformat(),
                "dry_run": True,
                "note": "Dry run - not actually scheduled"
            }

        try:
            self.client.schedule_post(
                post_id=post_id,
                scheduled_time=scheduled_time.isoformat()
            )

            return {
                "post_id": post_id,
                "platform": platform,
                "scheduled": True,
                "scheduled_at": scheduled_time.isoformat()
            }

        except PostBridgeError as e:
            return {
                "post_id": post_id,
                "platform": platform,
                "error": True,
                "reason": str(e)
            }

    def _next_optimal_time(self, platform_schedule: Dict) -> datetime:
        """
        Calculate next optimal posting time.

        Args:
            platform_schedule: Schedule for a specific platform

        Returns:
            Recommended datetime for posting
        """
        best_time = platform_schedule.get("best_time", "12:00")
        best_day = platform_schedule.get("best_day", "Tuesday")
        timezone_str = platform_schedule.get("timezone", "America/Chicago")

        # Parse time
        hour, minute = map(int, best_time.split(":"))

        # Find next occurrence of best_day
        now = datetime.utcnow()
        day_names = [
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"
        ]

        best_day_idx = day_names.index(best_day) if best_day in day_names else 1
        current_day_idx = now.weekday()

        # Calculate days until best day
        days_ahead = (best_day_idx - current_day_idx) % 7
        if days_ahead == 0:
            days_ahead = 7 if now.hour >= hour else 0

        # Schedule for next best day at best time
        next_date = now + timedelta(days=days_ahead)
        scheduled_time = next_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # Ensure we're at least 1 hour in the future
        min_future_time = now + timedelta(hours=1)
        if scheduled_time < min_future_time:
            scheduled_time += timedelta(days=7)

        return scheduled_time

    def _load_schedule(self) -> Optional[Dict]:
        """Load optimal posting schedule."""
        if not self.schedule_file.exists():
            return None

        try:
            with open(self.schedule_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None

    def _log_scheduling_decision(self, result: Dict) -> None:
        """Log scheduling decision to file."""
        result["timestamp"] = datetime.utcnow().isoformat()

        self.scheduling_log.parent.mkdir(parents=True, exist_ok=True)

        with open(self.scheduling_log, "a") as f:
            f.write(json.dumps(result) + "\n")


def main():
    """Run scheduler."""
    parser = argparse.ArgumentParser(description="Auto-schedule posts at optimal times")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be scheduled without actually scheduling"
    )

    args = parser.parse_args()

    scheduler = PostScheduler(dry_run=args.dry_run)
    results = scheduler.schedule_posts()

    # Pretty print results
    print(f"{'=' * 60}")
    print(f"Post Scheduling Results")
    print(f"{'=' * 60}")
    print(f"Scheduled: {results.get('scheduled', 0)}")
    print(f"Skipped: {results.get('skipped', 0)}")
    print(f"Errors: {results.get('errors', 0)}")

    if results.get("error"):
        print(f"\n❌ Error: {results['error']}")

    if results.get("scheduled_posts"):
        print(f"\n📅 Scheduled Posts:")
        for post in results.get("scheduled_posts", []):
            print(f"  - {post['post_id']} → {post['scheduled_at']} ({post['platform']})")

    if args.dry_run:
        print("\n⚠️  DRY RUN - No posts were actually scheduled")


if __name__ == "__main__":
    main()
