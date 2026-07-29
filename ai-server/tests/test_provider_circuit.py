"""Tests for LLM provider balance circuit breaker."""

from __future__ import annotations

from aegis_ai.llm.cost_tracker import CostTracker
from aegis_ai.llm.provider_circuit import LlmProviderCircuit, is_balance_error
from aegis_ai.health.alert_manager import HealthAlertManager


class _FakeBalanceError(Exception):
    def __init__(self, message: str = "Error code: 402 - Insufficient Balance", status_code: int = 402):
        super().__init__(message)
        self.status_code = status_code


def test_is_balance_error_detects_402() -> None:
    assert is_balance_error(_FakeBalanceError())
    assert is_balance_error(Exception("Insufficient Balance"))
    assert not is_balance_error(Exception("rate limit exceeded"))


def test_circuit_opens_after_threshold(tmp_path) -> None:
    circuit = LlmProviderCircuit(failure_threshold=2, cooldown_ms=60_000)
    assert not circuit.is_open()
    assert not circuit.record_error(Exception("timeout"))
    newly = circuit.record_error(_FakeBalanceError())
    assert newly is False
    newly = circuit.record_error(_FakeBalanceError())
    assert newly is True
    assert circuit.is_open()
    assert circuit.remaining_ms() > 0


def test_cost_tracker_denies_when_circuit_open(tmp_path, monkeypatch) -> None:
    from aegis_ai.llm import provider_circuit as pc

    circuit = LlmProviderCircuit(failure_threshold=1, cooldown_ms=60_000)
    monkeypatch.setattr(pc, "PROVIDER_CIRCUIT", circuit)
    circuit.record_error(_FakeBalanceError())

    tracker = CostTracker(daily_budget=10.0, monthly_budget=100.0, path=str(tmp_path / "cost.jsonl"))
    assert tracker.can_afford(100) is False
    assert tracker.provider_circuit_open() is True
    summary = tracker.get_usage_summary()
    assert summary["provider_circuit"]["open"] is True


def test_health_alert_on_open_circuit(tmp_path, monkeypatch) -> None:
    from aegis_ai.llm import provider_circuit as pc

    circuit = LlmProviderCircuit(failure_threshold=1, cooldown_ms=60_000)
    monkeypatch.setattr(pc, "PROVIDER_CIRCUIT", circuit)
    circuit.record_error(_FakeBalanceError())

    manager = HealthAlertManager(data_dir=str(tmp_path / "health"), llm_provider=object())
    # Give a stub with generate so only circuit triggers
    class _LLM:
        def generate(self, *args, **kwargs):
            return None

    manager = HealthAlertManager(data_dir=str(tmp_path / "health"), llm_provider=_LLM())
    alert = manager.check_llm_provider()
    assert alert is not None
    assert alert.alert_type == "llm_unavailable"
    assert alert.severity == "critical"
    assert "balance" in alert.message.lower() or "circuit" in alert.message.lower()


def test_android_unknown_does_not_alert(tmp_path) -> None:
    class _Status:
        def get_snapshot(self):
            return {"android-server": {"status": "unknown"}}

    manager = HealthAlertManager(
        data_dir=str(tmp_path / "health"),
        status_manager=_Status(),
    )
    alert = manager.check_server_reachable("android-server", "localhost", 50054)
    assert alert is None


def test_android_offline_alerts_without_tcp(tmp_path, monkeypatch) -> None:
    class _Status:
        def get_snapshot(self):
            return {"android-server": {"status": "offline", "last_heartbeat_ms": 1}}

    manager = HealthAlertManager(
        data_dir=str(tmp_path / "health"),
        status_manager=_Status(),
    )

    def _fail_tcp(*args, **kwargs):
        raise AssertionError("TCP probe must not be used for android-server")

    monkeypatch.setattr(manager, "_check_port", _fail_tcp)
    alert = manager.check_server_reachable("android-server", "localhost", 50054)
    assert alert is not None
    assert alert.details.get("check") == "presence"
