"""Service Permission Store — persistent fine-grained access control for external services."""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aegis_ai.permissions.service_scope_types import (
    Operation,
    OperationCategory,
    ServicePermissionScope,
    get_operation_category,
)

logger = logging.getLogger("aegis_ai.permissions.store")


@dataclass
class PermissionDecision:
    decision: str
    reason: str
    scope_id: str = ""
    category: str = ""
    risk_level: str = ""
    requires_approval: bool = False


# ── Default policies per service/operation ────────────────────

_DEFAULT_POLICIES: list[dict[str, Any]] = [
    # Gmail
    {"service": "gmail", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "gmail", "operation": "search", "allowed": True, "risk_level": "low"},
    {"service": "gmail", "operation": "summarize", "allowed": True, "risk_level": "low"},
    {"service": "gmail", "operation": "draft", "allowed": True, "risk_level": "low"},
    {"service": "gmail", "operation": "edit_draft", "allowed": True, "risk_level": "low"},
    {"service": "gmail", "operation": "send", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "gmail", "operation": "delete", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "gmail", "operation": "credential_access", "allowed": False, "risk_level": "critical"},
    # Calendar
    {"service": "calendar", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "calendar", "operation": "search", "allowed": True, "risk_level": "low"},
    {"service": "calendar", "operation": "create", "allowed": False, "requires_approval": True, "risk_level": "medium"},
    {"service": "calendar", "operation": "update", "allowed": False, "requires_approval": True, "risk_level": "medium"},
    {"service": "calendar", "operation": "delete", "allowed": False, "requires_approval": True, "risk_level": "high"},
    # GitHub
    {"service": "github", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "github", "operation": "search", "allowed": True, "risk_level": "low"},
    {"service": "github", "operation": "create", "allowed": True, "risk_level": "low"},
    {"service": "github", "operation": "draft", "allowed": True, "risk_level": "low"},
    {"service": "github", "operation": "publish", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "github", "operation": "send", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "github", "operation": "delete", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "github", "operation": "change_permission", "allowed": False,
     "requires_approval": True, "risk_level": "critical"},
    # SNS
    {"service": "sns", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "sns", "operation": "draft", "allowed": True, "risk_level": "low"},
    {"service": "sns", "operation": "send", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "sns", "operation": "publish", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "sns", "operation": "delete", "allowed": False, "requires_approval": True, "risk_level": "high"},
    # Discord
    {"service": "discord", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "discord", "operation": "draft", "allowed": True, "risk_level": "low"},
    {"service": "discord", "operation": "send", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "discord", "operation": "publish", "allowed": False, "requires_approval": True, "risk_level": "high"},
    # Slack
    {"service": "slack", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "slack", "operation": "draft", "allowed": True, "risk_level": "low"},
    {"service": "slack", "operation": "send", "allowed": False, "requires_approval": True, "risk_level": "high"},
    # X/Twitter
    {"service": "x_twitter", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "x_twitter", "operation": "draft", "allowed": True, "risk_level": "low"},
    {"service": "x_twitter", "operation": "publish", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "x_twitter", "operation": "send", "allowed": False, "requires_approval": True, "risk_level": "high"},
    # Notion
    {"service": "notion", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "notion", "operation": "search", "allowed": True, "risk_level": "low"},
    {"service": "notion", "operation": "create", "allowed": True, "risk_level": "low"},
    {"service": "notion", "operation": "update", "allowed": False, "requires_approval": True, "risk_level": "medium"},
    {"service": "notion", "operation": "delete", "allowed": False, "requires_approval": True, "risk_level": "high"},
    # Cloud Storage
    {"service": "cloud_storage", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "cloud_storage", "operation": "search", "allowed": True, "risk_level": "low"},
    {"service": "cloud_storage", "operation": "download", "allowed": True, "risk_level": "low"},
    {"service": "cloud_storage", "operation": "upload", "allowed": False,
     "requires_approval": True, "risk_level": "medium"},
    {"service": "cloud_storage", "operation": "share", "allowed": False,
     "requires_approval": True, "risk_level": "high"},
    {"service": "cloud_storage", "operation": "delete", "allowed": False,
     "requires_approval": True, "risk_level": "high"},
    {"service": "cloud_storage", "operation": "change_permission",
     "allowed": False, "requires_approval": True, "risk_level": "critical"},
    # Browser
    {"service": "browser", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "browser", "operation": "search", "allowed": True, "risk_level": "low"},
    {"service": "browser", "operation": "draft", "allowed": True, "risk_level": "low"},
    {"service": "browser", "operation": "send", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "browser", "operation": "publish", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "browser", "operation": "purchase", "allowed": False,
     "requires_approval": True, "risk_level": "critical"},
    {"service": "browser", "operation": "login", "allowed": False, "requires_approval": True, "risk_level": "high"},
    # File System
    {"service": "file_system", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "file_system", "operation": "create", "allowed": True, "risk_level": "low"},
    {"service": "file_system", "operation": "update", "allowed": False,
     "requires_approval": True, "risk_level": "medium"},
    {"service": "file_system", "operation": "delete", "allowed": False,
     "requires_approval": True, "risk_level": "high"},
    # PC
    {"service": "pc", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "pc", "operation": "send", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "pc", "operation": "delete", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "pc", "operation": "credential_access", "allowed": False, "risk_level": "critical"},
    # Android
    {"service": "android", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "android", "operation": "send", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "android", "operation": "delete", "allowed": False, "requires_approval": True, "risk_level": "high"},
    # AGORA
    {"service": "agora", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "agora", "operation": "search", "allowed": True, "risk_level": "low"},
    {"service": "agora", "operation": "summarize", "allowed": True, "risk_level": "low"},
    {"service": "agora", "operation": "draft", "allowed": True, "risk_level": "low"},
    {"service": "agora", "operation": "update", "allowed": True, "risk_level": "low"},
    {"service": "agora", "operation": "send", "allowed": False,
     "requires_approval": True, "risk_level": "high"},
    {"service": "agora", "operation": "delete", "allowed": False, "risk_level": "critical"},
    # External API
    {"service": "external_api", "operation": "read", "allowed": True, "risk_level": "low"},
    {"service": "external_api", "operation": "send", "allowed": False, "requires_approval": True, "risk_level": "high"},
    {"service": "external_api", "operation": "purchase", "allowed": False,
     "requires_approval": True, "risk_level": "critical"},
    # Financial/Universal
    {"service": "*", "operation": "purchase", "allowed": False,
     "requires_approval": True, "risk_level": "critical"},
    {"service": "*", "operation": "payment", "allowed": False,
     "requires_approval": True, "risk_level": "critical"},
    {"service": "*", "operation": "credential_access", "allowed": False, "risk_level": "critical"},
    {"service": "*", "operation": "admin", "allowed": False, "risk_level": "critical"},
]


