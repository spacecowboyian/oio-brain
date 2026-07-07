#!/usr/bin/env python3
"""
Event-linking resolver: attaches media/transcripts to car timeline events.

Matching rules precedence (highest confidence wins):
  1. manual_override   — user correction, always wins (confidence = 1.0)
  2. explicit_mention  — transcript/filename explicitly names car+event
  3. date_proximity    — media capture date matches event date
  4. visual_hint       — AI-identified car from image analysis

Conflict handling:
  - Top candidate confidence >= AUTO_LINK_THRESHOLD (0.80) AND gap from
    next-best >= CONFLICT_GAP (0.10) → auto-link
  - Otherwise → review queue (never silently auto-linked)

Overrides:
  - Call apply_override() to correct a link
  - Prior active record becomes inactive; history is preserved
  - Audit log is append-only (JSONL)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AUTO_LINK_THRESHOLD = 0.80
CONFLICT_GAP = 0.10
DATE_EXACT_BOOST = 0.30
DATE_NEAR_BOOST = 0.15   # within DATE_NEAR_DAYS
DATE_NEAR_DAYS = 3
EXPLICIT_MENTION_BOOST = 0.50
VISUAL_HINT_BOOST = 0.15
FILENAME_HINT_BOOST = 0.10

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_LINKAGE_ROOT = REPO_ROOT / "data" / "linkage"
DEFAULT_AUDIT_LOG = DEFAULT_LINKAGE_ROOT / "audit-log.jsonl"
DEFAULT_INDEX = DEFAULT_LINKAGE_ROOT / "index.json"
DEFAULT_REVIEW_QUEUE = DEFAULT_LINKAGE_ROOT / "review-queue.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _run_id() -> str:
    return "RES-" + uuid.uuid4().hex[:8].upper()


def _link_id(media_id: str, event_id: str) -> str:
    raw = f"{media_id}:{event_id}"
    return "LNK-" + hashlib.sha256(raw.encode()).hexdigest()[:12].upper()


def _queue_id(media_id: str) -> str:
    raw = f"queue:{media_id}:{_iso_now()}"
    return "RVW-" + hashlib.sha256(raw.encode()).hexdigest()[:12].upper()


def _parse_date(value: str) -> Optional[date]:
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(value[:19], fmt[:len(value[:19])]).date()
        except ValueError:
            pass
    return None


def _date_diff_days(a: str, b: str) -> Optional[int]:
    da, db = _parse_date(a), _parse_date(b)
    if da is None or db is None:
        return None
    return abs((da - db).days)


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def _load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _append_audit(entry: Dict[str, Any], audit_log: Path) -> None:
    audit_log.parent.mkdir(parents=True, exist_ok=True)
    with audit_log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")


# ---------------------------------------------------------------------------
# Timeline event loader (parses car Maintenance-Log.md files)
# ---------------------------------------------------------------------------

_DATE_HEADING_RE = re.compile(
    r"^##\s+(\d{4}-\d{2}-\d{2})\s*[—–-]\s*(.+)$", re.MULTILINE
)


def _car_slug_from_path(path: Path) -> str:
    """Derive car slug from directory name (e.g. 'mr2-goblin')."""
    return path.parent.name


# ---------------------------------------------------------------------------
# Adapter: convert JS normalizer output (OUT-285) to resolver input
# ---------------------------------------------------------------------------

def adapt_normalizer_output(
    js_result: Dict[str, Any],
    media_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convert the output of the JS normalizer (dev/pipeline/normalizer.js) into
    the format expected by this resolver.

    JS normalizer uses camelCase and `carId` / `date` fields; resolver expects
    snake_case and `car_slug` / `event_date`.

    The `media_id` is not produced by the normalizer — callers should set a
    stable identifier (e.g. SHA256 of the file path).
    """
    if media_id is None:
        raw_path = str(js_result.get("mediaPath", js_result.get("media_path", "")))
        media_id = "MED-" + hashlib.sha256(raw_path.encode()).hexdigest()[:12].upper()

    # Map signal types from JS to resolver conventions
    _signal_map = {
        "filename_match": "filename_hint",
        "transcript_mention": "explicit_mention",
        "exif_datetime": "exif",
        "file_mtime": "file_mtime",
        "iso_date_in_transcript": "exif",
        "month_day_in_transcript": "exif",
    }

    car_candidates: List[Dict[str, Any]] = []
    for cc in js_result.get("carCandidates", js_result.get("car_candidates", [])):
        car_id = cc.get("carId") or cc.get("car_slug") or cc.get("car_id", "")
        signals = cc.get("signals", [])
        # Determine dominant signal type
        sig_types = [_signal_map.get(s.get("type", ""), s.get("type", "")) for s in signals]
        # explicit_mention wins if present
        if "explicit_mention" in sig_types:
            sig_type = "explicit_mention"
        elif "visual_hint" in sig_types:
            sig_type = "visual_hint"
        elif "filename_hint" in sig_types:
            sig_type = "filename_hint"
        else:
            sig_type = sig_types[0] if sig_types else "unknown"

        car_candidates.append({
            "car_slug": car_id,
            "confidence": float(cc.get("confidence", 0.0)),
            "signal_type": sig_type,
            "signal_value": str(signals[0].get("pattern") or signals[0].get("sentence", "")) if signals else "",
        })

    date_candidates: List[Dict[str, Any]] = []
    for dc in js_result.get("dateCandidates", js_result.get("date_candidates", [])):
        raw_date = dc.get("date") or dc.get("event_date", "")
        signals = dc.get("signals", [])
        sig_type = _signal_map.get(
            signals[0].get("type", "") if signals else "",
            "unknown",
        )
        date_candidates.append({
            "event_date": raw_date,
            "confidence": float(dc.get("confidence", 0.0)),
            "signal_type": sig_type,
        })

    return {
        "media_id": media_id,
        "media_type": js_result.get("mediaType") or js_result.get("media_type", "unknown"),
        "media_path": js_result.get("mediaPath") or js_result.get("media_path", ""),
        "captured_at": None,
        "car_candidates": car_candidates,
        "date_candidates": date_candidates,
    }


