"""Verification types — data structures for post-execution verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class VerificationStatus(Enum):
    """Outcome of verification."""
    VERIFIED = "verified"
    FAILED = "failed"
    UNVERIFIED = "unverified"
    REQUIRES_OBSERVATION = "requires_observation"
    SKIPPED = "skipped"
    ERROR = "error"


class VerificationStrategy(Enum):
    """How to verify an operation."""
    NONE = "none"
    FILE_EXISTS = "file_exists"
    FILE_CONTENT_CONTAINS = "file_content_contains"
    FILE_NOT_EXISTS = "file_not_exists"
    DIRECTORY_EXISTS = "directory_exists"
    HTTP_STATUS = "http_status"
    API_RESPONSE_SCHEMA = "api_response_schema"
    BROWSER_URL = "browser_url"
    BROWSER_DOM = "browser_dom"
    BROWSER_SCREENSHOT = "browser_screenshot"
    PC_SCREEN_OBSERVATION = "pc_screen_observation"
    ANDROID_SCREEN_OBSERVATION = "android_screen_observation"
    PROCESS_RUNNING = "process_running"
    COMMAND_EXIT_CODE = "command_exit_code"
    STATE_DIFF = "state_diff"
    CUSTOM = "custom"


class CompletionObservable(Enum):
    """Observable state used by manifest completion checks."""
    SCREENSHOT = "screenshot"
    UI_TREE = "ui_tree"
    DOM = "dom"
    HTTP_STATUS = "http_status"
    FILE_EXISTS = "file_exists"
    EVENT = "event"
    OUTPUT_FIELD = "output_field"
    STATE_DIFF = "state_diff"


@dataclass
class CompletionCondition:
    """Declarative success condition attached to a capability manifest."""
    name: str = ""
    observable: CompletionObservable = CompletionObservable.OUTPUT_FIELD
    expected: Any = None
    capability_id: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    capture_before: bool = False
    expect_changed: bool = False
    min_value: int | None = None
    max_value: int | None = None
    repair_hint: str = ""

    @classmethod
    def from_manifest(cls, data: dict[str, Any]) -> "CompletionCondition":
        observable_raw = str(data.get("observable") or data.get("type") or "output_field")
        try:
            observable = CompletionObservable(observable_raw)
        except ValueError:
            observable = CompletionObservable.OUTPUT_FIELD
        return cls(
            name=str(data.get("name") or ""),
            observable=observable,
            expected=data.get("expected", data.get("equals")),
            capability_id=str(data.get("capability_id") or ""),
            params=dict(data.get("params") or {}),
            capture_before=bool(data.get("capture_before", False)),
            expect_changed=bool(data.get("expect_changed", False)),
            min_value=data.get("min"),
            max_value=data.get("max"),
            repair_hint=str(data.get("repair_hint") or data.get("on_failure") or ""),
        )


@dataclass
class VerificationRequest:
    """Request to verify a tool execution outcome."""
    verification_id: str = ""
    request_id: str = ""
    task_id: str = ""
    source: str = ""
    capability_id: str = ""
    tool_name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    expected_outcome: str = ""
    execution_output: dict[str, Any] = field(default_factory=dict)
    pre_observation: dict[str, Any] = field(default_factory=dict)
    post_observation: dict[str, Any] = field(default_factory=dict)
    verification_strategy: VerificationStrategy = VerificationStrategy.NONE
    completion_conditions: list[CompletionCondition] = field(default_factory=list)
    completion: dict[str, Any] = field(default_factory=dict)
    created_at: int = 0


@dataclass
class VerificationResult:
    """Result of verifying a tool execution."""
    verification_id: str = ""
    request_id: str = ""
    status: VerificationStatus = VerificationStatus.UNVERIFIED
    confidence: float = 0.0
    reason: str = ""
    evidence: list[str] = field(default_factory=list)
    failure_type: str = ""
    suggested_recovery: str = ""
    created_at: int = 0

    @property
    def is_verified(self) -> bool:
        return self.status == VerificationStatus.VERIFIED

    @property
    def is_failed(self) -> bool:
        return self.status == VerificationStatus.FAILED

    @property
    def needs_attention(self) -> bool:
        return self.status in (
            VerificationStatus.FAILED,
            VerificationStatus.UNVERIFIED,
            VerificationStatus.REQUIRES_OBSERVATION,
            VerificationStatus.ERROR,
        )
