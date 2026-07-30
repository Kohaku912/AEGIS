"""Capability risk edits must permanently rewrite JSON manifests."""

from __future__ import annotations

import json
from pathlib import Path

from aegis_ai.capability_catalog import CapabilityCatalog


def test_update_manifest_policy_rewrites_source_json_and_clears_override(tmp_path: Path) -> None:
    caps_dir = tmp_path / "capabilities"
    manifest_path = caps_dir / "builtin" / "pc-server" / "test" / "sample.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "server_id": "pc-server",
                "app_id": "test",
                "action": "sample",
                "operation_category": "test_operation",
                "title": "Sample",
                "risk": {"level": "low", "requires_approval": False},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    catalog = CapabilityCatalog(str(caps_dir), data_dir=str(tmp_path / "data"))
    catalog.get_override_store().upsert(
        "pc-server.test.sample",
        risk_level="HIGH_RISK",
        updated_by="test",
        reason="temporary",
    )
    catalog.reload()
    assert catalog.risk_details("pc-server.test.sample")["override_active"] is True

    catalog.update_manifest_policy(
        "pc-server.test.sample",
        risk_level="APPROVAL_REQUIRED",
        requires_approval=True,
    )
    catalog.reload()

    written = json.loads(manifest_path.read_text(encoding="utf-8"))
    details = catalog.risk_details("pc-server.test.sample")
    assert written["risk"]["level"] == "approval_required"
    assert written["risk"]["requires_approval"] is True
    assert details["override_active"] is False
    assert details["effective"]["risk_level"] == "approval_required"
    assert details["effective"]["requires_approval"] is True
