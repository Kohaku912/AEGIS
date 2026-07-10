from __future__ import annotations

import json
import time
from pathlib import Path
from types import SimpleNamespace


def test_llm_response_usage_fields_are_normalized() -> None:
    from aegis_ai.llm.router import LLMRouter

    provider_response = SimpleNamespace(
        content="ok",
        model_used="m",
        provider_used="p",
        tokens_used=17,
        input_tokens=11,
        output_tokens=6,
        input_cache_hit_tokens=4,
        input_cache_miss_tokens=7,
        provider_reported_cost=0.0012,
        cost_estimate=0.0,
        success=True,
        error="",
        tool_calls=None,
    )
    response = LLMRouter._normalize_provider_response(provider_response, "p", "rid")

    assert response.input_tokens == 11
    assert response.output_tokens == 6
    assert response.input_cache_hit_tokens == 4
    assert response.input_cache_miss_tokens == 7
    assert response.provider_reported_cost == 0.0012


def test_llm_router_audit_records_usage_and_context_detail() -> None:
    from aegis_ai.llm.router import LLMRequest, LLMRouter, TaskType

    class Audit:
        def __init__(self) -> None:
            self.entries = []

        def append(self, entry) -> None:
            self.entries.append(entry)

    class Provider:
        def generate(self, **_kwargs):
            return SimpleNamespace(
                content="ok",
                model_used="m",
                provider_used="p",
                tokens_used=18,
                input_tokens=12,
                output_tokens=6,
                input_cache_hit_tokens=5,
                input_cache_miss_tokens=7,
                provider_reported_cost=0.004,
                cost_estimate=0.0,
                success=True,
                error="",
            )

    audit = Audit()
    router = LLMRouter(audit_log=audit)
    router.register_provider("mock", Provider())
    router.route(LLMRequest(
        task_type=TaskType.SMALL_FAST_TASK,
        prompt="hello",
        request_id="req-1",
        caller="test",
        context_meta={"context_tokens": {"system": 3, "memory": 4}},
    ))

    entry = audit.entries[0]
    assert entry.request_id == "req-1"
    assert entry.tokens_used == 18
    assert entry.detail["input_tokens"] == 12
    assert entry.detail["output_tokens"] == 6
    assert entry.detail["input_cache_hit_tokens"] == 5
    assert entry.detail["input_cache_miss_tokens"] == 7
    assert entry.detail["provider_reported_cost"] == 0.004
    assert entry.detail["context_tokens"]["memory"] == 4


def test_context_builder_records_usage_breakdown() -> None:
    from aegis_ai.context_builder import ContextBuilder

    builder = ContextBuilder()
    ctx = builder.build(triggering_query="summarize recent state")
    meta = ctx.usage_meta()

    assert "context_tokens" in meta
    assert "memory" in meta["context_tokens"]
    assert "user_state" in meta["context_tokens"]
    assert meta["memory_budget_tokens"] >= 0
    assert meta["memory_reason"]


def test_llm_usage_context_breakdown_aggregates() -> None:
    from aegis_ai.observability.llm_usage.aggregator import breakdown_by_context
    from aegis_ai.observability.llm_usage.models import LLMTrace

    rows = breakdown_by_context([
        LLMTrace(context_tokens={"system": 10, "memory": 30}),
        LLMTrace(context_tokens={"system": 5, "tool_schema": 20}),
    ])
    by_key = {row.key: row for row in rows}

    assert by_key["system"].tokens == 15
    assert by_key["memory"].tokens == 30
    assert by_key["tool_schema"].tokens == 20


def test_llm_usage_retry_detection_uses_raw_entries_before_dedup() -> None:
    from aegis_ai.observability.llm_usage.service import LLMUsageService

    now = int(time.time() * 1000)

    class Audit:
        def read_recent_for_dashboard(self, limit=5000):
            return [
                {
                    "entry_id": f"e{i}",
                    "timestamp_ms": now - i,
                    "action": "llm_call",
                    "request_id": "same-request",
                    "tokens_used": 10,
                    "detail": {"success": False if i == 2 else True},
                }
                for i in range(3)
            ]

    candidates = LLMUsageService(audit_manager=Audit()).get_waste_candidates("1h")

    assert any(c["candidate_type"] == "retry_loop_suspect" for c in candidates)


class _FakeServerExecutor:
    def __init__(self, observations: list[dict[str, str]]) -> None:
        self.observations = observations
        self.executions = 0

    def set_catalog(self, catalog) -> None:
        self.catalog = catalog

    def execute(self, cap, arguments):
        self.executions += 1
        return {"ok": True, "execution": self.executions}

    def execute_capability(self, capability_id, params=None):
        if self.observations:
            return self.observations.pop(0)
        return {"screen": "last"}


