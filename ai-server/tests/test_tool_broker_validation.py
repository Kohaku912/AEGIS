from __future__ import annotations

import json
from pathlib import Path

from aegis_ai.capability_catalog import CapabilityCatalog
from policy_engine import PolicyEngine
from tool_broker import ExecutionSource, InvokeStatus, ToolBroker, ToolExecutionRequest
from tool_registry import ToolRegistry


def _catalog(tmp_path: Path) -> CapabilityCatalog:
    caps_dir = tmp_path / "capabilities"
    cap_path = caps_dir / "builtin" / "ai-server" / "strict" / "run.json"
    cap_path.parent.mkdir(parents=True, exist_ok=True)
    cap_path.write_text(
        json.dumps({
            "title": "Strict Tool",
            "description": "Strict validation test tool.",
            "server_id": "ai-server",
            "app_id": "strict",
            "action": "run",
            "operation_category": "observe",
            "risk": {"level": "low", "requires_approval": False},
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
                "additionalProperties": False,
            },
        }),
        encoding="utf-8",
    )
    return CapabilityCatalog(str(caps_dir))


def _broker(catalog: CapabilityCatalog, tmp_path: Path) -> ToolBroker:
    registry = ToolRegistry()
    for cap in catalog.to_tool_registry_capabilities():
        registry.register_capability(cap)
    return ToolBroker(
        registry=registry,
        policy_engine=PolicyEngine(data_dir=str(tmp_path / "data")),
        folder_registry=catalog.get_folder_registry(),
        catalog=catalog,
    )


def test_unknown_capability_is_rejected_before_execution(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    broker = _broker(catalog, tmp_path)

    result = broker.execute(ToolExecutionRequest(
        capability_id="ai-server.missing.run",
        arguments={},
        source=ExecutionSource.USER_EXPLICIT,
    ))

    assert result.status == InvokeStatus.NOT_FOUND
    assert "capability catalog" in result.error


def test_missing_required_argument_is_rejected_before_execution(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    broker = _broker(catalog, tmp_path)

    result = broker.execute(ToolExecutionRequest(
        capability_id="ai-server.strict.run",
        arguments={},
        source=ExecutionSource.USER_EXPLICIT,
    ))

    assert result.status == InvokeStatus.DENIED
    assert "Invalid arguments" in result.error
    assert "required" in result.error


def test_type_mismatch_is_rejected_before_execution(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    broker = _broker(catalog, tmp_path)

    result = broker.execute(ToolExecutionRequest(
        capability_id="ai-server.strict.run",
        arguments={"name": 123},
        source=ExecutionSource.USER_EXPLICIT,
    ))

    assert result.status == InvokeStatus.DENIED
    assert "not of type" in result.error


def test_additional_properties_are_rejected_before_execution(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    broker = _broker(catalog, tmp_path)

    result = broker.execute(ToolExecutionRequest(
        capability_id="ai-server.strict.run",
        arguments={"name": "ok", "extra": True},
        source=ExecutionSource.USER_EXPLICIT,
    ))

    assert result.status == InvokeStatus.DENIED
    assert "Additional properties" in result.error
