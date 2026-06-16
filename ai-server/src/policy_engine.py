"""Policy Engine — deterministic safety enforcement for all tool invocations.

NOT an LLM. NOT configurable by prompt. This is a structural safety gate that:
1. Classifies every action as ALLOW / ASK_APPROVAL / DENY
2. Uses RiskLevel from the capability schema
3. Supports custom rules for specific capabilities
4. Cannot be bypassed by any code path in ToolBroker
5. Integrates with ApprovalStore for user approval flow
6. Enforces explicit deny rules for high-risk operations

Architecture reference: docs/architecture.md §5.9, §7
"""

from __future__ import annotations

import json
import re
import threading
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any

from aegis_schema.models import Capability, RiskLevel
from approval import ApprovalRequest, ApprovalStore, ApprovalType


class PolicyDecision(Enum):
    """Outcome of a policy evaluation."""

    ALLOW = auto()  # Execute immediately
    ASK_APPROVAL = auto()  # Must present Approval UI to user
    DENY = auto()  # Blocked — never execute


@dataclass
class PolicyResult:
    """Result of evaluating a capability against the policy."""

    decision: PolicyDecision
    reason: str = ""
    capability_id: str = ""
    risk_level: RiskLevel = RiskLevel.UNSPECIFIED
    required_approval_type: ApprovalType | None = None  # Set when ASK_APPROVAL
    expires_at_ms: int = 0  # When an approval would expire
    audit_required: bool = True  # Whether to log to audit
    approval_request: ApprovalRequest | None = None  # Created approval (if any)


# Type alias for custom rules
RuleFunc = Callable[[Capability, dict[str, Any]], PolicyResult | None]


