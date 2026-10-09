"""L1 reaches the L2 boundary — and stops there, or hands off, on a recorded rule.

The two halves of the L1 route were already pinned, but **the dispatch in between was
not driven by any test**:

* ``tests/test_runtime_singleton.py`` drives ``_run_l1_pipeline_for_event`` and asserts the
  three/four L1 events (observation / decision / escalation, or the capability pair).
* ``tests/test_l1_runs_off_the_publisher_thread.py`` pins *where* the immediate route runs
  (a dedicated worker) and that its failure is reported.

What neither covers is ``_run_l1_immediate_pipeline``'s decision about what happens
**after** L1 has decided: hand the event to L2, notify ``initiative_engine`` and the
``AutonomousLoop``, or drop it. That is the "just before L2" boundary
(``DELEGATION.md`` section 4 items 24 / 48 / 49; the hand-off itself is the direct call at
``runtime.py:920-921``, not the ``l1.escalation`` event, which has no in-process consumer).

Measured 2026-10-09 by driving all four action types with and without ``l2_mind``. The
rules the code implements, and that this file now pins:

  action ``ignore``      -> return immediately: no L2, no notification (the L1 record is
                            already published by the pipeline, which is the point of the
                            distinction).
  action ``capability``  -> no L2; ``initiative_engine.record_trigger`` and return.
  anything else          -> if ``l2_mind`` is wired, call ``_run_l2_pipeline`` **once** with
                            ``trigger=event_type`` and the ``detail["l1"]`` projection; store
                            the result as ``detail["l2"]``. If L2 reports ``handled`` with an
                            action type outside ``{"noop", "observe"}``, notify the initiative
                            engine and return; otherwise (not handled, or a no-op/observe
                            result) fall through to ``record_trigger`` + ``evaluate_event``.
  no ``l2_mind``         -> skip the L2 call and fall through to the same two notifications.

The probe replaces ``_run_l2_pipeline`` by name, so a rename or a moved hand-off turns
``test_the_probe_replaces_the_l2_pipeline`` red instead of silently making every L2
assertion below vacuous.

⚠️ The fake runtime here is **richer than the default real one**: it supplies an
``autonomous_loop``, which a bare ``get_runtime()`` does not (the loop is created by the entry
point, ``start_autonomous_if_enabled``, not by the composition root). So the ``evaluate_event``
expectations below describe a configuration production has only once the entry point has run.
That gap is closed by measuring the surface itself on the real composition root --
``tests/test_l1_dispatch_surface_is_present_in_the_real_runtime.py`` (cycle 117).
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import aegis_ai.runtime as runtime_module

_IMMEDIATE = "_run_l1_immediate_pipeline"
_L2 = "_run_l2_pipeline"

_EVENT_TYPE = "pc.user_activity.snapshot"
# The two action types whose L2 result does NOT count as "handled" (runtime.py:923).
_FALL_THROUGH_ACTION_TYPES = ("noop", "observe")


# ── the doubles ───────────────────────────────────────────────────────────────────────


def _observation() -> SimpleNamespace:
    return SimpleNamespace(
        event_id="evt-boundary-1",
        meaning="user switched to the editor",
        value=0.6,
        priority=0.5,
        required_intelligence=SimpleNamespace(value="high"),
        confidence=0.7,
        raw={"summary_bucket": "foreground", "observed_action": "switch_app"},
    )


def _decision(action_type: str) -> SimpleNamespace:
    obs = _observation()
    return SimpleNamespace(
        event_id="evt-boundary-1",
        action=SimpleNamespace(
            type=SimpleNamespace(value=action_type),
            capability_id="pc-server.screenshot.get_screenshot",
            args={"display": 0},
            reason="why",
        ),
        reasoning="because",
        observation=obs,
    )


class _Router:
    def __init__(self, action_type: str) -> None:
        self._decision = _decision(action_type)

    def observe(self, event: Any, *, event_id: str = "", context_capsule: Any = None) -> Any:
        return self._decision.observation

    def decide(self, observation: Any) -> Any:
        return self._decision

    def escalate(self, observation: Any, *, reason: str = "") -> Any:
        return SimpleNamespace(to_payload=lambda: {"event_id": "evt-boundary-1", "reason": reason, "layer": "L1"})


class _EventManager:
    def __init__(self) -> None:
        self.kinds: list[str] = []

    def publish_event(self, event_type: str, *, source: str, payload: dict[str, Any]) -> bool:
        self.kinds.append(event_type)
        return True


class _InitiativeEngine:
    def __init__(self, notices: list[tuple[str, str]]) -> None:
        self._notices = notices

    def record_trigger(self, event_type: str, detail: dict[str, Any]) -> None:
        self._notices.append(("record_trigger", event_type))


class _AutonomousLoop:
    def __init__(self, notices: list[tuple[str, str]]) -> None:
        self._notices = notices

    def evaluate_event(self, event_type: str, detail: dict[str, Any]) -> None:
        self._notices.append(("evaluate_event", event_type))


def _event(event_type: str = _EVENT_TYPE) -> SimpleNamespace:
    return SimpleNamespace(
        event_id="evt-boundary-1",
        event_type=event_type,
        payload_json='{"app":"vscode"}',
        timestamp_ms=1,
        source_server_id="pc-server",
        source_server_type=SimpleNamespace(name="PC"),
    )


class _Probe:
    """Drives one immediate-route dispatch and records what it observed."""

    def __init__(
        self,
        monkeypatch: Any,
        *,
        l2_mind: bool = True,
        l2_result: dict[str, Any] | None = None,
    ) -> None:
        self.l2_calls: list[dict[str, Any]] = []
        self.notices: list[tuple[str, str]] = []
        self.event_manager = _EventManager()
        self._result = dict(l2_result if l2_result is not None else {"handled": True, "action_type": "act"})

        def _fake_l2(runtime: Any, *, trigger: str, detail: dict[str, Any]) -> dict[str, Any]:
            # Keep the *same* dict the pipeline passed: it writes detail["l2"] into it after
            # we return, so holding the reference lets us assert the result was recorded.
            self.l2_calls.append({"trigger": trigger, "detail": detail})
            return dict(self._result)

        monkeypatch.setattr(runtime_module, _L2, _fake_l2)
        self.runtime = SimpleNamespace(
            l1_router=_Router("escalate"),
            l1_executor=None,
            event_manager=self.event_manager,
            initiative_engine=_InitiativeEngine(self.notices),
            autonomous_loop=_AutonomousLoop(self.notices),
            l2_mind=(object() if l2_mind else None),
        )

    def run(self, action_type: str, *, event_type: str = _EVENT_TYPE) -> None:
        self.runtime.l1_router = _Router(action_type)
        getattr(runtime_module, _IMMEDIATE)(self.runtime, _event(event_type))

    @property
    def l2_count(self) -> int:
        return len(self.l2_calls)

    @property
    def notice_names(self) -> list[str]:
        return [name for name, _ in self.notices]


# ── control + non-vacuity ─────────────────────────────────────────────────────────────


def test_the_probe_replaces_the_l2_pipeline(monkeypatch) -> None:
    """Control: if the hand-off is renamed or moved, this fails instead of going quiet."""
    original = getattr(runtime_module, _L2)
    _Probe(monkeypatch)
    assert getattr(runtime_module, _L2) is not original, (
        f"the probe did not replace {_L2} -- every L2 assertion in this file would be vacuous"
    )


def test_the_hand_off_really_happens(monkeypatch) -> None:
    """Non-vacuity floor: at least one branch must reach L2, or the file proves nothing."""
    probe = _Probe(monkeypatch)
    probe.run("escalate")
    assert probe.l2_count == 1, (
        "the escalate branch never reached L2 -- the probe is vacuous, so the "
        "'no L2 call' assertions below cannot distinguish a rule from a dead probe"
    )


# ── the hand-off itself ───────────────────────────────────────────────────────────────


def test_escalate_hands_the_event_to_l2_once_with_the_l1_projection(monkeypatch) -> None:
    probe = _Probe(monkeypatch, l2_result={"handled": True, "action_type": "act"})
    probe.run("escalate")

    assert probe.l2_count == 1, "the event was not handed to L2 exactly once"
    call = probe.l2_calls[0]
    assert call["trigger"] == _EVENT_TYPE, (
        f"L2 was triggered with {call['trigger']!r}; the hand-off must carry the event type"
    )
    assert call["detail"]["l1"]["action_type"] == "escalate", (
        "the detail handed to L2 must carry the L1 projection (action_type)"
    )
    assert call["detail"]["l1"]["meaning"] == "user switched to the editor", (
        "the L1 projection must carry the observation's meaning, not just the action"
    )
    assert call["detail"]["l2"] == {"handled": True, "action_type": "act"}, (
        "the L2 result must be recorded back into the detail that continues downstream"
    )


def test_a_handled_l2_result_stops_before_the_autonomous_loop(monkeypatch) -> None:
    """L2 handled it -> the initiative engine is told and the loop is *not* woken."""
    probe = _Probe(monkeypatch, l2_result={"handled": True, "action_type": "act"})
    probe.run("escalate")

    assert probe.notice_names == ["record_trigger"], (
        f"a handled L2 result must notify the initiative engine and return; observed {probe.notice_names}"
    )


def test_an_unhandled_l2_result_falls_through_to_the_loop(monkeypatch) -> None:
    probe = _Probe(monkeypatch, l2_result={"handled": False, "action_type": "act"})
    probe.run("escalate")

    assert probe.notice_names == ["record_trigger", "evaluate_event"], (
        f"an unhandled L2 result must fall through to both notifications; observed {probe.notice_names}"
    )


def test_a_noop_or_observe_l2_result_falls_through(monkeypatch) -> None:
    """`handled` is not enough -- a no-op/observe result is treated as not handled.

    The two action types are read from the module docstring's list so that widening or
    narrowing the set has to be a deliberate edit to both the code and this test.
    """
    for action_type in _FALL_THROUGH_ACTION_TYPES:
        probe = _Probe(monkeypatch, l2_result={"handled": True, "action_type": action_type})
        probe.run("escalate")
        assert probe.notice_names == ["record_trigger", "evaluate_event"], (
            f"a handled L2 result with action_type={action_type!r} must fall through; observed {probe.notice_names}"
        )


# ── the branches that must NOT reach L2 ───────────────────────────────────────────────


def test_ignore_returns_before_any_notification(monkeypatch) -> None:
    """`ignore` stops the dispatch -- but L1's own record is already published."""
    probe = _Probe(monkeypatch)
    probe.run("ignore")

    assert probe.l2_count == 0, "an ignored event must not be handed to L2"
    assert probe.notice_names == [], "an ignored event must not notify anything"
    assert probe.event_manager.kinds == ["l1.observation", "l1.decision"], (
        "the L1 record is published by the pipeline, before the dispatch decision; "
        f"observed {probe.event_manager.kinds}"
    )


def test_capability_returns_before_l2(monkeypatch) -> None:
    probe = _Probe(monkeypatch)
    probe.run("capability")

    assert probe.l2_count == 0, "an L1-handled capability must not be escalated to L2"
    assert probe.notice_names == ["record_trigger"], (
        f"the capability branch must notify the initiative engine and return; observed {probe.notice_names}"
    )


def test_no_l2_mind_skips_the_call_but_still_notifies(monkeypatch) -> None:
    probe = _Probe(monkeypatch, l2_mind=False)
    probe.run("escalate")

    assert probe.l2_count == 0, "without an L2 mind the pipeline must not call L2"
    # The event still has to reach the initiative engine and the AutonomousLoop.
    assert probe.notice_names == ["record_trigger", "evaluate_event"], (
        f"no L2 mind: expected both notifications, observed {probe.notice_names}"
    )