class ServicePermissionStore:
    """Persistent store for service permission scopes."""

    def __init__(self, path: str = "data/service_permissions.json") -> None:
        self._path = Path(path)
        self._scopes: dict[str, ServicePermissionScope] = {}
        self._load()

    # ── Query API ──────────────────────────────────────────

    def get_scope(self, service: str, operation: str, resource: str = "*") -> ServicePermissionScope | None:
        key = f"{service}:{operation}:{resource}"
        scope = self._scopes.get(key)
        if scope and not scope.is_expired():
            return scope
        wildcard = f"{service}:{operation}:*"
        scope = self._scopes.get(wildcard)
        if scope and not scope.is_expired():
            return scope
        return None

    def list_scopes(self, service: str | None = None) -> list[ServicePermissionScope]:
        if service is None:
            return list(self._scopes.values())
        return [s for s in self._scopes.values() if s.service == service]

    def is_allowed(
        self,
        service: str,
        operation: str,
        resource: str = "*",
        source: str = "user_explicit",
    ) -> bool:
        decision = self._evaluate(service, operation, resource, source)
        return decision.decision == "allow"

    def requires_approval(
        self,
        service: str,
        operation: str,
        resource: str = "*",
        source: str = "user_explicit",
    ) -> bool:
        decision = self._evaluate(service, operation, resource, source)
        return decision.requires_approval

    def explain_decision(
        self,
        service: str,
        operation: str,
        resource: str = "*",
        source: str = "user_explicit",
    ) -> PermissionDecision:
        return self._evaluate(service, operation, resource, source)

    # ── Mutation API ───────────────────────────────────────

    def set_scope(self, scope: ServicePermissionScope) -> None:
        if not scope.scope_id:
            scope.scope_id = f"sp_{uuid.uuid4().hex[:10]}"
        if not scope.created_at:
            scope.created_at = int(time.time() * 1000)
        scope.updated_at = int(time.time() * 1000)
        key = f"{scope.service}:{scope.operation}:{scope.resource_pattern}"
        self._scopes[key] = scope
        self._save()

    def disable_scope(self, scope_id: str) -> bool:
        for scope in self._scopes.values():
            if scope.scope_id == scope_id:
                scope.allowed = False
                scope.requires_approval = True
                scope.updated_at = int(time.time() * 1000)
                self._save()
                return True
        return False

    def load_defaults(self) -> int:
        count = 0
        for policy in _DEFAULT_POLICIES:
            scope = ServicePermissionScope(
                scope_id=f"default_{policy['service']}_{policy['operation']}",
                service=policy["service"],
                operation=policy["operation"],
                allowed=policy.get("allowed", True),
                requires_approval=policy.get("requires_approval", False),
                risk_level=policy.get("risk_level", "low"),
                reason="Default policy",
            )
            key = f"{scope.service}:{scope.operation}:{scope.resource_pattern}"
            self._scopes[key] = scope
            count += 1
        self._save()
        return count

    # ── Internal ───────────────────────────────────────────

    def _evaluate(
        self,
        service: str,
        operation: str,
        resource: str,
        source: str,
    ) -> PermissionDecision:
        scope = self.get_scope(service, operation, resource)
        if scope is None:
            cat = _guess_category(operation)
            default_decision = _category_default(cat)
            return PermissionDecision(
                decision=default_decision,
                reason=f"No explicit scope for {service}:{operation}. Category default: {cat.value}.",
                category=cat.value,
                risk_level=cat.value,
                requires_approval=default_decision == "ask_approval",
            )

        if scope.requires_approval:
            return PermissionDecision(
                decision="ask_approval",
                reason=f"Scope {scope.scope_id} requires approval for {service}:{operation}.",
                scope_id=scope.scope_id,
                risk_level=scope.risk_level,
                requires_approval=True,
            )

        if not scope.allowed:
            return PermissionDecision(
                decision="deny",
                reason=f"Scope {scope.scope_id} explicitly denies {service}:{operation}.",
                scope_id=scope.scope_id,
                category=_guess_category(operation).value,
                risk_level=scope.risk_level,
            )

        if source not in scope.allowed_sources:
            return PermissionDecision(
                decision="ask_approval",
                reason=f"Source '{source}' not in allowed_sources for {service}:{operation}.",
                scope_id=scope.scope_id,
                risk_level=scope.risk_level,
                requires_approval=True,
            )

        return PermissionDecision(
            decision="allow",
            reason=f"Scope {scope.scope_id} allows {service}:{operation} from {source}.",
            scope_id=scope.scope_id,
            risk_level=scope.risk_level,
        )

    # ── Persistence ────────────────────────────────────────

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = [s.to_dict() for s in self._scopes.values()]
        self._path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _load(self) -> None:
        if not self._path.exists():
            self.load_defaults()
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            migrated = False
            for item in data:
                scope = ServicePermissionScope(
                    scope_id=item.get("scope_id", ""),
                    service=item.get("service", ""),
                    operation=item.get("operation", ""),
                    resource_pattern=item.get("resource_pattern", "*"),
                    allowed=item.get("allowed", True),
                    requires_approval=item.get("requires_approval", False),
                    risk_level=item.get("risk_level", "low"),
                    allowed_sources=item.get("allowed_sources", ["user_explicit"]),
                    requires_fresh_world_state=item.get("requires_fresh_world_state", False),
                    requires_verification=item.get("requires_verification", True),
                    requires_user_present=item.get("requires_user_present", False),
                    cooldown_seconds=item.get("cooldown_seconds", 0),
                    expires_at=item.get("expires_at", 0),
                    created_at=item.get("created_at", 0),
                    updated_at=item.get("updated_at", 0),
                    reason=item.get("reason", ""),
                )
                if (
                    scope.scope_id.startswith("default_")
                    and scope.operation in {"purchase", "payment"}
                    and not scope.requires_approval
                ):
                    scope.requires_approval = True
                    migrated = True
                key = f"{scope.service}:{scope.operation}:{scope.resource_pattern}"
                self._scopes[key] = scope
            if migrated:
                self._save()
        except Exception as exc:
            logger.warning("Failed to load service permissions: %s — loading defaults", exc)
            self.load_defaults()


def _guess_category(operation: str) -> OperationCategory:
    try:
        return get_operation_category(Operation(operation))
    except ValueError:
        return OperationCategory.MEDIUM_RISK_WRITE


def _category_default(cat: OperationCategory) -> str:
    return {
        OperationCategory.SAFE_READ: "allow",
        OperationCategory.LOW_RISK_WRITE: "allow",
        OperationCategory.MEDIUM_RISK_WRITE: "ask_approval",
        OperationCategory.HIGH_RISK_EXTERNAL_EFFECT: "ask_approval",
        OperationCategory.DESTRUCTIVE: "ask_approval",
        OperationCategory.FINANCIAL_OR_LEGAL: "ask_approval",
    }.get(cat, "ask_approval")
