"""World State types — unified model of AEGIS's understanding of the world."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

_SENSITIVE_PATTERNS = [
    re.compile(r"(api[_-]?key|token|password|secret|cookie|auth)[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"Bearer\s+\S+", re.IGNORECASE),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
]


def _mask_text(text: str) -> str:
    for pat in _SENSITIVE_PATTERNS:
        text = pat.sub("***MASKED***", text)
    return text


class Staleness(Enum):
    FRESH = "fresh"
    STALE = "stale"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


class StateSource(Enum):
    OBSERVATION = "observation"
    TOOL_RESULT = "tool_result"
    VERIFICATION = "verification"
    APPROVAL = "approval"
    MEMORY = "memory"
    REFLECTION = "reflection"
    SCHEDULER = "scheduler"
    USER_INPUT = "user_input"
    SYSTEM = "system"


class Visibility(Enum):
    LLM_VISIBLE = "llm_visible"
    INTERNAL_ONLY = "internal_only"
    HIDDEN = "hidden"


class Sensitivity(Enum):
    PUBLIC = "public"
    NORMAL = "normal"
    PERSONAL = "personal"
    SECRET = "secret"


# ── StateEntry ────────────────────────────────────────────────

@dataclass
class StateEntry:
    key: str = ""
    value: Any = None
    summary: str = ""
    source: str = "system"
    confidence: float = 0.5
    observed_at: int = 0
    expires_at: int = 0
    staleness: Staleness = Staleness.FRESH
    visibility: str = "llm_visible"
    sensitivity: str = "normal"
    evidence_ref: str = ""
    last_verified_at: int = 0

    def is_stale(self, now_ms: int | None = None) -> bool:
        now = now_ms if now_ms is not None else int(time.time() * 1000)
        if self.staleness == Staleness.EXPIRED:
            return True
        if self.expires_at > 0 and now > self.expires_at:
            return True
        return self.staleness == Staleness.STALE

    def to_context_string(self, max_len: int = 200) -> str:
        if self.sensitivity == "secret":
            val = "***MASKED***"
        elif isinstance(self.value, str):
            val = _mask_text(self.value[:max_len])
        else:
            val = str(self.value)[:max_len]
        return f"{self.key}={val} [{self.staleness.value}, conf={self.confidence:.1f}]"

    def to_dict(self) -> dict[str, Any]:
        val = self.value
        if self.sensitivity == "secret":
            val = "***MASKED***"
        elif isinstance(val, str):
            val = _mask_text(val[:500])
        return {
            "key": self.key,
            "value": val,
            "summary": self.summary[:300],
            "source": self.source,
            "confidence": self.confidence,
            "observed_at": self.observed_at,
            "expires_at": self.expires_at,
            "staleness": self.staleness.value,
            "visibility": self.visibility,
            "sensitivity": self.sensitivity,
        }


# ── Device States ─────────────────────────────────────────────

@dataclass
class PCState:
    active_window_title: str = ""
    active_process: str = ""
    screenshot_summary: str = ""
    visible_text_summary: str = ""
    detected_elements: list[dict[str, Any]] = field(default_factory=list)
    running_processes_summary: str = ""
    focused_element: str = ""
    mouse_position: tuple[int, int] = (0, 0)
    last_observation_id: str = ""
    last_verified_at: int = 0
    confidence: float = 0.0
    sensitivity_flags: list[str] = field(default_factory=list)

    def to_context_string(self, max_len: int = 300) -> str:
        parts = []
        if self.active_window_title:
            parts.append(f"window={self.active_window_title}")
        if self.active_process:
            parts.append(f"process={self.active_process}")
        if self.screenshot_summary:
            parts.append(f"screen={self.screenshot_summary[:100]}")
        if self.visible_text_summary:
            parts.append(f"text={self.visible_text_summary[:100]}")
        return _mask_text(" | ".join(parts))[:max_len]


@dataclass
class BrowserState:
    current_url: str = ""
    page_title: str = ""
    domain: str = ""
    dom_summary: str = ""
    accessibility_tree_summary: str = ""
    visible_text_summary: str = ""
    focused_element: str = ""
    forms_summary: str = ""
    detected_elements: list[dict[str, Any]] = field(default_factory=list)
    login_required: bool = False
    captcha_or_2fa_detected: bool = False
    last_observation_id: str = ""
    last_verified_at: int = 0
    confidence: float = 0.0
    sensitivity_flags: list[str] = field(default_factory=list)

    def to_context_string(self, max_len: int = 300) -> str:
        parts = []
        if self.current_url:
            parts.append(f"url={self.current_url[:100]}")
        if self.page_title:
            parts.append(f"title={self.page_title}")
        if self.domain:
            parts.append(f"domain={self.domain}")
        if self.login_required:
            parts.append("LOGIN_REQUIRED")
        if self.captcha_or_2fa_detected:
            parts.append("CAPTCHA/2FA_DETECTED")
        if self.visible_text_summary:
            parts.append(f"text={self.visible_text_summary[:100]}")
        return _mask_text(" | ".join(parts))[:max_len]


@dataclass
class AndroidState:
    current_package: str = ""
    current_activity: str = ""
    screenshot_summary: str = ""
    ui_tree_summary: str = ""
    visible_text_summary: str = ""
    focused_element: str = ""
    notification_summary: str = ""
    permission_dialog_detected: bool = False
    last_observation_id: str = ""
    last_verified_at: int = 0
    confidence: float = 0.0
    sensitivity_flags: list[str] = field(default_factory=list)

    def to_context_string(self, max_len: int = 300) -> str:
        parts = []
        if self.current_package:
            parts.append(f"app={self.current_package}")
        if self.current_activity:
            parts.append(f"activity={self.current_activity}")
        if self.permission_dialog_detected:
            parts.append("PERMISSION_DIALOG")
        if self.visible_text_summary:
            parts.append(f"text={self.visible_text_summary[:100]}")
        return _mask_text(" | ".join(parts))[:max_len]


@dataclass
class DevState:
    active_repo: str = ""
    active_branch: str = ""
    sandbox_id: str = ""
    worktree_path: str = ""
    git_status_summary: str = ""
    changed_files: list[str] = field(default_factory=list)
    test_status: str = ""
    lint_status: str = ""
    typecheck_status: str = ""
    last_diff_summary: str = ""
    last_verification_id: str = ""
    confidence: float = 0.0
    sensitivity_flags: list[str] = field(default_factory=list)

    def to_context_string(self, max_len: int = 300) -> str:
        parts = []
        if self.active_repo:
            parts.append(f"repo={self.active_repo}")
        if self.active_branch:
            parts.append(f"branch={self.active_branch}")
        if self.test_status:
            parts.append(f"tests={self.test_status}")
        if self.lint_status:
            parts.append(f"lint={self.lint_status}")
        if self.changed_files:
            parts.append(f"changed={len(self.changed_files)} files")
        return " | ".join(parts)[:max_len]


# ── Task / Approval / Desire states ───────────────────────────

class TaskPhase(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    WAITING_APPROVAL = "waiting_approval"
    EXECUTING = "executing"
    OBSERVING = "observing"
    VERIFYING = "verifying"
    RECOVERING = "recovering"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class TaskState:
    active_task_id: str = ""
    active_task_source: str = ""
    current_step: str = ""
    planned_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    blocked_reason: str = ""
    last_tool_request_id: str = ""
    last_verification_result: str = ""
    last_recovery_plan: str = ""
    status: TaskPhase = TaskPhase.IDLE

    def to_context_string(self) -> str:
        if self.status == TaskPhase.IDLE:
            return "No active task."
        parts = [f"task={self.active_task_id or 'unknown'}", f"status={self.status.value}"]
        if self.blocked_reason:
            parts.append(f"blocked={self.blocked_reason[:80]}")
        return " | ".join(parts)


@dataclass
class ApprovalState:
    pending_count: int = 0
    highest_risk_pending: str = ""
    pending_summaries: list[str] = field(default_factory=list)
    last_decision: str = ""
    last_rejected_action: str = ""
    last_approved_action: str = ""

    def to_context_string(self) -> str:
        if self.pending_count == 0:
            return "No pending approvals."
        return f"pending={self.pending_count}, highest_risk={self.highest_risk_pending}"


@dataclass
class DesireStateSummary:
    top_unsatisfied_desires: list[str] = field(default_factory=list)
    average_frustration: float = 0.0
    max_frustration: float = 0.0
    last_desire_driven_task: str = ""
    suppressed_desire_tasks: list[str] = field(default_factory=list)
    last_update_reason: str = ""

    def to_context_string(self) -> str:
        if not self.top_unsatisfied_desires:
            return "All desires satisfied."
        return (
            f"top_unsatisfied={self.top_unsatisfied_desires[:3]}, "
            f"avg_frust={self.average_frustration:.1f}"
        )


# ── WorldState ────────────────────────────────────────────────

# Section TTL defaults in seconds
_SECTION_TTL: dict[str, int] = {
    "pc_state": 30,
    "browser_state": 60,
    "android_state": 30,
    "dev_state": 120,
    "task_state": 60,
    "approval_state": 30,
    "desire_state": 300,
    "memory_summary": 600,
    "agora_state": 120,
}


@dataclass
class AgoraState:
    me_name: str = ""
    me_id: int = 0
    last_cursor: int = 0
    last_seen_post_id: int = 0
    unread_count: int = 0
    recent_posts_summary: str = ""
    recent_mentions_summary: str = ""
    pending_reply_candidates: list[int] = field(default_factory=list)
    last_post_created_by_aegis: int = 0
    last_observation_at: int = 0
    confidence: float = 1.0
    staleness: str = "fresh"

    def to_context_string(self, max_len: int = 300) -> str:
        parts = []
        if self.me_name:
            parts.append(f"account={self.me_name}")
        parts.append(f"cursor={self.last_cursor}")
        if self.unread_count > 0:
            parts.append(f"unread={self.unread_count}")
        if self.recent_posts_summary:
            parts.append(f"recent={self.recent_posts_summary[:100]}")
        if self.pending_reply_candidates:
            parts.append(f"pending_replies={len(self.pending_reply_candidates)}")
        return _mask_text(" | ".join(parts))[:max_len]


@dataclass
class WorldState:
    world_state_id: str = ""
    created_at: int = 0
    updated_at: int = 0
    version: int = 0

    pc_state: PCState = field(default_factory=PCState)
    browser_state: BrowserState = field(default_factory=BrowserState)
    android_state: AndroidState = field(default_factory=AndroidState)
    dev_state: DevState = field(default_factory=DevState)
    agora_state: AgoraState = field(default_factory=AgoraState)
    task_state: TaskState = field(default_factory=TaskState)
    approval_state: ApprovalState = field(default_factory=ApprovalState)
    desire_state: DesireStateSummary = field(default_factory=DesireStateSummary)
    memory_state_summary: str = ""
    active_goals: list[str] = field(default_factory=list)
    active_constraints: list[str] = field(default_factory=list)
    known_uncertainties: list[str] = field(default_factory=list)
    stale_sections: list[str] = field(default_factory=list)
    sensitivity_flags: list[str] = field(default_factory=list)

    def is_section_stale(self, section: str) -> bool:
        return section in self.stale_sections

    def mark_stale(self, section: str, reason: str = "") -> None:
        if section not in self.stale_sections:
            self.stale_sections.append(section)
        self.known_uncertainties.append(f"{section}: {reason}" if reason else section)

    def to_context_string(self, max_chars: int = 1500) -> str:
        parts = [f"WorldState v{self.version}:"]
        task_ctx = self.task_state.to_context_string()
        parts.append(f"Task: {task_ctx}")
        approval_ctx = self.approval_state.to_context_string()
        parts.append(f"Approvals: {approval_ctx}")
        desire_ctx = self.desire_state.to_context_string()
        parts.append(f"Desires: {desire_ctx}")

        if self.browser_state.current_url:
            parts.append(f"Browser: {self.browser_state.to_context_string()}")
        if self.pc_state.active_window_title:
            parts.append(f"PC: {self.pc_state.to_context_string()}")
        if self.android_state.current_package:
            parts.append(f"Android: {self.android_state.to_context_string()}")
        if self.dev_state.active_repo:
            parts.append(f"Dev: {self.dev_state.to_context_string()}")
        if self.agora_state.last_observation_at > 0:
            parts.append(f"AGORA: {self.agora_state.to_context_string()}")
        if self.stale_sections:
            parts.append(f"Stale: {', '.join(self.stale_sections[:5])}")
        if self.known_uncertainties:
            parts.append(f"Uncertain: {', '.join(self.known_uncertainties[:3])}")
        if self.active_constraints:
            parts.append(f"Constraints: {', '.join(self.active_constraints[:3])}")

        text = "\n".join(parts)
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        return text

    def to_dict(self) -> dict[str, Any]:
        return {
            "world_state_id": self.world_state_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "pc_state_summary": self.pc_state.to_context_string(),
            "browser_state_summary": self.browser_state.to_context_string(),
            "android_state_summary": self.android_state.to_context_string(),
            "dev_state_summary": self.dev_state.to_context_string(),
            "agora_state_summary": self.agora_state.to_context_string(),
            "agora_state_raw": {
                "me_name": self.agora_state.me_name,
                "last_cursor": self.agora_state.last_cursor,
                "unread_count": self.agora_state.unread_count,
                "staleness": self.agora_state.staleness,
            },
            "task_state": self.task_state.to_context_string(),
            "task_state_raw": {
                "active_task_id": self.task_state.active_task_id,
                "active_task_source": self.task_state.active_task_source,
                "status": self.task_state.status.value,
                "blocked_reason": self.task_state.blocked_reason,
            },
            "approval_state": self.approval_state.to_context_string(),
            "approval_state_raw": {
                "pending_count": self.approval_state.pending_count,
                "highest_risk_pending": self.approval_state.highest_risk_pending,
                "last_decision": self.approval_state.last_decision,
            },
            "desire_state": self.desire_state.to_context_string(),
            "desire_state_raw": {
                "top_unsatisfied_desires": self.desire_state.top_unsatisfied_desires,
                "average_frustration": self.desire_state.average_frustration,
                "max_frustration": self.desire_state.max_frustration,
            },
            "browser_state_raw": {
                "current_url": self.browser_state.current_url,
                "page_title": self.browser_state.page_title,
                "domain": self.browser_state.domain,
                "login_required": self.browser_state.login_required,
                "captcha_or_2fa_detected": self.browser_state.captcha_or_2fa_detected,
                "last_verified_at": self.browser_state.last_verified_at,
                "confidence": self.browser_state.confidence,
            },
            "pc_state_raw": {
                "active_window_title": self.pc_state.active_window_title,
                "active_process": self.pc_state.active_process,
                "last_verified_at": self.pc_state.last_verified_at,
                "confidence": self.pc_state.confidence,
            },
            "android_state_raw": {
                "current_package": self.android_state.current_package,
                "current_activity": self.android_state.current_activity,
                "permission_dialog_detected": self.android_state.permission_dialog_detected,
                "last_verified_at": self.android_state.last_verified_at,
                "confidence": self.android_state.confidence,
            },
            "dev_state_raw": {
                "active_repo": self.dev_state.active_repo,
                "active_branch": self.dev_state.active_branch,
                "sandbox_id": self.dev_state.sandbox_id,
                "test_status": self.dev_state.test_status,
                "lint_status": self.dev_state.lint_status,
                "confidence": self.dev_state.confidence,
            },
            "memory_state_summary": _mask_text(self.memory_state_summary[:500]),
            "active_goals": self.active_goals,
            "active_constraints": self.active_constraints,
            "known_uncertainties": self.known_uncertainties[:20],
            "stale_sections": self.stale_sections,
            "sensitivity_flags": self.sensitivity_flags,
        }


@dataclass
class WorldStateDiff:
    before_id: str = ""
    after_id: str = ""
    changed_sections: list[str] = field(default_factory=list)
    browser_url_changed: bool = False
    pc_window_changed: bool = False
    android_app_changed: bool = False
    dev_branch_changed: bool = False
    task_status_changed: bool = False
    approval_count_changed: bool = False
    new_errors: list[str] = field(default_factory=list)
    new_success_signals: list[str] = field(default_factory=list)
    summary: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "before_id": self.before_id,
            "after_id": self.after_id,
            "changed_sections": self.changed_sections,
            "browser_url_changed": self.browser_url_changed,
            "pc_window_changed": self.pc_window_changed,
            "android_app_changed": self.android_app_changed,
            "task_status_changed": self.task_status_changed,
            "summary": self.summary[:300],
            "confidence": self.confidence,
        }
