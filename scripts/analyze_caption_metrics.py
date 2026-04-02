#!/usr/bin/env python3
"""
OIO Racing - Caption Metrics Analysis

Analyzes caption generation metrics to identify quality trends, issues, and
feedback patterns. Generates reports and alerts for the monitoring dashboard.

Usage:
    python scripts/analyze_caption_metrics.py
    python scripts/analyze_caption_metrics.py --generate-reports
    python scripts/analyze_caption_metrics.py --past-days 14
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class CaptionMetricsAnalyzer:
    """Analyze caption generation metrics."""

    def __init__(self, metrics_dir: Optional[Path] = None):
        """Initialize analyzer."""
        if metrics_dir is None:
            metrics_dir = Path(__file__).parent.parent / "data" / "caption-metrics"
        self.metrics_dir = metrics_dir
        self.events_file = self.metrics_dir / "events.jsonl"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze metrics for the past N days.

        Args:
            days: Number of days to analyze

        Returns:
            Analysis results dictionary
        """
        if not self.events_file.exists():
            return self._empty_analysis()

        events = self._read_events()
        cutoff_time = datetime.utcnow().timestamp() - (days * 86400)
        filtered_events = [
            e for e in events
            if self._parse_timestamp(e.get("timestamp", "")) > cutoff_time
        ]

        return self._compute_analysis(filtered_events, days)

    def generate_reports(self, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive metrics reports."""
        analysis = self.analyze(days)

        # Get previous period for comparison
        analysis_prev = self.analyze(days * 2)
        prev_events = analysis_prev.get("events", [])
        if len(prev_events) > days * 100:  # Rough estimate of events in a day
            prev_analysis = self._compute_analysis(
                prev_events[:-int(len(prev_events) / 2)],
                days
            )
        else:
            prev_analysis = self._empty_analysis()

        # Generate alerts
        alerts = self._generate_alerts(analysis, prev_analysis)

        # Save reports
        self._save_json(
            self.metrics_dir / "metrics-summary.json",
            analysis
        )
        self._save_json(
            self.metrics_dir / "alerts.json",
            alerts
        )

        # Generate weekly summary markdown
        if self._is_monday():
            weekly_summary = self._generate_weekly_summary(analysis)
            self._save_text(
                self.metrics_dir / "weekly-summary.md",
                weekly_summary
            )

        return {
            "analysis": analysis,
            "alerts": alerts,
            "prev_analysis": prev_analysis
        }

    def _read_events(self) -> List[Dict[str, Any]]:
        """Read all events from JSONL file."""
        if not self.events_file.exists():
            return []

        events = []
        with open(self.events_file, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return events

    def _parse_timestamp(self, ts_str: str) -> float:
        """Parse ISO timestamp to Unix time."""
        try:
            return datetime.fromisoformat(ts_str).timestamp()
        except (ValueError, AttributeError):
            return 0.0

    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis."""
        return {
            "period_days": 7,
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "success_rate": 0.0,
            "avg_generation_time": 0.0,
            "total_captions_generated": 0,
            "total_captions_selected": 0,
            "selection_rate": 0.0,
            "feedback_counts": {"positive": 0, "negative": 0, "revision": 0},
            "events": []
        }

    def _compute_analysis(self, events: List[Dict[str, Any]], days: int) -> Dict[str, Any]:
        """Compute detailed analysis from events."""
        analysis = self._empty_analysis()
        analysis["period_days"] = days
        analysis["events"] = events

        # Count events by type
        started_events = [e for e in events if e.get("event_type") == "generation_started"]
        completed_events = [e for e in events if e.get("event_type") == "generation_completed"]
        failed_events = [e for e in events if e.get("event_type") == "generation_failed"]
        selected_events = [e for e in events if e.get("event_type") == "caption_selected"]
        feedback_events = [e for e in events if e.get("event_type") == "caption_feedback"]

        analysis["total_requests"] = len(started_events)
        analysis["successful"] = len(completed_events)
        analysis["failed"] = len(failed_events)

        # Success rate
        if analysis["total_requests"] > 0:
            analysis["success_rate"] = (
                analysis["successful"] / analysis["total_requests"] * 100
            )

        # Average generation time
        gen_times = [e.get("duration_seconds", 0) for e in completed_events]
        if gen_times:
            analysis["avg_generation_time"] = sum(gen_times) / len(gen_times)

        # Captions generated and selected
        analysis["total_captions_generated"] = sum(
            e.get("captions_count", 0) for e in completed_events
        )
        analysis["total_captions_selected"] = len(selected_events)

        if analysis["total_captions_generated"] > 0:
            analysis["selection_rate"] = (
                analysis["total_captions_selected"] / analysis["total_captions_generated"] * 100
            )

        # Feedback breakdown
        for feedback_event in feedback_events:
            ftype = feedback_event.get("feedback_type", "unknown")
            if ftype == "positive":
                analysis["feedback_counts"]["positive"] += 1
            elif ftype == "negative":
                analysis["feedback_counts"]["negative"] += 1
            elif ftype == "revision_needed":
                analysis["feedback_counts"]["revision"] += 1

        return analysis

    def _generate_alerts(
        self,
        analysis: Dict[str, Any],
        prev_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate alerts based on metric changes."""
        alerts = {
            "success_rate_dropped": False,
            "selection_rate_dropped": False,
            "high_failure_rate": False,
            "low_feedback_positive_rate": False
        }

        current_success = analysis.get("success_rate", 0)
        prev_success = prev_analysis.get("success_rate", 100)

        # Alert if success rate drops > 5%
        if current_success < 90 or (current_success < prev_success - 5):
            alerts["success_rate_dropped"] = True
            alerts["current_success_rate"] = round(current_success, 1)
            alerts["previous_success_rate"] = round(prev_success, 1)

        # Alert if selection rate drops below 75%
        current_selection = analysis.get("selection_rate", 0)
        prev_selection = prev_analysis.get("selection_rate", 100)

        if current_selection < 75 or (current_selection < prev_selection - 5):
            alerts["selection_rate_dropped"] = True
            alerts["current_selection_rate"] = round(current_selection, 1)
            alerts["previous_selection_rate"] = round(prev_selection, 1)

        # Alert if failure rate is high (> 10%)
        failure_rate = 100 - current_success
        if failure_rate > 10:
            alerts["high_failure_rate"] = True
            alerts["failure_rate"] = round(failure_rate, 1)

        # Alert if positive feedback rate is low
        feedback_total = sum(analysis.get("feedback_counts", {}).values())
        if feedback_total > 0:
            positive = analysis["feedback_counts"].get("positive", 0)
            positive_rate = (positive / feedback_total) * 100
            if positive_rate < 70:
                alerts["low_feedback_positive_rate"] = True
                alerts["positive_feedback_rate"] = round(positive_rate, 1)

        return alerts

    def _generate_weekly_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate human-readable weekly summary."""
        success = analysis.get("success_rate", 0)
        selection = analysis.get("selection_rate", 0)
        avg_time = analysis.get("avg_generation_time", 0)
        total_requests = analysis.get("total_requests", 0)
        total_captions = analysis.get("total_captions_generated", 0)
        feedback = analysis.get("feedback_counts", {})

        summary = f"""
### Metrics Summary

- **Total Requests:** {total_requests}
- **Success Rate:** {success:.1f}%
- **Average Generation Time:** {avg_time:.1f}s
- **Captions Generated:** {total_captions}
- **Caption Selection Rate:** {selection:.1f}%

### User Feedback

- **Positive:** {feedback.get('positive', 0)} ✅
- **Revision Needed:** {feedback.get('revision', 0)} 🔄
- **Negative:** {feedback.get('negative', 0)} ❌

### Assessment

"""

        if success >= 95 and selection >= 75:
            summary += "✅ **System performing well.** No action needed."
        elif success < 90:
            summary += "⚠️ **Success rate below target.** Check error logs and API health."
        elif selection < 70:
            summary += "⚠️ **Selection rate low.** Review rejected captions; consider prompt refinement."
        else:
            summary += "🟡 **Minor issues detected.** Monitor trends."

        return summary

    def _is_monday(self) -> bool:
        """Check if today is Monday."""
        return datetime.utcnow().weekday() == 0

    def _save_json(self, path: Path, data: Dict[str, Any]) -> None:
        """Save data as JSON."""
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _save_text(self, path: Path, text: str) -> None:
        """Save text to file."""
        with open(path, "w") as f:
            f.write(text)


def main():
    """Run analysis."""
    parser = argparse.ArgumentParser(description="Analyze caption metrics")
    parser.add_argument(
        "--generate-reports",
        action="store_true",
        help="Generate comprehensive reports"
    )
    parser.add_argument(
        "--past-days",
        type=int,
        default=7,
        help="Analyze past N days (default: 7)"
    )

    args = parser.parse_args()

    analyzer = CaptionMetricsAnalyzer()

    if args.generate_reports:
        result = analyzer.generate_reports(args.past_days)
        analysis = result["analysis"]
        alerts = result["alerts"]

        # Output for GitHub Actions
        print(f"::set-output name=success_rate_dropped::{alerts.get('success_rate_dropped', False)}")
        print(f"::set-output name=current_success_rate::{analysis.get('success_rate', 0):.1f}")
        print(f"::set-output name=previous_success_rate::{result['prev_analysis'].get('success_rate', 0):.1f}")
        print(f"::set-output name=selection_rate_dropped::{alerts.get('selection_rate_dropped', False)}")
        print(f"::set-output name=current_selection_rate::{analysis.get('selection_rate', 0):.1f}")
        print(f"::set-output name=previous_selection_rate::{result['prev_analysis'].get('selection_rate', 0):.1f}")

        print("\n✓ Reports generated")
    else:
        analysis = analyzer.analyze(args.past_days)
        print(json.dumps(analysis, indent=2, default=str))


if __name__ == "__main__":
    main()