def load_timeline_events_from_repo(
    cars_root: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Parse Maintenance-Log.md files from cars/{driver}/{car}/Maintenance-Log.md
    and return a list of structured timeline events.

    Each event has: event_id, event_date, car_slug, title, source_file.
    """
    if cars_root is None:
        # Try brain/cars first (new layout), fall back to cars/ (legacy)
        brain_cars = REPO_ROOT / "brain" / "cars"
        cars_root = brain_cars if brain_cars.exists() else REPO_ROOT / "cars"

    events: List[Dict[str, Any]] = []
    if not cars_root.exists():
        return events

    for log_file in sorted(cars_root.rglob("Maintenance-Log.md")):
        car_slug = _car_slug_from_path(log_file)
        try:
            content = log_file.read_text(encoding="utf-8")
        except OSError:
            continue

        for match in _DATE_HEADING_RE.finditer(content):
            event_date = match.group(1)
            title = match.group(2).strip()
            # Stable event_id: car + date + title slug
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
            event_id = f"EVT-{event_date}-{car_slug}-{slug}"
            events.append(
                {
                    "event_id": event_id,
                    "event_date": event_date,
                    "car_slug": car_slug,
                    "title": title,
                    "source_file": str(log_file.relative_to(REPO_ROOT)),
                }
            )

    return events


def load_timeline_events_from_file(path: Path) -> List[Dict[str, Any]]:
    """Load a pre-built events list from a JSON file."""
    data = _load_json(path, [])
    if isinstance(data, list):
        return data
    return data.get("events", [])


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _score_candidate(
    car_candidate: Dict[str, Any],
    event: Dict[str, Any],
    date_candidates: List[Dict[str, Any]],
    media_captured_at: Optional[str],
) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Compute a final confidence score for (car_candidate, event) pair.

    Returns (score, fired_signals).
    """
    base = float(car_candidate.get("confidence", 0.0))
    signals: List[Dict[str, Any]] = []

    signal_type = car_candidate.get("signal_type", "")

    if signal_type == "explicit_mention":
        base += EXPLICIT_MENTION_BOOST
        signals.append({"type": "explicit_mention", "boost": EXPLICIT_MENTION_BOOST})
    elif signal_type == "visual_hint":
        base += VISUAL_HINT_BOOST
        signals.append({"type": "visual_hint", "boost": VISUAL_HINT_BOOST})
    elif signal_type == "filename_hint":
        base += FILENAME_HINT_BOOST
        signals.append({"type": "filename_hint", "boost": FILENAME_HINT_BOOST})

    # Date matching
    event_date = event.get("event_date", "")
    best_date_boost = 0.0
    best_date_signal = None

    # Check date candidates from OUT-285 normalization
    for dc in date_candidates:
        candidate_date = dc.get("event_date", "")
        diff = _date_diff_days(candidate_date, event_date)
        if diff is None:
            continue
        if diff == 0:
            boost = DATE_EXACT_BOOST
        elif diff <= DATE_NEAR_DAYS:
            boost = DATE_NEAR_BOOST
        else:
            continue
        if boost > best_date_boost:
            best_date_boost = boost
            best_date_signal = {
                "type": "date_proximity",
                "boost": boost,
                "diff_days": diff,
                "signal_type": dc.get("signal_type", ""),
            }

    # Also check media captured_at against event date
    if media_captured_at and event_date:
        diff = _date_diff_days(media_captured_at, event_date)
        if diff is not None:
            if diff == 0:
                boost = DATE_EXACT_BOOST
            elif diff <= DATE_NEAR_DAYS:
                boost = DATE_NEAR_BOOST
            else:
                boost = 0.0
            if boost > best_date_boost:
                best_date_boost = boost
                best_date_signal = {
                    "type": "date_proximity",
                    "boost": boost,
                    "diff_days": diff,
                    "signal_type": "captured_at",
                }

    if best_date_signal:
        base += best_date_boost
        signals.append(best_date_signal)

    # Return raw score (caller caps at record time so gap comparison works)
    return base, signals


# ---------------------------------------------------------------------------
# Core resolver
# ---------------------------------------------------------------------------

def resolve_media(
    media_candidate: Dict[str, Any],
    timeline_events: List[Dict[str, Any]],
    run_id: str,
    linkage_root: Path = DEFAULT_LINKAGE_ROOT,
    audit_log: Path = DEFAULT_AUDIT_LOG,
) -> Dict[str, Any]:
    """
    Resolve a single media candidate to a timeline event.

    Returns a result dict with:
      - status: "auto_linked" | "review_queued"
      - link_id or queue_id
      - confidence, event_id, signals (for auto_linked)
      - candidates, reason (for review_queued)
    """
    media_id = media_candidate["media_id"]
    car_candidates = media_candidate.get("car_candidates", [])
    date_candidates = media_candidate.get("date_candidates", [])
    captured_at = media_candidate.get("captured_at")

    # Check for existing manual override
    index = _load_json(linkage_root / "index.json", {"version": 1, "links": {}})
    existing = index.get("links", {}).get(media_id)
    if existing and existing.get("link_quality") == "manually_overridden" and existing.get("is_active"):
        return {
            "status": "skipped_override",
            "media_id": media_id,
            "link_id": existing["link_id"],
            "message": "Manual override in place; resolver skipped.",
        }

    # Score all (car_candidate, event) combinations
    scored: List[Tuple[float, Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]] = []
    for cc in car_candidates:
        car_slug = cc.get("car_slug", "")
        matching_events = [e for e in timeline_events if e.get("car_slug") == car_slug]
        for event in matching_events:
            score, signals = _score_candidate(cc, event, date_candidates, captured_at)
            scored.append((score, cc, event, signals))

    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        reason = "no_match"
        result = _enqueue_review(
            media_candidate=media_candidate,
            candidates=[],
            reason=reason,
            run_id=run_id,
            linkage_root=linkage_root,
            audit_log=audit_log,
        )
        return result

    top_score, top_cc, top_event, top_signals = scored[0]
    second_score = scored[1][0] if len(scored) > 1 else 0.0
    gap = top_score - second_score

    if top_score >= AUTO_LINK_THRESHOLD and gap >= CONFLICT_GAP:
        # Auto-link (cap confidence at 1.0 in record)
        result = _write_linkage(
            media_candidate=media_candidate,
            event=top_event,
            confidence=min(top_score, 1.0),
            signals=top_signals,
            run_id=run_id,
            link_quality="auto_linked",
            linkage_root=linkage_root,
            audit_log=audit_log,
        )
        return result

    # Ambiguous → review queue
    reason = "below_threshold" if top_score < AUTO_LINK_THRESHOLD else "equal_confidence"
    top_candidates = [
        {
            "event_id": s[2]["event_id"],
            "event_date": s[2]["event_date"],
            "car_slug": s[1].get("car_slug"),
            "title": s[2]["title"],
            "confidence": round(min(s[0], 1.0), 4),
            "signals": s[3],
        }
        for s in scored[:5]
    ]
    result = _enqueue_review(
        media_candidate=media_candidate,
        candidates=top_candidates,
        reason=reason,
        run_id=run_id,
        linkage_root=linkage_root,
        audit_log=audit_log,
    )
    return result


def _write_linkage(
    media_candidate: Dict[str, Any],
    event: Dict[str, Any],
    confidence: float,
    signals: List[Dict[str, Any]],
    run_id: str,
    link_quality: str,
    linkage_root: Path,
    audit_log: Path,
) -> Dict[str, Any]:
    media_id = media_candidate["media_id"]
    event_id = event["event_id"]
    link_id = _link_id(media_id, event_id)
    now = _iso_now()

    record: Dict[str, Any] = {
        "link_id": link_id,
        "media_id": media_id,
        "media_type": media_candidate.get("media_type"),
        "media_path": media_candidate.get("media_path"),
        "event_id": event_id,
        "event_date": event.get("event_date"),
        "car_slug": event.get("car_slug"),
        "confidence": round(confidence, 4),
        "link_quality": link_quality,
        "signals": signals,
        "resolver_run_id": run_id,
        "created_at": now,
        "is_active": True,
        "history": [],
    }

    record_path = linkage_root / "records" / f"{link_id}.json"
    _save_json(record_path, record)

    index_path = linkage_root / "index.json"
    index = _load_json(index_path, {"version": 1, "links": {}})
    index["links"][media_id] = {
        "link_id": link_id,
        "event_id": event_id,
        "car_slug": event.get("car_slug"),
        "confidence": round(confidence, 4),
        "link_quality": link_quality,
        "is_active": True,
        "updated_at": now,
    }
    index["updated_at"] = now
    _save_json(index_path, index)

    _append_audit(
        {
            "action": "linked",
            "link_id": link_id,
            "media_id": media_id,
            "event_id": event_id,
            "confidence": round(confidence, 4),
            "link_quality": link_quality,
            "run_id": run_id,
            "ts": now,
        },
        audit_log,
    )

    return {
        "status": "auto_linked",
        "link_id": link_id,
        "media_id": media_id,
        "event_id": event_id,
        "car_slug": event.get("car_slug"),
        "event_date": event.get("event_date"),
        "confidence": round(confidence, 4),
        "signals": signals,
        "record_path": str(record_path.relative_to(REPO_ROOT) if record_path.is_relative_to(REPO_ROOT) else record_path),
    }


def _enqueue_review(
    media_candidate: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    reason: str,
    run_id: str,
    linkage_root: Path,
    audit_log: Path,
) -> Dict[str, Any]:
    media_id = media_candidate["media_id"]
    queue_id = _queue_id(media_id)
    now = _iso_now()

    entry: Dict[str, Any] = {
        "queue_id": queue_id,
        "media_id": media_id,
        "media_type": media_candidate.get("media_type"),
        "media_path": media_candidate.get("media_path"),
        "captured_at": media_candidate.get("captured_at"),
        "reason": reason,
        "top_candidates": candidates,
        "resolver_run_id": run_id,
        "created_at": now,
        "resolved": False,
    }

    review_queue_path = linkage_root / "review-queue.json"
    queue_data = _load_json(review_queue_path, {"version": 1, "items": []})
    existing_ids = {i["media_id"] for i in queue_data.get("items", [])}
    if media_id not in existing_ids:
        queue_data.setdefault("items", []).append(entry)
    else:
        queue_data["items"] = [
            entry if i["media_id"] == media_id else i
            for i in queue_data["items"]
        ]
    queue_data["updated_at"] = now
    _save_json(review_queue_path, queue_data)

    _append_audit(
        {
            "action": "review_queued",
            "queue_id": queue_id,
            "media_id": media_id,
            "reason": reason,
            "run_id": run_id,
            "ts": now,
        },
        audit_log,
    )

    return {
        "status": "review_queued",
        "queue_id": queue_id,
        "media_id": media_id,
        "reason": reason,
        "top_candidates": candidates,
    }


# ---------------------------------------------------------------------------
# Override mechanism
# ---------------------------------------------------------------------------

def apply_override(
    media_id: str,
    event_id: str,
    override_note: str = "",
    run_id: Optional[str] = None,
    linkage_root: Path = DEFAULT_LINKAGE_ROOT,
    audit_log: Path = DEFAULT_AUDIT_LOG,
    timeline_events: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Manually override a media→event link.

    - Loads or creates the linkage record for media_id
    - Marks prior record inactive and pushes it to history
    - Creates new active record with link_quality="manually_overridden"
    - Audit log entry written; history preserved
    """
    if run_id is None:
        run_id = _run_id()
    now = _iso_now()

    # Resolve event details
    event: Dict[str, Any] = {"event_id": event_id}
    if timeline_events:
        matched = [e for e in timeline_events if e.get("event_id") == event_id]
        if matched:
            event = matched[0]

    link_id = _link_id(media_id, event_id)
    record_path = linkage_root / "records" / f"{link_id}.json"

    index_path = linkage_root / "index.json"
    review_queue_path = linkage_root / "review-queue.json"

    # Load current active record (may be at a different link_id if event changed)
    index = _load_json(index_path, {"version": 1, "links": {}})
    current_entry = index.get("links", {}).get(media_id)
    prior_record = None
    prior_history: List[Dict[str, Any]] = []
    history_entry = None

    if current_entry and current_entry.get("is_active"):
        prior_link_id = current_entry.get("link_id")
        if prior_link_id:
            prior_path = linkage_root / "records" / f"{prior_link_id}.json"
            prior_record = _load_json(prior_path)
            if prior_record:
                prior_history = prior_record.get("history", [])
                history_entry = {
                    "link_id": prior_record.get("link_id"),
                    "event_id": prior_record.get("event_id"),
                    "confidence": prior_record.get("confidence"),
                    "link_quality": prior_record.get("link_quality"),
                    "deactivated_at": now,
                    "note": "superseded by manual override",
                }
                # Mark old record inactive
                prior_record["is_active"] = False
                prior_record["deactivated_at"] = now
                _save_json(prior_path, prior_record)

    new_record: Dict[str, Any] = {
        "link_id": link_id,
        "media_id": media_id,
        "event_id": event_id,
        "event_date": event.get("event_date"),
        "car_slug": event.get("car_slug"),
        "confidence": 1.0,
        "link_quality": "manually_overridden",
        "signals": [{"type": "manual_override", "note": override_note}],
        "resolver_run_id": run_id,
        "created_at": now,
        "is_active": True,
        "history": ([history_entry] if history_entry else []) + prior_history,
    }

    _save_json(record_path, new_record)

    index["links"][media_id] = {
        "link_id": link_id,
        "event_id": event_id,
        "car_slug": event.get("car_slug"),
        "confidence": 1.0,
        "link_quality": "manually_overridden",
        "is_active": True,
        "updated_at": now,
    }
    index["updated_at"] = now
    _save_json(index_path, index)

    # Remove from review queue if present
    queue_data = _load_json(review_queue_path, {"version": 1, "items": []})
    queue_data["items"] = [
        {**i, "resolved": True, "resolved_at": now, "resolved_link_id": link_id}
        if i["media_id"] == media_id
        else i
        for i in queue_data.get("items", [])
    ]
    queue_data["updated_at"] = now
    _save_json(review_queue_path, queue_data)

    _append_audit(
        {
            "action": "manual_override",
            "link_id": link_id,
            "media_id": media_id,
            "event_id": event_id,
            "override_note": override_note,
            "run_id": run_id,
            "ts": now,
        },
        audit_log,
    )

    return {
        "status": "overridden",
        "link_id": link_id,
        "media_id": media_id,
        "event_id": event_id,
        "car_slug": event.get("car_slug"),
    }


# ---------------------------------------------------------------------------
# Batch resolve
# ---------------------------------------------------------------------------

def resolve_batch(
    media_candidates: List[Dict[str, Any]],
    timeline_events: List[Dict[str, Any]],
    run_id: Optional[str] = None,
    linkage_root: Path = DEFAULT_LINKAGE_ROOT,
    audit_log: Path = DEFAULT_AUDIT_LOG,
) -> Dict[str, Any]:
    """
    Resolve a list of media candidates against a timeline events list.

    Returns summary with per-item results.
    """
    if run_id is None:
        run_id = _run_id()

    results: List[Dict[str, Any]] = []
    counts: Dict[str, int] = {"auto_linked": 0, "review_queued": 0, "skipped_override": 0}

    for mc in media_candidates:
        r = resolve_media(
            media_candidate=mc,
            timeline_events=timeline_events,
            run_id=run_id,
            linkage_root=linkage_root,
            audit_log=audit_log,
        )
        results.append(r)
        status = r.get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1

    return {
        "run_id": run_id,
        "total": len(media_candidates),
        "counts": counts,
        "results": results,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve media candidates to car timeline events"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # resolve
    r = sub.add_parser("resolve", help="Run resolver against a batch of media candidates")
    r.add_argument("--candidates", required=True, help="JSON file with media candidate list (from OUT-285 normalizer)")
    r.add_argument("--events", help="JSON file with timeline events (default: parse from cars/)")
    r.add_argument("--linkage-root", default=str(DEFAULT_LINKAGE_ROOT))
    r.add_argument("--audit-log", default=str(DEFAULT_AUDIT_LOG))

    # override
    o = sub.add_parser("override", help="Manually override a media→event link")
    o.add_argument("--media-id", required=True)
    o.add_argument("--event-id", required=True)
    o.add_argument("--note", default="", help="Reason for override")
    o.add_argument("--events", help="JSON file with timeline events")

    # review-queue
    sub.add_parser("review-queue", help="Print current review queue")

    # load-events
    sub.add_parser("load-events", help="Parse and print timeline events from cars/")

    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    linkage_root = Path(getattr(args, "linkage_root", str(DEFAULT_LINKAGE_ROOT)))
    audit_log = Path(getattr(args, "audit_log", str(DEFAULT_AUDIT_LOG)))

    if args.command == "load-events":
        events = load_timeline_events_from_repo()
        print(json.dumps({"count": len(events), "events": events}, indent=2))
        return 0

    if args.command == "review-queue":
        queue = _load_json(DEFAULT_REVIEW_QUEUE, {"version": 1, "items": []})
        pending = [i for i in queue.get("items", []) if not i.get("resolved")]
        print(json.dumps({"pending": len(pending), "items": pending}, indent=2))
        return 0

    if args.command == "override":
        events_path = getattr(args, "events", None)
        timeline_events = (
            load_timeline_events_from_file(Path(events_path))
            if events_path
            else load_timeline_events_from_repo()
        )
        result = apply_override(
            media_id=args.media_id,
            event_id=args.event_id,
            override_note=args.note,
            timeline_events=timeline_events,
        )
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "resolve":
        with open(args.candidates, "r", encoding="utf-8") as f:
            raw = json.load(f)
        candidates = raw if isinstance(raw, list) else raw.get("candidates", [])

        events_path = getattr(args, "events", None)
        timeline_events = (
            load_timeline_events_from_file(Path(events_path))
            if events_path
            else load_timeline_events_from_repo()
        )

        summary = resolve_batch(
            media_candidates=candidates,
            timeline_events=timeline_events,
            linkage_root=linkage_root,
            audit_log=audit_log,
        )
        print(json.dumps(summary, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
