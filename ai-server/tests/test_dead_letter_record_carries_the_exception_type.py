"""The dead-letter record must name the exception *type*, not only its message.

``EventBus._notify_subscribers`` is the frame that catches a raising subscriber.
On the background L1 route nothing above it reports the failure, so the
dead-letter record is the *only* signal -- and a signal that cannot tell
``KeyError`` from ``ValueError`` is not diagnostic. Before cycle 119 the bus
handed the record ``str(exc)``, so the type was lost and two different failures
left the identical string.

These tests drive a **real** ``EventBus`` (and, for the wiring test, a real
``EventManager``) with a subscriber that raises. The control proves the record
is not a fixed string: two different exception types must leave two different
records.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable

from aegis_schema.models import Event, ServerType


def _make_event(event_type: str = "pc.user_activity.snapshot") -> Event:
    return Event(
        event_id=f"evt_{uuid.uuid4().hex[:8]}",
        event_type=event_type,
        source_server_type=ServerType.PC,
        source_server_id="pc-server",
    )


def _raising(exc: BaseException) -> Callable[[Event], None]:
    def _handler(_event: Event) -> None:
        raise exc

    return _handler


def _record_for(exc: BaseException) -> str:
    """Publish one event to a bus whose only subscriber raises ``exc``."""
    from event_bus import EventBus

    bus = EventBus()
    seen: list[str] = []
    bus.set_dead_letter_handler(lambda _e, _h, err: seen.append(err))
    bus.subscribe(_raising(exc))
    assert bus.publish(_make_event()) is True
    assert len(seen) == 1, seen
    return seen[0]


def test_the_record_carries_the_exception_type() -> None:
    from event_bus import EventBus

    bus = EventBus()
    recorded: list[tuple[Event, str, str]] = []
    bus.set_dead_letter_handler(lambda e, h, err: recorded.append((e, h, err)))
    bus.subscribe(_raising(ValueError("downstream refused")))

    assert bus.publish(_make_event()) is True

    assert len(recorded) == 1, recorded
    _event, handler_id, error = recorded[0]
    assert "ValueError" in error, error
    assert "downstream refused" in error, error
    assert handler_id, "the subscriber id must still be recorded"


def test_two_exception_types_leave_two_different_records() -> None:
    """Control: the recorded text depends on the *type*, so it is not fixed."""
    key = _record_for(KeyError("payload"))
    value = _record_for(ValueError("payload"))

    assert key != value, (key, value)
    assert "KeyError" in key, key
    assert "ValueError" in value, value


def test_a_raising_subscriber_is_logged_loudly_with_a_traceback(caplog) -> None:
    from event_bus import EventBus

    bus = EventBus()
    bus.subscribe(_raising(RuntimeError("kaboom")))

    with caplog.at_level(logging.ERROR, logger="event_bus"):
        bus.publish(_make_event())

    errors = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert errors, caplog.records
    assert "RuntimeError" in errors[0].getMessage(), errors[0].getMessage()
    # ``LogRecord.exc_info`` is ``False`` -- not ``None`` -- when ``exc_info`` is
    # off, so the check must be truthiness; ``is not None`` would pass either way.
    assert errors[0].exc_info, "the traceback must be attached"
    assert errors[0].exc_info[0] is RuntimeError


def test_the_manager_persists_the_type_through_the_bus(tmp_path) -> None:
    """End-to-end: the real wiring (``EventManager`` registers itself on the
    bus) must carry the type into ``list_dead_letters()``."""
    from aegis_ai.event.event_manager import EventManager
    from event_bus import EventBus

    bus = EventBus()
    manager = EventManager(event_bus=bus, data_dir=str(tmp_path))
    bus.subscribe(_raising(KeyError("payload")))

    bus.publish(_make_event())

    dead = manager.list_dead_letters()
    assert len(dead) == 1, dead
    assert "KeyError" in dead[0]["error"], dead[0]["error"]
