"""BrowserTask — structured task definition for browser-use agent.

A BrowserTask is sent from AEGIS Core to Browser Server.
It contains the natural language goal and safety constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class TaskStatus(Enum):
    """Browser task execution status."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    STOPPED = auto()         # Stopped by safety boundary
    NEEDS_APPROVAL = auto()  # Hit approval boundary
    NEEDS_USER_INPUT = auto()  # Needs user input (password, 2FA)


@dataclass
class BrowserTask:
    """Structured task definition for browser-use agent.

    Sent from AEGIS Core to Browser Server.
    Contains natural language goal and safety constraints.
    """
    task_id: str = ""
    natural_language_goal: str = ""
    max_steps: int = 50

    # Safety constraints
    allowed_actions: list[str] = field(default_factory=lambda: [
        "read_page",
        "search_web",
        "open_link",
        "summarize",
        "extract_messages",
        "draft_text",
        "fill_non_sensitive_form",
        "create_free_account_if_no_payment_or_captcha",
        "save_draft",
    ])

    forbidden_actions: list[str] = field(default_factory=lambda: [
        "bypass_bot_detection",
        "use_proxy_for_evasion",
        "enter_password_without_user",
        "enter_2fa_without_user",
        "upload_identity_document",
        "purchase",
        "paid_subscription",
        "publish",
        "send_message",
        "send_email",
        "spam",
        "bulk_signup",
    ])

    # Target
    target_domains: list[str] = field(default_factory=list)

    # Context
    user_context: str = ""
    privacy_constraints: list[str] = field(default_factory=list)

    # Boundaries
    approval_boundaries: list[str] = field(default_factory=list)
    stop_conditions: list[str] = field(default_factory=list)

    # Output
    expected_output_schema: str = ""  # JSON schema for expected output


@dataclass
class BrowserTaskResult:
    """Result of a browser task execution."""
    task_id: str = ""
    status: TaskStatus = TaskStatus.PENDING
    result_text: str = ""
    extracted_data: dict[str, Any] = field(default_factory=dict)
    actions_taken: list[str] = field(default_factory=list)
    stopped_reason: str = ""
    needs_approval_for: list[str] = field(default_factory=list)
    needs_user_input_for: list[str] = field(default_factory=list)
    error: str = ""
    duration_ms: float = 0.0
    trace_id: str = ""


# ── Predefined task templates ──────────────────────────────

READONLY_TASK = BrowserTask(
    allowed_actions=[
        "read_page",
        "search_web",
        "open_link",
        "summarize",
        "extract_messages",
    ],
    forbidden_actions=[
        "solve_captcha",
        "bypass_bot_detection",
        "use_proxy_for_evasion",
        "enter_password_without_user",
        "enter_2fa_without_user",
        "upload_identity_document",
        "purchase",
        "paid_subscription",
        "publish",
        "send_message",
        "send_email",
        "spam",
        "bulk_signup",
        "fill_form",
        "click_button",
    ],
)

DRAFT_TASK = BrowserTask(
    allowed_actions=[
        "read_page",
        "search_web",
        "open_link",
        "summarize",
        "extract_messages",
        "draft_text",
        "save_draft",
    ],
    forbidden_actions=[
        "solve_captcha",
        "bypass_bot_detection",
        "use_proxy_for_evasion",
        "enter_password_without_user",
        "enter_2fa_without_user",
        "upload_identity_document",
        "purchase",
        "paid_subscription",
        "publish",
        "send_message",
        "send_email",
        "spam",
        "bulk_signup",
    ],
)

SIGNUP_TASK = BrowserTask(
    allowed_actions=[
        "read_page",
        "search_web",
        "open_link",
        "fill_non_sensitive_form",
        "create_free_account_if_no_payment_or_captcha",
        "fill_form",
        "click_button",
    ],
    forbidden_actions=[
        "bypass_bot_detection",
        "use_proxy_for_evasion",
        "enter_password_without_user",
        "enter_2fa_without_user",
        "upload_identity_document",
        "purchase",
        "paid_subscription",
        "publish",
        "send_message",
        "send_email",
        "spam",
        "bulk_signup",
        "solve_captcha",
    ],
    stop_conditions=[
        "captcha_detected",
        "payment_required",
        "identity_verification_required",
    ],
)
