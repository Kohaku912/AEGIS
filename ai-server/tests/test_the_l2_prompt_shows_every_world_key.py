"""The L2 prompt shows *every* world-state key -- the `World:` line no longer truncates
alphabetically.

``L2Context.to_prompt`` is the *only* thing the L2 LLM sees (``l2_mind.run_once`` passes
it as ``prompt=`` to ``gateway.request``; nothing else carries ``world_state``). Its
``World:`` line was ``sorted(world_state)[:8]``, and alphabetical order is the wrong
selector: measured 2026-10-11 (cycle 149), a production ``world_state`` carries **14**
keys -- 9 from ``runtime.py::_l2_world_state`` (all optional services present, as
``_build_runtime`` constructs them), 4 from ``_run_l2_pipeline``, ``now_ms`` from
``build_context`` -- and the first eight alphabetically are exactly the *counters*.
So ``situation_state``, ``trigger``, ``trigger_event_type``, ``trigger_source``,
``triggered_tasks`` and ``user_understanding`` never reached the model. Cycle 148 had
just threaded the trigger context into ``world_state`` for L2; the renderer dropped it
one layer later.

Both halves are driven, not asserted structurally: the *writer* (the real
``_run_l2_pipeline`` / ``_l2_world_state``) and the *renderer* (the real ``to_prompt``).
A pin that only built an ``L2Context`` by hand would not see a writer that renames a key.
"""

from __future__ import annotations

from typing import Any

from aegis_ai.autonomous.l2_models import L2Context, _WORLD_KEY_ORDER
from aegis_ai.runtime import _l2_world_state, _run_l2_pipeline


class _Situation:
    def get_state(self) -> dict[str, Any]:
        return {"state": "focused", "interruptibility": "low", "confidence": 0.8}


class _Status:
    def get_snapshot(self) -> dict[str, Any]:
        return {"pc-1": {"status": "online"}, "room-1": {"status": "degraded"}}


class _UserUnderstanding:
    def to_context_string(self, _: str) -> str:
        return "user prefers terse replies"


class _Rt:
    """The production shape: every optional service `_l2_world_state` probes is present."""

    situation_model = _Situation()
    status_manager = _Status()
    user_understanding_service = _UserUnderstanding()


class _Mind:
    last: L2Context | None = None

    def build_context(self) -> L2Context:
        self.last = L2Context(world_state=dict(_l2_world_state(_Rt())))
        return self.last

    def run_once(self, ctx: L2Context) -> dict[str, Any]:
        self.last = ctx
        return {"handled": True, "action_type": "observe"}


class _RtWithMind(_Rt):
    l2_mind = _Mind()
    event_manager = None


def _drive_pipeline(**detail: Any) -> tuple[L2Context, str]:
    """Run the real `_run_l2_pipeline` and return the context the LLM would be sent."""
    rt = _RtWithMind()
    _run_l2_pipeline(
        rt,
        trigger=str(detail.pop("trigger", "periodic_cycle")),
        detail={"source": "autonomous_loop", **detail},
    )
    assert rt.l2_mind.last is not None
    return rt.l2_mind.last, rt.l2_mind.last.to_prompt()


def test_the_prompt_the_llm_receives_names_the_trigger() -> None:
    """The write→render chain: what the pipeline sets for L2 must survive to the prompt."""
    ctx, prompt = _drive_pipeline(
        trigger="triggered:security-alert",
        type="triggered:security-alert",
        triggered_tasks=["Event 'pc.screen_changed' from PC (severity=2)"],
    )
    assert ctx.world_state["trigger"] == "triggered:security-alert"
    assert "trigger=triggered:security-alert" in prompt, (
        "the prompt did not name the trigger -- the LLM cannot see why the cycle ran"
    )
    assert "triggered_tasks=Event 'pc.screen_changed' from PC (severity=2)" in prompt, (
        "the trigger task's context did not reach the prompt"
    )


def test_every_key_the_l2_world_state_writes_renders() -> None:
    """Drive the writer with all optional services present; no key may be dropped."""
    world = _l2_world_state(_Rt())
    assert len(world) >= 5, f"the writer emitted only {sorted(world)} -- the stub is stale"
    outside_old_window = [k for k in world if k not in sorted(world)[:8]]
    assert outside_old_window, (
        "every key sorts inside the old 8-key window, so this fixture cannot witness the "
        f"truncation: {sorted(world)}"
    )
    prompt = L2Context(world_state=dict(world)).to_prompt()
    missing = sorted(k for k in world if f"{k}=" not in prompt)
    assert missing == [], (
        f"L2Context.to_prompt dropped {missing} -- a key the writer set never reaches the LLM"
    )


def test_the_full_production_key_set_is_not_truncated() -> None:
    """The 14-key production set: the old `sorted(...)[:8]` showed only the counters."""
    world = dict(_l2_world_state(_Rt()))
    world.update(
        {
            "now_ms": 1_700_000_000_000,
            "trigger": "triggered:security-alert",
            "trigger_source": "autonomous_loop",
            "trigger_event_type": "triggered:security-alert",
            "triggered_tasks": "Event 'pc.screen_changed' from PC (severity=2)",
        }
    )
    assert len(world) == 14, f"expected the production key set, got {sorted(world)}"
    prompt = L2Context(world_state=world).to_prompt()
    shown = [line for line in prompt.splitlines() if line.startswith("World: ")][0]
    for key in world:
        assert f"{key}=" in shown, f"{key!r} was silently dropped from the World line"
    # The old selector's output, as a named counter-example.
    for dropped in ("trigger", "triggered_tasks", "situation_state", "user_understanding"):
        assert dropped not in sorted(world)[:8], (
            f"{dropped!r} now sorts inside the old 8-key window -- the fixture no longer "
            "witnesses the defect"
        )


def test_a_desire_cycle_still_names_its_trigger() -> None:
    """Control: a desire-driven cycle is labelled, not omitted."""
    _, prompt = _drive_pipeline(trigger="periodic_cycle", type="periodic_cycle")
    assert "trigger=periodic_cycle" in prompt


def test_the_declared_order_puts_the_trigger_before_the_counters() -> None:
    """Control: the order is deliberate -- the trigger keys precede the alphabetical tail."""
    world = {
        "active_task_count": 3,
        "trigger": "triggered:security-alert",
        "triggered_tasks": "Event 'x'",
    }
    line = L2Context(world_state=world).to_prompt()
    assert line.index("trigger=") < line.index("active_task_count="), (
        "the World line fell back to alphabetical order"
    )
    assert _WORLD_KEY_ORDER[0] == "trigger"


def test_a_numeric_zero_is_not_erased() -> None:
    """Control: the renderer truncates text, not numbers -- `0` must survive."""
    line = L2Context(world_state={"active_task_count": 0, "situation_confidence": 0.0}).to_prompt()
    assert "active_task_count=0" in line, f"a zero count was rendered as blank: {line!r}"
    assert "situation_confidence=0.0" in line


def test_text_values_are_truncated() -> None:
    """Control: a long *text* value is shortened (the line stays a summary)."""
    line = L2Context(world_state={"user_understanding": "x" * 5000}).to_prompt()
    assert "x" * 5000 not in line
    assert "user_understanding=" in line
