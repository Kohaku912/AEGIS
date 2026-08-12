"""Helpers for building canonical Event objects from legacy publisher kwargs."""

from __future__ import annotations

import json
import time
import uuid
from typing import Any

from aegis_schema.models import Event, EventPriority, ServerType


def build_event(
    event_type: str,
    *,
    source_server_id: str = "ai-server",
    source: str | None = None,
    source_server_type: ServerType = ServerType.AI,
    payload: dict[str, Any] | None = None,
    payload_json: str | None = None,
    event_id: str | None = None,
    timestamp_ms: int | None = None,
    timestamp: int | None = None,
    priority: EventPriority = EventPriority.NORMAL,
    correlation_id: str = "",
    severity: int = 0,
    dedupe_key: str = "",
    attributes: dict[str, str] | None = None,
) -> Event:
    """Build a canonical Event, accepting legacy ``source`` / ``payload`` / ``timestamp``."""
    server_id = source_server_id or source or "ai-server"
    if payload_json is None:
        payload_json = json.dumps(payload or {}, ensure_ascii=False)
    ts = timestamp_ms if timestamp_ms is not None else (timestamp if timestamp is not None else int(time.time() * 1000))
    return Event(
        event_id=event_id or f"evt_{uuid.uuid4().hex[:12]}",
        event_type=event_type,
        source_server_type=source_server_type,
        source_server_id=server_id,
        timestamp_ms=ts,
        payload_json=payload_json,
        priority=priority,
        correlation_id=correlation_id,
        severity=severity,
        dedupe_key=dedupe_key,
        attributes=attributes or {},
    )


__all__ = ["build_event"]
