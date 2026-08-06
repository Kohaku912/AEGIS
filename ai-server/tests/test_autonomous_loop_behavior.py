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

    def list_autonomous_capabilities(self):
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
        return {server_id: {"server_id": server_id, "status": status} for server_id, status in self._statuses.items()}


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
    broker = _Broker(
        [
            "ai-server.memory.search",
            "browser-server.page.browse",
            "room-server.environment.get_environment",
            "dev-server.repo.status",
            "pc-server.screenshot.get_screenshot",
            "android-server.device.get_status",
        ]
    )
    status_manager = _StatusManager(
        {
            "browser-server": "online",
            "room-server": "degraded",
            "dev-server": "online",
            "pc-server": "offline",
            "android-server": "offline",
        }
    )
    loop = AutonomousLoop(
        tool_broker=broker,
        status_manager=status_manager,
        data_dir=str(tmp_path / "autonomous"),
    )

    available = loop._available_capability_ids()

    assert "ai-server.memory.search" in available
    assert "browser-server.page.browse" in available
    assert "room-server.environment.get_environment" in available
    assert "dev-server.repo.status" in available
    assert "pc-server.screenshot.get_screenshot" not in available
    assert "android-server.device.get_status" not in available
    assert loop.get_status()["available_capability_count"] == 4


def test_decision_axes_keep_four_operational_priorities(tmp_path) -> None:
    loop = AutonomousLoop(
        desire_system=_PressureDesire(),
        status_manager=_StatusManager({"pc-server": "offline", "browser-server": "online"}),
        curiosity_system=object(),
        data_dir=str(tmp_path / "autonomous"),
    )

    axes = loop._build_decision_axes(
        [
            {"name": "user_support", "pressure": 7.0},
            {"name": "growth", "pressure": 6.0},
        ]
    )

    assert set(axes) == {"user_commitment", "system_health", "learning", "curiosity"}
    assert axes["user_commitment"] == 7.0
    assert axes["system_health"] == 1.0
    assert axes["learning"] == 6.0
    assert axes["curiosity"] == 1.0


