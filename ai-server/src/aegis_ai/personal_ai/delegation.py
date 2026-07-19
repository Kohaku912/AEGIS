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


@dataclass
class DelegationRule:
    rule_id: str
    capability_pattern: str
    decision: str
    operation_category: str = ""
    description: str = ""
    enabled: bool = True
    created_at: int = 0
    updated_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DelegationRule":
        return cls(
            rule_id=str(data.get("rule_id") or f"del_{uuid.uuid4().hex[:10]}"),
            capability_pattern=str(data.get("capability_pattern") or "*"),
            decision=str(data.get("decision") or "approval_required"),
            operation_category=str(data.get("operation_category") or ""),
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

    def __init__(self, data_dir: str = "data/personal_ai", audit_manager: Any = None, user_model_store: Any = None) -> None:
        self._state = JsonStateFile(Path(data_dir) / "delegation_policy.json", {"rules": []})
        self._audit_manager = audit_manager
        self._user_model_store = user_model_store
        self._rules: list[DelegationRule] = []
        self._load()
        if not self._rules:
            self._install_defaults()

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
        for key in ("capability_pattern", "decision", "operation_category", "description", "enabled"):
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

    def evaluate(self, capability_id: str, params: dict[str, Any] | None = None, side_effects: list[str] | None = None) -> DelegationDecision:
        side_effects = [str(s).lower() for s in (side_effects or [])]
        category = self._infer_category(capability_id, side_effects)
        for rule in self._rules:
            if not rule.enabled:
                continue
            if rule.operation_category and rule.operation_category != category:
                continue
            if fnmatch.fnmatchcase(capability_id, rule.capability_pattern):
                return DelegationDecision(
                    decision=rule.decision,
                    reason=rule.description or f"Delegation policy matched {rule.capability_pattern}.",
                    rule_id=rule.rule_id,
                )
        if category in self.APPROVAL_CATEGORIES:
            return DelegationDecision(
                decision="approval_required",
                reason=f"Delegation policy requires approval for {category}.",
                rule_id="default_external_safety",
            )
        return DelegationDecision()

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
            lines.append(f"- {rule.capability_pattern}: {rule.decision} ({rule.operation_category or 'any'})")
        return "\n".join(lines)

    def _infer_category(self, capability_id: str, side_effects: list[str]) -> str:
        cid = capability_id.lower()
        text = " ".join([cid, *side_effects])
        if any(s in text for s in ("external_send", "send_email", "webhook.send", "send_dm", "send_message")):
            return "external_send"
        if any(s in text for s in ("social_post", "agora.post", "post_message", "tweet")):
            return "social_post"
        if any(s in text for s in ("delete", "remove", "rm_file")):
            return "delete"
        if any(s in text for s in ("git_push", ".push", "push_code")):
            return "push"
        if any(s in text for s in ("payment", "billing", "charge", "purchase")):
            return "payment"
        if any(s in text for s in ("physical", "lighting_control", "room-server.light", "device_control")):
            return "physical_device"
        if any(s in text for s in ("install", "update_package", "system_change")):
            return "system_change"
        if any(s in text for s in ("draft", "read", "get_", "list", "search")):
            return "read_or_draft"
        return "general"

    def _install_defaults(self) -> None:
        now = now_ms()
        defaults = [
            ("del_external_send", "*", "approval_required", "external_send", "External communication must be approved."),
            ("del_social_post", "*", "allow", "social_communication", "Social posting is allowed without approval."),
            ("del_delete", "*", "approval_required", "delete", "Deletion must be approved."),
            ("del_push", "*", "approval_required", "push", "Git push must be approved."),
            ("del_payment", "*", "approval_required", "payment", "Payment or billing APIs must be approved."),
            ("del_physical", "*", "approval_required", "physical_device", "Physical device control must be approved."),
        ]
        self._rules = [
            DelegationRule(rule_id=rid, capability_pattern=pattern, decision=decision, operation_category=cat, description=desc, created_at=now, updated_at=now)
            for rid, pattern, decision, cat, desc in defaults
        ]
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
            self._audit_manager.log_decision(action=action, actor="delegation_policy", decision="success", reason=action, detail=detail)
        except Exception:
            pass