def _write_capability(root: Path) -> None:
    path = root / "capabilities" / "builtin" / "pc-server" / "test" / "clickish.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "server_id": "pc-server",
                "app_id": "test",
                "action": "clickish",
                "operation_category": "test_operation",
                "title": "Clickish",
                "risk": {"level": "low", "requires_approval": False},
                "input_schema": {"type": "object", "properties": {}},
                "completion": {
                    "mode": "all",
                    "retry": {"max_attempts": 1, "delay_ms": 0},
                    "checks": [
                        {
                            "name": "screen_changed",
                            "type": "screenshot",
                            "capability_id": "pc-server.screenshot.get_screenshot",
                            "expect_changed": True,
                            "capture_before": True,
                        }
                    ],
                },
            }
        ),
        encoding="utf-8",
    )


def _broker(tmp_path, observations):
    from aegis_ai.capability_catalog import CapabilityCatalog
    from policy_engine import PolicyEngine
    from tool_broker import ToolBroker
    from tool_registry import ToolRegistry

    _write_capability(tmp_path)
    catalog = CapabilityCatalog(capabilities_dir=str(tmp_path / "capabilities"), apps_dir=str(tmp_path / "apps"))
    registry = ToolRegistry()
    for cap in catalog.to_tool_registry_capabilities():
        registry.register_capability(cap)
    executor = _FakeServerExecutor(observations)
    broker = ToolBroker(
        registry=registry,
        policy_engine=PolicyEngine(),
        server_executor=executor,
        catalog=catalog,
    )
    return broker, executor


def test_completion_condition_passes_when_observation_changes(tmp_path) -> None:
    from tool_broker import ExecutionSource, InvokeStatus, ToolExecutionRequest

    broker, executor = _broker(tmp_path, [{"screen": "before"}, {"screen": "after"}])
    result = broker.execute(ToolExecutionRequest(
        capability_id="pc-server.test.clickish",
        arguments={},
        source=ExecutionSource.USER_EXPLICIT,
    ))

    assert result.status == InvokeStatus.SUCCESS
    assert result.verification_status == "passed"
    assert executor.executions == 1


def test_completion_condition_retries_then_fails(tmp_path) -> None:
    from tool_broker import ExecutionSource, InvokeStatus, ToolExecutionRequest

    broker, executor = _broker(
        tmp_path,
        [{"screen": "same"}, {"screen": "same"}, {"screen": "same"}, {"screen": "same"}],
    )
    result = broker.execute(ToolExecutionRequest(
        capability_id="pc-server.test.clickish",
        arguments={},
        source=ExecutionSource.USER_EXPLICIT,
    ))

    assert result.status == InvokeStatus.EXECUTION_ERROR
    assert result.verification_status == "failed"
    assert executor.executions == 2
    assert "Completion verification failed" in result.error


def test_dashboard_route_modules_are_registered(monkeypatch, tmp_path) -> None:
    from aegis_ai.web import dashboard_routes
    from test_dashboard_routes import _runtime

    monkeypatch.setattr(dashboard_routes, "_DATA_DIR", str(tmp_path / "data"))
    app = dashboard_routes.DashboardApp(runtime=_runtime(tmp_path)).app
    blueprint_names = set(app.blueprints)

    assert "dashboard_chat" in blueprint_names
    assert "dashboard_autonomous_api" in blueprint_names
    assert "dashboard_approval" in blueprint_names
    assert "dashboard_health" in blueprint_names
    assert "dashboard_presentation" in blueprint_names
    assert "dashboard_llm_usage_page" in blueprint_names
    assert "dashboard_server_status" in blueprint_names
    assert "dashboard_memory" in blueprint_names
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/api/chat/send" in rules
    assert "/api/autonomous/status" in rules
    assert "/api/approvals/pending" in rules
    assert "/api/health/alerts" in rules
    assert "/dashboard/llm-usage" in rules
    assert Path("src/aegis_ai/web/routes/chat.py").exists()
    assert Path("src/aegis_ai/web/routes/memory.py").exists()


def test_task_execution_engine_fails_step_when_completion_verification_fails(tmp_path) -> None:
    from aegis_ai.task.execution_engine import TaskExecutionEngine
    from aegis_ai.task.task_manager import TaskManager
    from aegis_ai.task_plan import PlanStep, TaskPlan, StepStatus
    from tool_broker import InvokeStatus

    verification = SimpleNamespace(
        status="failed",
        details=["screen_changed: changed=False"],
        repair_hint="retry_or_user_confirmation",
        checks_passed=0,
        checks_failed=1,
    )
    result = SimpleNamespace(
        success=True,
        status=InvokeStatus.SUCCESS,
        output={"ok": True},
        error="",
        verification=verification,
        verification_status="failed",
        approval_id="",
    )
    broker = SimpleNamespace(execute=lambda _request: result)
    tm = TaskManager(data_dir=str(tmp_path / "tasks"))
    task = tm.create_task(title="verify", source="test")
    task_id = task["task_id"]
    tm.start_task(task_id)
    step = PlanStep(
        step_id="s1",
        description="click and verify",
        action_type="tool_invoke",
        capability_id="pc-server.test.clickish",
    )

    response = TaskExecutionEngine(task_manager=tm, tool_broker=broker).execute_task(
        task_id,
        TaskPlan(plan_id="p", steps=[step]),
    )

    assert step.status == StepStatus.FAILED
    assert tm.get_task(task_id)["status"] == "failed"
    assert "screen_changed" in response.text


