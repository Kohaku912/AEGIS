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
