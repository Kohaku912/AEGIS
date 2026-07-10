from __future__ import annotations

import json
from pathlib import Path


def _write_manifest(root: Path, cap_id: str = "pc-server.test.sample", risk: str = "safe") -> Path:
    path = root / "builtin" / "pc-server" / "test" / f"{cap_id.rsplit('.', 1)[-1]}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "id": cap_id,
                "server_id": "pc-server",
                "app_id": "test",
                "action": cap_id.rsplit(".", 1)[-1],
                "operation_category": "test_operation",
                "title": "Sample",
                "description": "Sample capability",
                "risk": {"level": risk, "requires_approval": False},
            }
        ),
        encoding="utf-8",
    )
    return path


def test_capability_override_persists_across_catalog_reload(tmp_path) -> None:
    from aegis_ai.capability_catalog import CapabilityCatalog

    capabilities_dir = tmp_path / "capabilities"
    data_dir = tmp_path / "data"
    _write_manifest(capabilities_dir)

    catalog = CapabilityCatalog(
        capabilities_dir=str(capabilities_dir),
        apps_dir=str(tmp_path / "apps"),
        data_dir=str(data_dir),
    )
    catalog.get_override_store().upsert(
        "pc-server.test.sample",
        risk_level="APPROVAL_REQUIRED",
        requires_approval=True,
        approval_mode="one_time",
        enabled=True,
        updated_by="test",
    )
    catalog.reload()

    details = catalog.risk_details("pc-server.test.sample")
    assert details["manifest"]["risk_level"] == "safe"
    assert details["override"]["risk_level"] == "APPROVAL_REQUIRED"
    assert details["effective"]["risk_level"] == "approval_required"
    assert details["effective"]["requires_approval"] is True

    reloaded = CapabilityCatalog(
        capabilities_dir=str(capabilities_dir),
        apps_dir=str(tmp_path / "apps"),
        data_dir=str(data_dir),
    )
    assert reloaded.risk_details("pc-server.test.sample")["effective"]["risk_level"] == "approval_required"


def test_capability_override_reset_restores_manifest_value(tmp_path) -> None:
    from aegis_ai.capability_catalog import CapabilityCatalog

    capabilities_dir = tmp_path / "capabilities"
    data_dir = tmp_path / "data"
    _write_manifest(capabilities_dir)
    catalog = CapabilityCatalog(
        capabilities_dir=str(capabilities_dir),
        apps_dir=str(tmp_path / "apps"),
        data_dir=str(data_dir),
    )
    catalog.get_override_store().upsert("pc-server.test.sample", risk_level="HIGH_RISK", updated_by="test")
    catalog.reload()
    assert catalog.risk_details("pc-server.test.sample")["effective"]["risk_level"] == "high_risk"

    assert catalog.get_override_store().reset("pc-server.test.sample") is True
    catalog.reload()
    details = catalog.risk_details("pc-server.test.sample")
    assert details["override_active"] is False
    assert details["effective"]["risk_level"] == "safe"


def test_corrupt_capability_override_store_falls_back_strictly(tmp_path) -> None:
    from aegis_ai.capability_catalog import CapabilityCatalog

    capabilities_dir = tmp_path / "capabilities"
    data_dir = tmp_path / "data"
    _write_manifest(capabilities_dir, risk="safe")
    override_path = data_dir / "settings" / "capability_overrides.json"
    override_path.parent.mkdir(parents=True, exist_ok=True)
    override_path.write_text("{not-json", encoding="utf-8")

    catalog = CapabilityCatalog(
        capabilities_dir=str(capabilities_dir),
        apps_dir=str(tmp_path / "apps"),
        data_dir=str(data_dir),
    )
    details = catalog.risk_details("pc-server.test.sample")

    assert details["override_store_corrupted"] is True
    assert details["effective"]["risk_level"] == "approval_required"
    assert details["effective"]["requires_approval"] is True


def test_tool_broker_denies_disabled_capability_override(tmp_path) -> None:
    from approval import ApprovalStore
    from policy_engine import PolicyEngine
    from tool_broker import ExecutionSource, InvokeStatus, ToolBroker, ToolExecutionRequest
    from tool_registry import ToolRegistry

    from aegis_ai.audit import AuditLog
    from aegis_ai.capability_catalog import CapabilityCatalog

    capabilities_dir = tmp_path / "capabilities"
    data_dir = tmp_path / "data"
    _write_manifest(capabilities_dir)
    catalog = CapabilityCatalog(
        capabilities_dir=str(capabilities_dir),
        apps_dir=str(tmp_path / "apps"),
        data_dir=str(data_dir),
    )
    catalog.get_override_store().upsert("pc-server.test.sample", enabled=False, updated_by="test")
    catalog.reload()

    broker = ToolBroker(
        registry=ToolRegistry(),
        policy_engine=PolicyEngine(approval_store=ApprovalStore(), data_dir=str(data_dir)),
        audit_log=AuditLog(path=str(data_dir / "audit.jsonl")),
        catalog=catalog,
    )
    result = broker.execute(
        ToolExecutionRequest(
            capability_id="pc-server.test.sample",
            arguments={},
            source=ExecutionSource.USER_EXPLICIT,
        )
    )

    assert result.status == InvokeStatus.DENIED
    assert "disabled" in result.error.lower()
