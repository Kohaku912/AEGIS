"""Event Manager — centralized event management with persistence and replay.

Wraps EventBus as internal implementation. Adds:
- Persistence of important events to JSONL
- Replay from timestamp
- Dead letter queue for failed handlers
- Cursor-based queries
"""

from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Any

from aegis_schema.models import Event, EventPriority, ServerType

from event_bus import EventBus

logger = logging.getLogger("aegis_ai.event.event_manager")

_PERSIST_EVENT_TYPES = {
    "task.created", "task.updated", "task.completed", "task.failed", "task.cancelled",
    "approval.created", "approval.approved", "approval.rejected", "approval.expired",
    "approval.cancelled", "approval.executing", "approval.executed", "approval.failed",
    "memory.sleep.started", "memory.sleep.completed",
    "status.changed",
    "notification.sent",
    "tool.executed",
    "verification.completed",
    "llm.request.completed",
    "android.connected",
    "android.disconnected",
    "android.heartbeat",
    "android.permission.changed",
    "android.notification.posted",
    "android.notification_received",
    "android.foreground_app.changed",
    "android.user_activity.changed",
    "android.presence.changed",
    "android.semantic_layout.changed",
    "android.current_app_changed",
    "android.device_state",
    "android.approval.decided",
    "pc.user_activity.snapshot",
    "browser.user_activity.changed",
    "capability.override.updated",
    "capability.override.reset",
    "capability.effective_policy.changed",
    "room.presence.changed",
    "webhook.presence.changed",
    "self_call",
    "social.webhook.received",
    "social.email.received",
    "social.inbox.received",
    "social.inbox.triaged",
    "social.inbox.failed",
    "social.reply.proposed",
    "hook.matched",
    "commitment.due",
}


