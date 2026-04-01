#!/usr/bin/env python3
"""
Update the caption monitoring dashboard with latest metrics.

Reads from metrics summary and updates CAPTION-MONITORING.md with
current KPIs, trends, and feedback breakdown.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta


class DashboardUpdater:
    """Update the caption monitoring dashboard."""

    def __init__(self):
        """Initialize updater."""
        self.repo_root = Path(__file__).parent.parent
        self.metrics_dir = self.repo_root / "OIO Brain" / "data" / "caption-metrics"
        self.dashboard_file = self.repo_root / "CAPTION-MONITORING.md"

    def update(self) -> None:
        """Update the dashboard with latest metrics."""
        # Load metrics
        metrics = self._load_metrics()

        if not metrics:
            print("No metrics data available")
            return

        # Read dashboard
        with open(self.dashboard_file, "r") as f:
            content = f.read()

        # Update each section
        content = self._update_metrics_table(content, metrics)
        content = self._update_kpis(content, metrics)
        content = self._update_platform_usage(content, metrics)
        content = self._update_feedback_breakdown(content, metrics)
        content = self._update_timestamp(content)

        # Write updated dashboard
        with open(self.dashboard_file, "w") as f:
            f.write(content)

        print("✓ Dashboard updated")

    def _load_metrics(self) -> dict:
        """Load the latest metrics summary."""
        metrics_file = self.metrics_dir / "metrics-summary.json"

        if not metrics_file.exists():
            return {}

        try:
            with open(metrics_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _update_metrics_table(self, content: str, metrics: dict) -> str:
        """Update the current metrics table."""
        success_rate = metrics.get("success_rate", 0)
        selection_rate = metrics.get("selection_rate", 0)
        avg_time = metrics.get("avg_generation_time", 0)
        total_requests = metrics.get("total_requests", 0)
        total_captions = metrics.get("total_captions_generated", 0)

        # Determine trends (simplified - would need historical data)
        success_trend = "↓" if success_rate < 95 else "→"
        selection_trend = "↓" if selection_rate < 75 else "→"
        time_trend = "↑" if avg_time > 60 else "→"

        table = f"""| Metric | Value | Trend |
|--------|-------|-------|
| Total Requests | {total_requests} | — |
| Success Rate | {success_rate:.1f}% | {success_trend} |
| Avg Generation Time | {avg_time:.1f}s | {time_trend} |
| Captions Generated | {total_captions} | — |
| Caption Selection Rate | {selection_rate:.1f}% | {selection_trend} |"""

        # Find and replace the metrics table
        pattern = r"(\| Metric \| Value \| Trend \|\n\|.*?\n.*?\n.*?\n.*?\n.*?\n.*?\|)"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            content = content.replace(match.group(1), table)

        return content

    def _update_kpis(self, content: str, metrics: dict) -> str:
        """Update KPI sections."""
        success_rate = metrics.get("success_rate", 0)
        avg_time = metrics.get("avg_generation_time", 0)
        selection_rate = metrics.get("selection_rate", 0)

        # Update success rate KPI
        kpi_pattern = r"(\*\*Current:\*\*) —"
        replacement = f"\\1 {success_rate:.1f}%"
        content = re.sub(
            r"(### Generation Success Rate.*?\n.*?\n.*?\n.*?\n\*\*Current:\*\*) —",
            f"\\1 {success_rate:.1f}%",
            content,
            flags=re.DOTALL
        )

        # Update average generation time KPI
        content = re.sub(
            r"(### Average Generation Time.*?\n.*?\n.*?\n.*?\n\*\*Current:\*\*) —",
            f"\\1 {avg_time:.1f}s",
            content,
            flags=re.DOTALL
        )

        # Update selection rate KPI
        content = re.sub(
            r"(### Caption Selection Rate.*?\n.*?\n.*?\n.*?\n\*\*Current:\*\*) —",
            f"\\1 {selection_rate:.1f}%",
            content,
            flags=re.DOTALL
        )

        return content

    def _update_platform_usage(self, content: str, metrics: dict) -> str:
        """Update platform usage breakdown."""
        by_platform = metrics.get("by_platform", {})

        if not by_platform:
            return content

        # Build platform table
        rows = []
        for platform, data in by_platform.items():
            selected = data.get("selected", 0)
            by_user = data.get("by_user", {})
            top_user = max(by_user.items(), key=lambda x: x[1])[0] if by_user else "—"
            rows.append(f"| {platform.capitalize()} | {selected} | {top_user} | — |")

        if rows:
            table = f"""| Platform | Captions Selected | Top User | Notes |
|----------|-------------------|----------|-------|
{chr(10).join(rows)}"""

            # Find and replace platform table
            pattern = r"(\| Platform \| Captions Selected \|.*?\n\|.*?\n(?:\|.*?\n)*)"
            content = re.sub(pattern, table + "\n", content, count=1)

        return content

    def _update_feedback_breakdown(self, content: str, metrics: dict) -> str:
        """Update feedback breakdown section."""
        feedback = metrics.get("feedback_counts", {})
        positive = feedback.get("positive", 0)
        revision = feedback.get("revision", 0)
        negative = feedback.get("negative", 0)
        total = positive + revision + negative

        if total == 0:
            return content

        # Calculate percentages
        pos_pct = int((positive / total) * 100)
        rev_pct = int((revision / total) * 100)
        neg_pct = int((negative / total) * 100)

        # Create bar charts
        def make_bar(pct):
            filled = int(pct / 10)
            empty = 10 - filled
            return "▓" * filled + "░" * empty

        feedback_section = f"""```
Positive Feedback:   {make_bar(pos_pct)} {pos_pct}%  ({positive} feedback items)
Revision Needed:     {make_bar(rev_pct)} {rev_pct}%  ({revision} feedback items)
Negative Feedback:   {make_bar(neg_pct)} {neg_pct}%  ({negative} feedback items)
```"""

        # Find and replace feedback breakdown
        pattern = r"```\nPositive Feedback:.*?\nNegative Feedback:.*?\n```"
        content = re.sub(pattern, feedback_section, content, flags=re.DOTALL)

        return content

    def _update_timestamp(self, content: str) -> str:
        """Update the modified timestamp."""
        now = datetime.utcnow().strftime("%Y-%m-%d")

        # Find and update the "updated:" field
        content = re.sub(
            r"updated: \d{4}-\d{2}-\d{2}",
            f"updated: {now}",
            content,
            count=1
        )

        # Also update the "This section is automatically updated" timestamp
        content = re.sub(
            r"(_This section is automatically updated.*? at )\d{4}-\d{2}-\d{2}",
            f"\\1{now}",
            content
        )

        return content


def main():
    """Update the dashboard."""
    updater = DashboardUpdater()
    updater.update()


if __name__ == "__main__":
    main()
