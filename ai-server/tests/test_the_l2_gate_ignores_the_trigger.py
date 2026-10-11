"""A trigger-driven wake can be gated out of L2 -- and then its reason is *dropped*, not kept.

``_execute_cycle`` is entered because a ``TaskRequest`` was drained (``_run_loop`` runs the cycle
when ``triggered_tasks`` is truthy), and the drained tasks are the only consumer of the reason:
they become the L2 label (``_trigger_label``) and the L2 detail (cycle 148, ``DELEGATION.md``
section 4 item 24). But the L2 *gate* never sees them.

``_l2_should_run_cycle`` is called with ``force_desire`` **only** -- in the loop
(``autonomous_loop.py``) and in the production callback (``runtime.py``) it is
``lambda force_desire=False: bool(force_desire) or l2_mind.should_run_cycle()
or bool(_pending_actionable_observations)``. ``l2_mind.should_run_cycle()`` is a **rate limiter**:
True only when ``last_cycle_at_ms == 0`` or ``now - last_cycle_at_ms >= cycle_interval_seconds *
1000``, and the default ``cycle_interval_seconds`` is **1800** (30 minutes). The cycle-level limiter
is much tighter (``min_action_interval_seconds`` defaults to **60** s) and is applied *before* the
drain (``can_execute``), so a trigger is drained -- and then, if the L2 gate is closed, it is gone:
the legacy path below the L2 block does not read ``triggered_tasks`` at all.

Measured 2026-10-11 (cycle 155) on the real ``_execute_cycle``, with the gate wired to the **real**
``L2AutonomousMind.should_run_cycle`` (not a stub):

  * ``triggered_tasks=[task]`` + a **closed** gate -> the L2 bridge is **never called** and the
    legacy path is entered (the reason is discarded, not queued);
  * the same call with an **open** gate -> the bridge is called with
    ``trigger="triggered:<rule_id>"`` (cycle 148's contract, unchanged);
  * ``force_desire=True`` -> the bridge is called even with the gate closed (the desire term is
    the *first* disjunct of the production lambda).

So the asymmetry is the defect: a *desire* wake bypasses the limiter, a *trigger* wake does not.
Whether to fix it is an owner decision -- the two branches trade **promptness** against **cost**
(honour the trigger -> L2 runs up to once per ``min_action_interval_seconds``, i.e. 30x more often;
or preserve the trigger -> L2 still runs at most every 30 min, but the reason is not lost). This pin
records the measured behaviour so either branch flips a test.

⚠️ The cycle-148 pin drives ``should_run=lambda force_desire=False: True`` -- it stubs the gate, so
it measures the *label*, never whether a trigger-driven cycle is *allowed* to reach L2.
"""

from __future__ import annotations

import ast
import pathlib
import time
from typing import Any

import pytest

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
from aegis_ai.autonomous.l2_mind import L2AutonomousMind

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_RUNTIME = _ROOT / "src" / "aegis_ai" / "runtime.py"
_LOOP = _ROOT / "src" / "aegis_ai" / "autonomous" / "autonomous_loop.py"

_RULE_ID = "probe-rule"
_INTERVAL_S = 1800


class _Desire:
    """``_execute_cycle`` only needs a truthy ``_desire`` with ``apply_decay``."""

    def apply_decay(self) -> None:
        pass


class _ReachedLegacyPath(Exception):
    """Raised by the ``_pressure_due`` spy to stop ``_execute_cycle`` after the L2 block."""


def _task() -> Any:
    """A real ``TaskRequest`` from the real engine (no hand-built object)."""
    from aegis_schema.models import Event, EventPriority, ServerType

    from trigger_engine import TriggerEngine, TriggerRule

    engine = TriggerEngine()
    engine.add_rule(
        TriggerRule(
            rule_id=_RULE_ID,
            event_type_pattern="probe.thing",
            min_severity=0,
            min_priority=EventPriority.URGENT,
        )
    )
    task = engine.on_event(
        Event(
            event_id="evt_c155",
            event_type="probe.thing",
            source_server_type=ServerType.PC,
            source_server_id="pc-c155",
            severity=5,
            priority=EventPriority.URGENT,
        )
    )
    assert task is not None, "the probe rule did not fire -- the fixture is broken"
    return task


