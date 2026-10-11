"""When several rules match one event, the *first-declared* rule wins -- and the catch-all is last.

`TriggerEngine.on_event` walks `self._rules` (a dict, so **insertion order**) and returns the
**first** rule that matches and passes cooldown (`trigger_engine.py`, the loop at the top of
`on_event`). So `create_default_rules()`'s **declaration order is load-bearing**: it decides which
task is generated when an event matches several rules, and therefore which `action_type` and which
cooldown apply. Nothing pinned that order -- measured 2026-10-11 (cycle 153).

The design is "most specific first, catch-all last": the twelfth rule is `high-severity-catchall`
(`event_type_pattern="*"`, `min_severity=9`), so it exists to catch severe events **no other rule
names** -- exactly the "the second registration is unreachable" shape that `DELEGATION.md` section 4
item 28 found in the route table, but here it is intentional and unpinned.

Why this is the *severity* pin's other half. Cycle 151 mapped the wire's `EventSeverity` (0-5) onto
the schema's `Event.severity` (0-10), which is what makes any of this reachable from gRPC at all: a
`CRITICAL` event used to arrive as severity 5, and **no rule matches severity 5** for a `security`
type (measured below), so the most severe events woke nothing. This pin drives the *behaviour* that
the mapping and the rule set together produce, through the real bus, not the matcher in isolation.

Measured 2026-10-11 (cycle 153) on the real composition root:

  * `x.security_y` @10 -> matches `[security-alert, high-severity-catchall]`, **one** task, named
    `security-alert`;
  * `x.unknown_thing` @9 -> matches `[high-severity-catchall]` alone, named `high-severity-catchall`;
  * `x.security_y` @5 -> matches **nothing**, generates **no** task (the old wire cap).

The gRPC half drives the real converter (`_event_from_proto`) rather than hand-building the schema
event, so the mapping is on the path the test measures.
"""

from __future__ import annotations

from typing import Any

import pytest

from generated.aegis import common_pb2

from aegis_ai.grpc_server import _event_from_proto

#: The rule declared last, with the wildcard pattern -- it must never shadow a specific rule.
_CATCH_ALL = "high-severity-catchall"
#: A rule that names a security type specifically.
_SPECIFIC = "security-alert"

_SECURITY_TYPE = "x.security_y"
_UNKNOWN_TYPE = "x.unknown_thing"


@pytest.fixture(autouse=True)
def _never_leak_the_runtime_singleton():
    """Boot the real runtime, but never leave it running (it starts a LAN-probing daemon)."""
    yield

    from aegis_ai.runtime import reset_runtime_for_tests

    reset_runtime_for_tests()


@pytest.fixture
def real_runtime(monkeypatch, tmp_path) -> Any:
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_BASE_URL", "")
    monkeypatch.setenv("AEGIS_DATA_DIR", str(tmp_path / "data"))

    from aegis_ai.runtime import get_runtime, reset_runtime_for_tests

    reset_runtime_for_tests()
    return get_runtime()


def _rules(real_runtime) -> list[Any]:
    return real_runtime.trigger_engine.list_rules()


def _fire(real_runtime, event) -> tuple[list[str], int, list[str]]:
    """Publish `event` on the real bus; return (rules that match, tasks made, tasks drained)."""
    engine = real_runtime.trigger_engine
    engine.reset_all_cooldowns()
    engine.drain_tasks()
    matched = [r.rule_id for r in _rules(real_runtime) if r.matches(event)]
    before = engine.stats.tasks_generated
    real_runtime.event_manager.publish(event)
    delta = engine.stats.tasks_generated - before
    drained = [t.triggered_by_rule_id for t in engine.drain_tasks()]
    return matched, delta, drained


def _schema_event(event_type: str, severity: int):
    from aegis_ai.event.helpers import build_event
    from aegis_schema.models import EventPriority

    return build_event(
        event_type,
        source_server_id="probe",
        severity=severity,
        priority=EventPriority.URGENT,
    )


