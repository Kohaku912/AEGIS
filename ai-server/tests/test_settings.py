"""Tests for Settings Store, Models, Validation, and Permissions."""

from __future__ import annotations

import json

from aegis_ai.settings.defaults import create_default_settings
from aegis_ai.settings.models import (
    AutonomousSettings,
    CapabilityPermission,
    MemorySettings,
    NotificationSettings,
    PrivacySettings,
    ServerSettings,
)
from aegis_ai.settings.permissions import SettingsPermissionGuard
from aegis_ai.settings.store import SettingsStore
from aegis_ai.settings.validation import FORBIDDEN_CAPABILITIES, validate_settings_change
from aegis_schema.models import Capability, RiskLevel, ServerType
from policy_engine import PolicyDecision, create_default_policy_engine

# ═══════════════════════════════════════════════════════════════
# 1. Settings Models
# ═══════════════════════════════════════════════════════════════


class TestSettingsModels:
    """Settings models have correct defaults."""

    def test_default_settings(self):
        """Default settings have expected values."""
        settings = create_default_settings()
        assert settings.version == "1.0.0"
        assert settings.servers.browser_server_enabled is True
        assert settings.servers.pc_server_enabled is True
        assert settings.autonomous.autonomous_loop_enabled is True
        assert settings.autonomous.support_agent_enabled is True
        assert settings.memory.episodic_retention_days == 90
        assert settings.privacy.clipboard_capture_enabled is True
        assert settings.privacy.camera_snapshot_enabled is False

    def test_server_settings_defaults(self):
        """Server settings have correct defaults."""
        s = ServerSettings()
        assert s.browser_server_enabled is True
        assert s.health_check_interval_seconds == 30
        assert s.reconnect_policy == "exponential"

    def test_autonomous_settings_defaults(self):
        """Autonomous settings have correct defaults."""
        a = AutonomousSettings()
        assert a.autonomous_loop_enabled is True
        assert a.support_agent_enabled is True
        assert a.max_autonomous_runs_per_hour == 20
        assert a.cooldown_seconds == 60

    def test_memory_settings_defaults(self):
        """Memory settings have correct defaults."""
        m = MemorySettings()
        assert m.episodic_retention_days == 90
        assert m.semantic_memory_enabled is True
        assert m.sensitive_data_storage_enabled is False

    def test_privacy_settings_defaults(self):
        """Privacy settings have safe defaults."""
        p = PrivacySettings()
        assert p.clipboard_capture_enabled is True
        assert p.camera_snapshot_enabled is False
        assert p.external_llm_allowed is True

    def test_notification_settings_defaults(self):
        """Notification settings have correct defaults."""
        n = NotificationSettings()
        assert n.approval_notification_enabled is True
        assert n.support_suggestions_enabled is True
        assert n.quiet_hours_enabled is False


# ═══════════════════════════════════════════════════════════════
# 2. Settings Store
# ═══════════════════════════════════════════════════════════════


