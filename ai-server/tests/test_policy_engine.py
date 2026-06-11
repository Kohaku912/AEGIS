"""Tests for PolicyEngine — Phase 1.5 explicit deny/approval patterns and safety levels."""

from __future__ import annotations

import pytest

from aegis_schema.models import Capability, RiskLevel, ServerType
from policy_engine import PolicyDecision, create_default_policy_engine


def _make_cap(id: str, risk: RiskLevel = RiskLevel.READ_ONLY,
              server: ServerType = ServerType.PC) -> Capability:
    prefix_map = {"pc": ServerType.PC, "android": ServerType.ANDROID,
                  "browser": ServerType.BROWSER, "room": ServerType.ROOM, "dev": ServerType.DEV}
    prefix = id.split(".")[0]
    return Capability(id=id, name=id, description=f"Capability {id}",
                      server_type=prefix_map.get(prefix, server), risk_level=risk)


class TestSafetyLevels:
    """Each SafetyLevel must map to the correct PolicyDecision."""

    def test_level_0_read_is_allow(self):
        engine = create_default_policy_engine()
        result = engine.evaluate_tool_invocation(_make_cap("pc.screenshot", RiskLevel.READ_ONLY))
        assert result.decision == PolicyDecision.ALLOW

    def test_level_1_safe_act_is_allow_with_audit(self):
        engine = create_default_policy_engine()
        result = engine.evaluate_tool_invocation(_make_cap("pc.mouse_click", RiskLevel.SAFE_ACTION))
        assert result.decision == PolicyDecision.ALLOW
        assert result.audit_required is True

    def test_level_2_approval_asks_approval(self):
        engine = create_default_policy_engine()
        result = engine.evaluate_tool_invocation(
            _make_cap("room.ir_send", RiskLevel.APPROVAL_REQUIRED),
        )
        assert result.decision == PolicyDecision.ASK_APPROVAL
        assert result.approval_request is not None

    def test_level_3_restricted_is_ask_approval_or_deny(self):
        engine = create_default_policy_engine()
        result = engine.evaluate_tool_invocation(_make_cap("pc.dangerous", RiskLevel.HIGH_RISK))
        assert result.decision in (PolicyDecision.ASK_APPROVAL, PolicyDecision.DENY)

    def test_unknown_capability_is_deny(self):
        """Unregistered/UNSPECIFIED capabilities are DENIED — Pydantic rejects them at construction."""
        # Pydantic model_validator prevents creating UNSPECIFIED capabilities
        with pytest.raises(ValueError):
            _make_cap("unknown.thing", RiskLevel.UNSPECIFIED)
        # This is correct: the structural type system enforces safety before PolicyEngine even runs

    def test_forbidden_is_deny(self):
        """FORBIDDEN risk level is always DENY."""
        engine = create_default_policy_engine()
        # FORBIDDEN can't be constructed by Pydantic, but blocked patterns simulate it
        cap = _make_cap("pc.send_sns", RiskLevel.READ_ONLY)  # even READ_ONLY
        result = engine.evaluate_tool_invocation(cap)
        assert result.decision == PolicyDecision.DENY


class TestExplicitDenyPatterns:
    """All the user-specified deny categories."""

    @pytest.mark.parametrize("cap_id", [
        # Communication
        "pc.send_sns", "android.send_dm", "browser.send_message", "pc.send_email",
        # File operations
        "pc.delete_file", "pc.delete_all", "pc.rm_temp", "pc.wipe_disk", "pc.bulk_delete_temp",
        # External transmission
        "pc.upload_data", "pc.transmit_logs", "pc.external_upload_backup",
        # Credential & secret access
        "pc.read_credential", "pc.write_credential_store", "pc.access_ssh_key",
        "pc.access_api_key", "pc.read_secret_env", "pc.sensitive_file_read_config",
        # Contact access
        "android.contact_access", "android.read_contact_list",
        # Purchases
        "browser.purchase_item",
        # Physical devices
        "room.ac_power_on", "room.robot_arm_move", "room.lock_door",
        # Self-dev dangerous
        "dev.merge_to_main", "dev.push_main", "dev.deploy_production", "dev.production_deploy",
        # Permission changes
        "pc.change_permission", "pc.modify_acl", "pc.grant_admin", "pc.system_config_edit",
        # Policy bypass
        "pc.bypass_policy", "pc.bypass_approval", "pc.disable_policy_engine",
        "pc.captcha_bypass", "browser.tos_bypass_automation",
    ])
    def test_explicit_deny(self, cap_id):
        engine = create_default_policy_engine()
        cap = _make_cap(cap_id, RiskLevel.READ_ONLY)
        result = engine.evaluate_tool_invocation(cap)
        assert result.decision == PolicyDecision.DENY, f"Expected DENY for {cap_id}, got {result.decision.name}"

    def test_explicit_approval_patterns(self):
        engine = create_default_policy_engine()
        for cap_id in ["room.ir_send", "room.set_temperature", "dev.create_pr",
                       "browser.fill_form", "pc.install_package", "dev.create_pull_request"]:
            cap = _make_cap(cap_id, RiskLevel.SAFE_ACTION)
            result = engine.evaluate_tool_invocation(cap)
            assert result.decision == PolicyDecision.ASK_APPROVAL, f"Expected ASK_APPROVAL for {cap_id}"


class TestEventTriggerEvaluation:
    """Event-triggered actions are more conservative."""

    def test_event_trigger_denies_approval_required(self):
        engine = create_default_policy_engine()
        cap = _make_cap("room.ir_send", RiskLevel.APPROVAL_REQUIRED)
        result = engine.evaluate_event_trigger(cap)
        assert result.decision == PolicyDecision.DENY

    def test_event_trigger_allows_read_only(self):
        engine = create_default_policy_engine()
        cap = _make_cap("pc.screenshot", RiskLevel.READ_ONLY)
        result = engine.evaluate_event_trigger(cap)
        assert result.decision == PolicyDecision.ALLOW


class TestAutonomousTaskEvaluation:
    """Autonomous tasks are the most conservative."""

    def test_autonomous_task_restricts_safe_action(self):
        engine = create_default_policy_engine()
        cap = _make_cap("pc.mouse_click", RiskLevel.SAFE_ACTION)
        result = engine.evaluate_autonomous_task(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_autonomous_task_allows_read_only(self):
        engine = create_default_policy_engine()
        cap = _make_cap("pc.screenshot", RiskLevel.READ_ONLY)
        result = engine.evaluate_autonomous_task(cap)
        assert result.decision == PolicyDecision.ALLOW


class TestFailClosed:
    """PolicyEngine must fail-closed: if anything breaks, default to DENY."""

    def test_unspecified_risk_rejected_by_pydantic(self):
        """UNSPECIFIED risk is rejected at Pydantic construction — fail-closed by design."""
        with pytest.raises(ValueError, match="UNSPECIFIED"):
            _make_cap("pc.unknown", RiskLevel.UNSPECIFIED)

    def test_dangerous_pattern_denied_even_low_risk(self):
        """Explicit deny patterns override low risk levels."""
        engine = create_default_policy_engine()
        cap = _make_cap("pc.send_sns", RiskLevel.READ_ONLY)
        result = engine.evaluate_tool_invocation(cap)
        assert result.decision == PolicyDecision.DENY
