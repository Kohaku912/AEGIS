"""Journal store tests."""

from __future__ import annotations

from aegis_ai.journal.journal_store import JournalStore


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
