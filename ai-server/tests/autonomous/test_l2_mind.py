"""L2 Autonomous Mind テスト — DASHBOARD_V3_PLAN.md Phase L4.

`L2AutonomousMind` の context 構築 / decision 解析 / escalation フローを検証する。
`LLMGateway` / memory / desire は mock で代替し、AEGIS 本体ロジックをピンポイントでテストする。
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# fakes
# ---------------------------------------------------------------------------
@dataclass
class _FakeResponse:
    success: bool = True
    content: str = "{}"
    error: str | None = None


@dataclass
class _FakeGateway:
    responses: list[_FakeResponse]  # 順番に消費
    captured: list[dict[str, Any]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.captured is None:
            self.captured = []

    def request(self, **kwargs: Any) -> _FakeResponse:
        self.captured.append(kwargs)
        if not self.responses:
            return _FakeResponse(success=False, error="no_response")
        return self.responses.pop(0)


@dataclass
class _FakeMemory:
    summary_text: str = "Recent memory summary"

    def summarize_recent(self, max_entries: int = 5) -> str:
        return self.summary_text


@dataclass
class _FakeDesire:
    snapshot: dict[str, float] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.snapshot is None:
            self.snapshot = {"user_support": 4.2, "social": 5.5, "growth": 3.1}

    def get_snapshot(self) -> dict[str, float]:
        return dict(self.snapshot)


def _patched_gateway(monkeypatch: pytest.MonkeyPatch, fake: _FakeGateway) -> None:
    """L2AutonomousMind._get_gateway を fake 返却に差し替え."""
    from aegis_ai.autonomous import l2_mind

    monkeypatch.setattr(l2_mind.L2AutonomousMind, "_get_gateway", lambda self: fake)


# ---------------------------------------------------------------------------
# import smoke
# ---------------------------------------------------------------------------
class TestImports:
    def test_l2_mind_importable(self) -> None:
        from aegis_ai.autonomous import L2AutonomousMind

        assert L2AutonomousMind is not None

    def test_l2_models_importable(self) -> None:
        from aegis_ai.autonomous import (
            L2Action,
            L2ActionType,
            L2Context,
            L2Decision,
            L2Escalation,
        )

        assert L2Action is not None
        assert L2ActionType is not None
        assert L2Context is not None
        assert L2Decision is not None
        assert L2Escalation is not None

    def test_l2_autonomous_loop_still_importable(self) -> None:
        from aegis_ai.autonomous import AutonomousLoop

        assert AutonomousLoop is not None

    def test_l2_action_type_enum(self) -> None:
        from aegis_ai.autonomous import L2ActionType

        assert L2ActionType.TASK.value == "task"
        assert L2ActionType.ESCALATE_L3.value == "escalate_l3"
        assert L2ActionType.OBSERVE.value == "observe"
        assert L2ActionType.NOOP.value == "noop"

    def test_l2_action_type_from_invalid(self) -> None:
        from aegis_ai.autonomous import L2ActionType

        with pytest.raises(ValueError):
            L2ActionType("garbage")


# ---------------------------------------------------------------------------
# L2Context
# ---------------------------------------------------------------------------
class TestL2Context:
    def test_to_prompt_empty(self) -> None:
        from aegis_ai.autonomous import L2Context

        ctx = L2Context()
        prompt = ctx.to_prompt()
        assert prompt == "(empty context)"

    def test_to_prompt_full(self) -> None:
        from aegis_ai.autonomous import L2Context

        ctx = L2Context(
            world_state={"active_tasks": 3, "queue_size": 0},
            memory_summary="user said hello",
            desire_snapshot={"user_support": 2.0, "social": 5.0, "growth": 7.0},
            task_state=[{"id": "t1", "title": "Investigate issue"}, {"id": "t2"}],
            l1_summaries=[{"event_id": "e1", "summary_bucket": "anomaly", "meaning": "Browser degraded"}],
            pending_obligations=[{"kind": "reply", "summary": "Reply to user"}],
            recent_failures=["cap.foo failed"],
        )
        prompt = ctx.to_prompt()
        assert "Desires:" in prompt
        assert "World:" in prompt
        assert "Memory:" in prompt
        assert "Active tasks: 2" in prompt
        assert "L1 summaries: 1" in prompt
        assert "Pending obligations: 1" in prompt
        assert "Recent failures: 1" in prompt
        assert "- task: Investigate issue" in prompt
        assert "- l1[anomaly/observe]: Browser degraded" in prompt
        assert "- obligation: Reply to user" in prompt
        assert "- failure: cap.foo failed" in prompt


# ---------------------------------------------------------------------------
# build_context
# ---------------------------------------------------------------------------
class TestBuildContext:
    def test_no_providers_returns_empty(self) -> None:
        from aegis_ai.autonomous import L2AutonomousMind

        mind = L2AutonomousMind()
        ctx = mind.build_context()
        assert ctx.memory_summary == ""
        assert ctx.desire_snapshot == {}
        assert ctx.task_state == []
        assert ctx.l1_summaries == []
        assert ctx.world_state.get("now_ms", 0) > 0

    def test_with_memory_and_desire(self) -> None:
        from aegis_ai.autonomous import L2AutonomousMind

        mem = _FakeMemory(summary_text="hello world")
        des = _FakeDesire()
        mind = L2AutonomousMind(memory_system=mem, desire_system=des)
        ctx = mind.build_context()
        assert ctx.memory_summary == "hello world"
        assert ctx.desire_snapshot["user_support"] == 4.2
        assert ctx.desire_snapshot["social"] == 5.5
        assert ctx.desire_snapshot["growth"] == 3.1

    def test_with_callable_providers(self) -> None:
        from aegis_ai.autonomous import L2AutonomousMind

        mind = L2AutonomousMind(
            task_state_provider=lambda: [{"id": "t1"}, {"id": "t2"}],
            l1_summaries_provider=lambda: [{"event_id": "e1"}],
        )
        ctx = mind.build_context()
        assert len(ctx.task_state) == 2
        assert len(ctx.l1_summaries) == 1

    def test_provider_failure_falls_back_to_default(self) -> None:
        from aegis_ai.autonomous import L2AutonomousMind

        def _bad() -> list[dict[str, Any]]:
            raise RuntimeError("boom")

        mind = L2AutonomousMind(
            task_state_provider=_bad,
            l1_summaries_provider=_bad,
        )
        ctx = mind.build_context()
        assert ctx.task_state == []
        assert ctx.l1_summaries == []


# ---------------------------------------------------------------------------
# decide()
# ---------------------------------------------------------------------------
class TestDecide:
    def test_disabled_returns_noop(self) -> None:
        from aegis_ai.autonomous import L2AutonomousMind

        mind = L2AutonomousMind(enabled=False)
        d = mind.decide()
        assert d.action.type.value == "noop"
        assert "disabled" in d.action.reason
        assert d.escalate_to_l3 is False

    def test_task_decision(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.autonomous import L2ActionType, L2AutonomousMind

        payload = {
            "action_type": "task",
            "task_spec": {"capability_id": "cap.read", "args": {}},
            "reason": "desire low",
            "plan": "execute cap.read",
            "confidence": 0.8,
            "escalate_to_l3": False,
        }
        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps(payload))])
        _patched_gateway(monkeypatch, fake)
        mind = L2AutonomousMind()
        d = mind.decide()
        assert d.action.type == L2ActionType.TASK
        assert d.action.task_spec["capability_id"] == "cap.read"
        assert d.plan == "execute cap.read"
        assert d.confidence == 0.8
        assert d.escalate_to_l3 is False
        # gateway 呼び出しは layer="L2" を使う
        assert fake.captured[0]["layer"] == "L2"
        assert fake.captured[0]["json_mode"] is True
        assert fake.captured[0]["context_meta"]["caller"] == "l2_mind"

    def test_explicit_escalate_l3(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.autonomous import L2ActionType, L2AutonomousMind

        payload = {
            "action_type": "escalate_l3",
            "l3_problem": {"problem": "complex plan"},
            "reason": "too complex",
            "confidence": 0.9,
            "escalate_to_l3": True,
        }
        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps(payload))])
        _patched_gateway(monkeypatch, fake)
        mind = L2AutonomousMind()
        d = mind.decide()
        assert d.action.type == L2ActionType.ESCALATE_L3
        assert d.escalate_to_l3 is True

    def test_auto_escalate_low_confidence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """confidence < threshold のとき escalate_to_l3 が自動 True 化される."""
        from aegis_ai.autonomous import L2ActionType, L2AutonomousMind

        payload = {
            "action_type": "task",
            "task_spec": {"capability_id": "cap.read"},
            "reason": "weak",
            "plan": "try",
            "confidence": 0.2,  # < 0.4
        }
        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps(payload))])
        _patched_gateway(monkeypatch, fake)
        mind = L2AutonomousMind()
        d = mind.decide()
        assert d.action.type == L2ActionType.TASK
        assert d.escalate_to_l3 is True
        assert "auto" in d.action.reason.lower() or "threshold" in d.action.reason.lower()

    def test_invalid_action_type_falls_back_to_noop(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.autonomous import L2ActionType, L2AutonomousMind

        payload = {"action_type": "garbage", "confidence": 0.5}
        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps(payload))])
        _patched_gateway(monkeypatch, fake)
        mind = L2AutonomousMind()
        d = mind.decide()
        assert d.action.type == L2ActionType.NOOP

    def test_json_parse_failure_returns_noop(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.autonomous import L2ActionType, L2AutonomousMind

        fake = _FakeGateway(responses=[_FakeResponse(content="not json {")])
        _patched_gateway(monkeypatch, fake)
        mind = L2AutonomousMind()
        d = mind.decide()
        assert d.action.type == L2ActionType.NOOP
        assert "json" in d.action.reason

    def test_gateway_exception_returns_noop(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.autonomous import L2ActionType, l2_mind

        class RaisingGateway:
            def request(self, **kwargs: Any) -> Any:
                raise RuntimeError("boom")

        monkeypatch.setattr(
            l2_mind.L2AutonomousMind, "_get_gateway", lambda self: RaisingGateway()
        )
        mind = l2_mind.L2AutonomousMind()
        d = mind.decide()
        assert d.action.type == L2ActionType.NOOP
        assert "gateway error" in d.action.reason

    def test_non_dict_llm_output_returns_noop(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.autonomous import L2ActionType, L2AutonomousMind

        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps([1, 2, 3]))])
        _patched_gateway(monkeypatch, fake)
        mind = L2AutonomousMind()
        d = mind.decide()
        assert d.action.type == L2ActionType.NOOP
        assert "non-dict" in d.action.reason

    def test_gateway_returns_failure(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.autonomous import L2ActionType, L2AutonomousMind

        fake = _FakeGateway(responses=[_FakeResponse(success=False, error="upstream")])
        _patched_gateway(monkeypatch, fake)
        mind = L2AutonomousMind()
        d = mind.decide()
        assert d.action.type == L2ActionType.NOOP


# ---------------------------------------------------------------------------
# event publish
# ---------------------------------------------------------------------------
class TestEventPublish:
    def test_l2_decision_published(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.autonomous import L2AutonomousMind

        published: list[tuple[str, dict[str, Any]]] = []

        def publisher(event_type: str, payload: dict[str, Any]) -> None:
            published.append((event_type, payload))

        payload = {
            "action_type": "task",
            "task_spec": {"capability_id": "cap.read"},
            "reason": "r",
            "plan": "p",
            "confidence": 0.7,
        }
        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps(payload))])
        _patched_gateway(monkeypatch, fake)
        mind = L2AutonomousMind(event_publisher=publisher)
        mind.decide()
        types = [t for t, _ in published]
        assert "l2.thinking" in types
        assert "l2.decision" in types

    def test_l2_escalation_published_when_escalate(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.autonomous import L2AutonomousMind

        published: list[tuple[str, dict[str, Any]]] = []

        def publisher(event_type: str, payload: dict[str, Any]) -> None:
            published.append((event_type, payload))

        payload = {
            "action_type": "escalate_l3",
            "l3_problem": {"problem": "deep question"},
            "reason": "need l3",
            "confidence": 0.9,
            "escalate_to_l3": True,
        }
        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps(payload))])
        _patched_gateway(monkeypatch, fake)
        mind = L2AutonomousMind(event_publisher=publisher)
        mind.decide()
        types = [t for t, _ in published]
        assert "l2.escalation" in types

    def test_publisher_failure_does_not_crash(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.autonomous import L2AutonomousMind

        def bad_publisher(event_type: str, payload: dict[str, Any]) -> None:
            raise RuntimeError("publish error")

        payload = {"action_type": "noop", "confidence": 0.5}
        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps(payload))])
        _patched_gateway(monkeypatch, fake)
        mind = L2AutonomousMind(event_publisher=bad_publisher)
        # should not raise
        d = mind.decide()
        assert d.action.type.value == "noop"


# ---------------------------------------------------------------------------
# should_run_cycle
# ---------------------------------------------------------------------------
class TestCycle:
    def test_first_cycle_should_run(self) -> None:
        from aegis_ai.autonomous import L2AutonomousMind

        mind = L2AutonomousMind()
        assert mind.should_run_cycle() is True

    def test_disabled_should_not_run(self) -> None:
        from aegis_ai.autonomous import L2AutonomousMind

        mind = L2AutonomousMind(enabled=False)
        assert mind.should_run_cycle() is False

    def test_too_soon_should_not_run(self) -> None:
        from aegis_ai.autonomous import L2AutonomousMind

        mind = L2AutonomousMind(cycle_interval_seconds=1800)
        now = 10_000_000
        mind.last_cycle_at_ms = now - 100  # 100ms 前
        assert mind.should_run_cycle(now_ms=now) is False

    def test_after_interval_should_run(self) -> None:
        from aegis_ai.autonomous import L2AutonomousMind

        mind = L2AutonomousMind(cycle_interval_seconds=60)
        now = 10_000_000
        mind.last_cycle_at_ms = now - 61_000  # 61 秒前
        assert mind.should_run_cycle(now_ms=now) is True


# ---------------------------------------------------------------------------
# L2Escalation / L2Decision payload
# ---------------------------------------------------------------------------
class TestPayloads:
    def test_l2_decision_to_payload(self) -> None:
        from aegis_ai.autonomous import L2Action, L2ActionType, L2Decision

        d = L2Decision(
            action=L2Action(
                type=L2ActionType.TASK,
                task_spec={"capability_id": "cap.read"},
                reason="r",
            ),
            plan="p",
            confidence=0.7,
            escalate_to_l3=False,
        )
        p = d.to_payload()
        assert p["action_type"] == "task"
        assert p["task_spec"]["capability_id"] == "cap.read"
        assert p["plan"] == "p"
        assert p["confidence"] == 0.7
        assert p["escalate_to_l3"] is False

    def test_l2_escalation_to_payload(self) -> None:
        from aegis_ai.autonomous import L2Escalation

        e = L2Escalation(
            problem="p",
            context_summary="ctx",
            l1_observations=[{"event_id": "e1"}],
            reason="r",
        )
        p = e.to_payload()
        assert p["problem"] == "p"
        assert p["context_summary"] == "ctx"
        assert p["l1_observations"] == [{"event_id": "e1"}]
        assert p["reason"] == "r"
