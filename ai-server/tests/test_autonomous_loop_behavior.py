from __future__ import annotations

import time
from types import SimpleNamespace

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
from aegis_ai.desire.fulfillment import TaskEffect, TaskResult


class _Catalog:
    def resolve(self, capability_id: str):
        return SimpleNamespace(server_id=capability_id.split(".", 1)[0])


class _Broker:
    def __init__(self, capability_ids: list[str]) -> None:
        self._capabilities = [SimpleNamespace(id=capability_id) for capability_id in capability_ids]
        self._catalog = _Catalog()

    def list_safe_capabilities(self):
        return self._capabilities


class _StatusManager:
    def __init__(self, statuses: dict[str, str]) -> None:
        self._statuses = statuses

    def get_snapshot(self):
        return {
            server_id: {"server_id": server_id, "status": status}
            for server_id, status in self._statuses.items()
        }


class _PressureDesire:
    def __init__(self) -> None:
        self.dimension = SimpleNamespace(
            hidden=False,
            pressure=10.0,
            value=2.0,
            expected_value=7.0,
            drift_rate=0.0,
        )
        self.reductions: list[tuple[str, float]] = []
        self.saved = False

    def get_all_desires(self):
        return {"growth": self.dimension}

    def get_pressure_signature(self):
        return "pressure-signature"

    def get_pressure_state(self):
        return {
            "growth": {
                "pressure": self.dimension.pressure,
                "threshold": 5.0,
                "drift_rate": self.dimension.drift_rate,
                "last_action_at": 0,
            }
        }

    def get_desire(self, name: str):
        return self.dimension if name == "growth" else None

    def reduce_pressure(self, name: str, effectiveness: float):
        self.reductions.append((name, effectiveness))

    def update_value(self, name: str, value: float, reason: str = ""):
        self.dimension.value = value

    def apply_decay(self):
        return None

    def save(self):
        self.saved = True


def test_available_capabilities_use_status_manager_not_localhost(tmp_path) -> None:
    broker = _Broker([
        "ai-server.memory.search",
        "browser-server.page.browse",
        "room-server.environment.get_environment",
        "dev-server.repo.status",
        "pc-server.screenshot.get_screenshot",
        "android-server.device.get_status",
    ])
    status_manager = _StatusManager({
        "browser-server": "online",
        "room-server": "degraded",
        "dev-server": "online",
        "pc-server": "offline",
        "android-server": "offline",
    })
    loop = AutonomousLoop(
        tool_broker=broker,
        status_manager=status_manager,
        data_dir=str(tmp_path / "autonomous"),
    )

    available = loop._available_safe_capability_ids()

    assert "ai-server.memory.search" in available
    assert "browser-server.page.browse" in available
    assert "room-server.environment.get_environment" in available
    assert "dev-server.repo.status" in available
    assert "pc-server.screenshot.get_screenshot" not in available
    assert "android-server.device.get_status" not in available
    assert loop.get_status()["available_capability_count"] == 4


def test_llm_interval_gate_waits_full_thirty_minutes(tmp_path) -> None:
    desire = _PressureDesire()
    loop = AutonomousLoop(
        llm_provider=object(),
        desire_system=desire,
        data_dir=str(tmp_path / "autonomous"),
        fallback_interval_seconds=60,
    )
    generated: list[bool] = []
    loop._generate_tasks = lambda low: generated.append(True) or []
    loop._execute_tasks = lambda tasks: []
    loop._update_desires = lambda results: None
    loop._record_experiences = lambda tasks, results: None
    loop._decide_next_interval = lambda results: 60
    loop._log_execution = lambda tasks, results: None

    loop._last_llm_call_ms = int(time.time() * 1000)
    loop._execute_cycle()
    assert generated == []
    assert loop.get_status()["last_skip_reason"].startswith("llm_interval_gate")

    loop._last_llm_call_ms = int(time.time() * 1000) - loop._min_llm_interval_ms
    loop._last_pressure_signature = ""
    loop._execute_cycle()
    assert generated == [True]


