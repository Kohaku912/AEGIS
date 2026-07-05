from __future__ import annotations

import time
from types import SimpleNamespace

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
from aegis_ai.desire.fulfillment import TaskEffect, TaskResult


class _Catalog:
    def __init__(self, capability_ids: list[str] | None = None) -> None:
        self._capability_ids = capability_ids or []

    def resolve(self, capability_id: str):
        return SimpleNamespace(
            server_id=capability_id.split(".", 1)[0],
            input_schema={"type": "object", "properties": {}, "required": []},
            operation_category="read",
            risk_level="read_only",
            side_effects=[],
            title=capability_id,
        )

    def list_for_tools(self, cap_ids: set[str] | list[str]):
        return [
            {
                "type": "function",
                "function": {
                    "name": capability_id.replace(".", "__").replace("-", "_"),
                    "description": capability_id,
                    "parameters": {"type": "object", "properties": {}},
                },
            }
            for capability_id in cap_ids
        ]

    def tool_name_to_cap_id(self, tool_name: str) -> str:
        for capability_id in self._capability_ids:
            if capability_id.replace(".", "__").replace("-", "_") == tool_name:
                return capability_id
        return tool_name.replace("__", ".").replace("_server", "-server")


class _Broker:
    def __init__(self, capability_ids: list[str]) -> None:
        self._capabilities = [SimpleNamespace(id=capability_id) for capability_id in capability_ids]
        self._catalog = _Catalog(capability_ids)

    def list_safe_capabilities(self):
        return self._capabilities


class _ExecutingBroker(_Broker):
    def __init__(self, capability_ids: list[str], output: dict | None = None) -> None:
        super().__init__(capability_ids)
        self.output = output or {"result": "ordinary successful result from broker"}

    def execute(self, request):
        from tool_broker import InvokeStatus, ToolExecutionResult

        return ToolExecutionResult(
            request_id=getattr(request, "request_id", ""),
            status=InvokeStatus.SUCCESS,
            output=self.output,
        )


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


def test_llm_interval_gate_waits_thirty_minutes_by_default(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("AEGIS_MIN_LLM_INTERVAL_MS", raising=False)
    desire = _PressureDesire()
    loop = AutonomousLoop(
        llm_provider=object(),
        desire_system=desire,
        data_dir=str(tmp_path / "autonomous"),
        fallback_interval_seconds=60,
    )
    assert loop._min_llm_interval_ms == 1_800_000
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


def test_same_pressure_signature_does_not_block_high_pressure_llm(tmp_path) -> None:
    desire = _PressureDesire()
    loop = AutonomousLoop(
        llm_provider=object(),
        desire_system=desire,
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._last_pressure_signature = desire.get_pressure_signature()

    should_proceed, reason = loop._preflight_check()

    assert should_proceed is True
    assert reason == "ok"


class _NoActionThenToolLLM:
    def __init__(self, tool_name: str) -> None:
        self.tool_name = tool_name
        self.calls = 0

    def generate_with_tools(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            return SimpleNamespace(success=True, content="I am unsure what to do.", tool_calls=[])
        return SimpleNamespace(
            success=True,
            content="",
            tool_calls=[{"function": self.tool_name, "arguments": {}}],
        )


class _NoActionLLM:
    def __init__(self) -> None:
        self.calls = 0

    def generate_with_tools(self, **kwargs):
        self.calls += 1
        return SimpleNamespace(success=True, content="No action.", tool_calls=[])


def test_high_pressure_no_action_is_reprompted_once(tmp_path) -> None:
    capability_ids = ["ai-server.memory.search"]
    broker = _Broker(capability_ids)
    tool_name = capability_ids[0].replace(".", "__").replace("-", "_")
    llm = _NoActionThenToolLLM(tool_name)
    loop = AutonomousLoop(
        llm_provider=llm,
        desire_system=_PressureDesire(),
        tool_broker=broker,
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._log_audit_event = lambda **kwargs: None

    tasks = loop._generate_tasks([{"name": "user_support", "gap": 5.0}])

    assert llm.calls == 2
    assert tasks
    assert tasks[0]["capability_id"] == "ai-server.memory.search"
    assert loop.get_status()["selected_tool_count"] == 1


def test_repeated_no_action_does_not_select_or_clear_pressure(tmp_path) -> None:
    llm = _NoActionLLM()
    loop = AutonomousLoop(
        llm_provider=llm,
        desire_system=_PressureDesire(),
        tool_broker=_Broker(["ai-server.memory.search"]),
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._log_audit_event = lambda **kwargs: None
    loop._record_failure_lesson = lambda **kwargs: None

    tasks = loop._generate_tasks([{"name": "user_support", "gap": 5.0}])

    assert tasks == []
    assert llm.calls == 2
    status = loop.get_status()
    assert status["selected_tool_count"] == 0
    assert status["last_decision"] == "no_action"
    assert status["last_no_action_reason"]


def test_execute_tasks_accepts_tool_execution_result_object(tmp_path) -> None:
    capability_id = "ai-server.memory.search"
    loop = AutonomousLoop(
        tool_broker=_ExecutingBroker([capability_id]),
        data_dir=str(tmp_path / "autonomous"),
    )

    results = loop._execute_tasks([{
        "desire": "growth",
        "action": "Search memory",
        "capability_id": capability_id,
        "arguments": {},
    }])

    assert results == [{
        "desire": "growth",
        "action": "Search memory",
        "capability_id": capability_id,
        "result": "ordinary successful result from broker",
        "success": True,
        "full_output": {"result": "ordinary successful result from broker"},
        "skill_used": None,
        "workflow_used": None,
    }]


def test_representative_capability_is_included_when_retriever_misses(tmp_path) -> None:
    capability_ids = ["ai-server.memory.search", "room-server.environment.get_environment"]
    broker = _Broker(capability_ids)
    tool_name = "ai_server__memory__search"
    llm = _NoActionThenToolLLM(tool_name)

    class _Retriever:
        def select_for_request(self, *args, **kwargs):
            return SimpleNamespace(retrieved_schema_tools=[], all_candidate_ids=[])

    loop = AutonomousLoop(
        llm_provider=llm,
        desire_system=_PressureDesire(),
        tool_broker=broker,
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._capability_retriever = _Retriever()
    loop._log_audit_event = lambda **kwargs: None

    tasks = loop._generate_tasks([{"name": "user_support", "gap": 5.0}])

    assert tasks[0]["capability_id"] == "ai-server.memory.search"
    assert "ai-server.memory.search" in loop.get_status()["candidate_capability_ids"]


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
            pressure_reduction=0.7,
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

    assert desire.reductions == [("growth", 0.7)]
    assert desire.dimension.value == 2.5
    assert desire.saved is True


def test_pressure_reduction_comes_from_llm_result(monkeypatch, tmp_path) -> None:
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
            pressure_reduction=0.25,
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

    assert desire.reductions == [("growth", 0.25)]


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
