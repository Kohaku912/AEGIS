"""Journal store tests."""

from __future__ import annotations

from aegis_ai.journal.journal_store import JournalStore
from aegis_ai.journal.projector import journal_event_for_ui


def test_journal_append_and_query_by_aggregate(tmp_path) -> None:
    store = JournalStore(data_dir=str(tmp_path))
    store.append(
        event_type="task.created",
        aggregate_type="task",
        aggregate_id="task_123",
        payload={"title": "demo"},
        correlation_id="corr_1",
    )
    store.append(
        event_type="task.updated",
        aggregate_type="task",
        aggregate_id="task_123",
        payload={"status": "running"},
        correlation_id="corr_1",
    )
    rows = store.list_for_aggregate("task_123")
    assert len(rows) == 2
    assert rows[0]["sequence"] == 1
    assert rows[1]["event_type"] == "task.updated"
    store.save_offset("projector", 2)
    assert store.load_offset("projector") == 2
    recent = store.list_recent(limit=1)
    assert len(recent) == 1
    assert recent[0]["event_type"] == "task.updated"
    ui = journal_event_for_ui(recent[0])
    assert ui["event_type"] == "task.updated"
    assert ui["target"] == "task_123"


def test_journal_append_attaches_otel_trace_ids(tmp_path) -> None:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider

    previous = trace.get_tracer_provider()
    trace.set_tracer_provider(TracerProvider())
    try:
        store = JournalStore(data_dir=str(tmp_path))
        entry = store.append(
            event_type="task.created",
            aggregate_type="task",
            aggregate_id="task_otel",
            payload={"title": "traced"},
        )
        meta = entry.model_dump()["metadata"]
        assert len(str(meta.get("otel_trace_id") or "")) == 32
        assert len(str(meta.get("otel_span_id") or "")) == 16
        ui = journal_event_for_ui(entry.model_dump())
        assert ui["trace_id"] == meta["otel_trace_id"]
        assert ui["span_id"] == meta["otel_span_id"]
    finally:
        trace.set_tracer_provider(previous)