def test_llm_interval_gate_waits_thirty_minutes_by_default(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("AEGIS_MIN_LLM_INTERVAL_MS", raising=False)
    desire = _PressureDesire()
    # Gate only applies when pressure is below the threshold (desire fires bypass it).
    desire.dimension.pressure = 1.0
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
    # Avoid preflight "all_pressure_below_threshold" short-circuit once the interval opens.
    loop._preflight_check = lambda: (True, "ok")
    loop._get_low_desires = lambda: [{"name": "growth", "gap": 1.0, "pressure": 1.0}]

    loop._last_llm_call_ms = int(time.time() * 1000)
    loop._execute_cycle(force_desire=False)
    assert generated == []
    assert loop.get_status()["last_skip_reason"].startswith("llm_interval_gate")

    loop._last_llm_call_ms = int(time.time() * 1000) - loop._min_llm_interval_ms
    loop._last_pressure_signature = ""
    loop._execute_cycle(force_desire=False)
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
            return SimpleNamespace(success=True, content="", tool_calls=[])
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


def test_empty_tool_response_is_retried_once(tmp_path) -> None:
    """An empty body with no tool call is not a decision — retry once for an answer."""
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
    assert len(tasks) == 1
    assert tasks[0]["capability_id"] == capability_ids[0]
    assert loop.get_status()["selected_tool_count"] == 1
    assert loop.get_status()["last_decision"] == "action_selected"


def test_explicit_no_action_reason_is_not_retried(tmp_path) -> None:
    """A stated non-action reason is intentional — do not double-call the LLM."""
    llm = _NoActionLLM()
    loop = AutonomousLoop(
        llm_provider=llm,
        desire_system=_PressureDesire(),
        tool_broker=_Broker(["ai-server.memory.search"]),
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._log_audit_event = lambda **kwargs: None

    tasks = loop._generate_tasks([{"name": "user_support", "gap": 5.0}])

    assert llm.calls == 1
    assert tasks == []
    assert loop.get_status()["last_decision"] == "no_action"


def test_repeated_no_action_does_not_select_or_clear_pressure(tmp_path) -> None:
    llm = _NoActionLLM()
    loop = AutonomousLoop(
        llm_provider=llm,
        desire_system=_PressureDesire(),
        tool_broker=_Broker(["ai-server.memory.search"]),
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._log_audit_event = lambda **kwargs: None
    failure_lessons = []
    loop._record_failure_lesson = lambda **kwargs: failure_lessons.append(kwargs)

    tasks = loop._generate_tasks([{"name": "user_support", "gap": 5.0}])

    assert tasks == []
    assert llm.calls == 1
    assert failure_lessons == []
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

    results = loop._execute_tasks(
        [
            {
                "desire": "growth",
                "action": "Search memory",
                "capability_id": capability_id,
                "arguments": {},
            }
        ]
    )

    assert results == [
        {
            "desire": "growth",
            "action": "Search memory",
            "capability_id": capability_id,
            "result": "ordinary successful result from broker",
            "success": True,
            "full_output": {"result": "ordinary successful result from broker"},
            "skill_used": None,
            "workflow_used": None,
            "goal_status": "",
            "verification_status": "pending",
        }
    ]


def test_representative_capability_is_included_when_retriever_misses(tmp_path) -> None:
    """Empty retrieval falls back to the full catalog — LLM remains free to choose."""
    capability_ids = [
        "browser-server.page.read",
        "ai-server.memory.search",
        "room-server.environment.get_environment",
    ]
    broker = _Broker(capability_ids)
    tool_name = "browser_server__page__read"
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
    # Pass through repetition check so LLM choice is not second-guessed here.
    loop._check_repetition = lambda tasks, _history: tasks  # type: ignore[method-assign]

    tasks = loop._generate_tasks([{"name": "user_support", "gap": 5.0, "pressure": 8.0}])

    assert tasks[0]["capability_id"] == "browser-server.page.read"
    assert "browser-server.page.read" in loop.get_status()["candidate_capability_ids"]


def test_llm_choice_is_not_vetoed_by_no_effect_history(tmp_path) -> None:
    """Past no_effect counts are observational only — never a hard denylist."""
    capability_ids = ["ai-server.agora.read_posts", "ai-server.memory.search"]
    broker = _Broker(capability_ids)
    tool_name = "ai_server__agora__read_posts"
    llm = _NoActionThenToolLLM(tool_name)

    loop = AutonomousLoop(
        llm_provider=llm,
        desire_system=_PressureDesire(),
        tool_broker=broker,
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._no_effect_counts["ai-server.agora.read_posts"] = 5
    loop._log_audit_event = lambda **kwargs: None
    loop._check_repetition = lambda tasks, _history: tasks  # type: ignore[method-assign]

    tasks = loop._generate_tasks([{"name": "social", "gap": 5.0, "pressure": 8.0}])

    assert tasks
    assert tasks[0]["capability_id"] == "ai-server.agora.read_posts"


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
            fulfillment_score=0.8,
            pressure_reduction=0.7,
            confidence=0.9,
            desire_delta_hint={"growth": 0.5},
            summary="Useful",
            details={"evaluator": "llm"},
        ),
    )

    loop._update_desires(
        [
            {
                "desire": "growth",
                "capability_id": "browser-server.page.browse",
                "success": True,
                "full_output": {"result": "Useful result"},
            }
        ]
    )

    assert desire.reductions == [("growth", 0.7)]
    assert desire.dimension.value == 2.5
    assert desire.saved is True


def test_needs_followup_does_not_reduce_pressure(monkeypatch, tmp_path) -> None:
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
            fulfillment_score=0.2,
            pressure_reduction=0.25,
            confidence=0.8,
            desire_delta_hint={"growth": 0.2},
            summary="Needs follow-up",
            details={"evaluator": "llm"},
        ),
    )

    loop._update_desires(
        [
            {
                "desire": "growth",
                "capability_id": "browser-server.page.browse",
                "success": True,
                "full_output": {"result": "Partial result"},
            }
        ]
    )

    assert desire.reductions == []
    assert desire.dimension.value == 2.0


def test_structural_useful_cannot_reduce_pressure(monkeypatch, tmp_path) -> None:
    """Even if a structural path claimed useful, the gate requires evaluator=llm."""
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
            fulfillment_score=0.9,
            pressure_reduction=0.8,
            confidence=0.9,
            desire_delta_hint={"growth": 0.5},
            summary="Structural fake useful",
            details={"evaluator": "structural"},
        ),
    )

    loop._update_desires(
        [
            {
                "desire": "growth",
                "capability_id": "ai-server.agora.read_posts",
                "success": True,
                "full_output": {"posts": [{"id": 1}]},
            }
        ]
    )

    assert desire.reductions == []
    assert desire.dimension.value == 2.0


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

    loop._update_desires(
        [
            {
                "desire": "growth",
                "capability_id": "ai-server.agora.read_posts",
                "success": True,
                "full_output": {"result": "AGORA: No new posts."},
            }
        ]
    )

    assert desire.reductions == []