class EventManager:
    """Centralized event management with persistence and replay.

    Wraps EventBus for pub/sub. Adds persistence, replay,
    dead letter queue, and cursor-based queries.

    Parameters
    ----------
    event_bus:
        The underlying EventBus instance.
    data_dir:
        Directory for persistence files.
    persist_important:
        Whether to persist important events to JSONL.
    """

    def __init__(
        self,
        event_bus: EventBus,
        data_dir: str = "data",
        persist_important: bool = True,
        journal_store: Any = None,
        journal_projector: Any = None,
    ) -> None:
        self._bus = event_bus
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._persist_path = self._data_dir / "events.jsonl"
        self._dead_letter_path = self._data_dir / "dead_letters.jsonl"
        self._persist_important = persist_important
        self._journal = journal_store
        self._journal_projector = journal_projector

        self._persisted_events: list[dict[str, Any]] = []
        self._dead_letters: deque[dict[str, Any]] = deque(maxlen=500)
        self._processed: dict[str, set[str]] = {}  # event_id -> set of processor IDs
        self._lock = threading.Lock()

        self._bus.set_dead_letter_handler(self.record_dead_letter)
        self._load_persisted()

    # ── Publish / Subscribe (delegate to EventBus) ────────────

    def publish(self, event: Event) -> bool:
        """Publish an event. Persists important events and appends to journal."""
        result = self._bus.publish(event)
        if result:
            if self._journal is not None:
                try:
                    payload = self._event_payload(event)
                    entry = self._journal.append(
                        event_type=event.event_type,
                        aggregate_type=self._aggregate_type(event.event_type),
                        aggregate_id=str(payload.get("task_id") or payload.get("approval_id") or event.event_id),
                        payload=payload,
                        correlation_id=event.correlation_id or event.event_id,
                    )
                    if self._journal_projector is not None:
                        self._journal_projector.project(entry.model_dump())
                except Exception:
                    logger.debug("Journal append failed", exc_info=True)
            if self._persist_important and self._should_persist(event):
                self._persist_event(event)
        return result

    def publish_event(self, event_type: str, *, source: str, payload: dict[str, Any]) -> bool:
        """Legacy publisher helper using canonical Event fields."""
        from aegis_ai.event.helpers import build_event

        return self.publish(build_event(event_type, source=source, payload=payload))

    def record_summary(self, event: Event, *, full_payload: dict[str, Any] | None = None) -> None:
        """Record a UI summary without re-publishing to the bus."""
        self._persist_event(event, full_payload=full_payload)

    def subscribe(self, handler, event_filter=None) -> str:
        """Subscribe to events. Returns subscriber ID."""
        return self._bus.subscribe(handler, event_filter)

    def unsubscribe(self, subscriber_id: str) -> bool:
        """Unsubscribe by ID."""
        return self._bus.unsubscribe(subscriber_id)

    # ── Query ─────────────────────────────────────────────────

    def list_recent(self, limit: int = 50, cursor: str | None = None) -> dict[str, Any]:
        """List recent events with cursor pagination.

        Returns: {events: [...], next_cursor: str | None}
        """
        with self._lock:
            events = list(self._persisted_events)

        if cursor:
            idx = 0
            for i, e in enumerate(events):
                if e.get("event_id") == cursor:
                    idx = i + 1
                    break
            events = events[idx:]

        page = events[:limit]
        next_cursor = page[-1].get("event_id") if len(page) == limit and page else None
        return {"events": page, "next_cursor": next_cursor}

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        """Get a single event by ID."""
        with self._lock:
            for e in self._persisted_events:
                if e.get("event_id") == event_id:
                    return e
        return None

    def cleanup_old_events(self, max_age_hours: int = 24) -> int:
        """Remove events older than max_age_hours. Returns number of removed events."""
        cutoff_ms = int((time.time() - max_age_hours * 3600) * 1000)
        with self._lock:
            before = len(self._persisted_events)
            self._persisted_events = [
                e for e in self._persisted_events
                if e.get("timestamp", 0) >= cutoff_ms
            ]
            removed = before - len(self._persisted_events)
        if removed > 0:
            self._rewrite_persisted()
        return removed

    def _rewrite_persisted(self) -> None:
        """Rewrite the persisted events file with current events."""
        try:
            with open(self._persist_path, "w", encoding="utf-8") as f:
                for entry in self._persisted_events:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            logger.debug("Failed to rewrite persisted events", exc_info=True)

    def replay(self, from_timestamp_ms: int) -> list[dict[str, Any]]:
        """Replay events from a timestamp."""
        with self._lock:
            return [e for e in self._persisted_events if e.get("timestamp", 0) >= from_timestamp_ms]

    def list_dead_letters(self, limit: int = 50) -> list[dict[str, Any]]:
        """List dead letter events."""
        with self._lock:
            return list(self._dead_letters)[-limit:]

    def mark_processed(self, event_id: str, processor_id: str) -> None:
        """Mark an event as processed by a specific processor."""
        with self._lock:
            if event_id not in self._processed:
                self._processed[event_id] = set()
            self._processed[event_id].add(processor_id)

    def is_processed(self, event_id: str, processor_id: str) -> bool:
        """Check if an event was processed by a specific processor."""
        with self._lock:
            return processor_id in self._processed.get(event_id, set())

    # ── Delegate to EventBus ──────────────────────────────────

    def list_recent_events(self, n: int = 50) -> list[Event]:
        """Delegate to EventBus.list_recent_events()."""
        return self._bus.list_recent_events(n)

    def pending_count(self) -> int:
        """Delegate to EventBus.pending_count()."""
        return self._bus.pending_count()

    def drain_all(self) -> list[Event]:
        """Delegate to EventBus.drain_all()."""
        return self._bus.drain_all()

    @property
    def stats(self):
        """Delegate to EventBus.stats."""
        return self._bus.stats

    # ── Dead letter ────────────────────────────────────────────

    def record_dead_letter(self, event: Event, handler_id: str, error: str) -> None:
        """Record a failed handler delivery as dead letter."""
        entry = {
            "event_id": getattr(event, "event_id", str(uuid.uuid4().hex[:10])),
            "event_type": getattr(event, "event_type", "unknown"),
            "handler_id": handler_id,
            "error": error,
            "timestamp": int(time.time() * 1000),
            "source_server_id": getattr(event, "source_server_id", ""),
            "payload": self._event_payload(event),
        }
        with self._lock:
            self._dead_letters.append(entry)
        self._persist_dead_letter(entry)
        logger.warning("Dead letter: event=%s handler=%s error=%s", entry["event_id"], handler_id, error)

    # ── Internal ──────────────────────────────────────────────

    def _should_persist(self, event: Event) -> bool:
        return event.event_type in _PERSIST_EVENT_TYPES

    @staticmethod
    def _aggregate_type(event_type: str) -> str:
        if event_type.startswith("task."):
            return "task"
        if event_type.startswith("approval."):
            return "approval"
        return "event"

    @staticmethod
    def _event_payload(event: Event) -> dict[str, Any]:
        raw = getattr(event, "payload_json", "") or "{}"
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {"value": parsed}
        except Exception:
            return {"raw": str(raw)[:2000]}

    def _persist_event(self, event: Event, *, full_payload: dict[str, Any] | None = None) -> None:
        payload = full_payload if full_payload is not None else self._event_payload(event)
        entry = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "source_server_id": event.source_server_id,
            "source_server_type": event.source_server_type.name,
            "timestamp": event.timestamp_ms,
            "priority": event.priority.name if hasattr(event.priority, "name") else "NORMAL",
            "severity": event.severity,
            "correlation_id": event.correlation_id,
            "payload_summary": str(payload)[:300],
            "payload": payload,
        }
        with self._lock:
            self._persisted_events.append(entry)
        try:
            with open(self._persist_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            logger.debug("Failed to persist event", exc_info=True)

    def _persist_dead_letter(self, entry: dict[str, Any]) -> None:
        try:
            with open(self._dead_letter_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            logger.debug("Failed to persist dead letter", exc_info=True)

    def _load_persisted(self, max_events: int = 500) -> None:
        if not self._persist_path.exists():
            return
        try:
            with open(self._persist_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self._persisted_events.append(json.loads(line))
            if len(self._persisted_events) > max_events:
                self._persisted_events = self._persisted_events[-max_events:]
            self.cleanup_old_events(max_age_hours=24)
        except Exception:
            logger.debug("Failed to load persisted events", exc_info=True)