def _mind(*, last_cycle_at_ms: int) -> L2AutonomousMind:
    """A real ``L2AutonomousMind`` with only the cadence attributes ``should_run_cycle`` reads."""
    mind = L2AutonomousMind.__new__(L2AutonomousMind)
    mind.enabled = True
    mind.cycle_interval_seconds = _INTERVAL_S
    mind.last_cycle_at_ms = last_cycle_at_ms
    return mind


def _production_gate(mind: L2AutonomousMind) -> Any:
    """Mirrors ``runtime.py``'s ``should_run`` lambda (the observations term is ``[]`` here).

    The *shape* is the point: ``bool(force_desire)`` first, then the rate limiter -- and no term
    that could carry the drained trigger.
    """
    return lambda force_desire=False: bool(force_desire) or mind.should_run_cycle()


def _closed_gate() -> Any:
    return _production_gate(_mind(last_cycle_at_ms=int(time.time() * 1000)))


def _open_gate() -> Any:
    return _production_gate(
        _mind(last_cycle_at_ms=int(time.time() * 1000) - _INTERVAL_S * 1000)
    )


def _loop(tmp_path: Any, handler: Any, should_run: Any) -> AutonomousLoop:
    loop = AutonomousLoop(desire_system=_Desire(), data_dir=str(tmp_path / "autonomous"))
    loop._desire = _Desire()
    loop._refresh_observations_for_cycle = lambda: None
    loop._pending_actionable_observations = []
    loop.set_l2_reasoning_handler(handler, should_run=should_run)
    return loop


# ── The static half: neither the loop nor the callback passes the trigger to the gate ──

def _lambda_params(func: ast.Lambda) -> list[str]:
    return [a.arg for a in func.args.args]


def _bridge_call(path: pathlib.Path) -> ast.Call:
    """The single ``set_l2_reasoning_handler(...)`` call in ``path``."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "set_l2_reasoning_handler"
    ]
    assert len(calls) == 1, f"expected one set_l2_reasoning_handler call, found {len(calls)}"
    return calls[0]


def _kw_lambda(call: ast.Call, name: str) -> ast.Lambda:
    values = [kw.value for kw in call.keywords if kw.arg == name]
    assert len(values) == 1 and isinstance(values[0], ast.Lambda), (
        f"the {name}= argument is not a single lambda"
    )
    return values[0]


def test_the_production_gate_cannot_see_the_trigger() -> None:
    """The ``should_run`` lambda in ``runtime.py`` takes ``force_desire`` only."""
    gate = _kw_lambda(_bridge_call(_RUNTIME), "should_run")
    params = _lambda_params(gate)
    assert params == ["force_desire"], (
        f"the production L2 gate now takes {params} -- if it gained `triggered_tasks`, this record "
        "is stale and the behaviour tests below should be inverted"
    )


def test_the_production_handler_does_carry_the_trigger() -> None:
    """The contrast: the *handler* is handed ``triggered_tasks`` -- only the *gate* is not.

    So the reason reaches L2 **iff** the gate opens; the gate is the only thing that can drop it.
    """
    call = _bridge_call(_RUNTIME)
    handler = call.args[0] if call.args else None
    assert isinstance(handler, ast.Lambda), "the L2 handler is no longer a positional lambda"
    assert "triggered_tasks" in _lambda_params(handler), (
        "the handler no longer takes triggered_tasks -- the reason would be unreachable even when "
        "L2 runs, which is a different defect"
    )


def test_the_production_gate_bypasses_the_limiter_for_a_desire_wake_only() -> None:
    """The asymmetry lives in the gate's body: ``bool(force_desire)`` is the first disjunct."""
    body = ast.unparse(_kw_lambda(_bridge_call(_RUNTIME), "should_run").body)
    assert "bool(force_desire)" in body, (
        f"the desire term is gone from the gate body ({body!r}) -- a desire wake would no longer "
        "bypass the rate limiter"
    )
    assert "triggered_tasks" not in body, (
        f"the gate body now mentions triggered_tasks ({body!r}) -- the record is stale"
    )