def test_task_execution_engine_completes_after_verification_service_verified(tmp_path) -> None:
    from aegis_ai.task.execution_engine import TaskExecutionEngine
    from aegis_ai.task.task_manager import TaskManager
    from aegis_ai.task_plan import PlanStep, TaskPlan, StepStatus
    from aegis_ai.verification import VerificationRequest, VerificationResult, VerificationStatus
    from tool_broker import InvokeStatus

    class FakeVerificationService:
        def __init__(self) -> None:
            self.request = None

        def build_request(self, tool_request, tool_result):
            return VerificationRequest(
                request_id=tool_request.request_id,
                task_id=tool_request.task_id,
                capability_id=tool_request.capability_id,
                execution_output=tool_result.output,
            )

        def verify(self, request):
            self.request = request
            assert request.completion["mode"] == "all"
            assert request.completion_conditions[0].name == "ok_field"
            return VerificationResult(
                verification_id="ver_ok",
                request_id=request.request_id,
                status=VerificationStatus.VERIFIED,
                confidence=0.9,
                reason="verified in test",
            )

        def record_verification(self, request, result):
            return None

    result = SimpleNamespace(
        success=True,
        status=InvokeStatus.SUCCESS,
        output={"ok": True},
        error="",
        approval_id="",
        request_id="req_verified",
        verification_status="pending",
    )
    catalog = SimpleNamespace(resolve=lambda _cap_id: SimpleNamespace(completion={
        "mode": "all",
        "checks": [{"name": "ok_field", "observable": "output_field", "field": "ok"}],
    }))
    broker = SimpleNamespace(execute=lambda _request: result, _catalog=catalog)
    verification = FakeVerificationService()
    tm = TaskManager(data_dir=str(tmp_path / "tasks"))
    task = tm.create_task(title="verify", source="test")
    task_id = task["task_id"]
    tm.start_task(task_id)
    step = PlanStep(
        step_id="s1",
        description="execute and verify",
        action_type="tool_invoke",
        capability_id="pc-server.test.ok",
    )

    response = TaskExecutionEngine(
        task_manager=tm,
        tool_broker=broker,
        verification_service=verification,
    ).execute_task(task_id, TaskPlan(plan_id="p", steps=[step]))

    assert step.status == StepStatus.COMPLETED
    assert tm.get_task(task_id)["status"] == "completed"
    assert verification.request is not None
    assert "OK" in response.text


def test_task_execution_engine_pauses_when_verification_requires_observation(tmp_path) -> None:
    from aegis_ai.task.execution_engine import TaskExecutionEngine
    from aegis_ai.task.task_manager import TaskManager
    from aegis_ai.task_plan import PlanStep, TaskPlan, StepStatus
    from aegis_ai.verification import VerificationRequest, VerificationResult, VerificationStatus
    from tool_broker import InvokeStatus

    class FakeVerificationService:
        def build_request(self, tool_request, tool_result):
            return VerificationRequest(
                request_id=tool_request.request_id,
                task_id=tool_request.task_id,
                capability_id=tool_request.capability_id,
                execution_output=tool_result.output,
            )

        def verify(self, request):
            return VerificationResult(
                verification_id="ver_observe",
                request_id=request.request_id,
                status=VerificationStatus.REQUIRES_OBSERVATION,
                confidence=0.2,
                reason="ui_tree unavailable",
                suggested_recovery="ask user to confirm screen",
            )

        def record_verification(self, request, result):
            return None

    result = SimpleNamespace(
        success=True,
        status=InvokeStatus.SUCCESS,
        output={"ok": True},
        error="",
        approval_id="",
        request_id="req_observe",
        verification_status="pending",
    )
    broker = SimpleNamespace(execute=lambda _request: result, _catalog=SimpleNamespace(resolve=lambda _cap_id: None))
    tm = TaskManager(data_dir=str(tmp_path / "tasks"))
    task = tm.create_task(title="observe", source="test")
    task_id = task["task_id"]
    tm.start_task(task_id)
    step = PlanStep(
        step_id="s1",
        description="tap and observe",
        action_type="tool_invoke",
        capability_id="android-server.ui.tap",
    )

    response = TaskExecutionEngine(
        task_manager=tm,
        tool_broker=broker,
        verification_service=FakeVerificationService(),
    ).execute_task(task_id, TaskPlan(plan_id="p", steps=[step]))

    assert step.status == StepStatus.REQUIRES_OBSERVATION
    assert tm.get_step(task_id, "s1")["status"] == "requires_observation"
    assert tm.get_task(task_id)["status"] == "paused"
    assert "OBSERVE" in response.text
