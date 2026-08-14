from __future__ import annotations

import json
import sys
from pathlib import Path

from aegis_ai.capability_catalog import CapabilityCatalog
from aegis_ai.production_readiness import (
    blocker_capability_ids,
    is_mock_like_output,
    load_production_blocker_report,
)
from policy_engine import PolicyEngine
from tool_broker import ExecutionSource, InvokeStatus, ToolBroker, ToolExecutionRequest
from tool_registry import ToolRegistry


def test_is_mock_like_output_detects_structural_markers() -> None:
    assert is_mock_like_output({"mock": True}) is True
    assert is_mock_like_output({"provider": "mock"}) is True
    assert is_mock_like_output({"nested": {"stub": True}}) is True
    assert is_mock_like_output({"message": "real result"}) is False


def test_load_blocker_report_handles_capability_ids(tmp_path: Path) -> None:
    path = tmp_path / "production_blockers.json"
    path.write_text(
        json.dumps({"blockers": [{"classification": "production_blocker", "capability_id": "pc-server.input.mouse_click"}]}),
        encoding="utf-8",
    )

    report = load_production_blocker_report(path)

    assert blocker_capability_ids(report) == {"pc-server.input.mouse_click"}


def _catalog(tmp_path: Path) -> CapabilityCatalog:
    caps_dir = tmp_path / "capabilities"
    cap_path = caps_dir / "builtin" / "ai-server" / "mock" / "run.json"
    cap_path.parent.mkdir(parents=True, exist_ok=True)
    cap_path.write_text(
        json.dumps({
            "title": "Mock Tool",
            "description": "Mock guard test tool.",
            "server_id": "ai-server",
            "app_id": "mock",
            "action": "run",
            "operation_category": "observe",
            "risk": {"level": "low", "requires_approval": False},
            "input_schema": {"type": "object", "properties": {}},
        }),
        encoding="utf-8",
    )
    return CapabilityCatalog(str(caps_dir))


class _MockServerExecutor:
    def set_catalog(self, catalog):
        self.catalog = catalog

    def execute(self, cap, arguments):
        return {"mock": True, "capability": cap.id}


def test_tool_broker_rejects_mock_success_in_production(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AEGIS_RUNTIME_MODE", "production")
    catalog = _catalog(tmp_path)
    registry = ToolRegistry()
    for cap in catalog.to_tool_registry_capabilities():
        registry.register_capability(cap)
    broker = ToolBroker(
        registry=registry,
        policy_engine=PolicyEngine(data_dir=str(tmp_path / "data")),
        folder_registry=catalog.get_folder_registry(),
        catalog=catalog,
        server_executor=_MockServerExecutor(),
    )

    result = broker.execute(ToolExecutionRequest(
        capability_id="ai-server.mock.run",
        arguments={},
        source=ExecutionSource.USER_EXPLICIT,
    ))

    assert result.status == InvokeStatus.EXECUTION_ERROR
    assert result.output["production_blocker"] is True
    assert "mock/stub output" in result.error


def test_audit_common_classifies_pc_mock_as_guarded_dev_marker() -> None:
    scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
    sys.path.insert(0, str(scripts_dir))
    try:
        import audit_common

        classification, reason = audit_common.classify(
            "pc-server/src/action.rs",
            "mock",
            'details: format!("[MOCK] Typed {} chars", text.len()),',
        )
    finally:
        sys.path.remove(str(scripts_dir))

    assert classification == "dev_only"
    assert "production ToolBroker" in reason


