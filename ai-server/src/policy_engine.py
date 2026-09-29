"""Policy Engine — deterministic hard stops for tool invocations.

NOT an LLM. NOT configurable by prompt. This is a structural gate that decides
whether an action is a **hard stop**; it no longer decides whether to *ask*.

Scope (narrowed 2026-09-27)
---------------------------
The project goal changed: the **only constraint** is that the user's information
must never leave the local environment. Approval, reversibility, policy consent and
reliability-proof are **no longer constraints**, so the interactive approval flow has
been retired (see ``docs/GOAL-CHANGE.md``).

Three hard stops remain (AGENTS.md §Security Policy):

1. **Egress** — enforced structurally by ``aegis_ai.egress``. This engine refuses
   capabilities whose id claims to bypass that gate, so the boundary cannot be
   talked out of its job.
2. **Purchases / payments** — irreversible, and a different axis from privacy.
3. **Gate / policy self-modification** — the boundary must not be able to disable
   itself.

Everything else executes, with audit. ``RiskLevel`` is retained as an
**annotation** for the owner's post-hoc visibility; it does not gate execution.

Architecture reference: docs/architecture.md §5.9, §7; docs/egress-gate.md
"""

from __future__ import annotations

import json
import re
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, ClassVar

from aegis_schema import safety_vocab
from aegis_schema.models import Capability, RiskLevel


class PolicyDecision(Enum):
    """Outcome of a policy evaluation.

    ``ASK_APPROVAL`` was removed on 2026-09-27 — approval is no longer a constraint.
    """

    ALLOW = auto()  # Execute immediately
    ALLOW_WITH_AUDIT = auto()  # Execute, but record the detail
    DENY = auto()  # Blocked — never execute (hard stop)
    UNAVAILABLE = auto()  # Server/device/permission missing


@dataclass
class PolicyResult:
    """Result of evaluating a capability against the policy.

    The risk fields (``reversibility``, ``destructive_effects``, ``data_loss_risk``,
    ``active_work_loss_risk``, ``blast_radius``, ``ownership_scope``) are
    **annotations** used for post-hoc visibility. They never block execution.
    Their vocabularies live in ``aegis_schema.safety_vocab``; an unset value
    reads as ``unknown`` rather than a safe-looking default.
    """

    decision: PolicyDecision
    reason: str = ""
    capability_id: str = ""
    risk_level: RiskLevel = RiskLevel.UNSPECIFIED
    audit_required: bool = True  # Whether to log to audit
    ownership_scope: str = safety_vocab.UNKNOWN
    reversibility: str = safety_vocab.UNKNOWN
    destructive_effects: list[str] = field(
        default_factory=lambda: [safety_vocab.UNKNOWN]
    )
    data_loss_risk: str = safety_vocab.UNKNOWN
    active_work_loss_risk: str = safety_vocab.UNKNOWN
    blast_radius: str = safety_vocab.UNKNOWN


# Type alias for custom rules
RuleFunc = Callable[[Capability, dict[str, Any]], PolicyResult | None]


class PolicyEngine:
    """Deterministic hard-stop rules engine.

    Architecture constraint (§7.3):
    - NOT an LLM prompt
    - Deterministic rules only
    - Fail-closed: unreachable PolicyEngine = all DENY
    - Every decision logged (Audit Log integration point)
    - Explicit deny rules for the three hard stops
    """

    # Monetary and self-protection actions are hard stops below. All other risk
    # levels execute with audit logging. Risk levels are annotations, not gates.
    DEFAULT_RISK_MAP: ClassVar[dict[RiskLevel, PolicyDecision]] = {
        RiskLevel.UNSPECIFIED: PolicyDecision.ALLOW_WITH_AUDIT,
        RiskLevel.READ_ONLY: PolicyDecision.ALLOW,
        RiskLevel.SAFE_ACTION: PolicyDecision.ALLOW_WITH_AUDIT,
        RiskLevel.APPROVAL_REQUIRED: PolicyDecision.ALLOW_WITH_AUDIT,
        RiskLevel.HIGH_RISK: PolicyDecision.ALLOW_WITH_AUDIT,
        RiskLevel.FORBIDDEN: PolicyDecision.DENY,
    }

    # Hard stops only: purchases/payments, egress-gate bypass, and policy
    # self-modification. The last group stays denied so this boundary cannot
    # disable itself or the egress gate.
    EXPLICIT_DENY_PATTERNS: ClassVar[list[str]] = [
        # 1. Purchases / payments — irreversible, separate axis from privacy.
        r".*\.purchase.*",
        r".*\.click_payment.*",
        r"pc\.click_payment.*$",
        r"android\.click_payment.*$",
        # 2. Egress gate bypass — the single constraint must not be circumventable.
        r".*\.bypass_egress.*",
        r".*\.disable_egress.*",
        r".*\.modify_egress.*$",
        r"dev\.disable_egress.*$",
        r"dev\.modify_egress.*$",
        # 3. Policy self-modification — the boundary must not disable itself.
        r".*\.bypass_policy.*",
        r".*\.disable_policy.*",
        r".*\.modify_policy.*$",
        r".*\.disable_policy_engine$",
        r"dev\.disable_policy_engine$",
        r"dev\.modify_policy.*$",
        r"pc\.modify_policy.*$",
    ]

    def __init__(self, data_dir: str = "data") -> None:
        self._rules: dict[str, list[RuleFunc]] = {}
        self._global_rules: list[RuleFunc] = []
        self._blocked_ids: set[str] = set()
        self._blocked_patterns: list[re.Pattern] = []
        self._risk_overrides: dict[str, RiskLevel] = {}
        self._explicit_deny: list[re.Pattern] = [re.compile(p) for p in self.EXPLICIT_DENY_PATTERNS]
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
                    "This is a hard stop (purchase/payment, egress bypass, or policy self-modification).",
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
                return result

        for rule in global_rules:
            result = rule(capability, params)
            if result is not None:
                return result

        effective_risk = risk_overrides.get(cap_id, capability.risk_level)
        decision = self.DEFAULT_RISK_MAP.get(effective_risk, PolicyDecision.ALLOW_WITH_AUDIT)

        reason_map = {
            PolicyDecision.ALLOW: f"Risk level {effective_risk.name} — allowed.",
            PolicyDecision.ALLOW_WITH_AUDIT: f"Risk level {effective_risk.name} — allowed with audit.",
            PolicyDecision.DENY: f"Risk level {effective_risk.name} — denied.",
        }
        return PolicyResult(
            decision=decision,
            reason=reason_map.get(decision, ""),
            capability_id=cap_id,
            risk_level=effective_risk,
            audit_required=(decision != PolicyDecision.ALLOW or effective_risk >= RiskLevel.SAFE_ACTION),
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


# ── Factory ──────────────────────────────────────────────────


def create_default_policy_engine() -> PolicyEngine:
    """Create a PolicyEngine with the purchase/egress-bypass/policy-bypass hard stops."""
    engine = PolicyEngine()
    engine.block_pattern(r".*\.purchase.*")
    engine.block_pattern(r".*\.bypass_egress.*")
    engine.block_pattern(r".*\.bypass_policy.*")
    engine.block_pattern(r".*\.disable_policy.*")
    return engine
