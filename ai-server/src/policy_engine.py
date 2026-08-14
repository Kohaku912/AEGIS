"""Policy Engine — deterministic safety enforcement for all tool invocations.

NOT an LLM. NOT configurable by prompt. This is a structural safety gate that:
1. Classifies every action as ALLOW / ALLOW_WITH_AUDIT / ASK_APPROVAL / DENY / UNAVAILABLE
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
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any

from aegis_schema.models import Capability, RiskLevel
from approval import ApprovalRequest, ApprovalStore, ApprovalType


class PolicyDecision(Enum):
    """Outcome of a policy evaluation."""

    ALLOW = auto()  # Execute immediately
    ALLOW_WITH_AUDIT = auto()  # No approval needed, but log details
    ASK_APPROVAL = auto()  # Must present Approval UI to user
    DENY = auto()  # Blocked — never execute
    UNAVAILABLE = auto()  # Server/device/permission missing


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
    ownership_scope: str = ""  # aegis | user | system | external
    reversibility: str = ""  # fully_reversible | recoverable | difficult | irreversible
    destructive_effects: list[str] = field(default_factory=list)
    data_loss_risk: str = "none"  # none | low | medium | high
    active_work_loss_risk: str = "none"
    blast_radius: str = "single"  # single | bounded | bulk | system_wide


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
        RiskLevel.UNSPECIFIED: PolicyDecision.ALLOW_WITH_AUDIT,
        RiskLevel.READ_ONLY: PolicyDecision.ALLOW,
        RiskLevel.SAFE_ACTION: PolicyDecision.ALLOW_WITH_AUDIT,
        RiskLevel.APPROVAL_REQUIRED: PolicyDecision.ALLOW_WITH_AUDIT,
        RiskLevel.HIGH_RISK: PolicyDecision.ALLOW_WITH_AUDIT,
        RiskLevel.FORBIDDEN: PolicyDecision.DENY,
    }

    # Hard stops only: purchases and policy self-modification.
    # Everything else is ALLOW_WITH_AUDIT; the user may tighten via Catalog overrides.
    EXPLICIT_DENY_PATTERNS: list[str] = [
        r".*\.purchase.*",
        r".*\.click_payment.*",
        r".*\.bypass_policy.*",
        r".*\.bypass_approval.*",
        r".*\.disable_policy.*",
        r".*\.modify_policy.*$",
        r".*\.disable_policy_engine$",
        r".*\.modify_approval_bypass$",
        r"dev\.disable_policy_engine$",
        r"dev\.modify_approval_bypass$",
        r"dev\.modify_policy.*$",
        r"pc\.modify_policy.*$",
        r"pc\.click_payment.*$",
        r"android\.click_payment.*$",
    ]

    def __init__(self, approval_store: ApprovalStore | None = None, data_dir: str = "data") -> None:
        self._rules: dict[str, list[RuleFunc]] = {}
        self._global_rules: list[RuleFunc] = []
        self._blocked_ids: set[str] = set()
        self._blocked_patterns: list[re.Pattern] = []
        self._risk_overrides: dict[str, RiskLevel] = {}
        self._explicit_deny: list[re.Pattern] = [re.compile(p) for p in self.EXPLICIT_DENY_PATTERNS]
        self._approval_store = approval_store or ApprovalStore()
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._overrides_path = self._data_dir / "risk_overrides.json"
        self._lock = threading.RLock()
        self._load_overrides()

    # ── Public Evaluation API ──────────────────────────────

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
        """Evaluate an event-triggered action (same path as chat/tool invocation)."""
        return self._evaluate(capability, params, "event_trigger")

    def evaluate_autonomous_task(
        self,
        capability: Capability,
        params: dict[str, Any] | None = None,
    ) -> PolicyResult:
        """Evaluate a self-initiated autonomous task (same path as chat/tool invocation)."""
        return self._evaluate(capability, params, "autonomous_task")

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

        # Catalog toggle: user may re-tighten a capability without changing risk maps.
        if capability.requires_approval:
            if self._approval_store is not None and self._approval_store.is_approved(cap_id):
                return PolicyResult(
                    decision=PolicyDecision.ALLOW,
                    reason=f"Valid approval exists for '{cap_id}'.",
                    capability_id=cap_id,
                    risk_level=capability.risk_level,
                    audit_required=True,
                )
            return self._create_approval_result(
                capability, params, reason_override=f"'{cap_id}' requires approval (catalog override)."
            )

        effective_risk = risk_overrides.get(cap_id, capability.risk_level)
        decision = self.DEFAULT_RISK_MAP.get(effective_risk, PolicyDecision.ALLOW_WITH_AUDIT)

        reason_map = {
            PolicyDecision.ALLOW: f"Risk level {effective_risk.name} — allowed.",
            PolicyDecision.ALLOW_WITH_AUDIT: f"Risk level {effective_risk.name} — allowed with audit.",
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
        """Post-process: upgrade to ALLOW if valid approval exists (deprecated path)."""
        if result.decision == PolicyDecision.ASK_APPROVAL:
            if self._approval_store is not None and self._approval_store.is_approved(capability.id):
                return PolicyResult(
                    decision=PolicyDecision.ALLOW,
                    reason=f"Valid approval exists for '{capability.id}'. Allowed.",
                    capability_id=capability.id,
                    risk_level=capability.risk_level,
                    audit_required=True,
                )
        return result

    def _create_approval_result(
        self, capability: Capability, params: dict[str, Any], reason_override: str | None = None
    ) -> PolicyResult:
        """Create an ASK_APPROVAL PolicyResult.

        NOTE: Does NOT create an ApprovalRequest. That responsibility
        has moved to ToolBroker/ApprovalManager. This method only
        returns the policy decision with expiry metadata.
        """
        # Calculate expiry based on risk level (matches approval_types._EXPIRY_BY_RISK)
        expiry_by_risk = {
            RiskLevel.READ_ONLY: 3_600_000,      # 1 hour
            RiskLevel.SAFE_ACTION: 3_600_000,     # 1 hour
            RiskLevel.APPROVAL_REQUIRED: 1_800_000,  # 30 min
            RiskLevel.HIGH_RISK: 600_000,         # 10 min
        }
        now_ms = int(time.time() * 1000)
        expiry_ms = expiry_by_risk.get(capability.risk_level, 1_800_000)
        expires_at_ms = now_ms + expiry_ms

        reason = reason_override or (
            f"Risk level {capability.risk_level.name} — approval required."
        )
        return PolicyResult(
            decision=PolicyDecision.ASK_APPROVAL,
            reason=reason,
            capability_id=capability.id,
            risk_level=capability.risk_level,
            required_approval_type=ApprovalType.ONE_TIME,
            expires_at_ms=expires_at_ms,
            audit_required=True,
            approval_request=None,
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

    def clear_risk_override(self, capability_id: str) -> None:
        """Remove a per-capability risk override so manifest JSON is authoritative."""
        with self._lock:
            if capability_id in self._risk_overrides:
                self._risk_overrides.pop(capability_id, None)
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
    """Create a PolicyEngine with purchase/policy-bypass hard stops."""
    engine = PolicyEngine()
    engine.block_pattern(r".*\.purchase.*")
    engine.block_pattern(r".*\.bypass_policy.*")
    engine.block_pattern(r".*\.disable_policy.*")
    return engine
