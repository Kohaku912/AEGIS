from __future__ import annotations

from types import SimpleNamespace

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
from aegis_ai.autonomous.initiative_engine import InitiativeEngine
from aegis_ai.autonomous.models import ActionCandidate, CapabilityDisposition
from aegis_ai.desire.pressure import PressureEngine


def test_unknown_event_applies_pressure_delta(tmp_path) -> None:
    engine = PressureEngine(str(tmp_path / "pressure"))
    engine.accumulate_from_event("user_support", "user_situation", 1.2)
    assert engine.get_pressure("user_support") >= 1.2


def test_preflight_allows_pending_observations(tmp_path) -> None:
    desire = SimpleNamespace(
        apply_decay=lambda: None,
        get_pressure_state=lambda: {"user_support": {"pressure": 0.2}},
    )
    loop = AutonomousLoop(
        llm_provider=SimpleNamespace(),
        desire_system=desire,
        data_dir=str(tmp_path / "loop"),
    )
    loop._pending_actionable_observations = [
        {"source": "social.inbox.received", "tags": ["event"], "description": "new mail"}
    ]
    ok, reason = loop._preflight_check()
    assert ok is True
    assert reason == "pending_observation"


def test_evaluate_event_queues_tagged_work(tmp_path) -> None:
    desire = SimpleNamespace(
        apply_decay=lambda: None,
        get_pressure_state=lambda: {"user_support": {"pressure": 0.0}},
        accumulate_pressure=lambda *args, **kwargs: None,
    )
    loop = AutonomousLoop(desire_system=desire, data_dir=str(tmp_path / "loop"))
    loop._initiative_engine = InitiativeEngine(str(tmp_path / "initiative"))
    result = loop.evaluate_event("social.inbox.received", {"safe_message": "reply needed", "urgency": 0.9})
    assert result["queued"] is True
    queued = loop._pending_actionable_observations[0]
    assert "event" in queued["tags"]
    assert loop._has_interval_bypass_work() is True


def test_cheap_interrupt_saves_become_execute_now(tmp_path) -> None:
    engine = InitiativeEngine(str(tmp_path / "initiative"))
    candidate = ActionCandidate(
        candidate_id="c1",
        goal="look up what the user is watching",
        why_now="idle at home",
        trigger="user_state",
        expected_benefit=0.5,
        urgency=0.4,
        relevance=0.5,
        risk=0.1,
        uncertainty=0.2,
        interruption_cost=0.1,
        candidate_capabilities=["browser-server.search.query"],
    )
    decision, _reason = engine.evaluate(candidate, CapabilityDisposition.EXECUTE_SAFE)
    assert decision.value == "execute_now"
