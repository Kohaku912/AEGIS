"""The gRPC severity is mapped onto the schema's scale (cycle 151's inversion of cycle 150).

Cycle 150 measured that ``grpc_server.py::_event_from_proto`` copied the wire's ``EventSeverity``
(0–5) **verbatim** into ``aegis_schema``'s ``Event.severity`` (0–10), capping every gRPC event at 5
-- "warning" on the 0–10 scale -- so the **5 of 12** default rules needing ``min_severity`` 6–9
(``dev-test-failure`` 7, ``dev-ci-error`` 8, ``android-call`` 6, ``security-alert`` 9,
``high-severity-catchall`` 9) were unreachable from the whole gRPC surface.

This pin fixes the *inverted* claim: the converter now maps the wire's five named levels onto the
schema's anchors (``_PROTO_SEVERITY_TO_SCHEMA``), so a ``CRITICAL`` event arrives as severity **10**
and the security rule *can* fire. It drives the real converter and the real matcher, and keeps the
two controls that make the change honest:

* ``INFO`` is unchanged (1) -- the one producer that stamps a severity
  (``AegisGrpcClient.sendEvent``, always ``INFO``) keeps the value it always had, so this is
  **behaviour-preserving for today's traffic**;
* the *remaining* gate is recorded, not hidden: no producer sends a high severity over the wire, so
  the rules stay starved for a **different** reason (nobody uses the upper half of the scale). That
  is ``DELEGATION.md`` section 4 item 105 branches ②/③.

An out-of-spec wire value (the enum is closed at 5, but the field is a bare int) falls back to
``UNSPECIFIED``, and the fallback is asserted so it cannot drift silently.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from aegis_schema.models import Event, EventPriority
from generated.aegis import common_pb2
from aegis_ai.grpc_server import (
    _PROTO_SEVERITY_TO_SCHEMA,
    _event_from_proto,
    _severity_from_proto,
)
from trigger_engine import create_default_rules

_ROOT = Path(__file__).resolve().parents[2]

#: The Android client that stamps a severity on every event it sends.
_KT_CLIENT = (
    _ROOT
    / "android-server"
    / "app"
    / "src"
    / "main"
    / "java"
    / "com"
    / "aegis"
    / "android"
    / "grpc"
    / "AegisGrpcClient.kt"
)


def _schema_max_severity() -> int:
    from annotated_types import Le

    for constraint in Event.model_fields["severity"].metadata:
        if isinstance(constraint, Le):
            return int(constraint.le)
    raise AssertionError("Event.severity has no Le() upper bound -- this pin's premise is gone")


def _grpc_event(
    event_type: str,
    *,
    severity: int,
    priority: int = common_pb2.EventPriority.EVENT_PRIORITY_NORMAL,
) -> Event:
    proto = common_pb2.Event(
        event_id="evt_probe",
        event_type=event_type,
        source_server_type=common_pb2.SERVER_TYPE_ANDROID,
        source_server_id="android-server",
        severity=severity,
        priority=priority,
    )
    return _event_from_proto(proto)


def _rule(rule_id: str) -> Any:
    for rule in create_default_rules():
        if rule.rule_id == rule_id:
            return rule
    raise AssertionError(f"rule {rule_id!r} is gone -- this pin's record is stale")


def test_the_mapping_covers_every_proto_severity() -> None:
    """Total over the enum: no wire value is left unmapped."""
    enum_values = {
        value
        for name, value in common_pb2.EventSeverity.items()
        if name.startswith("EVENT_SEVERITY")
    }
    assert set(_PROTO_SEVERITY_TO_SCHEMA) == enum_values


def test_the_mapping_is_strictly_increasing_and_spans_the_schema_scale() -> None:
    """Monotone, and its top *is* the schema's top -- that is the whole point of the fix."""
    ordered = [_PROTO_SEVERITY_TO_SCHEMA[k] for k in sorted(_PROTO_SEVERITY_TO_SCHEMA)]
    assert ordered == sorted(set(ordered)), f"not strictly increasing: {ordered}"
    assert ordered[0] == 0
    assert ordered[-1] == _schema_max_severity() == 10


