"""Journal store tests."""

from __future__ import annotations

import json

from aegis_ai.journal.projector import JournalProjector, journal_event_for_ui
from aegis_ai.event.event_manager import EventManager
from aegis_ai.journal.journal_store import JournalStore
from event_bus import EventBus


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


def test_journal_reload_recovers_latest_sequence_from_tail(tmp_path, monkeypatch) -> None:
    import aegis_ai.journal.journal_store as journal_store

    monkeypatch.setattr(journal_store, "_TAIL_READ_MAX_BYTES", 1024)
    store = JournalStore(data_dir=str(tmp_path))
    for index in range(40):
        store.append(
            event_type="task.updated",
            aggregate_type="task",
            aggregate_id="task_tail",
            payload={"index": index, "blob": "x" * 80},
        )

    # Corrupt the final line to ensure tail recovery walks backward to the last valid JSON row.
    path = tmp_path / "journal" / "events.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write("{bad json\n")

    reloaded = JournalStore(data_dir=str(tmp_path))
    entry = reloaded.append(
        event_type="task.completed",
        aggregate_type="task",
        aggregate_id="task_tail",
        payload={"done": True},
    )

    assert entry.sequence == 41
    rows = path.read_text(encoding="utf-8").strip().splitlines()
    assert json.loads(rows[-1])["sequence"] == 41


def test_journal_projector_preserves_relation_keys_when_correlation_missing(tmp_path) -> None:
    event_manager = EventManager(
        event_bus=EventBus(dedup_window_ms=60_000),
        data_dir=str(tmp_path / "events"),
        persist_important=True,
    )
    projector = JournalProjector(event_manager=event_manager)

    projector.project(
        {
            "sequence": 7,
            "event_type": "task.updated",
            "timestamp_ms": 123,
            "aggregate_id": "task-xyz",
            "correlation_id": "",
            "payload": {"task_id": "task-xyz", "status": "running"},
        }
    )

    events = event_manager.list_recent(limit=10)["events"]
    assert events
    assert events[-1]["aggregate_id"] == "task-xyz"
    assert events[-1]["correlation_id"] == "task-xyz"
