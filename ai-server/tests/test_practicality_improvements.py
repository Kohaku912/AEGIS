from __future__ import annotations

import json
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
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/api/chat/send" in rules
    assert "/api/autonomous/status" in rules
    assert "/api/approvals/pending" in rules
    assert "/api/health/alerts" in rules
    assert "/dashboard/llm-usage" in rules