class TestSettingsStore:
    """Settings store persistence and operations."""

    def test_store_persists_settings(self):
        """Settings persist across store instances."""
        path = "data/test_settings_persist.json"
        audit_path = "data/test_settings_persist_audit.jsonl"

        store1 = SettingsStore(path=path, audit_path=audit_path)
        settings = store1.get()
        settings.autonomous.support_agent_enabled = False
        store1.update(settings, changed_by="test", reason="test")

        store2 = SettingsStore(path=path, audit_path=audit_path)
        assert store2.get().autonomous.support_agent_enabled is False

    def test_update_section(self):
        """Section updates work correctly."""
        path = "data/test_settings_section.json"
        store = SettingsStore(path=path, audit_path="data/test_settings_section_audit.jsonl")

        errors = store.update_section("autonomous", {"support_agent_enabled": False}, changed_by="test")
        assert errors == []
        assert store.get().autonomous.support_agent_enabled is False

    def test_reset_to_defaults(self):
        """Reset restores default settings."""
        path = "data/test_settings_reset.json"
        store = SettingsStore(path=path, audit_path="data/test_settings_reset_audit.jsonl")

        settings = store.get()
        settings.autonomous.support_agent_enabled = False
        store.update(settings, changed_by="test")

        store.reset_to_defaults(changed_by="test")
        assert store.get().autonomous.support_agent_enabled is True

    def test_export_import(self):
        """Export/import round-trips correctly."""
        path = "data/test_settings_export.json"
        store = SettingsStore(path=path, audit_path="data/test_settings_export_audit.jsonl")

        settings = store.get()
        settings.autonomous.daily_briefing_enabled = False
        store.update(settings, changed_by="test")

        exported = store.export_json()
        store.reset_to_defaults()
        errors = store.import_json(exported, changed_by="test")
        assert errors == []
        assert store.get().autonomous.daily_briefing_enabled is False

    def test_audit_logged(self):
        """Settings changes are audited."""
        path = "data/test_settings_audit.json"
        audit_path = "data/test_settings_audit.jsonl"
        store = SettingsStore(path=path, audit_path=audit_path)

        settings = store.get()
        settings.autonomous.support_agent_enabled = False
        store.update(settings, changed_by="user", reason="Disabled support")

        with open(audit_path, encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) >= 1
        last = json.loads(lines[-1])
        assert last["changed_by"] == "user"
        assert last["reason"] == "Disabled support"


# ═══════════════════════════════════════════════════════════════
# 3. Validation
# ═══════════════════════════════════════════════════════════════


class TestValidation:
    """Settings validation prevents unsafe changes."""

    def test_forbidden_capability_not_in_allowlist(self):
        """Cannot add forbidden capabilities to allowlist."""
        current = create_default_settings()
        proposed = create_default_settings()
        proposed.capabilities.allowlist = ["browser.send_sns"]

        errors = validate_settings_change(current, proposed)
        assert len(errors) >= 1
        assert "forbidden" in errors[0].lower() or "allowlist" in errors[0].lower()

    def test_forbidden_capability_not_enabled(self):
        """Cannot enable forbidden capabilities."""
        current = create_default_settings()
        proposed = create_default_settings()
        proposed.capabilities.per_capability["browser.send_sns"] = CapabilityPermission(
            capability_id="browser.send_sns", enabled=True,
        )

        errors = validate_settings_change(current, proposed)
        assert len(errors) >= 1

    def test_camera_snapshot_requires_confirmation(self):
        """Enabling camera snapshot requires confirmation."""
        current = create_default_settings()
        proposed = create_default_settings()
        proposed.privacy.camera_snapshot_enabled = True

        errors = validate_settings_change(current, proposed)
        assert len(errors) >= 1
        assert "camera" in errors[0].lower()

    def test_valid_change_no_errors(self):
        """Valid settings change has no errors."""
        current = create_default_settings()
        proposed = create_default_settings()
        proposed.autonomous.support_agent_enabled = False

        errors = validate_settings_change(current, proposed)
        assert errors == []

    def test_forbidden_capabilities_list(self):
        """FORBIDDEN_CAPABILITIES contains expected entries."""
        assert "browser.send_sns" in FORBIDDEN_CAPABILITIES
        assert "pc.delete_file" in FORBIDDEN_CAPABILITIES
        assert "dev.merge_to_main" in FORBIDDEN_CAPABILITIES
        assert "room.move_robot_arm" in FORBIDDEN_CAPABILITIES


# ═══════════════════════════════════════════════════════════════
# 4. Permission Guard
# ═══════════════════════════════════════════════════════════════