def _grpc_event(event_type: str) -> Any:
    return _event_from_proto(
        common_pb2.Event(
            event_id="evt_c153",
            event_type=event_type,
            source_server_type=common_pb2.SERVER_TYPE_ANDROID,
            source_server_id="android-server",
            severity=common_pb2.EVENT_SEVERITY_CRITICAL,
            priority=common_pb2.EventPriority.EVENT_PRIORITY_URGENT,
        )
    )


def test_the_catch_all_is_the_only_wildcard_and_is_declared_last() -> None:
    """Structural: the wildcard rule must stay last, or it shadows every specific rule."""
    from trigger_engine import create_default_rules

    rules = create_default_rules()
    wildcards = [r.rule_id for r in rules if r.event_type_pattern == "*"]
    assert wildcards == [_CATCH_ALL], f"the wildcard rule set moved: {wildcards}"
    assert rules[-1].rule_id == _CATCH_ALL, (
        "the catch-all is no longer declared last -- on_event returns the FIRST match, so a "
        f"catch-all moved up would shadow the specific rules: {[r.rule_id for r in rules]}"
    )


def test_a_severe_security_event_fires_the_specific_rule_not_the_catch_all(real_runtime) -> None:
    """The behaviour the order buys: the specific rule wins even though both match."""
    matched, delta, drained = _fire(real_runtime, _schema_event(_SECURITY_TYPE, 10))
    assert matched == [_SPECIFIC, _CATCH_ALL], f"the match set moved: {matched}"
    assert delta == 1, "a severe event should generate exactly one task"
    assert drained == [_SPECIFIC], (
        f"the catch-all shadowed the specific rule: {drained} (expected [{_SPECIFIC!r}])"
    )


def test_only_one_task_is_generated_when_several_rules_match(real_runtime) -> None:
    """First-match-wins is the engine's contract: N matching rules still make ONE task.

    Stated explicitly because the opposite is easy to assume (one task per matching rule).
    """
    engine = real_runtime.trigger_engine
    engine.reset_all_cooldowns()
    engine.drain_tasks()
    event = _schema_event(_SECURITY_TYPE, 10)
    assert len([r for r in _rules(real_runtime) if r.matches(event)]) == 2, (
        "this control needs an event that two rules match"
    )
    before = engine.stats.tasks_generated
    real_runtime.event_manager.publish(event)
    assert engine.stats.tasks_generated == before + 1, "more than one task came from one event"
    engine.drain_tasks()


def test_a_severe_event_no_rule_names_falls_to_the_catch_all(real_runtime) -> None:
    """Control: the catch-all is not dead -- it fires for what nothing else names."""
    matched, delta, drained = _fire(real_runtime, _schema_event(_UNKNOWN_TYPE, 9))
    assert matched == [_CATCH_ALL], f"the catch-all's coverage moved: {matched}"
    assert delta == 1 and drained == [_CATCH_ALL], f"the catch-all did not fire: {drained}"


def test_the_old_wire_cap_fires_nothing(real_runtime) -> None:
    """The severity scale is load-bearing: at the wire's raw maximum (5) no rule matches.

    This is the regression guard for cycle 151 -- reverting the mapping would make a gRPC
    `CRITICAL` event arrive as severity 5, and this is the task it would (not) produce.
    """
    matched, delta, drained = _fire(real_runtime, _schema_event(_SECURITY_TYPE, 5))
    assert matched == [], f"a rule matches severity 5 for a security type: {matched}"
    assert delta == 0 and drained == [], f"a severity-5 event produced a task: {drained}"


def test_a_grpc_critical_event_reaches_the_specific_rule(real_runtime) -> None:
    """The composition: the real converter + the real bus + the real rule set.

    Drives `_event_from_proto` (not a hand-built schema event), so the mapping cycle 151 added is
    on the path this measures.
    """
    event = _grpc_event(_SECURITY_TYPE)
    assert event.severity == 10, f"the converter no longer maps CRITICAL to 10: {event.severity}"
    matched, delta, drained = _fire(real_runtime, event)
    assert _SPECIFIC in matched, f"a gRPC CRITICAL security event matches no specific rule: {matched}"
    assert delta == 1 and drained == [_SPECIFIC], (
        f"a gRPC CRITICAL security event did not reach the specific rule: {drained}"
    )
