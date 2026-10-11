"""The gRPC severity scale is not the trigger-rule severity scale.

``aegis_schema.models.Event.severity`` is a **0–10** scale (``ge=0, le=10``; the field's own
description reads ``0=info, 5=warning, 8=error, 10=critical``), and ``TriggerRule.min_severity``
is documented the same way (``# Minimum severity (0-10)``). But the wire format disagrees:
``protos/aegis/common.proto``'s ``EventSeverity`` tops out at **5**
(``UNSPECIFIED=0, INFO=1, LOW=2, MODERATE=3, HIGH=4, CRITICAL=5``), and ``grpc_server.py``'s
``_event_from_proto`` copies that value **verbatim** -- ``severity=int(event.severity)`` -- with
**no mapping** anywhere in ``src`` (measured: zero ``EVENT_SEVERITY`` references outside the
generated stubs).

**Measured 2026-10-11 (cycle 150).** A proto ``EVENT_SEVERITY_CRITICAL`` (5) converts to schema
``severity=5``, which on the 0–10 scale is only *"warning"*. So **no event that arrives over gRPC
can ever carry a severity above 5**, and every default rule that demands more than 5 is
unreachable from the entire gRPC surface:

============================  ==============
rule                          min_severity
============================  ==============
``dev-test-failure``          7
``dev-ci-error``              8
``android-call``              6
``security-alert``            9
``high-severity-catchall``    9
============================  ==============

That is **5 of the 12** default rules -- including the security rule and the catch-all, whose whole
purpose is to wake on the *most* severe events. The failure is a **unit mismatch**, not a policy
gap: the rules and the field speak 0–10, the wire speaks 0–5.

**It is independent of the naming gap** (``DELEGATION.md`` section 4 item 93, cycles 133/147): the
Android rule is blocked by *both* gates -- its pattern names ``android.notification_received`` while
the client emits ``android.notification.posted``, **and** its ``min_severity=3`` is above the
``INFO`` (1) that ``AegisGrpcClient.sendEvent`` stamps on *every* Android event. So aligning the
name alone would still not make it fire.

**What this pin does not do.** Choosing a proto->schema severity mapping (or rescaling the rules) is
a **behaviour change** -- it decides when AEGIS wakes -- and is recorded as an owner decision in
``DELEGATION.md`` section 4 item 93. This pin makes the mismatch *stable and measurable* so that a
future fix is a visible event rather than a silent one, and so the item-93 decision is made on the
real gates rather than the name alone.

The controls matter: a rule *within* the proto range still matches (``pc-screen-change``,
``min_severity=2``), and an unreachable rule *does* match the same event once the severity is raised
to a schema-level value -- so the block is the scale, not the matcher.
"""

from __future__ import annotations

from typing import Any

from aegis_schema.models import Event, EventPriority
from generated.aegis import common_pb2
from aegis_ai.grpc_server import _event_from_proto
from trigger_engine import create_default_rules

#: Every member of the proto ``EventSeverity`` enum, measured from the generated module.
_PROTO_SEVERITIES: dict[str, int] = {
    name: value
    for name, value in common_pb2.EventSeverity.items()
    if name.startswith("EVENT_SEVERITY")
}

#: The highest severity the wire format can carry.
_PROTO_MAX_SEVERITY = max(_PROTO_SEVERITIES.values())

#: The schema's declared upper bound, read from the pydantic field metadata (not a literal).
def _schema_max_severity() -> int:
    from annotated_types import Le

    for constraint in Event.model_fields["severity"].metadata:
        if isinstance(constraint, Le):
            return int(constraint.le)
    raise AssertionError("Event.severity has no Le() upper bound -- this pin's premise is gone")


#: The rules whose ``min_severity`` the wire format cannot express. Asserted by **equality** so a
#: new rule, a deleted rule, or a retuned threshold fails rather than silently re-scoping.
_UNREACHABLE_FROM_GRPC = frozenset(
    {
        "dev-test-failure",
        "dev-ci-error",
        "android-call",
        "security-alert",
        "high-severity-catchall",
    }
)

#: An event *type* that satisfies each unreachable rule's pattern (so only severity is in question).
_TYPE_FOR_RULE: dict[str, str] = {
    "dev-test-failure": "dev.test_failed",
    "dev-ci-error": "dev.ci_error",
    "android-call": "android.incoming_call",
    "security-alert": "x.security_y",
    "high-severity-catchall": "anything.at.all",
}


def _grpc_event(
    event_type: str,
    *,
    severity: int,
    priority: int = common_pb2.EventPriority.EVENT_PRIORITY_NORMAL,
) -> Event:
    """The most severe event the gRPC surface can deliver, via the **production** converter."""
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