def test_the_converter_applies_the_mapping() -> None:
    """The real converter, driven with every wire value."""
    for proto_value, expected in _PROTO_SEVERITY_TO_SCHEMA.items():
        event = _grpc_event("any.event", severity=proto_value)
        assert event.severity == expected, f"proto {proto_value} -> {event.severity} != {expected}"
    assert _grpc_event("any.event", severity=common_pb2.EVENT_SEVERITY_CRITICAL).severity == 10


def test_a_critical_grpc_event_now_reaches_the_security_rule() -> None:
    """The inversion of cycle 150: the scale no longer blocks the most severe rules."""
    rule = _rule("security-alert")
    assert rule.min_severity == 9  # needs more than the wire's raw maximum
    event = _grpc_event(
        "x.security_y",
        severity=common_pb2.EVENT_SEVERITY_CRITICAL,
        priority=rule.min_priority.value,
    )
    assert event.severity == 10
    assert rule.matches(event) is True


def test_an_info_grpc_event_is_unchanged_so_today_traffic_behaves_the_same() -> None:
    """Behaviour preservation: INFO stays 1, so the Android rule is blocked exactly as before."""
    assert _PROTO_SEVERITY_TO_SCHEMA[common_pb2.EVENT_SEVERITY_INFO] == 1
    rule = _rule("android-notification")
    event = _grpc_event(
        "android.notification.posted",
        severity=common_pb2.EVENT_SEVERITY_INFO,
        priority=rule.min_priority.value,
    )
    assert event.severity == 1
    # Still blocked -- by the name *and* by the severity (1 < 3); the mapping changed neither.
    assert rule.matches(event) is False


def test_an_out_of_spec_proto_severity_falls_back_to_unspecified() -> None:
    """The fallback is deliberate and asserted, so it cannot change silently."""
    assert _PROTO_SEVERITY_TO_SCHEMA.get(6) is None  # 6 is not in the enum ...
    assert _severity_from_proto(6) == 0              # ... and maps to UNSPECIFIED
    assert _severity_from_proto(-1) == 0


def test_the_only_producer_that_stamps_a_severity_still_sends_info() -> None:
    """The remaining gate, measured: the wire's upper half is unused by every producer."""
    source = _KT_CLIENT.read_text(encoding="utf-8")
    stamped = re.findall(r"setSeverity\(\s*Common\.EventSeverity\.([A-Z_]+)\s*\)", source)
    assert stamped == ["EVENT_SEVERITY_INFO"], f"the client's severities changed: {stamped}"
    # pc-server is the other bus emitter; it stamps no severity at all (proto default = 0).
    rust = "\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in (_ROOT / "pc-server" / "src").rglob("*.rs")
    )
    assert "set_severity" not in rust and "severity" not in rust.lower()


def test_priority_is_not_mismatched_only_severity_was() -> None:
    """The wire's priority enum maps 1:1 to the schema's, so this fix's scope was severity alone."""
    assert {
        "EVENT_PRIORITY_URGENT": common_pb2.EventPriority.EVENT_PRIORITY_URGENT,
        "EVENT_PRIORITY_NORMAL": common_pb2.EventPriority.EVENT_PRIORITY_NORMAL,
        "EVENT_PRIORITY_BACKGROUND": common_pb2.EventPriority.EVENT_PRIORITY_BACKGROUND,
    } == {
        "EVENT_PRIORITY_URGENT": EventPriority.URGENT.value,
        "EVENT_PRIORITY_NORMAL": EventPriority.NORMAL.value,
        "EVENT_PRIORITY_BACKGROUND": EventPriority.BACKGROUND.value,
    }