class TestPermissionGuard:
    """Settings permission guard integrates with PolicyEngine."""

    def test_disabled_capability_denied(self):
        """Disabled capability is denied by guard."""
        policy = create_default_policy_engine()
        store = SettingsStore(path="data/test_perm_disabled.json", audit_path="data/test_perm_disabled_audit.jsonl")

        settings = store.get()
        settings.capabilities.disabled_capabilities = ["browser.extract_text"]
        store.update(settings, changed_by="test")

        guard = SettingsPermissionGuard(policy, store)
        cap = Capability(
            id="browser.extract_text", name="Extract Text",
            description="Extract text from page",
            server_type=ServerType.BROWSER, risk_level=RiskLevel.READ_ONLY,
        )
        result = guard.evaluate(cap)
        assert result.decision == PolicyDecision.DENY
        assert "disabled" in result.reason.lower()

    def test_denylist_denied(self):
        """Denylisted capability is denied by guard."""
        policy = create_default_policy_engine()
        store = SettingsStore(path="data/test_perm_denylist.json", audit_path="data/test_perm_denylist_audit.jsonl")

        settings = store.get()
        settings.capabilities.denylist = ["browser.extract_text"]
        store.update(settings, changed_by="test")

        guard = SettingsPermissionGuard(policy, store)
        cap = Capability(
            id="browser.extract_text", name="Extract Text",
            description="Extract text from page",
            server_type=ServerType.BROWSER, risk_level=RiskLevel.READ_ONLY,
        )
        result = guard.evaluate(cap)
        assert result.decision == PolicyDecision.DENY
        assert "denylist" in result.reason.lower()

    def test_disabled_server_denied(self):
        """Capabilities from disabled server are denied."""
        policy = create_default_policy_engine()
        store = SettingsStore(path="data/test_perm_server.json", audit_path="data/test_perm_server_audit.jsonl")

        settings = store.get()
        settings.servers.browser_server_enabled = False
        store.update(settings, changed_by="test")

        guard = SettingsPermissionGuard(policy, store)
        cap = Capability(
            id="browser.extract_text", name="Extract Text",
            description="Extract text from page",
            server_type=ServerType.BROWSER, risk_level=RiskLevel.READ_ONLY,
        )
        result = guard.evaluate(cap)
        assert result.decision == PolicyDecision.DENY
        assert "disabled" in result.reason.lower()

    def test_clipboard_disabled_denied(self):
        """Clipboard capture disabled denies clipboard read."""
        policy = create_default_policy_engine()
        store = SettingsStore(path="data/test_perm_clipboard.json", audit_path="data/test_perm_clipboard_audit.jsonl")

        settings = store.get()
        settings.privacy.clipboard_capture_enabled = False
        store.update(settings, changed_by="test")

        guard = SettingsPermissionGuard(policy, store)
        cap = Capability(
            id="pc.get_clipboard", name="Get Clipboard",
            description="Read clipboard",
            server_type=ServerType.PC, risk_level=RiskLevel.READ_ONLY,
        )
        result = guard.evaluate(cap)
        assert result.decision == PolicyDecision.DENY
        assert "clipboard" in result.reason.lower()

    def test_camera_disabled_denied(self):
        """Camera snapshot disabled denies camera read."""
        policy = create_default_policy_engine()
        store = SettingsStore(path="data/test_perm_camera.json", audit_path="data/test_perm_camera_audit.jsonl")

        # Camera is disabled by default
        guard = SettingsPermissionGuard(policy, store)
        cap = Capability(
            id="room.get_camera_snapshot", name="Camera Snapshot",
            description="Capture camera snapshot",
            server_type=ServerType.ROOM, risk_level=RiskLevel.APPROVAL_REQUIRED,
        )
        result = guard.evaluate(cap)
        assert result.decision == PolicyDecision.DENY
        assert "camera" in result.reason.lower()

    def test_allowed_capability_passes_through(self):
        """Allowed capability passes through to PolicyEngine."""
        policy = create_default_policy_engine()
        store = SettingsStore(path="data/test_perm_allowed.json", audit_path="data/test_perm_allowed_audit.jsonl")

        guard = SettingsPermissionGuard(policy, store)
        cap = Capability(
            id="browser.extract_text", name="Extract Text",
            description="Extract text from page",
            server_type=ServerType.BROWSER, risk_level=RiskLevel.READ_ONLY,
        )
        result = guard.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_forbidden_still_denied_by_guard(self):
        """Forbidden capabilities are still denied by PolicyEngine through guard."""
        policy = create_default_policy_engine()
        store = SettingsStore(path="data/test_perm_forbidden.json", audit_path="data/test_perm_forbidden_audit.jsonl")

        guard = SettingsPermissionGuard(policy, store)
        cap = Capability(
            id="browser.send_sns", name="Send SNS",
            description="Post to social media",
            server_type=ServerType.BROWSER, risk_level=RiskLevel.READ_ONLY,
        )
        result = guard.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_is_capability_enabled(self):
        """is_capability_enabled reflects settings state."""
        policy = create_default_policy_engine()
        store = SettingsStore(path="data/test_perm_enabled.json", audit_path="data/test_perm_enabled_audit.jsonl")
        store.reset_to_defaults(changed_by="test")

        guard = SettingsPermissionGuard(policy, store)
        assert guard.is_capability_enabled("browser.extract_text") is True

        settings = store.get()
        settings.capabilities.disabled_capabilities = ["browser.extract_text"]
        store.update(settings, changed_by="test")

        assert guard.is_capability_enabled("browser.extract_text") is False


