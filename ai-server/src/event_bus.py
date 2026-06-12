"""Event Bus — central event ingestion and distribution.

Receives events from capability servers, deduplicates, prioritizes,
and distributes to subscribers (Trigger Engine is the primary subscriber).

Architecture reference: docs/architecture.md §6.3
"""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

from aegis_schema.models import Event, EventPriority

# ── Type aliases ──────────────────────────────────────────────

EventHandler = Callable[[Event], None]
EventFilter = Callable[[Event], bool]


@dataclass
class EventBusStats:
    """Runtime statistics for the Event Bus."""
    total_published: int = 0
    total_deduplicated: int = 0
    total_delivered: int = 0
    queue_size: int = 0
    subscriber_count: int = 0


@dataclass
class _Subscription:
    """Internal subscription record."""
    handler: EventHandler
    event_filter: EventFilter | None = None
    subscriber_id: str = ""


class EventBus:
    """In-memory event bus with deduplication and priority queue.

    Thread-safe: no. Single-threaded asyncio usage assumed.

    Features:
    - publish/subscribe pattern
    - Deduplication by dedupe_key within a configurable time window
    - Priority-based ordering (URGENT processed before NORMAL before BACKGROUND)
    - Recent event history for diagnostics
    - Batching support (defer BACKGROUND events)

    Usage:
        bus = EventBus()
        bus.subscribe(lambda e: e.priority == EventPriority.URGENT, my_handler)
        bus.publish(event)
    """

    # Default deduplication window: 30 seconds
    DEFAULT_DEDUP_WINDOW_MS = 30_000

    # Maximum events retained in recent history
    MAX_RECENT_EVENTS = 1000

    # Maximum queued events before warning
    MAX_QUEUE_SIZE = 10_000

    def __init__(self, dedup_window_ms: int = DEFAULT_DEDUP_WINDOW_MS) -> None:
        self._dedup_window_ms = dedup_window_ms

        # Dedup tracking: dedupe_key → timestamp of last occurrence
        self._dedup_tracker: dict[str, float] = {}

        # Priority queues (simple lists — sorted on publish)
        self._urgent_queue: deque[Event] = deque()
        self._normal_queue: deque[Event] = deque()
        self._background_queue: deque[Event] = deque()

        # Recent events ring buffer for diagnostics
        self._recent_events: deque[Event] = deque(maxlen=self.MAX_RECENT_EVENTS)

        # Subscribers
        self._subscriptions: list[_Subscription] = []
        self._sub_counter: int = 0

        # Stats
        self.stats = EventBusStats()

    # ── Publish ──────────────────────────────────────────────

    def publish(self, event: Event) -> bool:
        """Publish an event to the bus.

        Returns True if the event was accepted, False if it was deduplicated.
        """
        self.stats.total_published += 1

        # 1. Dedup check
        if self._is_duplicate(event):
            self.stats.total_deduplicated += 1
            return False

        # 2. Track dedup key
        if event.dedupe_key:
            self._dedup_tracker[event.dedupe_key] = time.monotonic()

        # 3. Enqueue by priority
        self._enqueue(event)

        # 4. Add to recent history
        self._recent_events.append(event)

        # 5. Notify subscribers (filtered)
        self._notify_subscribers(event)

        # 6. Update stats
        self.stats.total_delivered += 1
        self.stats.queue_size = self._queue_size()

        return True

    # ── Subscribe ────────────────────────────────────────────

    def subscribe(
        self,
        handler: EventHandler,
        event_filter: EventFilter | None = None,
    ) -> str:
        """Register a subscriber.

        Args:
            handler: Called for each matching event.
            event_filter: Optional filter. If None, handler receives ALL events.

        Returns:
            A subscriber ID that can be used with unsubscribe().
        """
        self._sub_counter += 1
        sub_id = f"sub_{self._sub_counter}"
        self._subscriptions.append(
            _Subscription(
                handler=handler,
                event_filter=event_filter,
                subscriber_id=sub_id,
            )
        )
        self.stats.subscriber_count = len(self._subscriptions)
        return sub_id

    def unsubscribe(self, subscriber_id: str) -> bool:
        """Remove a subscriber by ID. Returns True if found and removed."""
        for i, sub in enumerate(self._subscriptions):
            if sub.subscriber_id == subscriber_id:
                self._subscriptions.pop(i)
                self.stats.subscriber_count = len(self._subscriptions)
                return True
        return False

    # ── Query ────────────────────────────────────────────────

    def list_recent_events(self, n: int = 50) -> list[Event]:
        """Return the most recent N events."""
        items = list(self._recent_events)
        return items[-n:] if n < len(items) else items

    def drain_urgent(self) -> list[Event]:
        """Drain and return all URGENT events from the queue."""
        return self._drain_queue(self._urgent_queue)

    def drain_normal(self) -> list[Event]:
        """Drain and return all NORMAL events from the queue."""
        return self._drain_queue(self._normal_queue)

    def drain_background(self) -> list[Event]:
        """Drain and return all BACKGROUND events from the queue."""
        return self._drain_queue(self._background_queue)

    def drain_all(self) -> list[Event]:
        """Drain all queued events in priority order."""
        return (
            self.drain_urgent() +
            self.drain_normal() +
            self.drain_background()
        )

    def pending_count(self) -> int:
        """Number of events waiting in queues."""
        return self._queue_size()

    # ── Internal ─────────────────────────────────────────────

    def _is_duplicate(self, event: Event) -> bool:
        """Check if an event is a duplicate based on dedupe_key and time window."""
        if not event.dedupe_key:
            return False

        last_time = self._dedup_tracker.get(event.dedupe_key)
        if last_time is None:
            return False

        elapsed_ms = (time.monotonic() - last_time) * 1000
        return elapsed_ms < self._dedup_window_ms

    def _enqueue(self, event: Event) -> None:
        """Add event to the appropriate priority queue."""
        queue = {
            EventPriority.URGENT: self._urgent_queue,
            EventPriority.NORMAL: self._normal_queue,
            EventPriority.BACKGROUND: self._background_queue,
        }.get(event.priority, self._normal_queue)

        queue.append(event)

        # Safety limit — drop oldest if queue grows too large
        if len(queue) > self.MAX_QUEUE_SIZE:
            queue.popleft()

    def _notify_subscribers(self, event: Event) -> None:
        """Notify all subscribers whose filter matches the event."""
        for sub in self._subscriptions:
            try:
                if sub.event_filter is None or sub.event_filter(event):
                    sub.handler(event)
            except Exception:
                # Subscriber errors must not crash the bus
                pass

    def _queue_size(self) -> int:
        return (
            len(self._urgent_queue) +
            len(self._normal_queue) +
            len(self._background_queue)
        )

    @staticmethod
    def _drain_queue(queue: deque[Event]) -> list[Event]:
        events: list[Event] = []
        while queue:
            events.append(queue.popleft())
        return events
