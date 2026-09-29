"""Assert Personal Data Core is fed even when EventBus dedupes."""

from __future__ import annotations

from pathlib import Path

from aegis_ai.event.event_manager import EventManager
from aegis_schema.models import Event, EventPriority, ServerType
from event_bus import EventBus


def test_publish_feeds_pdc_even_when_deduped(tmp_path: Path) -> None:
    bus = EventBus(dedup_window_ms=60_000)
    em = EventManager(event_bus=bus, data_dir=str(tmp_path / "events"), persist_important=False)
    seen: list[str] = []

    class FakePdc:
        def ingest_bus_event(self, event: Event) -> dict:
            seen.append(event.event_type)
            return {"ok": True}

    em._personal_data_core = FakePdc()
    event = Event(
        event_id="evt_test1",
        event_type="android.ui.tapped",
        source_server_type=ServerType.ANDROID,
        source_server_id="android-server",
        timestamp_ms=1,
        payload_json="{}",
        priority=EventPriority.NORMAL,
        dedupe_key="android.ui.tapped:device:same",
    )
    assert em.publish(event) is True
    # Second publish with same dedupe key is rejected by the bus...
    event2 = Event(
        event_id="evt_test2",
        event_type="android.ui.tapped",
        source_server_type=ServerType.ANDROID,
        source_server_id="android-server",
        timestamp_ms=2,
        payload_json="{}",
        priority=EventPriority.NORMAL,
        dedupe_key="android.ui.tapped:device:same",
    )
    assert em.publish(event2) is False
    # ...but PDC still receives both.
    assert seen == ["android.ui.tapped", "android.ui.tapped"]


def test_persisted_event_uses_same_relation_keys_as_journal(tmp_path: Path) -> None:
    bus = EventBus(dedup_window_ms=60_000)
    em = EventManager(event_bus=bus, data_dir=str(tmp_path / "events"), persist_important=True)
    event = Event(
        event_id="evt_relation1",
        event_type="task.created",
        source_server_type=ServerType.AI,
        source_server_id="ai-server",
        timestamp_ms=10,
        payload_json='{"task_id":"task-123","title":"demo"}',
        priority=EventPriority.NORMAL,
        correlation_id="",
    )

    assert em.publish(event) is True

    recent = em.list_recent(limit=10)["events"]
    assert recent
    persisted = recent[-1]
    assert persisted["aggregate_id"] == "task-123"
    assert persisted["correlation_id"] == "task-123"


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        test_publish_feeds_pdc_even_when_deduped(Path(td))
    print("ok")
