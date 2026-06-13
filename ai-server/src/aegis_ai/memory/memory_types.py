"""Memory types — unified memory record system for AEGIS."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MemoryType(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    USER_PREFERENCE = "user_preference"
    SAFETY_LESSON = "safety_lesson"
    FAILURE_LESSON = "failure_lesson"
    APPROVAL_LESSON = "approval_lesson"
    DESIRE_LESSON = "desire_lesson"
    PROJECT_CONTEXT = "project_context"


class MemorySource(Enum):
    USER_EXPLICIT = "user_explicit"
    TOOL_RESULT = "tool_result"
    VERIFICATION_RESULT = "verification_result"
    APPROVAL_DECISION = "approval_decision"
    REFLECTION = "reflection"
    DESIRE_UPDATE = "desire_update"
    SYSTEM_OBSERVATION = "system_observation"


class Visibility(Enum):
    LLM_VISIBLE = "llm_visible"
    INTERNAL_ONLY = "internal_only"
    HIDDEN = "hidden"


class Sensitivity(Enum):
    PUBLIC = "public"
    NORMAL = "normal"
    PERSONAL = "personal"
    SECRET = "secret"


class FailureType(Enum):
    POLICY_DENIED = "policy_denied"
    APPROVAL_REJECTED = "approval_rejected"
    APPROVAL_EXPIRED = "approval_expired"
    TOOL_UNAVAILABLE = "tool_unavailable"
    TIMEOUT = "timeout"
    INVALID_ARGUMENTS = "invalid_arguments"
    CAPABILITY_MISSING = "capability_missing"
    VERIFICATION_FAILED = "verification_failed"
    OBSERVATION_MISSING = "observation_missing"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    AUTHENTICATION_REQUIRED = "authentication_required"
    PERMISSION_DENIED = "permission_denied"
    USER_INTERRUPTION = "user_interruption"
    LLM_PARSE_ERROR = "llm_parse_error"
    PLANNING_ERROR = "planning_error"
    REPEATED_LOOP = "repeated_loop"
    UNKNOWN = "unknown"


_SENSITIVE_KEYS = {"key", "token", "password", "secret", "cookie", "auth", "credential"}


def _mask_sensitive(value: Any, key: str = "") -> Any:
    if key and any(s in key.lower() for s in _SENSITIVE_KEYS):
        return "***MASKED***"
    if isinstance(value, str):
        value = re.sub(r"Bearer\s+\S+", "Bearer ***", value, flags=re.IGNORECASE)
        value = re.sub(r"sk-[a-zA-Z0-9]{20,}", "sk-***", value)
    return value


def _should_include_in_context(record: MemoryRecord, max_chars: int) -> bool:
    if record.visibility == Visibility.HIDDEN:
        return False
    if record.sensitivity == Sensitivity.SECRET:
        return False
    return True


def _score_for_context(record: MemoryRecord) -> float:
    now_ms = int(time.time() * 1000)
    age_hours = (now_ms - record.created_at) / 3_600_000 if record.created_at > 0 else 0
    recency = max(0.0, 1.0 - age_hours / 168.0)
    return record.importance * 0.5 + record.confidence * 0.3 + recency * 0.2


@dataclass
class MemoryRecord:
    memory_id: str = ""
    memory_type: str = ""
    title: str = ""
    content: str = ""
    structured_data: dict[str, Any] = field(default_factory=dict)
    source: str = ""
    related_task_id: str = ""
    related_request_id: str = ""
    related_approval_id: str = ""
    related_verification_id: str = ""
    related_desire: str = ""
    confidence: float = 0.5
    importance: float = 0.5
    recency: float = 1.0
    created_at: int = 0
    updated_at: int = 0
    expires_at: int = 0
    tags: list[str] = field(default_factory=list)
    visibility: str = "llm_visible"
    sensitivity: str = "normal"
    evidence: str = ""
    supersedes: str = ""
    superseded_by: str = ""

    def __post_init__(self) -> None:
        self.content = _mask_sensitive(self.content, self.title)

    def is_expired(self, now_ms: int | None = None) -> bool:
        now = now_ms if now_ms is not None else int(time.time() * 1000)
        return self.expires_at > 0 and now > self.expires_at

    def to_context_string(self, max_len: int = 300) -> str:
        masked = _mask_sensitive(self.content)
        content = masked[:max_len] + "..." if len(str(masked)) > max_len else str(masked)
        return f"[{self.memory_type}] {self.title}: {content}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type,
            "title": self.title,
            "content": _mask_sensitive(self.content),
            "structured_data": self.structured_data,
            "source": self.source,
            "related_task_id": self.related_task_id,
            "related_request_id": self.related_request_id,
            "related_approval_id": self.related_approval_id,
            "related_verification_id": self.related_verification_id,
            "related_desire": self.related_desire,
            "confidence": self.confidence,
            "importance": self.importance,
            "recency": self.recency,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "tags": self.tags,
            "visibility": self.visibility,
            "sensitivity": self.sensitivity,
            "evidence": self.evidence,
            "supersedes": self.supersedes,
            "superseded_by": self.superseded_by,
        }


@dataclass
class ReflectionResult:
    reflection_id: str = ""
    task_id: str = ""
    summary: str = ""
    outcome: str = ""
    root_cause: str = ""
    what_worked: list[str] = field(default_factory=list)
    what_failed: list[str] = field(default_factory=list)
    lessons: list[str] = field(default_factory=list)
    memory_records_to_store: list[MemoryRecord] = field(default_factory=list)
    planner_hints: list[str] = field(default_factory=list)
    policy_hints: list[str] = field(default_factory=list)
    desire_update_hints: dict[str, float] = field(default_factory=dict)
    should_retry: bool = False
    retry_strategy: str = ""
    should_suppress_similar_task: bool = False
    created_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "reflection_id": self.reflection_id,
            "task_id": self.task_id,
            "summary": self.summary,
            "outcome": self.outcome,
            "root_cause": self.root_cause,
            "what_worked": self.what_worked,
            "what_failed": self.what_failed,
            "lessons": self.lessons,
            "planner_hints": self.planner_hints,
            "policy_hints": self.policy_hints,
            "desire_update_hints": self.desire_update_hints,
            "should_retry": self.should_retry,
            "retry_strategy": self.retry_strategy,
            "should_suppress_similar_task": self.should_suppress_similar_task,
            "created_at": self.created_at,
        }
