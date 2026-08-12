"""Project journal entries into read models."""

from __future__ import annotations

import json
import logging
from typing import Any

from aegis_schema.models import Event, EventPriority, ServerType

logger = logging.getLogger("aegis_ai.journal.projector")


class JournalProjector:
    """Projects full journal events into EventManager summaries and optional stores."""

    def __init__(self, event_manager: Any = None, operation_store: Any = None) -> None:
        self._event_manager = event_manager
        self._operation_store = operation_store

    def project(self, entry: dict[str, Any]) -> None:
        event_type = str(entry.get("event_type") or "")
        payload = entry.get("payload") if isinstance(entry.get("payload"), dict) else {}
        aggregate_id = str(entry.get("aggregate_id") or "")
        if self._event_manager is not None and event_type:
            try:
                summary = Event(
                    event_id=f"journal_{entry.get('sequence', 0)}",
                    event_type=event_type,
                    source_server_type=ServerType.AI,
                    source_server_id="journal",
                    timestamp_ms=int(entry.get("timestamp_ms") or 0),
                    payload_json=json.dumps(payload, ensure_ascii=False),
                    priority=EventPriority.NORMAL,
                    correlation_id=str(entry.get("correlation_id") or aggregate_id),
                )
                # Write UI summary directly (bypass 24h trim on hot path).
                self._event_manager.record_summary(summary, full_payload=payload)
            except Exception:
                logger.debug("Journal -> EventManager projection failed", exc_info=True)
        if self._operation_store is not None and event_type.startswith("task."):
            try:
                if hasattr(self._operation_store, "record_journal_event"):
                    self._operation_store.record_journal_event(entry)
            except Exception:
                logger.debug("Journal -> OperationStore projection failed", exc_info=True)


def journal_event_for_ui(entry: dict[str, Any]) -> dict[str, Any]:
    """Project a journal row into the dashboard Logs table."""
    payload = entry.get("payload") if isinstance(entry.get("payload"), dict) else {}
    metadata = entry.get("metadata") if isinstance(entry.get("metadata"), dict) else {}
    event_type = str(entry.get("event_type") or "event")
    title = str(
        payload.get("title")
        or payload.get("summary")
        or payload.get("safe_title")
        or event_type
    )
    summary = str(
        payload.get("message")
        or payload.get("safe_message")
        or payload.get("summary")
        or payload.get("status")
        or payload.get("result")
        or ""
    )
    target = str(
        payload.get("capability_id")
        or payload.get("server_id")
        or payload.get("target")
        or entry.get("aggregate_id")
        or ""
    )
    trace_id = str(
        metadata.get("otel_trace_id")
        or metadata.get("trace_id")
        or payload.get("trace_id")
        or ""
    )
    return {
        "id": f"journal-{entry.get('sequence', 0)}",
        "sequence": entry.get("sequence", 0),
        "timestamp_ms": entry.get("timestamp_ms", 0),
        "updated_at": entry.get("timestamp_ms", 0),
        "event_type": event_type,
        "aggregate_type": entry.get("aggregate_type", ""),
        "aggregate_id": entry.get("aggregate_id", ""),
        "correlation_id": entry.get("correlation_id", ""),
        "trace_id": trace_id,
        "span_id": str(metadata.get("otel_span_id") or metadata.get("span_id") or ""),
        "title": title,
        "summary": summary,
        "what_happened": title,
        "reason": summary or event_type,
        "status": str(payload.get("status") or payload.get("result") or "recorded"),
        "target": target,
        "kind": event_type,
        "kind_label": str(entry.get("aggregate_type") or "journal"),
        "payload": payload,
        "metadata": metadata,
    }
