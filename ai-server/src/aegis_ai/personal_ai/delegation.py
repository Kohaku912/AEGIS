"""User-specific delegation policy layered on top of PolicyEngine."""

from __future__ import annotations

import fnmatch
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aegis_ai.personal_ai.storage import JsonStateFile, now_ms


@dataclass
class DelegationDecision:
    decision: str = "no_match"  # auto_allowed | approval_required | forbidden | no_match
    reason: str = ""
    rule_id: str = ""
    dimensions: dict[str, str] = field(default_factory=dict)


@dataclass
class DelegationContext:
    """Explicit delegation dimensions supplied by planning or manifests."""

    operation_category: str = "general"
    scope: str = "aegis"
    audience: str = "private"
    content_sensitivity: str = "normal"
    reversibility: str = "reversible"

    def to_dict(self) -> dict[str, str]:
        return self.__dict__.copy()


@dataclass
class DelegationRule:
    rule_id: str
    capability_pattern: str
    decision: str
    operation_category: str = ""
    scope: str = ""
    audience: str = ""
    content_sensitivity: str = ""
    reversibility: str = ""
    description: str = ""
    enabled: bool = True
    created_at: int = 0
    updated_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DelegationRule:
        return cls(
            rule_id=str(data.get("rule_id") or f"del_{uuid.uuid4().hex[:10]}"),
            capability_pattern=str(data.get("capability_pattern") or "*"),
            decision=str(data.get("decision") or "approval_required"),
            operation_category=str(data.get("operation_category") or ""),
            scope=str(data.get("scope") or ""),
            audience=str(data.get("audience") or ""),
            content_sensitivity=str(data.get("content_sensitivity") or ""),
            reversibility=str(data.get("reversibility") or ""),
            description=str(data.get("description") or ""),
            enabled=bool(data.get("enabled", True)),
            created_at=int(data.get("created_at") or 0),
            updated_at=int(data.get("updated_at") or 0),
        )