def test_successful_result_is_sent_to_llm_followup_decision(tmp_path) -> None:
    loop = AutonomousLoop(
        llm_provider=object(),
        tool_broker=object(),
        data_dir=str(tmp_path / "autonomous"),
    )
    followup_calls = []
    loop._generate_follow_up_tasks = lambda tasks, results: followup_calls.append((tasks, results)) or []
    tasks = [{"capability_id": "ai-server.agora.read_posts"}]
    results = [{"success": True, "result": "ordinary successful result"}]

    assert loop._self_regressive_loop(tasks, results, max_iterations=1) == []
    assert followup_calls == [(tasks, results)]


def test_execution_log_stores_image_digest_instead_of_base64(tmp_path) -> None:
    loop = AutonomousLoop(data_dir=str(tmp_path / "autonomous"))
    image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADElEQVR42mP8z8BQDwAFgwJ/luzG8QAAAABJRU5ErkJggg=="

    loop._log_execution(
        [{"desire": "growth", "action": "look", "capability_id": "pc-server.screenshot.get_screenshot"}],
        [{"success": True, "result": "ok", "full_output": {"image_base64": image_base64, "image_mime": "image/png"}}],
    )

    log_text = (tmp_path / "autonomous" / "execution_log.jsonl").read_text(encoding="utf-8")
    assert image_base64 not in log_text
    assert "image_payload" in log_text
    assert "payload_omitted" in log_text
    assert not any((tmp_path / "autonomous" / "artifacts").iterdir())


class _ReleaseTrackingDesire(_PressureDesire):
    def __init__(self) -> None:
        super().__init__()
        self.releases: list[float] = []

    def release_cycle_pressure(self, *, effectiveness: float = 1.0) -> None:
        self.releases.append(effectiveness)


def test_empty_cycle_does_not_satisfy_desires(tmp_path) -> None:
    desire = _ReleaseTrackingDesire()
    loop = AutonomousLoop(desire_system=desire, data_dir=str(tmp_path / "autonomous"))

    loop._release_cycle_pressure([], [])

    assert desire.releases == []


def test_tool_success_alone_does_not_release_cycle_pressure(tmp_path) -> None:
    """Mechanical cycle release is disabled — only LLM fulfillment drains pressure."""
    desire = _ReleaseTrackingDesire()
    loop = AutonomousLoop(desire_system=desire, data_dir=str(tmp_path / "autonomous"))

    loop._release_cycle_pressure([{"action": "look"}], [{"success": False}])
    loop._release_cycle_pressure([{"action": "look"}], [{"success": True}])

    assert desire.releases == []


def test_no_effect_history_persists_for_reflection(tmp_path) -> None:
    desire = _PressureDesire()
    loop = AutonomousLoop(desire_system=desire, data_dir=str(tmp_path / "autonomous"))
    loop._no_effect_counts["ai-server.agora.read_posts"] = 1
    loop._save()

    reloaded = AutonomousLoop(desire_system=desire, data_dir=str(tmp_path / "autonomous"))
    assert reloaded._no_effect_counts.get("ai-server.agora.read_posts") == 1


def test_needs_followup_updates_outcome_history(monkeypatch, tmp_path) -> None:
    desire = _PressureDesire()
    loop = AutonomousLoop(desire_system=desire, data_dir=str(tmp_path / "autonomous"))
    loop._no_effect_counts["ai-server.commitment.list"] = 1
    monkeypatch.setattr(
        "aegis_ai.desire.fulfillment.evaluate_task_result",
        lambda **kwargs: TaskResult(
            tool_success=True,
            task_effect=TaskEffect.NEEDS_FOLLOWUP,
            fulfillment_score=0.0,
            pressure_reduction=0.0,
            confidence=0.3,
            summary="Structural fallback",
            details={"evaluator": "structural"},
        ),
    )

    loop._update_desires(
        [
            {
                "desire": "growth",
                "capability_id": "ai-server.commitment.list",
                "success": True,
                "full_output": {"commitments": []},
            }
        ]
    )

    assert loop._no_effect_counts.get("ai-server.commitment.list", 0) >= 2


def test_no_effect_experience_is_not_recorded_as_learning(tmp_path) -> None:
    recorded: list[dict] = []

    class _Experiential:
        def record_experience(self, **kwargs):
            recorded.append(kwargs)

    loop = AutonomousLoop(
        experiential_memory=_Experiential(),
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._record_experiences(
        [{"action": "read agora", "capability_id": "ai-server.agora.read_posts", "desire": "social"}],
        [
            {
                "success": True,
                "result": "AGORA: Retrieved 10 post(s); durable processing is queued. " + ("x" * 40),
                "task_effect": "no_effect",
                "fulfillment_score": 0.0,
            }
        ],
    )

    assert recorded == []
