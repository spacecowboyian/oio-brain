#!/usr/bin/env python3
"""
OIO Racing - Caption Generation Metrics Logger

Tracks caption generation metrics for quality monitoring and iterative refinement:
- Caption generation requests and completions
- User selections (which captions were chosen)
- Generation times and performance metrics
- Error rates and failure analysis
- Quality feedback from team members

Metrics are logged to: OIO Brain/data/caption-metrics/events.jsonl
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class CaptionMetricsLogger:
    """Log and analyze caption generation metrics."""

    def __init__(self):
        """Initialize the metrics logger."""
        self.metrics_dir = Path(__file__).parent.parent / "OIO Brain" / "data" / "caption-metrics"
        self.events_file = self.metrics_dir / "events.jsonl"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

    def log_generation_started(
        self,
        request_id: str,
        media_ids: List[str],
        media_urls: List[str],
        context: str,
        caption_count: int,
        triggered_by: str = "unknown"
    ) -> None:
        """Log a caption generation request."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "generation_started",
            "request_id": request_id,
            "media_ids": media_ids,
            "media_urls": media_urls,
            "context": context,
            "caption_count": caption_count,
            "triggered_by": triggered_by
        }
        self._append_event(event)

    def log_generation_completed(
        self,
        request_id: str,
        task_id: str,
        captions: List[Dict[str, Any]],
        duration_seconds: float,
        context_sources: List[str],
        status: str = "success"
    ) -> None:
        """Log a completed caption generation."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "generation_completed",
            "request_id": request_id,
            "task_id": task_id,
            "captions_count": len(captions),
            "captions": captions,
            "duration_seconds": duration_seconds,
            "context_sources": context_sources,
            "status": status
        }
        self._append_event(event)

    def log_generation_failed(
        self,
        request_id: str,
        task_id: Optional[str],
        error_message: str,
        duration_seconds: float
    ) -> None:
        """Log a failed caption generation."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "generation_failed",
            "request_id": request_id,
            "task_id": task_id,
            "error_message": error_message,
            "duration_seconds": duration_seconds
        }
        self._append_event(event)

    def log_caption_selected(
        self,
        request_id: str,
        caption_index: int,
        caption_text: str,
        selected_by: str,
        selected_for_platform: str
    ) -> None:
        """Log when a caption is selected for use."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "caption_selected",
            "request_id": request_id,
            "caption_index": caption_index,
            "caption_text": caption_text,
            "selected_by": selected_by,
            "selected_for_platform": selected_for_platform
        }
        self._append_event(event)

    def log_caption_feedback(
        self,
        request_id: str,
        caption_index: int,
        feedback_type: str,  # "positive", "negative", "revision_needed"
        feedback_text: str,
        feedback_by: str
    ) -> None:
        """Log feedback on generated captions."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "caption_feedback",
            "request_id": request_id,
            "caption_index": caption_index,
            "feedback_type": feedback_type,
            "feedback_text": feedback_text,
            "feedback_by": feedback_by
        }
        self._append_event(event)

    def get_metrics_summary(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Generate a metrics summary for the past N days.

        Args:
            days_back: Number of days to include

        Returns:
            Dictionary with aggregated metrics
        """
        if not self.events_file.exists():
            return self._empty_summary()

        events = self._read_events()
        cutoff_time = datetime.utcnow().timestamp() - (days_back * 86400)

        filtered_events = [
            e for e in events
            if datetime.fromisoformat(e["timestamp"]).timestamp() > cutoff_time
        ]

        return self._compute_summary(filtered_events)

    def _append_event(self, event: Dict[str, Any]) -> None:
        """Append an event to the JSONL file."""
        with open(self.events_file, "a") as f:
            f.write(json.dumps(event) + "\n")

    def _read_events(self) -> List[Dict[str, Any]]:
        """Read all events from the JSONL file."""
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

    def _empty_summary(self) -> Dict[str, Any]:
        """Return an empty metrics summary."""
        return {
            "period_days": 7,
            "total_requests": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "success_rate": 0.0,
            "avg_generation_time": 0.0,
            "captions_generated": 0,
            "captions_selected": 0,
            "caption_selection_rate": 0.0,
            "feedback_summary": {
                "positive": 0,
                "negative": 0,
                "revision_needed": 0
            },
            "top_context_sources": [],
            "by_platform": {},
            "most_common_triggers": []
        }

    def _compute_summary(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute metrics summary from events."""
        summary = self._empty_summary()

        # Count events by type
        event_types = {}
        for event in events:
            event_type = event.get("event_type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1

        # Compute key metrics
        started = event_types.get("generation_started", 0)
        completed = event_types.get("generation_completed", 0)
        failed = event_types.get("generation_failed", 0)
        selected = event_types.get("caption_selected", 0)
        feedback = event_types.get("caption_feedback", 0)

        summary["total_requests"] = started
        summary["successful_generations"] = completed
        summary["failed_generations"] = failed
        summary["success_rate"] = (
            completed / started if started > 0 else 0.0
        )

        # Average generation time
        gen_times = []
        for event in events:
            if event.get("event_type") == "generation_completed":
                gen_times.append(event.get("duration_seconds", 0))

        summary["avg_generation_time"] = (
            sum(gen_times) / len(gen_times) if gen_times else 0.0
        )

        # Count captions
        captions_generated = sum(
            event.get("captions_count", 0)
            for event in events
            if event.get("event_type") == "generation_completed"
        )
        summary["captions_generated"] = captions_generated
        summary["captions_selected"] = selected
        summary["caption_selection_rate"] = (
            selected / captions_generated if captions_generated > 0 else 0.0
        )

        # Feedback breakdown
        feedback_events = [
            e for e in events if e.get("event_type") == "caption_feedback"
        ]
        for feedback_event in feedback_events:
            ftype = feedback_event.get("feedback_type", "unknown")
            if ftype in summary["feedback_summary"]:
                summary["feedback_summary"][ftype] += 1

        # Top context sources
        context_sources = {}
        for event in events:
            if event.get("event_type") == "generation_completed":
                sources = event.get("context_sources", [])
                for source in sources:
                    context_sources[source] = context_sources.get(source, 0) + 1

        summary["top_context_sources"] = sorted(
            context_sources.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Platform breakdown
        platform_usage = {}
        for event in events:
            if event.get("event_type") == "caption_selected":
                platform = event.get("selected_for_platform", "unknown")
                if platform not in platform_usage:
                    platform_usage[platform] = {"selected": 0, "by_user": {}}
                platform_usage[platform]["selected"] += 1
                user = event.get("selected_by", "unknown")
                platform_usage[platform]["by_user"][user] = (
                    platform_usage[platform]["by_user"].get(user, 0) + 1
                )

        summary["by_platform"] = platform_usage

        # Most common triggers
        triggers = {}
        for event in events:
            if event.get("event_type") == "generation_started":
                trigger = event.get("triggered_by", "unknown")
                triggers[trigger] = triggers.get(trigger, 0) + 1

        summary["most_common_triggers"] = sorted(
            triggers.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return summary
