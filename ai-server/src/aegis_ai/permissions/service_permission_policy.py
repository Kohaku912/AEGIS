"""Service Permission Policy — integrates service scopes with PolicyEngine and browser inference."""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.permissions.service_permission_store import ServicePermissionStore
from aegis_ai.permissions.service_scope_types import (
    OAuthScopeMapping,
    Operation,
    get_operation_category,
    infer_operation_from_element,
    infer_service_from_url,
)

logger = logging.getLogger("aegis_ai.permissions.policy")


# ── OAuth Scope Mappings ──────────────────────────────────────

_DEFAULT_OAUTH_MAPPINGS: list[OAuthScopeMapping] = [
    OAuthScopeMapping(
        service="gmail",
        oauth_scope="https://www.googleapis.com/auth/gmail.readonly",
        internal_scopes=["gmail:read", "gmail:search", "gmail:summarize"],
        risk_level="low",
        description="Read Gmail messages",
    ),
    OAuthScopeMapping(
        service="gmail",
        oauth_scope="https://www.googleapis.com/auth/gmail.compose",
        internal_scopes=["gmail:draft", "gmail:edit_draft"],
        risk_level="medium",
        description="Compose Gmail drafts",
        requires_user_explanation=True,
    ),
    OAuthScopeMapping(
        service="gmail",
        oauth_scope="https://www.googleapis.com/auth/gmail.send",
        internal_scopes=["gmail:send"],
        risk_level="high",
        description="Send Gmail messages",
        requires_user_explanation=True,
    ),
    OAuthScopeMapping(
        service="calendar",
        oauth_scope="https://www.googleapis.com/auth/calendar.readonly",
        internal_scopes=["calendar:read", "calendar:search"],
        risk_level="low",
        description="Read calendar events",
    ),
    OAuthScopeMapping(
        service="calendar",
        oauth_scope="https://www.googleapis.com/auth/calendar.events",
        internal_scopes=["calendar:create", "calendar:update", "calendar:delete"],
        risk_level="medium",
        description="Manage calendar events",
        requires_user_explanation=True,
    ),
    OAuthScopeMapping(
        service="github",
        oauth_scope="repo",
        internal_scopes=["github:read", "github:create", "github:update"],
        risk_level="medium",
        description="Full repository access",
        requires_user_explanation=True,
    ),
    OAuthScopeMapping(
        service="github",
        oauth_scope="public_repo",
        internal_scopes=["github:read"],
        risk_level="low",
        description="Public repository read access",
    ),
    OAuthScopeMapping(
        service="github",
        oauth_scope="write:repo_hook",
        internal_scopes=["github:create"],
        risk_level="medium",
        description="Create repository webhooks",
        requires_user_explanation=True,
    ),
]


class ServicePermissionPolicy:
    """Integrates ServicePermissionStore with PolicyEngine for fine-grained access control."""

    def __init__(self, store: ServicePermissionStore | None = None) -> None:
        self._store = store or ServicePermissionStore()
        self._oauth_mappings = list(_DEFAULT_OAUTH_MAPPINGS)

    @property
    def store(self) -> ServicePermissionStore:
        return self._store

    def evaluate_service_operation(
        self,
        service: str,
        operation: str,
        resource: str = "*",
        source: str = "user_explicit",
        world_state: Any = None,
    ) -> dict[str, Any]:
        """Evaluate a service operation against permission scopes."""
        decision = self._store.explain_decision(service, operation, resource, source)

        if decision.decision == "allow" and world_state is not None:
            scope = self._store.get_scope(service, operation, resource)
            if scope and scope.requires_fresh_world_state:
                stale_sections = getattr(world_state, "stale_sections", [])
                if service in stale_sections or "all" in stale_sections:
                    return {
                        "decision": "ask_approval",
                        "reason": f"WorldState is stale for '{service}'. Refresh required before high-risk operation.",
                        "requires_approval": True,
                        "risk_level": decision.risk_level,
                        "scope_id": decision.scope_id,
                    }

        return {
            "decision": decision.decision,
            "reason": decision.reason,
            "requires_approval": decision.requires_approval,
            "risk_level": decision.risk_level,
            "scope_id": decision.scope_id,
            "category": decision.category,
        }

    def evaluate_browser_action(
        self,
        url: str,
        element_label: str,
        source: str = "user_explicit",
        world_state: Any = None,
    ) -> dict[str, Any]:
        """Evaluate a browser action by inferring service/operation from URL and element."""
        service = infer_service_from_url(url)
        operation = infer_operation_from_element(element_label)
        return self.evaluate_service_operation(
            service=service,
            operation=operation,
            resource=url,
            source=source,
            world_state=world_state,
        )

    def get_oauth_explanation(self, service: str, oauth_scope: str) -> dict[str, Any] | None:
        """Explain what internal scopes an OAuth scope maps to."""
        for mapping in self._oauth_mappings:
            if mapping.service == service and mapping.oauth_scope == oauth_scope:
                return {
                    "service": mapping.service,
                    "oauth_scope": mapping.oauth_scope,
                    "internal_scopes": mapping.internal_scopes,
                    "risk_level": mapping.risk_level,
                    "description": mapping.description,
                    "requires_user_explanation": mapping.requires_user_explanation,
                }
        return None

    def list_oauth_mappings(self, service: str | None = None) -> list[dict[str, Any]]:
        """List all OAuth scope mappings, optionally filtered by service."""
        result = []
        for m in self._oauth_mappings:
            if service is not None and m.service != service:
                continue
            result.append({
                "service": m.service,
                "oauth_scope": m.oauth_scope,
                "internal_scopes": m.internal_scopes,
                "risk_level": m.risk_level,
                "description": m.description,
                "requires_user_explanation": m.requires_user_explanation,
            })
        return result

    def explain_decision(
        self,
        service: str,
        operation: str,
        resource: str = "*",
        source: str = "user_explicit",
    ) -> dict[str, Any]:
        """Explain why a decision was made."""
        decision = self._store.explain_decision(service, operation, resource, source)
        scope = self._store.get_scope(service, operation, resource)

        result: dict[str, Any] = {
            "service": service,
            "operation": operation,
            "resource": resource,
            "source": source,
            "decision": decision.decision,
            "reason": decision.reason,
            "requires_approval": decision.requires_approval,
            "risk_level": decision.risk_level,
            "category": decision.category,
        }

        if scope:
            result["scope"] = {
                "scope_id": scope.scope_id,
                "allowed": scope.allowed,
                "requires_approval": scope.requires_approval,
                "allowed_sources": scope.allowed_sources,
                "requires_verification": scope.requires_verification,
                "cooldown_seconds": scope.cooldown_seconds,
                "expires_at": scope.expires_at,
                "reason": scope.reason,
            }

        op_enum = None
        try:
            op_enum = Operation(operation)
        except ValueError:
            pass
        if op_enum:
            cat = get_operation_category(op_enum)
            result["operation_category"] = cat.value

        return result


def infer_service_operation_from_browser_action(
    url: str,
    element_label: str,
) -> dict[str, str]:
    """Infer service and operation from browser URL and element label.

    Used by PolicyEngine to apply service scopes to browser-based actions.
    """
    service = infer_service_from_url(url)
    operation = infer_operation_from_element(element_label)
    return {"service": service, "operation": operation}
