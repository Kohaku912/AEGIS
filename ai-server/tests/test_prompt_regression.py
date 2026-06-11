"""Tests for Prompt Regression Pack — policy/tool-use safety regression."""

from __future__ import annotations

from aegis_ai.evaluation.prompt_regression import (
    ALL_REGRESSION_CASES,
    BUILTIN_APPROVAL_BYPASS,
    BUILTIN_PHYSICAL_SAFETY,
    BUILTIN_SAFETY_WEAKENING,
    BUILTIN_TOOL_INJECTION,
    BUILTIN_USER_DANGEROUS,
    BUILTIN_WEB_INJECTION,
    PromptRegressionRunner,
    Severity,
)
from policy_engine import create_default_policy_engine

# ═══════════════════════════════════════════════════════════════
# 1. Regression Case Definitions
# ═══════════════════════════════════════════════════════════════


class TestRegressionCases:
    """Regression case definitions are valid."""

    def test_all_cases_not_empty(self):
        """ALL_REGRESSION_CASES has cases."""
        assert len(ALL_REGRESSION_CASES) >= 10

    def test_case_ids_unique(self):
        """Case IDs are unique."""
        ids = [c.case_id for c in ALL_REGRESSION_CASES]
        assert len(ids) == len(set(ids))

    def test_web_injection_cases(self):
        """Web injection cases exist."""
        assert len(BUILTIN_WEB_INJECTION) >= 2

    def test_tool_injection_cases(self):
        """Tool injection cases exist."""
        assert len(BUILTIN_TOOL_INJECTION) >= 1

    def test_user_dangerous_cases(self):
        """User dangerous cases exist."""
        assert len(BUILTIN_USER_DANGEROUS) >= 3

    def test_approval_bypass_cases(self):
        """Approval bypass cases exist."""
        assert len(BUILTIN_APPROVAL_BYPASS) >= 1

    def test_safety_weakening_cases(self):
        """Safety weakening cases exist."""
        assert len(BUILTIN_SAFETY_WEAKENING) >= 1

    def test_physical_safety_cases(self):
        """Physical safety cases exist."""
        assert len(BUILTIN_PHYSICAL_SAFETY) >= 1

    def test_all_cases_have_forbidden_actions(self):
        """All cases have at least one forbidden action."""
        for case in ALL_REGRESSION_CASES:
            assert len(case.forbidden_actions) >= 1, f"{case.case_id} has no forbidden_actions"

    def test_critical_severity_web_injection(self):
        """Web injection cases are critical severity."""
        for case in BUILTIN_WEB_INJECTION:
            assert case.severity == Severity.CRITICAL


# ═══════════════════════════════════════════════════════════════
# 2. Prompt Regression Runner
# ═══════════════════════════════════════════════════════════════


class TestPromptRegressionRunner:
    """Runner executes regression tests correctly."""

    def test_runner_with_default_policy(self):
        """Runner works with default PolicyEngine."""
        policy = create_default_policy_engine()
        runner = PromptRegressionRunner(policy_engine=policy)
        results = runner.run_all()
        assert len(results) >= 10

    def test_runner_no_policy(self):
        """Runner handles missing PolicyEngine."""
        runner = PromptRegressionRunner(policy_engine=None)
        result = runner.run_case(ALL_REGRESSION_CASES[0])
        assert result.passed is False
        assert "No PolicyEngine" in result.details

    def test_runner_with_audit(self):
        """Runner logs to audit log."""
        import os
        import tempfile

        from aegis_ai.audit import AuditLog
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        audit = AuditLog(path)
        policy = create_default_policy_engine()
        runner = PromptRegressionRunner(policy_engine=policy, audit_log=audit)
        runner.run_case(ALL_REGRESSION_CASES[0])
        assert len(audit.list_recent(10)) >= 1

    def test_runner_generates_report(self):
        """Runner generates human-readable report."""
        policy = create_default_policy_engine()
        runner = PromptRegressionRunner(policy_engine=policy)
        results = runner.run_all()
        report = runner.generate_report(results)
        assert "Prompt Regression Report" in report
        assert "Total:" in report


# ═══════════════════════════════════════════════════════════════
# 3. Policy Enforcement Tests
# ═══════════════════════════════════════════════════════════════


class TestPolicyEnforcement:
    """PolicyEngine correctly denies dangerous actions."""

    def _make_cap(self, cap_id: str, risk_level):
        """Helper to create a Capability with required fields."""
        from aegis_schema.models import Capability, ServerType
        server_map = {
            "pc.": ServerType.PC,
            "android.": ServerType.ANDROID,
            "browser.": ServerType.BROWSER,
            "room.": ServerType.ROOM,
            "dev.": ServerType.DEV,
        }
        server_type = ServerType.PC
        for prefix, st in server_map.items():
            if cap_id.startswith(prefix):
                server_type = st
                break
        return Capability(
            id=cap_id, name=cap_id, description=f"Test {cap_id}",
            server_type=server_type, risk_level=risk_level,
        )

    def test_send_sns_denied(self):
        """SNS posting is denied by explicit deny pattern."""
        from aegis_schema.models import RiskLevel
        policy = create_default_policy_engine()
        # Use APPROVAL_REQUIRED since FORBIDDEN can't be instantiated;
        # PolicyEngine EXPLICIT_DENY_PATTERNS catches *.send_sns
        cap = self._make_cap("browser.send_sns", RiskLevel.APPROVAL_REQUIRED)
        result = policy.evaluate(cap, {})
        assert result.decision.name == "DENY"

    def test_send_dm_denied(self):
        """DM sending is denied by explicit deny pattern."""
        from aegis_schema.models import RiskLevel
        policy = create_default_policy_engine()
        cap = self._make_cap("android.send_dm", RiskLevel.APPROVAL_REQUIRED)
        result = policy.evaluate(cap, {})
        assert result.decision.name == "DENY"

    def test_delete_file_denied(self):
        """File deletion is denied by explicit deny pattern."""
        from aegis_schema.models import RiskLevel
        policy = create_default_policy_engine()
        cap = self._make_cap("pc.delete_file", RiskLevel.APPROVAL_REQUIRED)
        result = policy.evaluate(cap, {})
        assert result.decision.name == "DENY"

    def test_merge_to_main_denied(self):
        """Merge to main is denied by explicit deny pattern."""
        from aegis_schema.models import RiskLevel
        policy = create_default_policy_engine()
        cap = self._make_cap("dev.merge_to_main", RiskLevel.APPROVAL_REQUIRED)
        result = policy.evaluate(cap, {})
        assert result.decision.name == "DENY"

    def test_send_email_denied(self):
        """Email sending is denied by explicit deny pattern."""
        from aegis_schema.models import RiskLevel
        policy = create_default_policy_engine()
        cap = self._make_cap("browser.send_email", RiskLevel.APPROVAL_REQUIRED)
        result = policy.evaluate(cap, {})
        assert result.decision.name == "DENY"

    def test_mouse_click_approval(self):
        """Mouse click requires approval."""
        from aegis_schema.models import RiskLevel
        policy = create_default_policy_engine()
        cap = self._make_cap("pc.mouse_click", RiskLevel.APPROVAL_REQUIRED)
        result = policy.evaluate(cap, {})
        assert result.decision.name == "ASK_APPROVAL"

    def test_read_only_allowed(self):
        """Read-only actions are allowed."""
        from aegis_schema.models import RiskLevel
        policy = create_default_policy_engine()
        cap = self._make_cap("pc.get_screenshot", RiskLevel.READ_ONLY)
        result = policy.evaluate(cap, {})
        assert result.decision.name == "ALLOW"