def test_useful_result_reduces_pressure(monkeypatch, tmp_path) -> None:
    desire = _PressureDesire()
    loop = AutonomousLoop(
        desire_system=desire,
        data_dir=str(tmp_path / "autonomous"),
    )

    monkeypatch.setattr(
        "aegis_ai.desire.fulfillment.evaluate_task_result",
        lambda **kwargs: TaskResult(
            tool_success=True,
            task_effect=TaskEffect.USEFUL,
            desire_delta_hint={"growth": 0.5},
            summary="Useful",
        ),
    )

    loop._update_desires([{
        "desire": "growth",
        "capability_id": "browser-server.page.browse",
        "success": True,
        "full_output": {"result": "Useful result"},
    }])

    assert desire.reductions == [("growth", 1.0)]
    assert desire.dimension.value == 2.5
    assert desire.saved is True


def test_needs_followup_uses_half_pressure_reduction(monkeypatch, tmp_path) -> None:
    desire = _PressureDesire()
    loop = AutonomousLoop(
        desire_system=desire,
        data_dir=str(tmp_path / "autonomous"),
    )
    monkeypatch.setattr(
        "aegis_ai.desire.fulfillment.evaluate_task_result",
        lambda **kwargs: TaskResult(
            tool_success=True,
            task_effect=TaskEffect.NEEDS_FOLLOWUP,
            desire_delta_hint={"growth": 0.2},
            summary="Needs follow-up",
        ),
    )

    loop._update_desires([{
        "desire": "growth",
        "capability_id": "browser-server.page.browse",
        "success": True,
        "full_output": {"result": "Partial result"},
    }])

    assert desire.reductions == [("growth", 0.5)]


def test_no_effect_does_not_reduce_pressure(monkeypatch, tmp_path) -> None:
    desire = _PressureDesire()
    loop = AutonomousLoop(
        desire_system=desire,
        data_dir=str(tmp_path / "autonomous"),
    )
    monkeypatch.setattr(
        "aegis_ai.desire.fulfillment.evaluate_task_result",
        lambda **kwargs: TaskResult(
            tool_success=True,
            task_effect=TaskEffect.NO_EFFECT,
            desire_delta_hint={"growth": 0.0},
            summary="No effect",
        ),
    )

    loop._update_desires([{
        "desire": "growth",
        "capability_id": "ai-server.agora.read_posts",
        "success": True,
        "full_output": {"result": "AGORA: No new posts."},
    }])

    assert desire.reductions == []


def test_successful_result_is_sent_to_llm_followup_decision(tmp_path) -> None:
    loop = AutonomousLoop(
        llm_provider=object(),
        tool_broker=object(),
        data_dir=str(tmp_path / "autonomous"),
    )
    followup_calls = []
    loop._generate_follow_up_tasks = (
        lambda tasks, results: followup_calls.append((tasks, results)) or []
    )
    tasks = [{"capability_id": "ai-server.agora.read_posts"}]
    results = [{"success": True, "result": "ordinary successful result"}]

    assert loop._self_regressive_loop(tasks, results, max_iterations=1) == []
    assert followup_calls == [(tasks, results)]


def test_execution_log_stores_image_artifact_instead_of_base64(tmp_path) -> None:
    loop = AutonomousLoop(data_dir=str(tmp_path / "autonomous"))
    image_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADElEQVR42mP8z8BQDwAFgwJ/luzG8QAAAABJRU5ErkJggg=="
    )

    loop._log_execution(
        [{"desire": "growth", "action": "look", "capability_id": "pc-server.screenshot.get_screenshot"}],
        [{"success": True, "result": "ok", "full_output": {"image_base64": image_base64, "image_mime": "image/png"}}],
    )

    log_text = (tmp_path / "autonomous" / "execution_log.jsonl").read_text(encoding="utf-8")
    assert image_base64 not in log_text
    assert "image_artifact" in log_text
    assert any((tmp_path / "autonomous" / "artifacts").iterdir())
