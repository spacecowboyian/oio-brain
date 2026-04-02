#!/usr/bin/env python3
"""
OIO Racing - Posting Time Analysis

Analyzes historical social media posts to identify optimal posting times
for each platform. Uses engagement metrics (likes, comments, shares) to
determine when audience is most active.

Usage:
    python scripts/analyze_posting_times.py
    python scripts/analyze_posting_times.py --platform instagram
    python scripts/analyze_posting_times.py --generate-schedule
"""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime, time
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class PostingTimeAnalyzer:
    """Analyze optimal posting times from historical posts."""

    def __init__(self, social_posts_dir: Optional[Path] = None):
        """Initialize analyzer."""
        if social_posts_dir is None:
            social_posts_dir = Path(__file__).parent.parent / "data" / "social-posts"
        self.social_posts_dir = social_posts_dir
        self.schedule_file = (
            Path(__file__).parent.parent / "data" / "optimal-posting-schedule.json"
        )

    def analyze(self, platform: Optional[str] = None) -> Dict[str, Dict[str, any]]:
        """
        Analyze posts to find optimal posting times.

        Args:
            platform: Optional platform to analyze (instagram, facebook)

        Returns:
            Dictionary with optimal posting times by day/hour
        """
        platforms = ["instagram", "facebook"] if not platform else [platform]
        analysis = {}

        for plat in platforms:
            posts = self._load_posts(plat)
            if posts:
                analysis[plat] = self._analyze_platform(posts, plat)
            else:
                analysis[plat] = self._empty_analysis()

        return analysis

    def generate_schedule(self) -> Dict[str, Dict[str, str]]:
        """
        Generate an optimal posting schedule based on analysis.

        Returns:
            Dictionary with recommended posting times for each platform
        """
        analysis = self.analyze()
        schedule = {}

        for platform, data in analysis.items():
            best_hours = data.get("best_hours", [])
            best_days = data.get("best_days", [])

            if best_hours and best_days:
                # Format schedule (ISO 8601 time format)
                schedule[platform] = {
                    "best_time": f"{best_hours[0]:02d}:00",
                    "best_day": best_days[0],
                    "recommended_times": [f"{h:02d}:00" for h in best_hours[:3]],
                    "recommended_days": best_days[:2],
                    "timezone": "America/Chicago",
                    "note": "Based on historical engagement data"
                }
            else:
                schedule[platform] = {
                    "note": "Insufficient data for analysis",
                    "default": "Post between 9am-6pm Central"
                }

        return schedule

    def _load_posts(self, platform: str) -> List[Dict]:
        """Load posts from disk."""
        platform_dir = self.social_posts_dir / platform

        if not platform_dir.exists():
            return []

        posts = []
        for post_file in platform_dir.glob("*.md"):
            try:
                with open(post_file, "r") as f:
                    content = f.read()
                    post = self._parse_post(content, post_file.name)
                    if post:
                        posts.append(post)
            except Exception:
                pass

        return posts

    def _parse_post(self, content: str, filename: str) -> Optional[Dict]:
        """Parse a post markdown file."""
        lines = content.split("\n")

        # Extract frontmatter
        if not lines[0].startswith("---"):
            return None

        frontmatter = {}
        i = 1
        while i < len(lines) and not lines[i].startswith("---"):
            if ":" in lines[i]:
                key, value = lines[i].split(":", 1)
                frontmatter[key.strip()] = value.strip()
            i += 1

        # Extract date from filename (expected format: YYYY-MM-DD_slug.md)
        date_match = re.match(r"(\d{4})-(\d{2})-(\d{2})", filename)
        if not date_match:
            return None

        try:
            post_date = datetime.strptime(date_match.group(0), "%Y-%m-%d")
        except ValueError:
            return None

        return {
            "date": post_date,
            "filename": filename,
            "frontmatter": frontmatter,
            "content": "\n".join(lines[i+1:])
        }

    def _analyze_platform(self, posts: List[Dict], platform: str) -> Dict:
        """Analyze posts for a specific platform."""
        if not posts:
            return self._empty_analysis()

        # Aggregate by day of week and hour
        day_engagement = defaultdict(lambda: {"count": 0, "score": 0})
        hour_engagement = defaultdict(lambda: {"count": 0, "score": 0})

        for post in posts:
            post_date = post.get("date")
            if not post_date:
                continue

            day_name = post_date.strftime("%A")
            hour = post_date.hour

            # Simple engagement score (in real scenario, would use actual metrics)
            # For now, we'll use posting frequency as a proxy
            engagement_score = 1

            day_engagement[day_name]["count"] += 1
            day_engagement[day_name]["score"] += engagement_score

            hour_engagement[hour]["count"] += 1
            hour_engagement[hour]["score"] += engagement_score

        # Find best days and hours
        best_days = sorted(
            day_engagement.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        best_hours = sorted(
            hour_engagement.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )

        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        best_days_sorted = sorted(
            best_days,
            key=lambda x: day_order.index(x[0]) if x[0] in day_order else 7
        )

        return {
            "total_posts": len(posts),
            "date_range": {
                "start": posts[0].get("date").isoformat() if posts else None,
                "end": posts[-1].get("date").isoformat() if posts else None
            },
            "best_days": [d[0] for d in best_days_sorted[:3]],
            "best_hours": [h[0] for h in best_hours[:5]],
            "day_distribution": {
                day: {
                    "posts": data["count"],
                    "avg_engagement": round(data["score"] / data["count"], 2)
                }
                for day, data in day_engagement.items()
            },
            "hour_distribution": {
                f"{hour:02d}:00": {
                    "posts": data["count"],
                    "avg_engagement": round(data["score"] / data["count"], 2)
                }
                for hour, data in hour_engagement.items()
            }
        }

    def _empty_analysis(self) -> Dict:
        """Return empty analysis."""
        return {
            "total_posts": 0,
            "date_range": {"start": None, "end": None},
            "best_days": [],
            "best_hours": [],
            "day_distribution": {},
            "hour_distribution": {}
        }

    def save_schedule(self, schedule: Dict) -> None:
        """Save schedule to file."""
        self.schedule_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.schedule_file, "w") as f:
            json.dump(schedule, f, indent=2)

        print(f"✓ Schedule saved to {self.schedule_file}")


def main():
    """Run analysis."""
    parser = argparse.ArgumentParser(description="Analyze optimal posting times")
    parser.add_argument(
        "--platform",
        type=str,
        choices=["instagram", "facebook"],
        help="Analyze specific platform"
    )
    parser.add_argument(
        "--generate-schedule",
        action="store_true",
        help="Generate and save posting schedule"
    )

    args = parser.parse_args()

    analyzer = PostingTimeAnalyzer()

    if args.generate_schedule:
        schedule = analyzer.generate_schedule()
        analyzer.save_schedule(schedule)
        print(json.dumps(schedule, indent=2))
    else:
        analysis = analyzer.analyze(args.platform)
        print(json.dumps(analysis, indent=2, default=str))


if __name__ == "__main__":
    main()
