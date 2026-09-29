"""Tests for L1 Router (DASHBOARD_V3_PLAN.md Phase L2)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from aegis_ai.intake.l1_models import (
    L1Action,
    L1ActionType,
    L1Decision,
    L1Escalation,
    L1Observation,
    RequiredIntelligence,
)
from aegis_ai.intake.l1_router import L1Router
from aegis_ai.llm.gateway import LLMGateway
from aegis_ai.llm.router import LLMResponse
from aegis_ai.llm.settings_resolver import LLMSettingsResolver


# ── Fixtures ──────────────────────────────────────────────────


@pytest.fixture()
def llm_yaml_with_layers(tmp_path: Path) -> Path:
    data = {
        "version": "1.0.0",
        "profiles": {
            "l1_default": {
                "provider": "openai",
                "model": "deepseek-v4-flash",
                "max_tokens": 1024,
                "temperature": 0.3,
                "reasoning_level": "low",
                "timeout_seconds": 15,
                "max_tool_rounds": 3,
            },
        },
        "safety": {
            "allowed_models": ["deepseek-v4-flash"],
            "max_tokens_upper_bound": 128000,
            "max_temperature": 2.0,
            "min_temperature": 0.0,
        },
    }
    p = tmp_path / "llm.yaml"
    p.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return p


class _ScriptedGateway:
    """request_json() の戻り値を script で制御する fake LLMGateway."""

    def __init__(self, response_payload: dict[str, Any] | None = None, *, fail: bool = False) -> None:
        self.response_payload = response_payload or {
            "meaning": "User said hello",
            "value": 0.3,
            "priority": 0.2,
            "required_intelligence": "low",
            "confidence": 0.8,
        }
        self.fail = fail
        self.calls: list[dict[str, Any]] = []

    def request_json(
        self,
        layer: str,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int | None = None,
        temperature: float | None = None,
        context_meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.calls.append(
            {
                "layer": layer,
                "prompt": prompt,
                "system_prompt": system_prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "context_meta": context_meta,
            }
        )
        if self.fail:
            return {"error": "synthetic_failure"}
        return self.response_payload


@pytest.fixture()
def scripted_gateway() -> _ScriptedGateway:
    return _ScriptedGateway()


@pytest.fixture()
def l1_router(scripted_gateway: _ScriptedGateway) -> L1Router:
    return L1Router(llm_gateway=scripted_gateway)  # type: ignore[arg-type]


# ── Models 単体テスト ──────────────────────────────────────


class TestL1Models:
    def test_required_intelligence_enum(self) -> None:
        assert RequiredIntelligence.LOW.value == "low"
        assert RequiredIntelligence.MEDIUM.value == "medium"
        assert RequiredIntelligence.HIGH.value == "high"

    def test_l1_observation_defaults(self) -> None:
        obs = L1Observation(event_id="e1", meaning="x")
        assert obs.event_id == "e1"
        assert obs.meaning == "x"
        assert obs.value == 0.0
        assert obs.priority == 0.0
        assert obs.required_intelligence == RequiredIntelligence.LOW
        assert obs.confidence == 0.0

    def test_l1_action_escalate(self) -> None:
        a = L1Action(type=L1ActionType.ESCALATE, reason="test")
        assert a.type == L1ActionType.ESCALATE
        assert a.reason == "test"
        assert a.capability_id == ""

    def test_l1_escalation_to_payload(self) -> None:
        esc = L1Escalation(
            event_id="e1",
            reason="needs deep reasoning",
            problem="complex X",
            context={"v": 0.9},
            required_intelligence=RequiredIntelligence.HIGH,
        )
        payload = esc.to_payload()
        assert payload["event_id"] == "e1"
        assert payload["required_intelligence"] == "high"
        assert payload["problem"] == "complex X"
        assert payload["context"] == {"v": 0.9}


# ── L1Router.observe() テスト ──────────────────────────────


class TestL1RouterObserve:
    def test_observe_calls_l1_layer(self, l1_router: L1Router, scripted_gateway: _ScriptedGateway) -> None:
        l1_router.observe(
            {"type": "user.message", "message": "hello"},
            event_id="e1",
            context_capsule={"user_state": {"current_activity": "coding"}},
        )
        assert len(scripted_gateway.calls) == 1
        call = scripted_gateway.calls[0]
        assert call["layer"] == "L1"
        assert call["max_tokens"] == 512
        assert call["temperature"] == 0.1
        # system prompt は L1 仕様
        assert "L1" in call["system_prompt"] or "Perception" in call["system_prompt"]
        # context_meta に event_id
        assert call["context_meta"]["event_id"] == "e1"
        assert call["context_meta"]["l1_state"]["event_focus"]["message"] == "hello"
        assert (
            call["context_meta"]["l1_state"]["aegis_context"]["user_state"]["current_activity"]
            == "coding"
        )

    def test_observe_returns_observation(self, l1_router: L1Router) -> None:
        obs = l1_router.observe({"type": "user.message", "message": "hi"}, event_id="e1")
        assert obs.event_id == "e1"
        assert obs.meaning == "User said hello"
        assert obs.value == 0.3
        assert obs.priority == 0.2
        assert obs.required_intelligence == RequiredIntelligence.LOW
        assert obs.confidence == 0.8

    def test_observe_handles_high_intelligence(self) -> None:
        gateway = _ScriptedGateway(
            response_payload={
                "meaning": "complex request",
                "value": 0.9,
                "priority": 0.8,
                "required_intelligence": "high",
                "confidence": 0.7,
            }
        )
        router = L1Router(llm_gateway=gateway)  # type: ignore[arg-type]
        obs = router.observe({"type": "task.request", "summary": "design X"}, event_id="e2")
        assert obs.required_intelligence == RequiredIntelligence.HIGH
        assert obs.value == 0.9

    def test_observe_handles_invalid_intelligence_string(self) -> None:
        """不正な required_intelligence 文字列は LOW にフォールバック."""
        gateway = _ScriptedGateway(
            response_payload={"meaning": "x", "value": 0.1, "priority": 0.1, "required_intelligence": "mega", "confidence": 0.5}
        )
        router = L1Router(llm_gateway=gateway)  # type: ignore[arg-type]
        obs = router.observe({"type": "x"}, event_id="e3")
        assert obs.required_intelligence == RequiredIntelligence.LOW

    def test_observe_disabled_returns_default(self) -> None:
        gateway = _ScriptedGateway()
        router = L1Router(llm_gateway=gateway, enabled=False)  # type: ignore[arg-type]
        obs = router.observe({"type": "x"}, event_id="e1")
        assert obs.meaning == "<l1 disabled>"
        assert obs.value == 0.0
        # LLM 呼び出しが行われない
        assert len(gateway.calls) == 0

    def test_observe_handles_llm_failure(self) -> None:
        gateway = _ScriptedGateway(fail=True)
        router = L1Router(llm_gateway=gateway)  # type: ignore[arg-type]
        obs = router.observe({"type": "x"}, event_id="e1")
        # error 時は fail-closed anomaly
        assert obs.meaning == "<l1 unavailable>"
        assert obs.value == 1.0
        assert obs.required_intelligence == RequiredIntelligence.HIGH
        assert "error" in obs.raw


# ── L1Router.decide() テスト ───────────────────────────────


class TestL1RouterDecide:
    def test_high_intelligence_escalates(self, l1_router: L1Router) -> None:
        obs = L1Observation(
            event_id="e1",
            meaning="complex",
            value=0.5,
            priority=0.5,
            required_intelligence=RequiredIntelligence.HIGH,
        )
        decision = l1_router.decide(obs)
        assert decision.action.type == L1ActionType.ESCALATE
        assert "L1 escalates to L2" in decision.reasoning

    def test_high_priority_value_escalates(self, l1_router: L1Router) -> None:
        obs = L1Observation(
            event_id="e1",
            meaning="urgent",
            value=0.9,
            priority=0.9,
            required_intelligence=RequiredIntelligence.MEDIUM,
        )
        decision = l1_router.decide(obs)
        assert decision.action.type == L1ActionType.ESCALATE

    def test_low_value_ignores(self, l1_router: L1Router) -> None:
        obs = L1Observation(
            event_id="e1",
            meaning="trivial",
            value=0.1,  # min_value_for_action=0.3 未満
            priority=0.1,
            required_intelligence=RequiredIntelligence.LOW,
        )
        decision = l1_router.decide(obs)
        assert decision.action.type == L1ActionType.IGNORE

    def test_moderate_value_observes(self, l1_router: L1Router) -> None:
        obs = L1Observation(
            event_id="e1",
            meaning="normal",
            value=0.5,  # min 以上 / escalation 閾値未満
            priority=0.3,
            required_intelligence=RequiredIntelligence.LOW,
        )
        decision = l1_router.decide(obs)
        assert decision.action.type == L1ActionType.OBSERVE

    def test_should_escalate_helper(self, l1_router: L1Router) -> None:
        # HIGH intelligence
        obs_high = L1Observation(event_id="e1", meaning="x", required_intelligence=RequiredIntelligence.HIGH)
        assert l1_router.should_escalate(obs_high) is True
        # HIGH priority/value
        obs_pv = L1Observation(event_id="e2", meaning="x", value=0.9, priority=0.9, required_intelligence=RequiredIntelligence.LOW)
        assert l1_router.should_escalate(obs_pv) is True
        # LOW everything
        obs_low = L1Observation(event_id="e3", meaning="x", value=0.1, priority=0.1, required_intelligence=RequiredIntelligence.LOW)
        assert l1_router.should_escalate(obs_low) is False


# ── L1Router.escalate() / route() テスト ─────────────────────


class TestL1RouterEscalateAndRoute:
    def test_escalate_creates_escalation(self, l1_router: L1Router) -> None:
        obs = L1Observation(
            event_id="e1",
            meaning="complex X",
            value=0.8,
            priority=0.7,
            required_intelligence=RequiredIntelligence.HIGH,
        )
        esc = l1_router.escalate(obs, reason="test reason")
        assert esc.event_id == "e1"
        assert esc.reason == "test reason"
        assert esc.problem == "complex X"
        assert esc.required_intelligence == RequiredIntelligence.HIGH
        payload = esc.to_payload()
        assert payload["required_intelligence"] == "high"

    def test_route_combines_observe_and_decide(self, l1_router: L1Router) -> None:
        # デフォルト scripted: low intelligence → OBSERVE
        decision = l1_router.route({"type": "user.message", "message": "hi"}, event_id="e1")
        assert decision.event_id == "e1"
        assert decision.action.type == L1ActionType.OBSERVE
        assert decision.observation is not None
        assert decision.observation.meaning == "User said hello"

    def test_route_with_high_intelligence_escalates(self) -> None:
        gateway = _ScriptedGateway(
            response_payload={
                "meaning": "complex",
                "value": 0.9,
                "priority": 0.9,
                "required_intelligence": "high",
                "confidence": 0.7,
            }
        )
        router = L1Router(llm_gateway=gateway)  # type: ignore[arg-type]
        decision = router.route({"type": "task.request"}, event_id="e1")
        assert decision.action.type == L1ActionType.ESCALATE


# ── L1Router.summarize_event 動作確認 ─────────────────────────


class TestSummarizeEvent:
    def test_summarize_extracts_known_fields(self, l1_router: L1Router) -> None:
        from aegis_ai.intake.l1_router import _summarize_event
        s = _summarize_event({"type": "x", "message": "hi", "event_id": "e1"})
        assert "type=x" in s
        assert "message=hi" in s
        assert "event_id=e1" in s

    def test_summarize_falls_back_to_first_keys(self, l1_router: L1Router) -> None:
        from aegis_ai.intake.l1_router import _summarize_event
        s = _summarize_event({"foo": "bar", "baz": "qux"})
        assert "foo=bar" in s
        assert "baz=qux" in s

    def test_summarize_empty(self, l1_router: L1Router) -> None:
        from aegis_ai.intake.l1_router import _summarize_event
        assert _summarize_event({}) == "<empty event>"
