"""Tests for EventBus — publish, subscribe, dedup, priority queue."""

from __future__ import annotations

import json
import time
from pathlib import Path

from aegis_schema.models import Event, EventPriority, ServerType
from event_bus import EventBus

SAMPLES_DIR = Path(__file__).parent.parent / "samples"


def _make_event(
    event_id: str = "evt-001",
    event_type: str = "pc.screen_changed",
    server_type: ServerType = ServerType.PC,
    priority: EventPriority = EventPriority.NORMAL,
    severity: int = 3,
    dedupe_key: str = "",
) -> Event:
    return Event(
        event_id=event_id,
        event_type=event_type,
        source_server_type=server_type,
        source_server_id="test-server",
        priority=priority,
        severity=severity,
        dedupe_key=dedupe_key,
    )


# ═══════════════════════════════════════════════════════════════
# Basic Publish / Subscribe
# ═══════════════════════════════════════════════════════════════

class TestPublishSubscribe:
    def test_publish_returns_true(self):
        bus = EventBus()
        event = _make_event()
        assert bus.publish(event) is True

    def test_subscriber_receives_event(self):
        bus = EventBus()
        received: list[Event] = []

        bus.subscribe(lambda e: received.append(e))
        bus.publish(_make_event())

        assert len(received) == 1
        assert received[0].event_id == "evt-001"

    def test_filtered_subscriber(self):
        bus = EventBus()
        received: list[Event] = []

        bus.subscribe(
            lambda e: received.append(e),
            event_filter=lambda e: e.priority == EventPriority.URGENT,
        )

        bus.publish(_make_event("evt-1", priority=EventPriority.NORMAL))
        bus.publish(_make_event("evt-2", priority=EventPriority.URGENT))

        assert len(received) == 1
        assert received[0].event_id == "evt-2"

    def test_multiple_subscribers(self):
        bus = EventBus()
        count = {"a": 0, "b": 0}

        bus.subscribe(lambda e: count.__setitem__("a", count["a"] + 1))
        bus.subscribe(lambda e: count.__setitem__("b", count["b"] + 1))
        bus.publish(_make_event())

        assert count["a"] == 1
        assert count["b"] == 1

    def test_unsubscribe(self):
        bus = EventBus()
        received: list[Event] = []

        sub_id = bus.subscribe(lambda e: received.append(e))
        bus.publish(_make_event("evt-1"))
        assert len(received) == 1

        bus.unsubscribe(sub_id)
        bus.publish(_make_event("evt-2"))
        assert len(received) == 1  # still 1

    def test_subscriber_error_does_not_crash_bus(self):
        bus = EventBus()

        def bad_handler(e: Event) -> None:
            raise RuntimeError("subscriber error")

        bus.subscribe(bad_handler)
        # Should not raise
        result = bus.publish(_make_event())
        assert result is True


# ═══════════════════════════════════════════════════════════════
# Deduplication
# ═══════════════════════════════════════════════════════════════

class TestDedup:
    def test_dedupe_blocks_duplicate_within_window(self):
        bus = EventBus(dedup_window_ms=5000)
        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        e1 = _make_event("evt-1", dedupe_key="key-1")
        e2 = _make_event("evt-2", dedupe_key="key-1")  # same dedupe key

        assert bus.publish(e1) is True
        assert bus.publish(e2) is False  # deduplicated
        assert len(received) == 1

    def test_dedupe_allows_after_window(self):
        """After the dedup window expires, the same key is allowed again."""
        bus = EventBus(dedup_window_ms=1)  # 1ms window
        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        e1 = _make_event("evt-1", dedupe_key="key-1")
        assert bus.publish(e1) is True

        time.sleep(0.01)  # wait beyond 1ms window

        e2 = _make_event("evt-2", dedupe_key="key-1")
        assert bus.publish(e2) is True
        assert len(received) == 2

    def test_no_dedupe_key_allows_all(self):
        bus = EventBus()
        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        bus.publish(_make_event("evt-1", dedupe_key=""))
        bus.publish(_make_event("evt-2", dedupe_key=""))
        bus.publish(_make_event("evt-3", dedupe_key=""))

        assert len(received) == 3

    def test_different_keys_not_deduped(self):
        bus = EventBus()
        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        bus.publish(_make_event("evt-1", dedupe_key="key-a"))
        bus.publish(_make_event("evt-2", dedupe_key="key-b"))

        assert len(received) == 2


