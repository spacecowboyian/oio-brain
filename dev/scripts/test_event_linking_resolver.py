#!/usr/bin/env python3
"""Smoke tests for the event-linking resolver."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

# Allow running from any directory
sys.path.insert(0, str(Path(__file__).parent))

from event_linking_resolver import (
    AUTO_LINK_THRESHOLD,
    apply_override,
    load_timeline_events_from_repo,
    resolve_batch,
    resolve_media,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

EVENTS = [
    {
        "event_id": "EVT-2026-03-18-mr2-goblin-quick-rack-recovery",
        "event_date": "2026-03-18",
        "car_slug": "mr2-goblin",
        "title": "Quick Rack Recovery and Installation",
        "source_file": "cars/ian/mr2-goblin/Maintenance-Log.md",
    },
    {
        "event_id": "EVT-2026-03-28-mr2-goblin-diagnostic",
        "event_date": "2026-03-28",
        "car_slug": "mr2-goblin",
        "title": "Follow-Up Diagnostic Findings",
        "source_file": "cars/ian/mr2-goblin/Maintenance-Log.md",
    },
    {
        "event_id": "EVT-2026-03-18-corolla-killer-suspension",
        "event_date": "2026-03-18",
        "car_slug": "corolla-killer",
        "title": "Suspension Adjustment",
        "source_file": "cars/ian/corolla-killer/Maintenance-Log.md",
    },
]


def _clear_candidate(
    car_slug: str = "mr2-goblin",
    signal_type: str = "explicit_mention",
    base_confidence: float = 0.75,
    event_date: str = "2026-03-18",
    captured_at: str = "2026-03-18T10:00:00Z",
) -> dict:
    return {
        "media_id": "MED-TEST-001",
        "media_type": "image",
        "media_path": "photos/Ian/IMG_9991.jpg",
        "captured_at": captured_at,
        "car_candidates": [
            {"car_slug": car_slug, "confidence": base_confidence, "signal_type": signal_type}
        ],
        "date_candidates": [
            {"event_date": event_date, "confidence": 0.9, "signal_type": "exif"}
        ],
    }


def _ambiguous_candidate() -> dict:
    """Equal-confidence candidates for two events."""
    return {
        "media_id": "MED-TEST-AMB",
        "media_type": "image",
        "media_path": "photos/Ian/IMG_ambiguous.jpg",
        "captured_at": "2026-03-18T11:00:00Z",
        "car_candidates": [
            {"car_slug": "mr2-goblin", "confidence": 0.50, "signal_type": "visual_hint"},
            {"car_slug": "corolla-killer", "confidence": 0.49, "signal_type": "visual_hint"},
        ],
        "date_candidates": [
            {"event_date": "2026-03-18", "confidence": 0.6, "signal_type": "file_mtime"}
        ],
    }


def _no_match_candidate() -> dict:
    return {
        "media_id": "MED-TEST-NOMATCH",
        "media_type": "video",
        "media_path": "clips/unknown.mov",
        "captured_at": "2022-01-01T00:00:00Z",
        "car_candidates": [],
        "date_candidates": [],
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_auto_link_explicit_mention(linkage_root: Path, audit_log: Path) -> None:
    """Explicit mention + exact date should auto-link."""
    candidate = _clear_candidate(
        car_slug="mr2-goblin",
        signal_type="explicit_mention",
        base_confidence=0.55,
        event_date="2026-03-18",
        captured_at="2026-03-18T10:00:00Z",
    )
    result = resolve_media(candidate, EVENTS, run_id="RUN-TEST", linkage_root=linkage_root, audit_log=audit_log)
    assert result["status"] == "auto_linked", f"Expected auto_linked, got: {result['status']}"
    assert result["event_id"] == "EVT-2026-03-18-mr2-goblin-quick-rack-recovery"
    assert result["confidence"] >= AUTO_LINK_THRESHOLD
    print("PASS: auto_link_explicit_mention")


def test_review_queue_ambiguous(linkage_root: Path, audit_log: Path) -> None:
    """Equal-confidence candidates → review queue."""
    candidate = _ambiguous_candidate()
    result = resolve_media(candidate, EVENTS, run_id="RUN-TEST", linkage_root=linkage_root, audit_log=audit_log)
    assert result["status"] == "review_queued", f"Expected review_queued, got: {result['status']}"
    assert result["reason"] in ("below_threshold", "equal_confidence")
    print("PASS: review_queue_ambiguous")


def test_no_match_goes_to_queue(linkage_root: Path, audit_log: Path) -> None:
    """No car candidates → review queue with reason=no_match."""
    candidate = _no_match_candidate()
    result = resolve_media(candidate, EVENTS, run_id="RUN-TEST", linkage_root=linkage_root, audit_log=audit_log)
    assert result["status"] == "review_queued"
    assert result["reason"] == "no_match"
    print("PASS: no_match_goes_to_queue")


def test_manual_override_preserves_history(linkage_root: Path, audit_log: Path) -> None:
    """Override deactivates prior link and preserves history."""
    # First auto-link something
    candidate = _clear_candidate(
        car_slug="mr2-goblin",
        signal_type="explicit_mention",
        base_confidence=0.55,
        event_date="2026-03-18",
        captured_at="2026-03-18T10:00:00Z",
    )
    candidate["media_id"] = "MED-OVERRIDE-TEST"
    resolve_media(candidate, EVENTS, run_id="RUN-A", linkage_root=linkage_root, audit_log=audit_log)

    # Now override to a different event
    override_result = apply_override(
        media_id="MED-OVERRIDE-TEST",
        event_id="EVT-2026-03-28-mr2-goblin-diagnostic",
        override_note="Ian corrected: this was from the March 28 diagnostic session",
        timeline_events=EVENTS,
        linkage_root=linkage_root,
        audit_log=audit_log,
    )
    assert override_result["status"] == "overridden"
    assert override_result["event_id"] == "EVT-2026-03-28-mr2-goblin-diagnostic"

    # Verify the record has history
    from event_linking_resolver import _link_id, _load_json
    link_id = _link_id("MED-OVERRIDE-TEST", "EVT-2026-03-28-mr2-goblin-diagnostic")
    record_path = linkage_root / "records" / f"{link_id}.json"
    record = _load_json(record_path)
    assert record["is_active"] is True
    assert record["link_quality"] == "manually_overridden"
    assert record["confidence"] == 1.0
    assert len(record["history"]) >= 1, "History should have the prior link"
    print("PASS: manual_override_preserves_history")


def test_override_skips_resolver(linkage_root: Path, audit_log: Path) -> None:
    """Once manually overridden, resolver skips re-linking."""
    media_id = "MED-SKIP-TEST"
    # Apply override first
    apply_override(
        media_id=media_id,
        event_id="EVT-2026-03-18-mr2-goblin-quick-rack-recovery",
        override_note="pre-set",
        timeline_events=EVENTS,
        linkage_root=linkage_root,
        audit_log=audit_log,
    )

    candidate = _clear_candidate(
        car_slug="mr2-goblin",
        signal_type="explicit_mention",
        base_confidence=0.55,
    )
    candidate["media_id"] = media_id

    result = resolve_media(candidate, EVENTS, run_id="RUN-SKIP", linkage_root=linkage_root, audit_log=audit_log)
    assert result["status"] == "skipped_override"
    print("PASS: override_skips_resolver")


def test_batch_resolve(linkage_root: Path, audit_log: Path) -> None:
    """Batch resolve processes multiple candidates and returns summary counts."""
    candidates = [
        {**_clear_candidate(signal_type="explicit_mention", base_confidence=0.55), "media_id": "MED-BATCH-1"},
        {**_ambiguous_candidate(), "media_id": "MED-BATCH-AMB"},
        {**_no_match_candidate(), "media_id": "MED-BATCH-NOMATCH"},
    ]
    summary = resolve_batch(candidates, EVENTS, linkage_root=linkage_root, audit_log=audit_log)
    assert summary["total"] == 3
    assert summary["counts"]["auto_linked"] == 1
    assert summary["counts"]["review_queued"] == 2
    print("PASS: batch_resolve")


def test_audit_log_written(linkage_root: Path, audit_log: Path) -> None:
    """Audit log file should be populated."""
    assert audit_log.exists(), "Audit log not created"
    lines = audit_log.read_text().strip().splitlines()
    assert len(lines) > 0, "Audit log is empty"
    first = json.loads(lines[0])
    assert "action" in first and "ts" in first
    print("PASS: audit_log_written")


def test_load_events_from_repo() -> None:
    """load_timeline_events_from_repo should not crash even if cars/ is missing."""
    events = load_timeline_events_from_repo(cars_root=Path("/nonexistent/cars"))
    assert isinstance(events, list)
    print("PASS: load_events_from_repo_graceful")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        linkage_root = Path(td) / "linkage"
        audit_log = linkage_root / "audit-log.jsonl"

        # Patch module-level defaults so helpers inside the module write here
        import event_linking_resolver as elr
        orig_index = elr.DEFAULT_INDEX
        orig_queue = elr.DEFAULT_REVIEW_QUEUE
        elr.DEFAULT_INDEX = linkage_root / "index.json"
        elr.DEFAULT_REVIEW_QUEUE = linkage_root / "review-queue.json"

        try:
            test_auto_link_explicit_mention(linkage_root, audit_log)
            test_review_queue_ambiguous(linkage_root, audit_log)
            test_no_match_goes_to_queue(linkage_root, audit_log)
            test_manual_override_preserves_history(linkage_root, audit_log)
            test_override_skips_resolver(linkage_root, audit_log)
            test_batch_resolve(linkage_root, audit_log)
            test_audit_log_written(linkage_root, audit_log)
            test_load_events_from_repo()
        finally:
            elr.DEFAULT_INDEX = orig_index
            elr.DEFAULT_REVIEW_QUEUE = orig_queue

    print("\nAll tests PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
