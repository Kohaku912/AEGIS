from __future__ import annotations

import time
from types import SimpleNamespace

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
from aegis_ai.desire.fulfillment import TaskEffect, TaskResult


class _Catalog:
    def __init__(self, capability_ids: list[str] | None = None) -> None:
        self._capability_ids = capability_ids or []

    def resolve(self, capability_id: str):
        parts = capability_id.split(".")
        action = parts[2] if len(parts) > 2 else capability_id
        tags = ["inventory"] if action in {"list", "status", "read_posts", "search"} else []
        category = "social_read" if "agora" in capability_id else "read"
        return SimpleNamespace(
            server_id=parts[0] if parts else "",
            app_id=parts[1] if len(parts) > 1 else "",
            action=action,
            input_schema={"type": "object", "properties": {}, "required": []},
            operation_category=category,
            risk_level="read_only",
            side_effects=[],
            title=capability_id,
            tags=tags,
            extra={},
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


def test_disabled_and_unconfigured_servers_are_unavailable(tmp_path) -> None:
    broker = _Broker(
        [
            "ai-server.memory.search",
            "dev-server.repo.status",
            "room-server.environment.get_environment",
        ]
    )
    loop = AutonomousLoop(
        tool_broker=broker,
        status_manager=_StatusManager(
            {
                "dev-server": "disabled",
                "room-server": "unconfigured",
            }
        ),
        data_dir=str(tmp_path / "autonomous"),
    )

    available = loop._available_capability_ids()

    assert "ai-server.memory.search" in available
    assert "dev-server.repo.status" not in available
    assert "room-server.environment.get_environment" not in available


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


def test_llm_interval_gate_is_off_by_default(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("AEGIS_MIN_LLM_INTERVAL_MS", raising=False)
    desire = _PressureDesire()
    desire.dimension.pressure = 1.0
    loop = AutonomousLoop(
        llm_provider=object(),
        desire_system=desire,
        data_dir=str(tmp_path / "autonomous"),
        fallback_interval_seconds=60,
    )
    assert loop._min_llm_interval_ms == 0
    generated: list[bool] = []
    loop._generate_tasks = lambda low: generated.append(True) or []
    loop._execute_tasks = lambda tasks: []
    loop._update_desires = lambda results: None
    loop._record_experiences = lambda tasks, results: None
    loop._decide_next_interval = lambda results: 60
    loop._log_execution = lambda tasks, results: None
    loop._preflight_check = lambda: (True, "ok")
    loop._get_low_desires = lambda: [{"name": "growth", "gap": 1.0, "pressure": 1.0}]

    loop._last_llm_call_ms = int(time.time() * 1000)
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


def _cap_candidate(cap_id: str, desire: str = "user_support") -> dict:
    return {
        "capability_id": cap_id,
        "arguments": {},
        "desire": desire,
        "goal": f"use {cap_id}",
        "why_now": "pressure",
        "expected_effect": "useful",
    }


def _tool_call(cap_id: str) -> dict:
    return {"function": cap_id.replace(".", "__").replace("-", "_"), "arguments": {}}


class _TwoStageLLM:
    def __init__(
        self,
        *,
        candidates: list[dict] | dict,
        tool_calls: list | None = None,
        select_content: str = "",
        empty_select_then_tool: bool = False,
        select_success: bool = True,
        select_error: str = "",
        finish_reason: str = "",
    ) -> None:
        self.candidates = candidates
        self.tool_calls = tool_calls
        self.select_content = select_content
        self.empty_select_then_tool = empty_select_then_tool
        self.select_success = select_success
        self.select_error = select_error
        self.finish_reason = finish_reason
        self.propose_calls = 0
        self.select_calls = 0
        self.calls = 0
        self.propose_kwargs: list[dict] = []
        self.select_kwargs: list[dict] = []
        self.call_order: list[str] = []

    def generate_json(self, **kwargs):
        self.propose_calls += 1
        self.call_order.append("propose")
        self.propose_kwargs.append(kwargs)
        if isinstance(self.candidates, dict):
            return self.candidates
        return {"candidates": self.candidates}

    def generate_with_tools(self, **kwargs):
        tools = kwargs.get("tools") or []
        names = {str((tool.get("function") or {}).get("name") or "") for tool in tools}
        if "submit_candidates" in names:
            self.propose_calls += 1
            self.call_order.append("propose")
            self.propose_kwargs.append(kwargs)
            payload = self.candidates if isinstance(self.candidates, dict) else {"candidates": self.candidates}
            return SimpleNamespace(
                success=True,
                content="",
                tool_calls=[{"function": "submit_candidates", "arguments": payload}],
            )
        self.select_calls += 1
        self.calls += 1
        self.call_order.append("select")
        self.select_kwargs.append(kwargs)
        if not self.select_success:
            return SimpleNamespace(
                success=False,
                error=self.select_error or "fail",
                content="",
                tool_calls=[],
            )
        if self.empty_select_then_tool and self.select_calls == 1:
            return SimpleNamespace(
                success=True,
                content="",
                tool_calls=[],
                finish_reason=self.finish_reason,
            )
        return SimpleNamespace(
            success=True,
            content=self.select_content,
            tool_calls=list(self.tool_calls or []),
            finish_reason=self.finish_reason,
        )


class _NoActionThenToolLLM(_TwoStageLLM):
    def __init__(self, cap_id: str) -> None:
        super().__init__(
            candidates=[_cap_candidate(cap_id)],
            tool_calls=[_tool_call(cap_id)],
            empty_select_then_tool=True,
        )


class _NoActionLLM(_TwoStageLLM):
    def __init__(self, cap_id: str = "ai-server.memory.search") -> None:
        super().__init__(
            candidates=[_cap_candidate(cap_id)],
            tool_calls=[],
            select_content="No action.",
        )


def test_empty_tool_response_is_retried_once(tmp_path) -> None:
    """An empty body with no tool call is not a decision — retry once for an answer."""
    capability_ids = ["ai-server.memory.search"]
    broker = _Broker(capability_ids)
    llm = _NoActionThenToolLLM(capability_ids[0])
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
    llm = _NoActionThenToolLLM("browser-server.page.read")

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


def test_repeated_no_effect_capability_cools_down_and_alternative_remains(tmp_path) -> None:
    capability_ids = ["ai-server.agora.read_posts", "ai-server.memory.search"]
    broker = _Broker(capability_ids)
    llm = _TwoStageLLM(
        candidates=[_cap_candidate(capability_id, desire="social") for capability_id in capability_ids],
        tool_calls=[_tool_call("ai-server.memory.search")],
    )

    loop = AutonomousLoop(
        llm_provider=llm,
        desire_system=_PressureDesire(),
        tool_broker=broker,
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._no_effect_counts["ai-server.agora.read_posts"] = 5
    loop._log_audit_event = lambda **kwargs: None

    tasks = loop._generate_tasks([{"name": "social", "gap": 5.0, "pressure": 8.0}])

    assert tasks
    assert tasks[0]["capability_id"] == "ai-server.memory.search"
    assert "ai-server.agora.read_posts" not in loop.get_status()["candidate_capability_ids"]
    assert "ai-server.agora.read_posts" in loop._last_propose_prompt
    assert "temporarily cooling down" in loop._last_propose_prompt


def test_proposal_prompt_includes_capability_semantics_and_diversity_rule(tmp_path) -> None:
    capability_ids = ["ai-server.commitment.list", "ai-server.memory.search"]
    loop = AutonomousLoop(
        llm_provider=_NoActionLLM("ai-server.memory.search"),
        desire_system=_PressureDesire(),
        tool_broker=_Broker(capability_ids),
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._log_audit_event = lambda **kwargs: None

    loop._generate_tasks([{"name": "growth", "gap": 5.0, "pressure": 8.0}])

    assert "Candidate capabilities with descriptions:" in loop._last_propose_prompt
    assert '"category": "read"' in loop._last_propose_prompt
    assert "span at least two operation categories" in loop._last_propose_prompt
    assert "do not re-list state already present" in loop._last_propose_prompt


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


def test_diversity_cooldown_persists_and_expires(tmp_path) -> None:
    desire = _PressureDesire()
    loop = AutonomousLoop(desire_system=desire, data_dir=str(tmp_path / "autonomous"))
    now = int(time.time() * 1000)
    loop._capability_cooldowns["ai-server.agora.read_posts"] = now + 60_000
    loop._save()

    reloaded = AutonomousLoop(desire_system=desire, data_dir=str(tmp_path / "autonomous"))

    assert "ai-server.agora.read_posts" in reloaded._cooling_capability_ids(now)
    assert "ai-server.agora.read_posts" not in reloaded._cooling_capability_ids(now + 60_001)


def test_desire_strategies_remember_outcomes_and_inform_selection(monkeypatch, tmp_path) -> None:
    desire = _PressureDesire()
    capability_ids = ["ai-server.memory.search", "ai-server.agora.read_posts"]
    llm = _TwoStageLLM(
        candidates=[_cap_candidate("ai-server.memory.search", "growth")],
        tool_calls=[_tool_call("ai-server.memory.search")],
    )
    loop = AutonomousLoop(
        llm_provider=llm,
        desire_system=desire,
        tool_broker=_Broker(capability_ids),
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._memory_root = lambda: tmp_path
    loop._log_audit_event = lambda **kwargs: None
    outcomes = iter(
        [
            TaskResult(
                tool_success=True,
                task_effect=TaskEffect.USEFUL,
                fulfillment_score=0.8,
                pressure_reduction=0.5,
                confidence=0.9,
                summary="Found reusable project knowledge",
                details={"evaluator": "llm"},
            ),
            TaskResult(
                tool_success=True,
                task_effect=TaskEffect.NO_EFFECT,
                fulfillment_score=0.0,
                confidence=0.8,
                summary="No new social activity",
                details={"evaluator": "llm"},
            ),
        ]
    )
    monkeypatch.setattr(
        "aegis_ai.desire.fulfillment.evaluate_task_result",
        lambda **kwargs: next(outcomes),
    )

    loop._update_desires(
        [
            {
                "desire": "growth",
                "goal": "reuse project knowledge",
                "capability_id": "ai-server.memory.search",
                "success": True,
                "full_output": {"result": "knowledge"},
            },
            {
                "desire": "growth",
                "goal": "find something new",
                "capability_id": "ai-server.agora.read_posts",
                "success": True,
                "full_output": {"posts": []},
            },
        ]
    )

    strategies = loop._desire_strategy_context(["growth"])
    assert {item["effect"] for item in strategies} == {"useful", "no_effect"}
    assert {item["capability_id"] for item in strategies} == set(capability_ids)

    loop._generate_tasks([{"name": "growth", "gap": 5.0, "pressure": 8.0}])
    assert "Found reusable project knowledge" in loop._last_propose_prompt
    assert "Do not repeat blindly" in loop._last_select_prompt


def test_commitment_list_remains_available_when_obligations_present(tmp_path) -> None:
    capability_ids = ["ai-server.commitment.list", "ai-server.memory.search"]
    broker = _Broker(capability_ids)
    llm = _TwoStageLLM(
        candidates=[_cap_candidate("ai-server.memory.search")],
        tool_calls=[],
        select_content="No action needed.",
    )

    loop = AutonomousLoop(
        llm_provider=llm,
        desire_system=_PressureDesire(),
        tool_broker=broker,
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._log_audit_event = lambda **kwargs: None
    loop._priority_obligations = lambda: [  # type: ignore[method-assign]
        {"kind": "commitment", "obligation_id": "c1", "summary": "Finish deploy"}
    ]

    loop._generate_tasks([{"name": "user_support", "gap": 5.0, "pressure": 8.0}])

    assert llm.propose_calls == 1
    propose_prompt = loop._last_propose_prompt
    assert "ai-server.commitment.list" in propose_prompt
    assert "ai-server.memory.search" in propose_prompt
    assert "ai-server.commitment.list" in loop.get_status()["candidate_capability_ids"]
    assert "ai-server.memory.search" in loop.get_status()["candidate_capability_ids"]


def test_follow_up_may_run_after_inventory_cycle(tmp_path) -> None:
    class _NoFollowUpLLM:
        def generate_with_tools(self, **_kwargs):
            return SimpleNamespace(success=True, content="No follow-up needed.", tool_calls=[])

    loop = AutonomousLoop(
        llm_provider=_NoFollowUpLLM(),
        tool_broker=_Broker(["ai-server.commitment.list"]),
        data_dir=str(tmp_path / "autonomous"),
    )
    tasks = [{"capability_id": "ai-server.commitment.list", "action": "list commitments"}]
    results = [{"success": True, "result": "3 open commitment(s): ship fix"}]

    assert loop._generate_follow_up_tasks(tasks, results) == []


def test_decide_next_interval_retries_after_no_effect_success(tmp_path) -> None:
    from aegis_ai.desire.desire_system import DesireSystem

    desire = DesireSystem(data_dir=str(tmp_path / "desire"))
    for name, obj in desire.get_all_desires().items():
        if obj.hidden:
            continue
        obj.pressure = 8.0
        if desire._pressure_engine is not None:
            desire._pressure_engine._pressures[name] = 8.0
    loop = AutonomousLoop(
        desire_system=desire,
        data_dir=str(tmp_path / "autonomous"),
        fallback_interval_seconds=3600,
    )

    interval = loop._decide_next_interval(
        [{"success": True, "task_effect": "no_effect", "result": "No open commitments."}]
    )

    assert interval <= 300
    assert interval < loop._fallback_interval


def test_needs_followup_starts_diversity_cooldown_after_repeat(monkeypatch, tmp_path) -> None:
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

    assert loop._no_effect_counts.get("ai-server.commitment.list", 0) == 0
    assert "ai-server.commitment.list" in loop._capability_cooldowns


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


def test_safe_span_does_not_abort_when_tracing_breaks(monkeypatch) -> None:
    from aegis_ai.autonomous import autonomous_loop as loop_mod

    class _Boom:
        def __enter__(self):
            raise AttributeError("trace_id")

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(
        "aegis_ai.observability.otel_tracing.start_span",
        lambda *args, **kwargs: _Boom(),
    )
    ran = False
    with loop_mod._safe_span("test"):
        ran = True
    assert ran is True


def test_propose_uses_submit_candidates_tool(tmp_path) -> None:
    llm = _TwoStageLLM(
        candidates=[_cap_candidate("ai-server.memory.search")],
        tool_calls=[_tool_call("ai-server.memory.search")],
    )
    loop = AutonomousLoop(
        llm_provider=llm,
        desire_system=_PressureDesire(),
        tool_broker=_Broker(["ai-server.memory.search"]),
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._log_audit_event = lambda **kwargs: None
    tasks = loop._generate_tasks([{"name": "user_support", "gap": 5.0, "pressure": 8.0}])
    assert llm.call_order == ["propose", "select"]
    assert "submit_candidates" in {
        str((tool.get("function") or {}).get("name") or "")
        for tool in llm.propose_kwargs[0]["tools"]
    }
    assert tasks[0]["capability_id"] == "ai-server.memory.search"


def test_two_stage_proposal_then_selection_picks_one(tmp_path) -> None:
    capability_ids = [
        "ai-server.memory.search",
        "ai-server.agora.read_posts",
        "browser-server.page.read",
    ]
    llm = _TwoStageLLM(
        candidates=[_cap_candidate(cap_id) for cap_id in capability_ids],
        tool_calls=[_tool_call("ai-server.memory.search"), _tool_call("browser-server.page.read")],
    )
    loop = AutonomousLoop(
        llm_provider=llm,
        desire_system=_PressureDesire(),
        tool_broker=_Broker(capability_ids),
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._log_audit_event = lambda **kwargs: None

    tasks = loop._generate_tasks([{"name": "user_support", "gap": 5.0, "pressure": 8.0}])

    assert llm.call_order == ["propose", "select"]
    assert len(tasks) == 1
    assert tasks[0]["capability_id"] == "ai-server.memory.search"
    select_tools = {tool["function"]["name"] for tool in llm.select_kwargs[0]["tools"]}
    assert select_tools == {
        "ai_server__memory__search",
        "ai_server__agora__read_posts",
        "browser_server__page__read",
    }
    status = loop.get_status()
    assert status["selected_tool_count"] == 1
    assert status["selected_candidate"]["capability_id"] == "ai-server.memory.search"
    assert status["max_pressure_mode"] is False
    assert len(status["proposed_candidates"]) == 3


def test_cannot_select_capability_outside_proposed_list(tmp_path) -> None:
    llm = _TwoStageLLM(
        candidates=[_cap_candidate("ai-server.memory.search")],
        tool_calls=[_tool_call("ai-server.agora.read_posts")],
    )
    loop = AutonomousLoop(
        llm_provider=llm,
        desire_system=_PressureDesire(),
        tool_broker=_Broker(["ai-server.memory.search", "ai-server.agora.read_posts"]),
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._log_audit_event = lambda **kwargs: None

    tasks = loop._generate_tasks([{"name": "user_support", "gap": 5.0, "pressure": 8.0}])

    assert tasks == []
    assert loop.get_status()["last_decision"] == "no_valid_tasks"
    select_tools = {tool["function"]["name"] for tool in llm.select_kwargs[0]["tools"]}
    assert "ai_server__agora__read_posts" not in select_tools
    assert "ai_server__memory__search" in select_tools


def test_normal_pressure_allows_reasoned_no_action(tmp_path) -> None:
    llm = _TwoStageLLM(
        candidates={"candidates": [], "no_action_reason": "user is focused and nothing is urgent"},
        tool_calls=[_tool_call("ai-server.memory.search")],
    )
    loop = AutonomousLoop(
        llm_provider=llm,
        desire_system=_PressureDesire(),
        tool_broker=_Broker(["ai-server.memory.search"]),
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._log_audit_event = lambda **kwargs: None

    tasks = loop._generate_tasks([{"name": "user_support", "gap": 5.0, "pressure": 8.0}])

    assert tasks == []
    assert llm.select_calls == 0
    status = loop.get_status()
    assert status["last_decision"] == "no_action"
    assert "nothing is urgent" in status["last_no_action_reason"]
    assert "MAX PRESSURE" not in loop._last_propose_system_prompt
    assert "no_action_reason" in loop._last_propose_prompt


def test_max_pressure_prompts_forbid_inaction_but_do_not_force_a_pick(tmp_path) -> None:
    llm = _TwoStageLLM(
        candidates=[_cap_candidate("ai-server.memory.search")],
        tool_calls=[],
        select_content="Still declining.",
    )
    loop = AutonomousLoop(
        llm_provider=llm,
        desire_system=_PressureDesire(),
        tool_broker=_Broker(["ai-server.memory.search"]),
        data_dir=str(tmp_path / "autonomous"),
    )
    loop._log_audit_event = lambda **kwargs: None

    tasks = loop._generate_tasks([{"name": "growth", "gap": 8.0, "pressure": 10.0}])

    assert tasks == []
    assert llm.propose_calls == 1
    assert llm.select_calls == 1
    status = loop.get_status()
    assert status["max_pressure_mode"] is True
    assert status["selected_tool_count"] == 0
    assert status["last_decision"] == "no_action"
    for text in (
        loop._last_propose_system_prompt,
        loop._last_propose_prompt,
        loop._last_select_system_prompt,
        loop._last_select_prompt,
    ):
        assert "MAX PRESSURE" in text
        assert "Do not choose no_action" in text
    assert "no_action_reason" not in loop._last_propose_prompt
    assert "Select no capability" not in loop._last_select_prompt


def test_max_pressure_does_not_bypass_missing_provider_or_empty_catalog(tmp_path) -> None:
    desire = _PressureDesire()
    desire.dimension.pressure = 10.0
    no_llm = AutonomousLoop(
        desire_system=desire,
        data_dir=str(tmp_path / "autonomous-no-llm"),
    )
    should_proceed, reason = no_llm._preflight_check()
    assert should_proceed is False
    assert reason == "provider_unavailable"

    llm = _TwoStageLLM(candidates=[_cap_candidate("ai-server.memory.search")], tool_calls=[_tool_call("ai-server.memory.search")])
    empty = AutonomousLoop(
        llm_provider=llm,
        desire_system=desire,
        tool_broker=_Broker([]),
        data_dir=str(tmp_path / "autonomous-empty"),
    )
    empty._log_audit_event = lambda **kwargs: None
    tasks = empty._generate_tasks([{"name": "growth", "gap": 8.0, "pressure": 10.0}])
    assert tasks == []
    assert llm.propose_calls == 0
    assert llm.select_calls == 0


def test_max_pressure_does_not_bypass_provider_circuit(monkeypatch, tmp_path) -> None:
    desire = _PressureDesire()
    desire.dimension.pressure = 10.0
    loop = AutonomousLoop(
        llm_provider=object(),
        desire_system=desire,
        data_dir=str(tmp_path / "autonomous"),
    )
    monkeypatch.setattr(
        "aegis_ai.llm.provider_circuit.PROVIDER_CIRCUIT",
        SimpleNamespace(is_open=lambda: True, remaining_ms=lambda: 12_000),
    )

    should_proceed, reason = loop._preflight_check()

    assert should_proceed is False
    assert "llm_provider_circuit_open" in reason


def test_max_pressure_still_routes_approval_and_hard_stops_through_broker(tmp_path) -> None:
    from tool_broker import InvokeStatus, ToolExecutionResult

    class _PolicyBroker(_ExecutingBroker):
        def __init__(self) -> None:
            super().__init__(["ai-server.memory.search", "pc-server.commerce.purchase"])
            self.requests: list = []

        def execute(self, request):
            self.requests.append(request)
            if request.capability_id == "pc-server.commerce.purchase":
                return ToolExecutionResult(
                    status=InvokeStatus.DENIED,
                    error="purchase hard-stop",
                    policy_decision="DENY",
                )
            return ToolExecutionResult(
                status=InvokeStatus.APPROVAL_NEEDED,
                approval_id="appr-1",
            )

    broker = _PolicyBroker()
    loop = AutonomousLoop(
        tool_broker=broker,
        data_dir=str(tmp_path / "autonomous"),
    )

    approved = loop._execute_tasks(
        [{"desire": "growth", "action": "search", "capability_id": "ai-server.memory.search", "arguments": {}}]
    )
    denied = loop._execute_tasks(
        [{"desire": "growth", "action": "buy", "capability_id": "pc-server.commerce.purchase", "arguments": {}}]
    )

    assert broker.requests
    assert approved[0]["success"] is True
    assert "Awaiting approval" in approved[0]["result"]
    assert denied[0]["success"] is False
    assert "purchase hard-stop" in denied[0]["result"]


def test_failed_and_no_effect_keep_max_pressure(monkeypatch, tmp_path) -> None:
    desire = _PressureDesire()
    desire.dimension.pressure = 10.0
    loop = AutonomousLoop(desire_system=desire, data_dir=str(tmp_path / "autonomous"))

    monkeypatch.setattr(
        "aegis_ai.desire.fulfillment.evaluate_task_result",
        lambda **kwargs: TaskResult(
            tool_success=False,
            task_effect=TaskEffect.FAILED,
            desire_delta_hint={"growth": -0.3},
            summary="Failed",
            details={"evaluator": "llm"},
        ),
    )
    loop._update_desires(
        [{"desire": "growth", "capability_id": "ai-server.memory.search", "success": False, "full_output": {}}]
    )
    assert desire.reductions == []
    assert desire.dimension.pressure == 10.0

    monkeypatch.setattr(
        "aegis_ai.desire.fulfillment.evaluate_task_result",
        lambda **kwargs: TaskResult(
            tool_success=True,
            task_effect=TaskEffect.NO_EFFECT,
            desire_delta_hint={"growth": 0.0},
            summary="No effect",
            details={"evaluator": "llm"},
        ),
    )
    loop._update_desires(
        [
            {
                "desire": "growth",
                "capability_id": "ai-server.agora.read_posts",
                "success": True,
                "full_output": {"result": "No new posts"},
            }
        ]
    )
    assert desire.reductions == []
    assert desire.dimension.pressure == 10.0

