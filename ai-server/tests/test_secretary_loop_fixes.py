"""Tests for secretary-loop gap fixes (circuit, android health, fulfillment, goals)."""

from __future__ import annotations

from pathlib import Path

from aegis_ai.desire.fulfillment import TaskEffect, evaluate_task_result, _structural_fallback
from aegis_ai.health.alert_manager import HealthAlertManager
from aegis_ai.llm.cost_tracker import CostTracker
from aegis_ai.llm.provider_circuit import LlmProviderCircuit, is_balance_error
from aegis_ai.personal_ai.situation import _normalize_observation_source


class _FakeBalanceError(Exception):
    def __init__(self, message: str = "Error code: 402 - Insufficient Balance", status_code: int = 402):
        super().__init__(message)
        self.status_code = status_code


def test_is_balance_error_detects_402() -> None:
    assert is_balance_error(_FakeBalanceError())
    assert is_balance_error(Exception("Insufficient Balance"))
    assert not is_balance_error(Exception("rate limit exceeded"))


def test_circuit_opens_after_threshold(tmp_path: Path) -> None:
    circuit = LlmProviderCircuit(failure_threshold=2, cooldown_ms=60_000)
    assert not circuit.is_open()
    assert not circuit.record_error(Exception("timeout"))
    assert circuit.record_error(_FakeBalanceError()) is False
    assert circuit.record_error(_FakeBalanceError()) is True
    assert circuit.is_open()


def test_cost_tracker_denies_when_circuit_open(tmp_path: Path, monkeypatch) -> None:
    from aegis_ai.llm import provider_circuit as pc

    circuit = LlmProviderCircuit(failure_threshold=1, cooldown_ms=60_000)
    monkeypatch.setattr(pc, "PROVIDER_CIRCUIT", circuit)
    circuit.record_error(_FakeBalanceError())
    tracker = CostTracker(daily_budget=10.0, monthly_budget=100.0, path=str(tmp_path / "cost.jsonl"))
    assert tracker.can_afford(100) is False


def test_health_alert_on_open_circuit(tmp_path: Path, monkeypatch) -> None:
    from aegis_ai.llm import provider_circuit as pc

    circuit = LlmProviderCircuit(failure_threshold=1, cooldown_ms=60_000)
    monkeypatch.setattr(pc, "PROVIDER_CIRCUIT", circuit)
    circuit.record_error(_FakeBalanceError())

    class _LLM:
        def generate(self, *args, **kwargs):
            return None

    manager = HealthAlertManager(data_dir=str(tmp_path / "health"), llm_provider=_LLM())
    alert = manager.check_llm_provider()
    assert alert is not None
    assert alert.severity == "critical"


def test_android_unknown_does_not_alert(tmp_path: Path) -> None:
    class _Status:
        def get_snapshot(self):
            return {"android-server": {"status": "unknown"}}

    manager = HealthAlertManager(data_dir=str(tmp_path / "health"), status_manager=_Status())
    assert manager.check_server_reachable("android-server", "localhost", 50054) is None


def test_android_offline_alerts_without_tcp(tmp_path: Path, monkeypatch) -> None:
    class _Status:
        def get_snapshot(self):
            return {"android-server": {"status": "offline", "last_heartbeat_ms": 1}}

    manager = HealthAlertManager(data_dir=str(tmp_path / "health"), status_manager=_Status())

    def _fail_tcp(*args, **kwargs):
        raise AssertionError("TCP probe must not be used for android-server")

    monkeypatch.setattr(manager, "_check_port", _fail_tcp)
    alert = manager.check_server_reachable("android-server", "localhost", 50054)
    assert alert is not None
    assert alert.details.get("check") == "presence"


def test_structural_fulfillment_empty_and_error() -> None:
    empty = _structural_fallback(
        capability_id="ai-server.agora.read_posts",
        tool_success=True,
        output={"count": 0, "posts": []},
        desire_name="social",
    )
    assert empty is not None
    assert empty.task_effect == TaskEffect.NO_EFFECT
    assert empty.pressure_reduction > 0

    failed = evaluate_task_result(
        capability_id="browser-server.page.read",
        tool_success=False,
        output={"error": {"message": "timeout"}},
        desire_name="user_support",
        llm_provider=None,
    )
    assert failed.task_effect == TaskEffect.FAILED


def test_normalize_observation_source() -> None:
    assert _normalize_observation_source("android-server") == "android"
    assert _normalize_observation_source("pc-server") == "pc"
    assert _normalize_observation_source("android") == "android"


def test_interval_bypass_and_goal_helpers(tmp_path: Path) -> None:
    from aegis_ai.autonomous.autonomous_loop import AutonomousLoop

    loop = AutonomousLoop(data_dir=str(tmp_path / "auto"))
    loop._pending_actionable_observations = [
        {"source": "obligation", "description": "Finish packing list", "tags": ["obligation"]}
    ]
    assert loop._has_interval_bypass_work() is True
    goal = loop._resolve_task_goal(
        desire="user_support",
        pending_observations=loop._pending_actionable_observations,
        obligation={"summary": "BrowserStartEvent timeout error"},
        guide={"goal": "generic guide"},
        index=0,
    )
    assert goal == "Finish packing list"
    normalized = loop._user_facing_obligation_summary({"summary": "BrowserStartEvent timeout error"})
    assert "browser" in normalized.lower() or "recover" in normalized.lower()
