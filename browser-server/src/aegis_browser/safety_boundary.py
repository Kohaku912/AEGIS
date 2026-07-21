"""Safety Boundary — enforces safety rules for browser-use agent.

Detects forbidden actions and stop conditions during browser task execution.
If a forbidden action is detected, the task is stopped immediately.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from aegis_browser.task_models import BrowserTask

logger = logging.getLogger("aegis_browser.safety_boundary")


@dataclass
class SafetyCheckResult:
    """Result of a safety check."""
    allowed: bool = True
    reason: str = ""
    risk_level: str = "READ"
    needs_approval: bool = False
    needs_user_input: bool = False
    should_stop: bool = False


class BrowserSafetyBoundary:
    """Enforces safety rules for browser-use agent.

    Usage:
        boundary = BrowserSafetyBoundary(task)
        result = boundary.check_action("click", {"element": "submit_button"})
    """

    STOP_BOUNDARIES = {
        "captcha": "CAPTCHA detected",
        "bot_detection": "Bot detection detected",
        "payment": "Payment or purchase boundary detected",
        "contract": "Contract acceptance boundary detected",
        "identity_verification": "Identity verification boundary detected",
    }
    USER_INPUT_BOUNDARIES = {
        "credentials": "Credential input required",
        "two_factor": "Two-factor authentication required",
        "one_time_password": "One-time password required",
    }
    APPROVAL_BOUNDARIES = {
        "publish": "Publish action requires approval",
        "submit": "Submission requires approval",
        "upload": "Upload requires approval",
        "account_creation": "Account creation requires approval",
    }

    def __init__(self, task: BrowserTask) -> None:
        self._task = task
        self._actions_taken: list[str] = []

    def check_page_observation(self, observation: dict[str, Any]) -> SafetyCheckResult:
        """Apply runtime boundaries to a structured browser observation."""
        boundary = str(observation.get("boundary") or "none")
        if boundary in self.STOP_BOUNDARIES:
            reason = self.STOP_BOUNDARIES[boundary]
            logger.warning("Safety stop: %s", reason)
            return SafetyCheckResult(
                allowed=False,
                reason=reason,
                risk_level="BLOCKED",
                should_stop=True,
            )
        if boundary in self.APPROVAL_BOUNDARIES:
            return SafetyCheckResult(
                allowed=False,
                reason=self.APPROVAL_BOUNDARIES[boundary],
                risk_level="APPROVAL",
                needs_approval=True,
            )
        if boundary in self.USER_INPUT_BOUNDARIES:
            return SafetyCheckResult(
                allowed=False,
                reason=self.USER_INPUT_BOUNDARIES[boundary],
                risk_level="USER_INPUT",
                needs_user_input=True,
            )
        return SafetyCheckResult(allowed=True)

    def check_page_content(self, content: str) -> SafetyCheckResult:
        """Reject policy inference from unstructured page prose."""
        del content
        return SafetyCheckResult(
            allowed=False,
            reason="Structured browser observation is required for safety evaluation",
            risk_level="UNVERIFIED",
            needs_user_input=True,
        )

    def check_action(self, action: str, params: dict[str, Any] | None = None) -> SafetyCheckResult:
        """Check if an action is allowed."""
        params = params or {}

        # Check against forbidden actions
        for forbidden in self._task.forbidden_actions:
            if forbidden == action:
                return SafetyCheckResult(
                    allowed=False,
                    reason=f"Forbidden action: {forbidden}",
                    risk_level="BLOCKED",
                )

        # Check against allowed actions
        if self._task.allowed_actions:
            allowed = action in self._task.allowed_actions
            if not allowed:
                return SafetyCheckResult(
                    allowed=False,
                    reason=f"Action not in allowed list: {action}",
                    risk_level="BLOCKED",
                )

        return SafetyCheckResult(allowed=True)

    def check_domain(self, url: str) -> SafetyCheckResult:
        """Check if a domain is allowed."""
        if not self._task.target_domains:
            return SafetyCheckResult(allowed=True)

        hostname = (urlparse(url).hostname or "").lower()
        for domain in self._task.target_domains:
            expected = domain.lower().lstrip(".")
            if hostname == expected or hostname.endswith(f".{expected}"):
                return SafetyCheckResult(allowed=True)

        return SafetyCheckResult(
            allowed=False,
            reason=f"Domain not in target list: {url}",
            risk_level="BLOCKED",
        )

    def record_action(self, action: str) -> None:
        """Record an action taken."""
        self._actions_taken.append(action)

    def get_actions_taken(self) -> list[str]:
        """Get all actions taken."""
        return list(self._actions_taken)