def test_the_proto_severity_enum_tops_out_below_the_schema_bound() -> None:
    """The two scales disagree, and the wire's is the smaller."""
    assert _PROTO_SEVERITIES == {
        "EVENT_SEVERITY_UNSPECIFIED": 0,
        "EVENT_SEVERITY_INFO": 1,
        "EVENT_SEVERITY_LOW": 2,
        "EVENT_SEVERITY_MODERATE": 3,
        "EVENT_SEVERITY_HIGH": 4,
        "EVENT_SEVERITY_CRITICAL": 5,
    }
    assert _PROTO_MAX_SEVERITY == 5
    assert _schema_max_severity() == 10
    assert _PROTO_MAX_SEVERITY < _schema_max_severity()


def test_the_converter_copies_the_proto_value_verbatim() -> None:
    """No mapping: each proto severity lands unchanged in the 0-10 field."""
    for name, value in _PROTO_SEVERITIES.items():
        event = _grpc_event("android.notification.posted", severity=value)
        assert event.severity == value, f"{name} ({value}) became {event.severity}"


def test_no_converted_grpc_event_can_exceed_the_proto_max() -> None:
    """The ceiling is the enum, not the field."""
    worst = max(
        _grpc_event("any.event", severity=value).severity
        for value in _PROTO_SEVERITIES.values()
    )
    assert worst == _PROTO_MAX_SEVERITY


def test_the_rules_needing_a_severity_the_grpc_scale_cannot_express() -> None:
    """Exactly these rules demand more than the wire can carry."""
    rules = create_default_rules()
    actual = frozenset(r.rule_id for r in rules if r.min_severity > _PROTO_MAX_SEVERITY)
    assert actual == _UNREACHABLE_FROM_GRPC
    # Non-vacuity: the finding is a *proper* subset, so the scan is neither empty nor total.
    assert 0 < len(actual) < len(rules)


def test_such_a_rule_cannot_match_the_most_severe_grpc_event() -> None:
    """Even a perfect type match at the wire's maximum is rejected -- and *only* by severity."""
    for rule_id in sorted(_UNREACHABLE_FROM_GRPC):
        rule = _rule(rule_id)
        event = _grpc_event(
            _TYPE_FOR_RULE[rule_id],
            severity=_PROTO_MAX_SEVERITY,
            priority=rule.min_priority.value,
        )
        assert rule.matches(event) is False, f"{rule_id} matched at severity {_PROTO_MAX_SEVERITY}"

        # Isolation: raise *only* the severity to a schema-level value and it matches, so the
        # block really is the scale and not the pattern or the priority gate.
        raised = event.model_copy(update={"severity": rule.min_severity})
        assert rule.matches(raised) is True, f"{rule_id} did not match even at its own threshold"


def test_a_rule_within_the_proto_range_still_matches() -> None:
    """Control: the machinery works -- a rule at severity 2 fires on a severity-2 gRPC event."""
    rule = _rule("pc-screen-change")
    assert rule.min_severity <= _PROTO_MAX_SEVERITY
    event = _grpc_event(
        "pc.screen_changed",
        severity=rule.min_severity,
        priority=rule.min_priority.value,
    )
    assert rule.matches(event) is True


def test_the_android_rule_is_blocked_by_name_and_severity() -> None:
    """The item-93 rule has two independent blockers, so aligning the name is not sufficient."""
    rule = _rule("android-notification")
    emitted = "android.notification.posted"
    # Gate 1: the pattern names a type nothing emits.
    assert rule.event_type_pattern == "android.notification_received"
    assert rule._match_pattern(rule.event_type_pattern, emitted) is False
    # Gate 2: the client stamps INFO (1) on every event; the rule wants 3.
    client_severity = common_pb2.EventSeverity.EVENT_SEVERITY_INFO
    assert client_severity < rule.min_severity
    # A real Android notification therefore cannot match, even though its name is close.
    event = _grpc_event(emitted, severity=client_severity, priority=rule.min_priority.value)
    assert rule.matches(event) is False


def test_priority_is_not_mismatched_only_severity_is() -> None:
    """The wire's priority enum maps 1:1 to the schema's, so this pin's scope is severity alone."""
    assert {
        "EVENT_PRIORITY_URGENT": common_pb2.EventPriority.EVENT_PRIORITY_URGENT,
        "EVENT_PRIORITY_NORMAL": common_pb2.EventPriority.EVENT_PRIORITY_NORMAL,
        "EVENT_PRIORITY_BACKGROUND": common_pb2.EventPriority.EVENT_PRIORITY_BACKGROUND,
    } == {
        "EVENT_PRIORITY_URGENT": EventPriority.URGENT.value,
        "EVENT_PRIORITY_NORMAL": EventPriority.NORMAL.value,
        "EVENT_PRIORITY_BACKGROUND": EventPriority.BACKGROUND.value,
    }
