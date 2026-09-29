from __future__ import annotations

from types import SimpleNamespace

from aegis_ai.intake.l1_models import L1ActionType, L1Observation, RequiredIntelligence
from aegis_ai.intake.l1_router import L1Router


def test_decide_returns_direct_capability_for_structured_low_risk_event() -> None:
    router = L1Router(llm_gateway=SimpleNamespace())
    observation = L1Observation(
        event_id="evt-1",
        meaning="Turn on the room light",
        value=0.8,
        priority=0.4,
        required_intelligence=RequiredIntelligence.LOW,
        confidence=0.9,
        raw={
            "summary_bucket": "task_candidate",
            "should_execute_directly": True,
            "_event": {
                "capability_id": "room-server.light.turn_on",
                "capability_args": {"room": "bedroom"},
            },
        },
    )

    decision = router.decide(observation)

    assert decision.action.type == L1ActionType.CAPABILITY
    assert decision.action.capability_id == "room-server.light.turn_on"
    assert decision.action.args == {"room": "bedroom"}
    assert "directly" in decision.reasoning.lower()


def test_decide_keeps_observe_when_direct_signal_missing() -> None:
    router = L1Router(llm_gateway=SimpleNamespace())
    observation = L1Observation(
        event_id="evt-2",
        meaning="The user opened GitHub Desktop",
        value=0.5,
        priority=0.2,
        required_intelligence=RequiredIntelligence.LOW,
        confidence=0.8,
        raw={
            "summary_bucket": "user_state",
            "_event": {
                "capability_id": "pc-server.window.capture_active_window",
                "capability_args": {},
            },
        },
    )

    decision = router.decide(observation)

    assert decision.action.type == L1ActionType.OBSERVE