class PolicyEngine:
    """Deterministic safety rules engine with ApprovalStore integration.

    Architecture constraint (§7.3):
    - NOT an LLM prompt
    - Deterministic rules only
    - Fail-closed: unreachable PolicyEngine = all DENY
    - Every decision logged (Audit Log integration point)
    - Explicit deny rules for high-risk operations
    - ApprovalStore manages user approval lifecycle
    """

    # Default risk-level → decision mapping
    DEFAULT_RISK_MAP: dict[RiskLevel, PolicyDecision] = {
        RiskLevel.UNSPECIFIED: PolicyDecision.DENY,
        RiskLevel.READ_ONLY: PolicyDecision.ALLOW,
        RiskLevel.SAFE_ACTION: PolicyDecision.ALLOW,
        RiskLevel.APPROVAL_REQUIRED: PolicyDecision.ASK_APPROVAL,
        RiskLevel.HIGH_RISK: PolicyDecision.ASK_APPROVAL,
        RiskLevel.FORBIDDEN: PolicyDecision.DENY,
    }

    # ── Explicitly denied patterns (always DENY, regardless of risk_level) ──
    # Per AGENTS.md Security Policy and architecture §7.
    # Phase 1.5: Expanded with all mandatory deny categories.
    EXPLICIT_DENY_PATTERNS: list[str] = [
        # ── Communication: SNS/DM/Email (non-browser) ──
        r".*\.send_sns$",
        r".*\.post_sns$",
        r"android\.send_dm$",
        r"android\.send_message$",
        r"android\.send_email$",
        r"pc\.send_dm$",
        r"pc\.send_message$",
        r"pc\.send_email$",
        r"room\.send_dm$",
        r"room\.send_message$",
        r"room\.send_email$",
        r"dev\.send_dm$",
        r"dev\.send_message$",
        r"dev\.send_email$",
        r"ai\.send_dm$",
        r"ai\.send_message$",
        r"ai\.send_email$",
        # Browser DM is still denied (not in approval patterns)
        r"browser\.send_dm$",
        # ── File operations ──
        r".*\.delete_file$",
        r".*\.delete_all$",
        r".*\.rm_.*",
        r".*\.wipe_.*",
        r".*\.bulk_delete.*",
        # ── External transmission ──
        r".*\.upload_.*",
        r".*\.transmit_.*",
        r".*\.external_upload.*",
        # ── Credential & secret access ──
        r".*\.read_credential.*",
        r".*\.write_credential.*",
        r".*\.access_ssh.*",
        r".*\.access_.*key.*",
        r".*\.read_secret.*",
        r".*\.sensitive_file_read.*",
        # ── Contact & privacy ──
        r".*\.contact_access.*",
        r".*\.read_contact.*",
        # ── Purchases ──
        r".*\.purchase.*",
        # ── Physical device control (high-risk) ──
        r"room\.ac_power_on$",
        r"room\.lock_.*",
        r"room\.move_robot_arm$",  # Level 3 — physical safety risk
        r"room\.robot_arm_move$",
        # ── Self-development (dangerous) ──
        r"dev\.merge_to_main$",
        r"dev\.push_main$",
        r"dev\.deploy_production$",
        r"dev\.production_deploy$",
        r"dev\.read_secrets$",
        r"dev\.delete_repo$",
        r"dev\.mount_docker_socket$",
        r"dev\.install_system_package$",
        r"dev\.disable_policy_engine$",
        r"dev\.modify_approval_bypass$",
        r"dev\.modify_policy.*$",
        # ── Permission & system changes ──
        r".*\.change_permission.*",
        r".*\.modify_acl.*",
        r".*\.grant_.*",
        r".*\.system_config.*",
        # ── Policy bypass (structural protection) ──
        r".*\.bypass_policy.*",
        r".*\.bypass_approval.*",
        r".*\.disable_policy.*",
        r".*\.captcha_bypass.*",
        r".*\.tos_bypass.*",
        # ── PC dangerous actions ──
        r"pc\.delete_file$",
        r"pc\.bulk_delete$",
        r"pc\.read_secret_file$",
        r"pc\.write_system_config$",
        r"pc\.run_shell.*$",
        r"pc\.type_password$",
        r"pc\.click_payment.*$",
        r"pc\.modify_policy.*$",
        # ── Android dangerous actions ──
        r"android\.send_sms$",
        r"android\.send_dm$",
        r"android\.post_sns$",
        r"android\.access_contacts$",
        r"android\.make_call$",
        r"android\.type_password$",
        r"android\.click_payment.*$",
        r"android\.captcha_bypass$",
        r"android\.tos_bypass.*$",
    ]

    # ── Explicitly approval-required patterns ────────────────
    # Phase 1.5: Expanded with mandatory approval categories.
    EXPLICIT_APPROVAL_PATTERNS: list[str] = [
        # Room/Physical control
        r"room\.ir_send$",
        r"room\.set_temperature$",
        r"room\.set_light$",
        r"room\.send_ir_command$",
        r"room\.set_air_conditioner$",
        r"room\.set_smart_plug$",
        r"room\.get_camera_snapshot$",
        # Dev server
        r"dev\.create_pr$",
        r"dev\.commit_changes$",
        r"dev\.apply_patch$",
        r"dev\.create_commit$",
        r"dev\.create_pull_request$",
        r"dev\.revert_changes$",
        # Browser interaction
        r"browser\.fill_form$",
        r"browser\.submit_form$",
        # Browser publish/send (always approval)
        r"browser\.publish_post$",
        r"browser\.send_message$",
        r"browser\.send_email$",
        # Browser signup (non-permissive profiles)
        r"browser\.submit_signup$",
        # PC operations
        r"pc\.install_package$",
        r"pc\.modify_registry$",
        # PC action operations (Level 2)
        r"pc\.mouse_click$",
        r"pc\.keyboard_type$",
        r"pc\.press_hotkey$",
        r"pc\.close_window$",
        r"pc\.write_clipboard$",
        r"pc\.write_file$",
        # Android action operations (Level 2)
        r"android\.tap$",
        r"android\.swipe$",
        r"android\.type_text$",
        # Self-dev PR and main-related
        r"dev\.create_pull_request$",
        # AGORA operations (external chat — always approval)
        r"^agora\.create_post$",
        r"^agora\.send_message$",
        r"^agora\.publish$",
    ]

    # ── Permissive-owner-allowed patterns (no approval needed) ──
    # These are allowed without approval in permissive_owner_assisted profile.
    # Always audited. Conditions: user logged in, no external send.
    PERMISSIVE_READ_PATTERNS: list[str] = [
        r"browser\.read_owned_account_page$",
        r"browser\.read_messages$",
        r"browser\.summarize_messages$",
        r"browser\.draft_reply$",
        r"browser\.draft_post$",
        r"browser\.check_signup_risk$",
        r"browser\.detect_payment_required$",
        r"browser\.detect_captcha$",
        r"browser\.detect_identity_verification$",
        r"browser\.detect_external_publish_action$",
        r"agora\.get_me$",
        r"agora\.read_posts$",
        r"agora\.read_thread_posts$",
        r"agora\.read_mentions$",
        r"agora\.get_cursor$",
        r"agora\.draft_reply$",
    ]

    # Low-risk signup patterns (allowed in permissive if risk check passes)
    PERMISSIVE_SIGNUP_PATTERNS: list[str] = [
        r"browser\.fill_signup_form$",
        r"browser\.submit_low_risk_signup$",
    ]

    def __init__(self, approval_store: ApprovalStore | None = None, data_dir: str = "data") -> None:
        self._rules: dict[str, list[RuleFunc]] = {}
        self._global_rules: list[RuleFunc] = []
        self._blocked_ids: set[str] = set()
        self._blocked_patterns: list[re.Pattern] = []
        self._risk_overrides: dict[str, RiskLevel] = {}
        self._explicit_deny: list[re.Pattern] = [re.compile(p) for p in self.EXPLICIT_DENY_PATTERNS]
        self._explicit_approval: list[re.Pattern] = [re.compile(p) for p in self.EXPLICIT_APPROVAL_PATTERNS]
        self._permissive_read: list[re.Pattern] = [re.compile(p) for p in self.PERMISSIVE_READ_PATTERNS]
        self._permissive_signup: list[re.Pattern] = [re.compile(p) for p in self.PERMISSIVE_SIGNUP_PATTERNS]
        self._approval_store = approval_store or ApprovalStore()
        self._autonomy_profile: str = "permissive_owner_assisted"
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._overrides_path = self._data_dir / "risk_overrides.json"
        self._lock = threading.RLock()
        self._load_overrides()

    # ── Public Evaluation API ──────────────────────────────

    def set_autonomy_profile(self, profile: str) -> None:
        """Set the autonomy profile."""
        valid = ("conservative", "balanced", "permissive_owner_assisted")
        if profile in valid:
            with self._lock:
                self._autonomy_profile = profile

    def evaluate_tool_invocation(
        self,
        capability: Capability,
        params: dict[str, Any] | None = None,
    ) -> PolicyResult:
        """Evaluate a tool invocation (primary ToolBroker entry point)."""
        return self._evaluate(capability, params, "tool_invocation")

    def evaluate_event_trigger(
        self,
        capability: Capability,
        params: dict[str, Any] | None = None,
    ) -> PolicyResult:
        """Evaluate an event-triggered action (more conservative)."""
        result = self._evaluate(capability, params, "event_trigger")
        if result.decision == PolicyDecision.ASK_APPROVAL:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason=f"Event-triggered execution denied: {result.reason}",
                capability_id=capability.id,
                risk_level=capability.risk_level,
                audit_required=True,
            )
        return result

    def evaluate_autonomous_task(
        self,
        capability: Capability,
        params: dict[str, Any] | None = None,
    ) -> PolicyResult:
        """Evaluate a self-initiated autonomous task (most conservative)."""
        result = self._evaluate(capability, params, "autonomous_task")
        if capability.risk_level == RiskLevel.SAFE_ACTION and result.decision == PolicyDecision.ALLOW:
            return self._create_approval_result(
                capability, params, reason_override="Autonomous task requires approval even for SAFE_ACTION."
            )
        return result

    def evaluate(
        self,
        capability: Capability,
        params: dict[str, Any] | None = None,
    ) -> PolicyResult:
        """Backward-compatible alias for evaluate_tool_invocation."""
        return self.evaluate_tool_invocation(capability, params)

    # ── Internal ───────────────────────────────────────────

    def _evaluate(
        self,
        capability: Capability,
        params: dict[str, Any] | None,
        context: str,
    ) -> PolicyResult:
        params = params or {}
        cap_id = capability.id
        with self._lock:
            blocked_ids = set(self._blocked_ids)
            blocked_patterns = list(self._blocked_patterns)
            rules = list(self._rules.get(cap_id, []))
            global_rules = list(self._global_rules)
            risk_overrides = dict(self._risk_overrides)
            autonomy_profile = self._autonomy_profile

        if cap_id in blocked_ids:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason=f"Capability '{cap_id}' is permanently blocked.",
                capability_id=cap_id,
                risk_level=capability.risk_level,
            )

        for pattern in self._explicit_deny:
            if pattern.match(cap_id):
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason=f"'{cap_id}' matches explicit deny pattern '{pattern.pattern}'. "
                    "This operation requires direct user action.",
                    capability_id=cap_id,
                    risk_level=RiskLevel.FORBIDDEN,
                    audit_required=True,
                )

        for pattern in blocked_patterns:
            if pattern.match(cap_id):
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason=f"'{cap_id}' matches blocked pattern '{pattern.pattern}'.",
                    capability_id=cap_id,
                    risk_level=capability.risk_level,
                )

        for rule in rules:
            result = rule(capability, params)
            if result is not None:
                return self._finalize(result, capability, params)

        for rule in global_rules:
            result = rule(capability, params)
            if result is not None:
                return self._finalize(result, capability, params)

        # ── Permissive owner-assisted patterns (no approval needed) ──
        if autonomy_profile == "permissive_owner_assisted":
            for pattern in self._permissive_read:
                if pattern.match(cap_id):
                    return PolicyResult(
                        decision=PolicyDecision.ALLOW,
                        reason=f"'{cap_id}' allowed in permissive_owner_assisted (read/draft).",
                        capability_id=cap_id,
                        risk_level=RiskLevel.READ_ONLY,
                        audit_required=True,
                    )
            for pattern in self._permissive_signup:
                if pattern.match(cap_id):
                    return PolicyResult(
                        decision=PolicyDecision.ALLOW,
                        reason=f"'{cap_id}' allowed in permissive_owner_assisted (low-risk signup).",
                        capability_id=cap_id,
                        risk_level=RiskLevel.SAFE_ACTION,
                        audit_required=True,
                    )

        for pattern in self._explicit_approval:
            if pattern.match(cap_id):
                # Check if already approved — if so, allow
                if self._approval_store.is_approved(cap_id):
                    return PolicyResult(
                        decision=PolicyDecision.ALLOW,
                        reason=f"Valid approval exists for '{cap_id}'.",
                        capability_id=cap_id,
                        risk_level=capability.risk_level,
                        audit_required=True,
                    )
                return self._create_approval_result(
                    capability, params, reason_override=f"'{cap_id}' matches explicit approval pattern."
                )

        effective_risk = risk_overrides.get(cap_id, capability.risk_level)
        decision = self.DEFAULT_RISK_MAP.get(effective_risk, PolicyDecision.DENY)

        reason_map = {
            PolicyDecision.ALLOW: f"Risk level {effective_risk.name} — allowed.",
            PolicyDecision.ASK_APPROVAL: f"Risk level {effective_risk.name} — approval required.",
            PolicyDecision.DENY: f"Risk level {effective_risk.name} — denied.",
        }
        result = PolicyResult(
            decision=decision,
            reason=reason_map.get(decision, ""),
            capability_id=cap_id,
            risk_level=effective_risk,
            audit_required=(decision != PolicyDecision.ALLOW or effective_risk >= RiskLevel.SAFE_ACTION),
        )
        return self._finalize(result, capability, params)

    def _finalize(self, result: PolicyResult, capability: Capability, params: dict[str, Any]) -> PolicyResult:
        """Post-process: create approval requests or upgrade to ALLOW if approved."""
        if result.decision == PolicyDecision.ASK_APPROVAL:
            # Check if there's already a valid approval
            if self._approval_store.is_approved(capability.id):
                return PolicyResult(
                    decision=PolicyDecision.ALLOW,
                    reason=f"Valid approval exists for '{capability.id}'. Allowed.",
                    capability_id=capability.id,
                    risk_level=capability.risk_level,
                    audit_required=True,
                )
            if result.approval_request is None:
                return self._create_approval_result(capability, params)
        return result

    def _create_approval_result(
        self, capability: Capability, params: dict[str, Any], reason_override: str | None = None
    ) -> PolicyResult:
        payload_str = str(params)
        if len(payload_str) > 200:
            payload_str = payload_str[:197] + "..."
        req = self._approval_store.create_request(
            capability_id=capability.id,
            tool_name=capability.name,
            requested_action=f"Execute '{capability.name}' ({capability.id})",
            human_readable_summary=(
                f"AEGIS wants to: {capability.description}\n"
                f"Risk level: {capability.risk_level.name}\n"
                f"Side effects: {', '.join(capability.side_effects) if capability.side_effects else 'None'}"
            ),
            risk_explanation=(
                f"Classified as {capability.risk_level.name}. "
                f"{'Side effects: ' + ', '.join(capability.side_effects) if capability.side_effects else ''}"
            ),
            payload_preview=payload_str,
            risk_level=capability.risk_level.value,
        )
        reason = reason_override or (
            f"Risk level {capability.risk_level.name} — approval required. Approval ID: {req.approval_id}"
        )
        return PolicyResult(
            decision=PolicyDecision.ASK_APPROVAL,
            reason=reason,
            capability_id=capability.id,
            risk_level=capability.risk_level,
            required_approval_type=ApprovalType.ONE_TIME,
            expires_at_ms=req.expires_at_ms,
            audit_required=True,
            approval_request=req,
        )

    # ── Configuration API ───────────────────────────────────

    def block_capability(self, capability_id: str) -> None:
        with self._lock:
            self._blocked_ids.add(capability_id)

    def block_pattern(self, pattern: str) -> None:
        with self._lock:
            self._blocked_patterns.append(re.compile(pattern))

    def set_risk_override(self, capability_id: str, risk_level: RiskLevel) -> None:
        if risk_level.value < 1:
            raise ValueError("Cannot override to UNSPECIFIED risk level")
        with self._lock:
            self._risk_overrides[capability_id] = risk_level
            self._save_overrides()

    def _load_overrides(self) -> None:
        if not self._overrides_path.exists():
            return
        try:
            with open(self._overrides_path, encoding="utf-8") as f:
                data = json.load(f)
            for cap_id, level_name in data.items():
                try:
                    self._risk_overrides[cap_id] = RiskLevel[level_name]
                except KeyError:
                    pass
        except Exception:
            pass

    def _save_overrides(self) -> None:
        data = {cap_id: level.name for cap_id, level in self._risk_overrides.items()}
        with open(self._overrides_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_rule(self, capability_id: str, rule: RuleFunc) -> None:
        with self._lock:
            if capability_id not in self._rules:
                self._rules[capability_id] = []
            self._rules[capability_id].append(rule)

    def add_global_rule(self, rule: RuleFunc) -> None:
        with self._lock:
            self._global_rules.append(rule)

    @property
    def approval_store(self) -> ApprovalStore:
        return self._approval_store


# ── Factory ──────────────────────────────────────────────────


def create_default_policy_engine() -> PolicyEngine:
    """Create a PolicyEngine with all explicit deny/approval patterns + blocked patterns."""
    engine = PolicyEngine()
    engine.block_pattern(r".*\.purchase.*")
    engine.block_pattern(r".*\.production_deploy$")
    return engine