class DelegationPolicyStore:
    """Persistent personal delegation policy.

    This store can only add restrictions. It never weakens PolicyEngine.
    """

    APPROVAL_CATEGORIES = {
        "external_send",
        "social_post",
        "delete",
        "push",
        "payment",
        "physical_device",
        "system_change",
    }

    def __init__(
        self, data_dir: str = "data/personal_ai", audit_manager: Any = None, user_model_store: Any = None
    ) -> None:
        self._state = JsonStateFile(Path(data_dir) / "delegation_policy.json", {"rules": []})
        self._audit_manager = audit_manager
        self._user_model_store = user_model_store
        self._rules: list[DelegationRule] = []
        self._load()
        if not self._rules:
            self._install_defaults()
        else:
            self._migrate_builtin_rules()

    def list_rules(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self._rules]

    def upsert_rule(self, patch: dict[str, Any]) -> dict[str, Any]:
        now = now_ms()
        rule_id = str(patch.get("rule_id") or f"del_{uuid.uuid4().hex[:10]}")
        rule = next((r for r in self._rules if r.rule_id == rule_id), None)
        if rule is None:
            rule = DelegationRule(
                rule_id=rule_id,
                capability_pattern=str(patch.get("capability_pattern") or "*"),
                decision=str(patch.get("decision") or "approval_required"),
                created_at=now,
                updated_at=now,
            )
            self._rules.append(rule)
        for key in (
            "capability_pattern",
            "decision",
            "operation_category",
            "scope",
            "audience",
            "content_sensitivity",
            "reversibility",
            "description",
            "enabled",
        ):
            if key in patch:
                setattr(rule, key, bool(patch[key]) if key == "enabled" else str(patch[key]))
        rule.updated_at = now
        self._save()
        self._audit("delegation_policy_updated", {"rule": rule.to_dict()})
        return rule.to_dict()

    def delete_rule(self, rule_id: str) -> bool:
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.rule_id != rule_id]
        changed = len(self._rules) != before
        if changed:
            self._save()
            self._audit("delegation_policy_deleted", {"rule_id": rule_id})
        return changed

    def evaluate(
        self,
        capability_id: str,
        params: dict[str, Any] | None = None,
        side_effects: list[str] | None = None,
        operation_context: DelegationContext | dict[str, Any] | None = None,
    ) -> DelegationDecision:
        """Evaluate an operation from declared dimensions, never message text."""
        context = self._normalize_context(
            params=params,
            side_effects=side_effects,
            operation_context=operation_context,
        )
        for rule in self._rules:
            if not rule.enabled:
                continue
            if rule.operation_category and rule.operation_category != context.operation_category:
                continue
            if rule.scope and rule.scope != context.scope:
                continue
            if rule.audience and rule.audience != context.audience:
                continue
            if rule.content_sensitivity and rule.content_sensitivity != context.content_sensitivity:
                continue
            if rule.reversibility and rule.reversibility != context.reversibility:
                continue
            if fnmatch.fnmatchcase(capability_id, rule.capability_pattern):
                return DelegationDecision(
                    decision=rule.decision,
                    reason=rule.description or f"Delegation policy matched {rule.capability_pattern}.",
                    rule_id=rule.rule_id,
                    dimensions=context.to_dict(),
                )
        if (
            context.operation_category in self.APPROVAL_CATEGORIES
            or context.scope in {"user", "external", "system"}
            or context.audience in {"shared", "public", "third_party"}
            or context.content_sensitivity in {"personal", "confidential", "secret"}
            or context.reversibility in {"difficult", "irreversible"}
        ):
            return DelegationDecision(
                decision="approval_required",
                reason=(
                    "Delegation contract requires approval for the declared scope, audience, content, or reversibility."
                ),
                rule_id="default_delegation_contract",
                dimensions=context.to_dict(),
            )
        return DelegationDecision(dimensions=context.to_dict())

    def get_summary(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for rule in self._rules:
            counts[rule.decision] = counts.get(rule.decision, 0) + 1
        return {"rules": self.list_rules(), "counts": counts}

    def to_context_string(self) -> str:
        active = [r for r in self._rules if r.enabled][:8]
        if not active:
            return "Delegation policy: no personal overrides."
        lines = ["Delegation policy:"]
        for rule in active:
            dimensions = "/".join(
                value
                for value in (
                    rule.operation_category,
                    rule.scope,
                    rule.audience,
                    rule.content_sensitivity,
                    rule.reversibility,
                )
                if value
            )
            lines.append(f"- {rule.capability_pattern}: {rule.decision} ({dimensions or 'any'})")
        return "\n".join(lines)

    def _normalize_context(
        self,
        *,
        params: dict[str, Any] | None,
        side_effects: list[str] | None,
        operation_context: DelegationContext | dict[str, Any] | None,
    ) -> DelegationContext:
        if isinstance(operation_context, DelegationContext):
            return operation_context
        declared = dict(operation_context or {})
        argument_context = dict((params or {}).get("_delegation_context") or {})
        for key, value in argument_context.items():
            declared.setdefault(key, value)
        effects = [str(item) for item in (side_effects or [])]
        category = str(declared.get("operation_category") or "")
        if not category:
            category = next(
                (item for item in effects if item in self.APPROVAL_CATEGORIES),
                "general",
            )
        return DelegationContext(
            operation_category=category,
            scope=str(declared.get("scope") or "aegis"),
            audience=str(declared.get("audience") or "private"),
            content_sensitivity=str(declared.get("content_sensitivity") or "normal"),
            reversibility=str(declared.get("reversibility") or "reversible"),
        )

    def _install_defaults(self) -> None:
        now = now_ms()
        defaults = [
            (
                "del_external_send",
                "*",
                "approval_required",
                "external_send",
                "External communication must be approved.",
            ),
            (
                "del_social_post",
                "*",
                "approval_required",
                "social_communication",
                "Social posting requires an audience-aware approval.",
            ),
            ("del_delete", "*", "approval_required", "delete", "Deletion must be approved."),
            ("del_push", "*", "approval_required", "push", "Git push must be approved."),
            ("del_payment", "*", "approval_required", "payment", "Payment or billing APIs must be approved."),
            ("del_physical", "*", "approval_required", "physical_device", "Physical device control must be approved."),
        ]
        self._rules = [
            DelegationRule(
                rule_id=rid,
                capability_pattern=pattern,
                decision=decision,
                operation_category=cat,
                description=desc,
                created_at=now,
                updated_at=now,
            )
            for rid, pattern, decision, cat, desc in defaults
        ]
        self._save()

    def _migrate_builtin_rules(self) -> None:
        """Keep shipped safety rules current without changing user rules."""
        changed = False
        for rule in self._rules:
            if rule.rule_id == "del_social_post" and rule.decision == "allow":
                rule.decision = "approval_required"
                rule.description = (
                    "Social posting requires an audience-aware approval."
                )
                rule.updated_at = now_ms()
                changed = True
        if changed:
            self._save()

    def _load(self) -> None:
        data = self._state.load()
        self._rules = [DelegationRule.from_dict(x) for x in data.get("rules", []) if isinstance(x, dict)]

    def _save(self) -> None:
        self._state.save({"rules": [r.to_dict() for r in self._rules], "updated_at": now_ms()})

    def _audit(self, action: str, detail: dict[str, Any]) -> None:
        if self._audit_manager is None:
            return
        try:
            self._audit_manager.log_decision(
                action=action, actor="delegation_policy", decision="success", reason=action, detail=detail
            )
        except Exception:
            pass