def test_the_loop_does_not_pass_the_trigger_to_the_gate() -> None:
    """The call site passes ``force_desire`` only -- the gate cannot see the trigger."""
    tree = ast.parse(_LOOP.read_text(encoding="utf-8"))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "_l2_should_run_cycle"
    ]
    assert len(calls) == 1, f"expected exactly one _l2_should_run_cycle call, found {len(calls)}"
    keywords = sorted(kw.arg for kw in calls[0].keywords)
    assert keywords == ["force_desire"], (
        f"the gate call now passes {keywords} -- the record must be updated with the measurement"
    )


# ── The measured half: the real gate drops the trigger's reason ──

def test_a_triggered_wake_with_a_closed_gate_never_reaches_l2(tmp_path) -> None:
    """The record: the cycle runs, the reason is dropped, nothing queues it for later."""
    seen: list[Any] = []

    def _handler(**_kwargs: Any) -> dict[str, Any]:
        seen.append(_kwargs)
        return {"handled": True, "action_type": "observe"}

    loop = _loop(tmp_path, _handler, _closed_gate())
    loop._pressure_due = lambda: (_ for _ in ()).throw(_ReachedLegacyPath())

    with pytest.raises(_ReachedLegacyPath):
        loop._execute_cycle(triggered_tasks=[_task()])

    assert seen == [], (
        "the L2 bridge ran despite the gate -- the record is stale, invert this test"
    )


def test_a_triggered_wake_with_an_open_gate_reaches_l2(tmp_path) -> None:
    """Control (cycle 148's contract): with the gate open the label carries the rule id."""
    seen: dict[str, Any] = {}

    def _handler(trigger: str = "periodic_cycle", **_: Any) -> dict[str, Any]:
        seen["trigger"] = trigger
        return {"handled": True, "action_type": "observe"}

    loop = _loop(tmp_path, _handler, _open_gate())
    loop._execute_cycle(triggered_tasks=[_task()])
    assert seen.get("trigger") == f"triggered:{_RULE_ID}", (
        f"an open gate did not carry the rule id: {seen.get('trigger')!r}"
    )


def test_force_desire_bypasses_the_closed_gate(tmp_path) -> None:
    """The asymmetry: a *desire* wake reaches L2 through the same closed gate."""
    seen: list[Any] = []

    def _handler(**kwargs: Any) -> dict[str, Any]:
        seen.append(kwargs)
        return {"handled": True, "action_type": "observe"}

    loop = _loop(tmp_path, _handler, _closed_gate())
    loop._execute_cycle(force_desire=True)
    assert len(seen) == 1, (
        "force_desire no longer bypasses the gate -- the two wake kinds would then be symmetric"
    )


def test_the_gate_is_a_rate_limiter_that_the_trigger_does_not_satisfy() -> None:
    """The gate's own semantics: it is interval-based, and it knows nothing of a trigger.

    Driven directly, so the claim is about the gate's *body*, not about the wiring.
    """
    mind = _mind(last_cycle_at_ms=0)
    assert mind.should_run_cycle(now_ms=10_000) is True, "a never-run mind must run once"

    mind.last_cycle_at_ms = 10_000
    assert mind.should_run_cycle(now_ms=10_000 + _INTERVAL_S * 1000 - 1000) is False, (
        "the gate no longer rate-limits within cycle_interval_seconds"
    )
    assert mind.should_run_cycle(now_ms=10_000 + _INTERVAL_S * 1000) is True, (
        "the gate no longer opens at cycle_interval_seconds"
    )
    import inspect

    params = list(inspect.signature(mind.should_run_cycle).parameters)
    assert params == ["now_ms"], (
        f"should_run_cycle now takes {params} -- if it gained a trigger argument, the loop could "
        "consult it, and this record changes"
    )
