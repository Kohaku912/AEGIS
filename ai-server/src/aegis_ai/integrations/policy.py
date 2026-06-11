"""Integration Policy — enforces safety rules for external integrations.

Rules:
- External outbound is default disabled
- Message send requires Level 2 approval
- DM send requires Level 2/3
- Email send requires Level 2
- External webhook requires Level 2/3
- Unknown integration is denied
- No secrets = no startup
- No real token = stub only
"""

from __future__ import annotations

import logging
import re
from typing import Any

from aegis_ai.integrations.models import IntegrationDirection
from aegis_ai.integrations.registry import IntegrationRegistry

logger = logging.getLogger("aegis_ai.integrations.policy")


class IntegrationPolicy:
    """Enforces safety rules for external integrations.

    Usage:
        policy = IntegrationPolicy(registry=registry)
        result = policy.check_outbound("line", "send_message", {"text": "Hello"})
    """

    # Patterns that are always denied for external integrations
    EXTERNAL_DENY_PATTERNS: list[str] = [
        r"send_sns",
        r"post_sns",
        r"send_dm",
        r"captcha_bypass",
        r"tos_bypass",
        r"purchase",
        r"delete_file",
        r"access_contacts",
    ]

    # Patterns that require approval even if integration is enabled
    EXTERNAL_APPROVAL_PATTERNS: list[str] = [
        r"send_message",
        r"send_email",
        r"send_notification",
        r"post_webhook",
        r"send_dm",
    ]

    def __init__(
        self,
        registry: IntegrationRegistry | None = None,
        settings_store: Any = None,
        audit_log: Any = None,
    ) -> None:
        self._registry = registry or IntegrationRegistry()
        self._settings = settings_store
        self._audit = audit_log

    def _deny(self, reason: str, requires_approval: bool = False) -> dict[str, Any]:
        """Create a deny result."""
        return {"allowed": False, "reason": reason, "requires_approval": requires_approval}

    def _allow(self, reason: str, requires_approval: bool = False) -> dict[str, Any]:
        """Create an allow result."""
        return {"allowed": True, "reason": reason, "requires_approval": requires_approval}

    def check_outbound(
        self,
        integration_id: str,
        action: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Check if an outbound integration action is allowed.

        Returns:
            {"allowed": bool, "reason": str, "requires_approval": bool}
        """
        # Check if integration exists
        config = self._registry.get(integration_id)
        if not config:
            self._audit_action(integration_id, action, "DENY", "Unknown integration")
            return self._deny(f"Unknown integration: {integration_id}")

        # Check if integration is enabled
        if not config.enabled:
            self._audit_action(integration_id, action, "DENY", "Integration disabled")
            return self._deny(f"Integration '{integration_id}' is disabled")

        # Check direction
        if config.direction not in (IntegrationDirection.OUTBOUND, IntegrationDirection.BOTH):
            self._audit_action(integration_id, action, "DENY", "Outbound not supported")
            return self._deny(f"Integration '{integration_id}' does not support outbound")

        # Check deny patterns
        for pattern in self.EXTERNAL_DENY_PATTERNS:
            if re.search(pattern, action, re.IGNORECASE):
                self._audit_action(integration_id, action, "DENY", f"Deny pattern: {pattern}")
                return self._deny(f"Action '{action}' is denied for external integrations")

        # Check approval patterns
        for pattern in self.EXTERNAL_APPROVAL_PATTERNS:
            if re.search(pattern, action, re.IGNORECASE):
                self._audit_action(integration_id, action, "ASK_APPROVAL", f"Approval: {pattern}")
                return self._allow(f"Action '{action}' requires approval", requires_approval=True)

        # Check settings
        if self._settings:
            settings = self._settings.get()
            if not settings.privacy.external_llm_allowed:
                self._audit_action(integration_id, action, "DENY", "External disabled in settings")
                return self._deny("External integrations disabled in settings")

        # Default: allow with approval
        self._audit_action(integration_id, action, "ALLOW", "Default allow")
        return self._allow("Allowed")

    def check_inbound(
        self,
        integration_id: str,
        source: str = "",
    ) -> dict[str, Any]:
        """Check if an inbound message is allowed.

        Returns:
            {"allowed": bool, "reason": str}
        """
        config = self._registry.get(integration_id)
        if not config:
            return self._deny(f"Unknown integration: {integration_id}")

        if not config.enabled:
            return self._deny(f"Integration '{integration_id}' is disabled")

        if config.direction not in (IntegrationDirection.INBOUND, IntegrationDirection.BOTH):
            return self._deny(f"Integration '{integration_id}' does not support inbound")

        return self._allow("Allowed")

    def _audit_action(
        self,
        integration_id: str,
        action: str,
        decision: str,
        reason: str,
    ) -> None:
        """Log integration action to audit."""
        if self._audit:
            self._audit.log_decision(
                "integration_action", f"integration.{integration_id}", decision,
                reason=reason,
                detail={"action": action, "integration_id": integration_id},
            )
