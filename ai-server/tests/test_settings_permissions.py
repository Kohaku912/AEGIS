from __future__ import annotations

from aegis_ai.settings.store import SettingsStore
from aegis_ai.settings.permissions import SettingsPermissionGuard
from aegis_schema.models import Capability, RiskLevel, ServerType
from policy_engine import PolicyDecision, PolicyResult


class AllowPolicy:
    def evaluate(self, capability: Capability, params=None) -> PolicyResult:
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            capability_id=capability.id,
            risk_level=capability.risk_level,
        )


def _store(tmp_path) -> SettingsStore:
    return SettingsStore(
        path=str(tmp_path / "config" / "settings.json"),
        audit_path=str(tmp_path / "data" / "settings_audit.jsonl"),
    )


def _cap(capability_id: str, server_type: ServerType) -> Capability:
    return Capability(
        id=capability_id,
        name="Test capability",
        description="Test capability",
        server_type=server_type,
        risk_level=RiskLevel.READ_ONLY,
    )


def test_settings_guard_applies_canonical_pc_server_prefix(tmp_path) -> None:
    store = _store(tmp_path)
    settings = store.get()
    settings.servers.pc_server_enabled = False
    assert store.update(settings) == []

    guard = SettingsPermissionGuard(AllowPolicy(), store)
    result = guard.evaluate(_cap("pc-server.system.get_os_info", ServerType.PC))

    assert result.decision == PolicyDecision.DENY
    assert "disabled" in result.reason


def test_settings_guard_applies_clipboard_privacy_to_canonical_id(tmp_path) -> None:
    store = _store(tmp_path)
    settings = store.get()
    settings.privacy.clipboard_capture_enabled = False
    assert store.update(settings) == []

    guard = SettingsPermissionGuard(AllowPolicy(), store)
    result = guard.evaluate(_cap("pc-server.clipboard.get_clipboard", ServerType.PC))

    assert result.decision == PolicyDecision.DENY
    assert "Clipboard" in result.reason
