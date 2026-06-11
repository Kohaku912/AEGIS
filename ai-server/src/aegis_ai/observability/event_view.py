"""Event View — provides event history and stats from EventBus."""

from __future__ import annotations

import time
from typing import Any


class EventView:
    """Read-only view of EventBus for dashboard display."""

    def __init__(self, event_bus: Any = None, trigger_engine: Any = None) -> None:
        self._bus = event_bus
        self._engine = trigger_engine

    def get_recent_events(self, n: int = 50) -> list[dict[str, Any]]:
        """Get recent events as dicts."""
        if not self._bus:
            return []

        events = self._bus.list_recent_events(n)
        result = []
        for e in events:
            result.append({
                "event_id": e.event_id,
                "event_type": e.event_type,
                "source_server_type": e.source_server_type.name,
                "source_server_id": e.source_server_id,
                "severity": e.severity,
                "priority": e.priority.name,
                "dedupe_key": e.dedupe_key,
                "timestamp_ms": e.timestamp_ms,
                "age_seconds": (int(time.time() * 1000) - e.timestamp_ms) // 1000 if e.timestamp_ms else -1,
            })
        return result

    def get_stats(self) -> dict[str, Any]:
        """Get EventBus statistics."""
        if not self._bus:
            return {}
        stats = self._bus.stats
        return {
            "total_published": stats.total_published,
            "total_deduplicated": stats.total_deduplicated,
            "total_delivered": stats.total_delivered,
            "queue_size": stats.queue_size,
            "subscriber_count": stats.subscriber_count,
        }

    def get_trigger_stats(self) -> dict[str, Any]:
        """Get TriggerEngine statistics."""
        if not self._engine:
            return {}
        stats = self._engine.stats
        return {
            "events_received": stats.events_received,
            "rules_matched": stats.rules_matched,
            "tasks_generated": stats.tasks_generated,
            "suppressed_by_cooldown": stats.activations_suppressed_by_cooldown,
            "suppressed_by_no_match": stats.activations_suppressed_by_no_match,
        }

    def get_pending_tasks(self) -> list[dict[str, Any]]:
        """Get pending tasks from TriggerEngine."""
        if not self._engine:
            return []
        tasks = self._engine.drain_tasks()
        # Re-add them since drain clears the queue
        result = []
        for t in tasks:
            result.append({
                "task_id": t.task_id,
                "action_type": t.action_type.name,
                "triggered_by_event_type": t.triggered_by_event_type,
                "triggered_by_rule_id": t.triggered_by_rule_id,
                "priority": t.priority.name,
                "created_at_ms": t.created_at_ms,
                "context_summary": t.context_summary,
            })
        return result
