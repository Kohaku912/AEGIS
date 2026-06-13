"""Recovery Planner — plans safe recovery steps when operations fail."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FailureType(Enum):
    ELEMENT_NOT_FOUND = "element_not_found"
    PAGE_LOADING = "page_loading"
    LOGIN_REQUIRED = "login_required"
    CAPTCHA_BLOCKED = "captcha_blocked"
    TWO_FA_REQUIRED = "two_fa_required"
    ERROR_DIALOG = "error_dialog"
    WRONG_INPUT = "wrong_input"
    APP_NOT_RUNNING = "app_not_running"
    NETWORK_ERROR = "network_error"
    PERMISSION_DENIED = "permission_denied"
    TIMEOUT = "timeout"
    SEND_FAILED = "send_failed"
    UNKNOWN = "unknown"


class RecoveryAction(Enum):
    RE_OBSERVE = "re_observe"
    SCROLL = "scroll"
    WAIT_AND_RETRY = "wait_and_retry"
    ASK_USER = "ask_user"
    RETRY_CLICK = "retry_click"
    REFOCUS_INPUT = "refocus_input"
    LAUNCH_APP = "launch_app"
    CLOSE_DIALOG = "close_dialog"
    STOP = "stop"


# Operations that must NOT be auto-retried
_NO_AUTO_RETRY = {"send", "post", "publish", "purchase", "delete", "submit", "pay", "email", "dm"}

_RISKY_PATTERNS = {"payment", "purchase", "buy", "checkout", "transfer", "submit_order", "submit_payment", "pay"}


@dataclass
class RecoveryStep:
    action: RecoveryAction = RecoveryAction.RE_OBSERVE
    description: str = ""
    requires_approval: bool = False
    timeout_seconds: int = 10


@dataclass
class RecoveryPlan:
    recovery_id: str = ""
    task_id: str = ""
    request_id: str = ""
    failure_type: FailureType = FailureType.UNKNOWN
    current_state_summary: str = ""
    possible_causes: list[str] = field(default_factory=list)
    safe_recovery_steps: list[RecoveryStep] = field(default_factory=list)
    requires_user_help: bool = False
    requires_approval: bool = False
    should_retry: bool = False
    retry_limit: int = 0
    backoff_seconds: int = 0
    reason: str = ""
    created_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "recovery_id": self.recovery_id,
            "task_id": self.task_id,
            "request_id": self.request_id,
            "failure_type": self.failure_type.value,
            "current_state_summary": self.current_state_summary[:300],
            "possible_causes": self.possible_causes[:5],
            "safe_recovery_steps": [
                {"action": s.action.value, "description": s.description, "requires_approval": s.requires_approval}
                for s in self.safe_recovery_steps
            ],
            "requires_user_help": self.requires_user_help,
            "requires_approval": self.requires_approval,
            "should_retry": self.should_retry,
            "retry_limit": self.retry_limit,
            "backoff_seconds": self.backoff_seconds,
            "reason": self.reason,
            "created_at": self.created_at,
        }


def _is_risky_operation(capability_id: str) -> bool:
    cap_lower = capability_id.lower()
    return any(p in cap_lower for p in _RISKY_PATTERNS)


def _is_no_auto_retry(capability_id: str) -> bool:
    cap_lower = capability_id.lower()
    return any(p in cap_lower for p in _NO_AUTO_RETRY)


class RecoveryPlanner:
    """Plans safe recovery steps after operation failures."""

    def __init__(self, max_retries: int = 3, default_backoff: int = 5) -> None:
        self._max_retries = max_retries
        self._default_backoff = default_backoff

    def plan_recovery(
        self,
        task_id: str,
        request_id: str,
        capability_id: str,
        failure_type: str,
        state_summary: str = "",
        error_message: str = "",
        observation_summary: str = "",
        retry_count: int = 0,
    ) -> RecoveryPlan:
        ft = self._classify_failure(failure_type, error_message)
        is_risky = _is_risky_operation(capability_id)
        no_retry = _is_no_auto_retry(capability_id)

        plan = RecoveryPlan(
            recovery_id=f"rec_{uuid.uuid4().hex[:10]}",
            task_id=task_id,
            request_id=request_id,
            failure_type=ft,
            current_state_summary=state_summary,
            created_at=int(time.time() * 1000),
        )

        if ft == FailureType.ELEMENT_NOT_FOUND:
            plan.possible_causes = ["Element changed position", "Page not fully loaded", "Dynamic content"]
            plan.safe_recovery_steps = [
                RecoveryStep(RecoveryAction.RE_OBSERVE, "Re-observe current state"),
                RecoveryStep(RecoveryAction.SCROLL, "Scroll to find element"),
            ]
            plan.should_retry = not is_risky and retry_count < self._max_retries
            plan.retry_limit = self._max_retries
            plan.backoff_seconds = self._default_backoff

        elif ft == FailureType.PAGE_LOADING:
            plan.possible_causes = ["Slow network", "Server delay"]
            plan.safe_recovery_steps = [
                RecoveryStep(RecoveryAction.WAIT_AND_RETRY, "Wait and re-observe"),
            ]
            plan.should_retry = retry_count < 2
            plan.retry_limit = 2
            plan.backoff_seconds = 10

        elif ft == FailureType.LOGIN_REQUIRED:
            plan.possible_causes = ["Session expired", "Not authenticated"]
            plan.safe_recovery_steps = [
                RecoveryStep(RecoveryAction.ASK_USER, "Ask user to log in"),
            ]
            plan.requires_user_help = True
            plan.requires_approval = True
            plan.should_retry = False

        elif ft == FailureType.CAPTCHA_BLOCKED:
            plan.possible_causes = ["Anti-bot protection"]
            plan.safe_recovery_steps = [
                RecoveryStep(RecoveryAction.ASK_USER, "Ask user to solve CAPTCHA"),
            ]
            plan.requires_user_help = True
            plan.requires_approval = True
            plan.should_retry = False

        elif ft == FailureType.TWO_FA_REQUIRED:
            plan.possible_causes = ["2FA verification needed"]
            plan.safe_recovery_steps = [
                RecoveryStep(RecoveryAction.ASK_USER, "Ask user to complete 2FA"),
            ]
            plan.requires_user_help = True
            plan.requires_approval = True
            plan.should_retry = False

        elif ft == FailureType.ERROR_DIALOG:
            plan.possible_causes = ["Application error", "Invalid operation"]
            plan.safe_recovery_steps = [
                RecoveryStep(RecoveryAction.CLOSE_DIALOG, "Close error dialog"),
                RecoveryStep(RecoveryAction.RE_OBSERVE, "Re-observe state"),
            ]
            plan.should_retry = not is_risky and retry_count < 1
            plan.retry_limit = 1

        elif ft == FailureType.WRONG_INPUT:
            plan.possible_causes = ["Input field lost focus", "Wrong field targeted"]
            plan.safe_recovery_steps = [
                RecoveryStep(RecoveryAction.REFOCUS_INPUT, "Refocus and verify input"),
                RecoveryStep(RecoveryAction.RE_OBSERVE, "Re-observe input state"),
            ]
            plan.should_retry = not is_risky and retry_count < 1
            plan.retry_limit = 1

        elif ft == FailureType.APP_NOT_RUNNING:
            plan.possible_causes = ["App crashed", "Not launched"]
            plan.safe_recovery_steps = [
                RecoveryStep(RecoveryAction.LAUNCH_APP, "Relaunch application"),
                RecoveryStep(RecoveryAction.WAIT_AND_RETRY, "Wait for startup"),
            ]
            plan.should_retry = retry_count < 1
            plan.retry_limit = 1
            plan.backoff_seconds = 5

        elif ft == FailureType.SEND_FAILED:
            plan.possible_causes = ["Network error", "Permission denied", "Rate limited"]
            plan.safe_recovery_steps = [
                RecoveryStep(RecoveryAction.ASK_USER, "Notify user of send failure"),
            ]
            plan.requires_user_help = True
            plan.should_retry = False
            plan.reason = "Send/post operations must not be auto-retried."

        elif ft == FailureType.PERMISSION_DENIED:
            plan.possible_causes = ["Insufficient permissions", "OS restriction"]
            plan.safe_recovery_steps = [
                RecoveryStep(RecoveryAction.ASK_USER, "Ask user for permission"),
            ]
            plan.requires_user_help = True
            plan.requires_approval = True
            plan.should_retry = False

        elif ft == FailureType.TIMEOUT:
            plan.possible_causes = ["Operation took too long", "System unresponsive"]
            plan.safe_recovery_steps = [
                RecoveryStep(RecoveryAction.WAIT_AND_RETRY, "Wait and re-observe"),
            ]
            plan.should_retry = not no_retry and retry_count < 1
            plan.retry_limit = 1
            plan.backoff_seconds = 10

        else:
            plan.possible_causes = ["Unknown failure cause"]
            plan.safe_recovery_steps = [
                RecoveryStep(RecoveryAction.RE_OBSERVE, "Re-observe current state"),
            ]
            plan.requires_user_help = True
            plan.should_retry = False
            plan.reason = "Unknown failure — stopping to avoid damage."

        if is_risky:
            plan.requires_approval = True
            plan.safe_recovery_steps.insert(
                0,
                RecoveryStep(RecoveryAction.ASK_USER, "Risky operation — needs user confirmation"),
            )

        return plan

    def _classify_failure(self, failure_type: str, error_message: str) -> FailureType:
        ft_lower = failure_type.lower()
        err_lower = error_message.lower()
        combined = f"{ft_lower} {err_lower}"

        if "element" in combined and ("not found" in combined or "missing" in combined):
            return FailureType.ELEMENT_NOT_FOUND
        if "loading" in combined or "timeout" in combined and "page" in combined:
            return FailureType.PAGE_LOADING
        if "login" in combined or "auth" in combined or "session" in combined:
            return FailureType.LOGIN_REQUIRED
        if "captcha" in combined:
            return FailureType.CAPTCHA_BLOCKED
        if "2fa" in combined or "two.factor" in combined or "verification code" in combined:
            return FailureType.TWO_FA_REQUIRED
        if "dialog" in combined or "modal" in combined or "alert" in combined:
            return FailureType.ERROR_DIALOG
        if "input" in combined or "field" in combined or "focus" in combined:
            return FailureType.WRONG_INPUT
        if "app" in combined and ("not running" in combined or "crash" in combined):
            return FailureType.APP_NOT_RUNNING
        if "send" in combined or "post" in combined or "publish" in combined:
            return FailureType.SEND_FAILED
        if "permission" in combined or "denied" in combined:
            return FailureType.PERMISSION_DENIED
        if "timeout" in combined:
            return FailureType.TIMEOUT

        try:
            return FailureType(failure_type)
        except (ValueError, KeyError):
            return FailureType.UNKNOWN