# ═══════════════════════════════════════════════════════════════
# Priority Queue
# ═══════════════════════════════════════════════════════════════

class TestPriorityQueue:
    def test_drain_returns_in_priority_order(self):
        bus = EventBus()

        bus.publish(_make_event("bg", priority=EventPriority.BACKGROUND))
        bus.publish(_make_event("urg", priority=EventPriority.URGENT))
        bus.publish(_make_event("norm", priority=EventPriority.NORMAL))

        events = bus.drain_all()
        assert events[0].event_id == "urg"
        assert events[1].event_id == "norm"
        assert events[2].event_id == "bg"

    def test_drain_urgent_only(self):
        bus = EventBus()
        bus.publish(_make_event("n1", priority=EventPriority.NORMAL))
        bus.publish(_make_event("u1", priority=EventPriority.URGENT))
        bus.publish(_make_event("u2", priority=EventPriority.URGENT))

        urgent = bus.drain_urgent()
        assert len(urgent) == 2
        remaining = bus.drain_all()
        assert len(remaining) == 1

    def test_drain_clears_queue(self):
        bus = EventBus()
        bus.publish(_make_event("e1"))
        bus.drain_all()
        assert bus.pending_count() == 0

    def test_queue_size_limit(self):
        """Very large number of events should not crash — old ones get dropped."""
        bus = EventBus()
        bus.subscribe(lambda e: None)

        # Publish beyond max queue size
        for i in range(15000):
            bus.publish(_make_event(f"evt-{i}", priority=EventPriority.NORMAL))

        # Should not crash, oldest events dropped
        assert bus.pending_count() <= 10000


# ═══════════════════════════════════════════════════════════════
# Recent Events History
# ═══════════════════════════════════════════════════════════════

class TestRecentEvents:
    def test_recent_events_returns_published_events(self):
        bus = EventBus()
        bus.publish(_make_event("e1"))
        bus.publish(_make_event("e2"))
        recent = bus.list_recent_events(10)
        assert len(recent) == 2
        assert recent[0].event_id == "e1"
        assert recent[1].event_id == "e2"

    def test_recent_events_respects_limit(self):
        bus = EventBus()
        for i in range(10):
            bus.publish(_make_event(f"evt-{i}"))
        recent = bus.list_recent_events(3)
        assert len(recent) == 3  # last 3


# ═══════════════════════════════════════════════════════════════
# Stats
# ═══════════════════════════════════════════════════════════════

class TestStats:
    def test_stats_track_published(self):
        bus = EventBus()
        bus.publish(_make_event("e1"))
        bus.publish(_make_event("e2", dedupe_key="k1"))
        bus.publish(_make_event("e3", dedupe_key="k1"))  # deduped

        assert bus.stats.total_published == 3
        assert bus.stats.total_deduplicated == 1
        assert bus.stats.total_delivered == 2

    def test_stats_subscriber_count(self):
        bus = EventBus()
        assert bus.stats.subscriber_count == 0
        bus.subscribe(lambda e: None)
        bus.subscribe(lambda e: None)
        assert bus.stats.subscriber_count == 2


# ═══════════════════════════════════════════════════════════════
# Sample Events Integration
# ═══════════════════════════════════════════════════════════════

class TestSampleEvents:
    def test_sample_events_load_and_publish(self):
        """All sample events should be valid and publishable."""
        with open(SAMPLES_DIR / "events.json", encoding="utf-8") as f:
            data = json.load(f)

        bus = EventBus()
        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        for item in data:
            event = Event.model_validate(item)
            bus.publish(event)

        assert len(received) == len(data)
        assert bus.stats.total_delivered == len(data)

    def test_sample_events_have_varied_severity(self):
        with open(SAMPLES_DIR / "events.json", encoding="utf-8") as f:
            data = json.load(f)

        severities = {item["severity"] for item in data}
        # Should have a range of severities
        assert min(severities) <= 3
        assert max(severities) >= 8
