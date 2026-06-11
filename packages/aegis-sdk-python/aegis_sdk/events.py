"""Event client — pushes events to AEGIS Core EventBus.

Provides structured event helpers and dedupe_key generation.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any

from aegis_schema.models import Event, EventPriority, ServerType


def make_event(
    event_type: str,
    server_type: ServerType,
    server_id: str,
    payload: dict[str, Any] | None = None,
    severity: int = 3,
    priority: EventPriority = EventPriority.NORMAL,
    dedupe_key: str = "",
    correlation_id: str = "",
) -> Event:
    """Create a structured event.

    Args:
        event_type: Event type (e.g. "weather.forecast_updated").
        server_type: Source server type.
        server_id: Source server ID.
        payload: Event payload as dict.
        severity: Event severity (0-10).
        priority: Event priority.
        dedupe_key: Deduplication key. Auto-generated if empty.
        correlation_id: Optional correlation ID.

    Returns:
        A validated Event object.
    """
    if not dedupe_key:
        dedupe_key = f"{event_type}:{server_id}:{uuid.uuid4().hex[:8]}"

    return Event(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type=event_type,
        source_server_type=server_type,
        source_server_id=server_id,
        timestamp_ms=int(time.time() * 1000),
        payload_json=json.dumps(payload or {}),
        severity=severity,
        priority=priority,
        dedupe_key=dedupe_key,
        correlation_id=correlation_id,
    )


def make_dedupe_key(event_type: str, server_id: str, *parts: str) -> str:
    """Create a deduplication key from event type, server ID, and additional parts.

    Usage:
        key = make_dedupe_key("weather.forecast_updated", "weather-server", "tokyo")
    """
    all_parts = [event_type, server_id] + list(parts)
    return ":".join(all_parts)


class EventClient:
    """Pushes events to AEGIS Core EventBus.

    Usage:
        client = EventClient(
            server_type=ServerType.ROOM,
            server_id="weather-server",
        )
        client.publish(bus, "weather.forecast_updated", {"temp_c": 25})
    """

    def __init__(
        self,
        server_type: ServerType,
        server_id: str,
    ) -> None:
        self._server_type = server_type
        self._server_id = server_id

    def publish(
        self,
        event_bus: Any,
        event_type: str,
        payload: dict[str, Any] | None = None,
        severity: int = 3,
        priority: EventPriority = EventPriority.NORMAL,
        dedupe_key: str = "",
    ) -> bool:
        """Publish an event to the EventBus.

        Returns True if the event was accepted (not deduplicated).
        """
        event = make_event(
            event_type=event_type,
            server_type=self._server_type,
            server_id=self._server_id,
            payload=payload,
            severity=severity,
            priority=priority,
            dedupe_key=dedupe_key,
        )
        return event_bus.publish(event)

    def publish_state_change(
        self,
        event_bus: Any,
        state_type: str,
        old_value: Any,
        new_value: Any,
        severity: int = 3,
    ) -> bool:
        """Publish a state change event with old/new values."""
        payload = {
            "state_type": state_type,
            "old_value": old_value,
            "new_value": new_value,
            "changed_at_ms": int(time.time() * 1000),
        }
        dedupe_key = make_dedupe_key(
            f"{self._server_id}.state_changed",
            self._server_id,
            state_type,
            str(new_value),
        )
        return self.publish(
            event_bus,
            f"{self._server_id}.state_changed",
            payload,
            severity=severity,
            dedupe_key=dedupe_key,
        )
