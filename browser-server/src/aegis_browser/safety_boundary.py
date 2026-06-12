"""Safety Boundary — enforces safety rules for browser-use agent.

Detects forbidden actions and stop conditions during browser task execution.
If a forbidden action is detected, the task is stopped immediately.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from aegis_browser.task_models import BrowserTask, TaskStatus

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

    # Patterns that always trigger stop
    STOP_PATTERNS = [
        (r"captcha", "CAPTCHA detected"),
        (r"recaptcha", "reCAPTCHA detected"),
        (r"hcaptcha", "hCAPTCHA detected"),
        (r"bot\s*detection", "Bot detection detected"),
        (r"verify\s*you\s*are\s*human", "Human verification required"),
    ]

    # Patterns that require approval
    APPROVAL_PATTERNS = [
        (r"publish", "Publish action detected"),
        (r"post\s*(to|on|public)", "Public post detected"),
        (r"send\s*(message|email|dm)", "Send action detected"),
        (r"submit\s*(form|post)", "Form submission detected"),
        (r"share\s*(to|with|public)", "Share action detected"),
    ]

    # Patterns that require user input
    USER_INPUT_PATTERNS = [
        (r"password", "Password field detected"),
        (r"2fa|two.factor|authenticator", "2FA field detected"),
        (r"otp|one.time.pass", "OTP field detected"),
        (r"credit.card|card.number", "Payment field detected"),
    ]

    # Patterns that indicate payment requirement
    PAYMENT_PATTERNS = [
        (r"pay\s*now|payment\s*required", "Payment required"),
        (r"subscribe|subscription", "Subscription required"),
        (r"\$\d+|\d+\s*(USD|EUR|JPY)", "Price detected"),
        (r"credit.card|debit.card|paypal", "Payment method required"),
    ]

    # Patterns that indicate identity verification
    IDENTITY_PATTERNS = [
        (r"upload\s*(id|passport|license)", "Identity document upload required"),
        (r"verify\s*identity", "Identity verification required"),
        (r"age\s*verification", "Age verification required"),
        (r"kyc|know.your.customer", "KYC verification required"),
    ]

    def __init__(self, task: BrowserTask) -> None:
        self._task = task
        self._actions_taken: list[str] = []

    def check_page_content(self, content: str) -> SafetyCheckResult:
        """Check page content for safety violations."""
        content_lower = content.lower()

        # Check for CAPTCHA
        for pattern, reason in self.STOP_PATTERNS:
            if re.search(pattern, content_lower):
                logger.warning("Safety stop: %s", reason)
                return SafetyCheckResult(
                    allowed=False,
                    reason=reason,
                    risk_level="BLOCKED",
                    should_stop=True,
                )

        # Check for payment
        for pattern, reason in self.PAYMENT_PATTERNS:
            if re.search(pattern, content_lower):
                if "purchase" in self._task.forbidden_actions or "paid_subscription" in self._task.forbidden_actions:
                    logger.warning("Safety stop: %s", reason)
                    return SafetyCheckResult(
                        allowed=False,
                        reason=reason,
                        risk_level="BLOCKED",
                        should_stop=True,
                    )

        # Check for identity verification
        for pattern, reason in self.IDENTITY_PATTERNS:
            if re.search(pattern, content_lower):
                if "upload_identity_document" in self._task.forbidden_actions:
                    logger.warning("Safety stop: %s", reason)
                    return SafetyCheckResult(
                        allowed=False,
                        reason=reason,
                        risk_level="BLOCKED",
                        should_stop=True,
                    )

        # Check for approval boundaries
        for pattern, reason in self.APPROVAL_PATTERNS:
            if re.search(pattern, content_lower):
                logger.info("Approval needed: %s", reason)
                return SafetyCheckResult(
                    allowed=False,
                    reason=reason,
                    risk_level="APPROVAL",
                    needs_approval=True,
                )

        # Check for user input requirements
        for pattern, reason in self.USER_INPUT_PATTERNS:
            if re.search(pattern, content_lower):
                if "enter_password_without_user" in self._task.forbidden_actions:
                    logger.info("User input needed: %s", reason)
                    return SafetyCheckResult(
                        allowed=False,
                        reason=reason,
                        risk_level="USER_INPUT",
                        needs_user_input=True,
                    )

        return SafetyCheckResult(allowed=True)

    def check_action(self, action: str, params: dict[str, Any] | None = None) -> SafetyCheckResult:
        """Check if an action is allowed."""
        action_lower = action.lower()
        params = params or {}

        # Check against forbidden actions
        for forbidden in self._task.forbidden_actions:
            if forbidden.lower() in action_lower:
                return SafetyCheckResult(
                    allowed=False,
                    reason=f"Forbidden action: {forbidden}",
                    risk_level="BLOCKED",
                )

        # Check against allowed actions
        if self._task.allowed_actions:
            allowed = any(a.lower() in action_lower for a in self._task.allowed_actions)
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

        for domain in self._task.target_domains:
            if domain in url:
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