# ═══════════════════════════════════════════════════════════════
# 5. Web Routes
# ═══════════════════════════════════════════════════════════════


class TestSettingsWebRoutes:
    """Settings web routes work correctly."""

    def test_get_settings(self):
        """Get settings returns full config."""
        from aegis_ai.web.settings_routes import SettingsWebApp

        store = SettingsStore(path="data/test_web_get.json", audit_path="data/test_web_get_audit.jsonl")
        app = SettingsWebApp(settings_store=store)

        result = app.get_settings()
        assert "servers" in result
        assert "autonomous" in result
        assert "privacy" in result

    def test_get_section(self):
        """Get section returns specific section."""
        from aegis_ai.web.settings_routes import SettingsWebApp

        store = SettingsStore(path="data/test_web_section.json", audit_path="data/test_web_section_audit.jsonl")
        app = SettingsWebApp(settings_store=store)

        result = app.get_section("autonomous")
        assert "support_agent_enabled" in result

    def test_update_section(self):
        """Update section changes settings."""
        from aegis_ai.web.settings_routes import SettingsWebApp

        store = SettingsStore(path="data/test_web_update.json", audit_path="data/test_web_update_audit.jsonl")
        app = SettingsWebApp(settings_store=store)

        result = app.update_section("autonomous", {"support_agent_enabled": False}, changed_by="test")
        assert result["success"] is True
        assert store.get().autonomous.support_agent_enabled is False

    def test_reset_to_defaults(self):
        """Reset restores defaults."""
        from aegis_ai.web.settings_routes import SettingsWebApp

        store = SettingsStore(path="data/test_web_reset.json", audit_path="data/test_web_reset_audit.jsonl")
        app = SettingsWebApp(settings_store=store)

        app.update_section("autonomous", {"support_agent_enabled": False})
        result = app.reset_to_defaults()
        assert result["success"] is True
        assert store.get().autonomous.support_agent_enabled is True

    def test_export_import(self):
        """Export/import round-trips through web routes."""
        from aegis_ai.web.settings_routes import SettingsWebApp

        store = SettingsStore(path="data/test_web_export.json", audit_path="data/test_web_export_audit.jsonl")
        app = SettingsWebApp(settings_store=store)

        app.update_section("autonomous", {"daily_briefing_enabled": False})
        exported = app.export_settings()

        app.reset_to_defaults()
        result = app.import_settings(exported)
        assert result["success"] is True
        assert store.get().autonomous.daily_briefing_enabled is False
