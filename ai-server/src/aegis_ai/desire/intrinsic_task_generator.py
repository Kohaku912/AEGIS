"""Intrinsic Task Generator — desire-frustration-driven task candidates.

Rule-based generator that inspects a DesireSnapshot and produces
IntrinsicTask candidates for desires whose frustration exceeds a threshold.

Safety:
- Generation only, never execution.
- HIGH_RISK tasks always require user approval.
- Notification tasks carry mandatory cooldowns.
- Duplicate suppression via fingerprint + cooldown window.
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum, auto

from aegis_ai.desire.desire_system import DesireSnapshot

logger = logging.getLogger("aegis_ai.desire.intrinsic_task_generator")


class RiskLevel(Enum):
    NONE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    FORBIDDEN = auto()


@dataclass
class IntrinsicTask:
    task_id: str
    source_desire: str
    title: str
    description: str
    priority: float
    expected_desire_effects: dict[str, float]
    required_capabilities: list[str]
    risk_level: RiskLevel
    requires_user_approval: bool
    cooldown_seconds: int
    created_at: int
    reason: str
    fingerprint: str = ""


@dataclass
class _TaskTemplate:
    title: str
    description: str
    expected_desire_effects: dict[str, float]
    required_capabilities: list[str]
    risk_level: RiskLevel
    requires_user_approval: bool
    cooldown_seconds: int


# ── Per-desire task templates ────────────────────────────────────────────

_TASK_TEMPLATES: dict[str, list[_TaskTemplate]] = {
    "learning_progress": [
        _TaskTemplate(
            title="Review recent failure logs",
            description="Read recent test failures and error logs, propose improvements.",
            expected_desire_effects={"learning_progress": 2.0, "reliability": 0.5},
            required_capabilities=["read_file"],
            risk_level=RiskLevel.LOW,
            requires_user_approval=False,
            cooldown_seconds=3600,
        ),
        _TaskTemplate(
            title="Summarize development history learnings",
            description="Analyze recent commits and changes to extract lessons learned.",
            expected_desire_effects={"learning_progress": 1.5, "purpose": 0.5},
            required_capabilities=["read_file"],
            risk_level=RiskLevel.NONE,
            requires_user_approval=False,
            cooldown_seconds=7200,
        ),
    ],
    "reliability": [
        _TaskTemplate(
            title="Check test suite health",
            description="Run tests and report failures, unhandled exceptions, flaky tests.",
            expected_desire_effects={"reliability": 2.0, "system_safety": 0.5},
            required_capabilities=["run_command"],
            risk_level=RiskLevel.LOW,
            requires_user_approval=False,
            cooldown_seconds=1800,
        ),
        _TaskTemplate(
            title="Scan for unhandled exceptions in logs",
            description="Review application logs for unhandled errors and propose fixes.",
            expected_desire_effects={"reliability": 1.5},
            required_capabilities=["read_file"],
            risk_level=RiskLevel.NONE,
            requires_user_approval=False,
            cooldown_seconds=3600,
        ),
    ],
    "system_safety": [
        _TaskTemplate(
            title="Audit PolicyEngine and ToolBroker status",
            description="Verify safety gates are active and no rules are bypassed.",
            expected_desire_effects={"system_safety": 2.0, "reliability": 0.5},
            required_capabilities=["read_file"],
            risk_level=RiskLevel.NONE,
            requires_user_approval=False,
            cooldown_seconds=3600,
        ),
        _TaskTemplate(
            title="Review high-risk operation logs",
            description="Check recent high-risk and denied operations for anomalies.",
            expected_desire_effects={"system_safety": 1.5},
            required_capabilities=["read_file"],
            risk_level=RiskLevel.NONE,
            requires_user_approval=False,
            cooldown_seconds=3600,
        ),
    ],
    "curiosity": [
        _TaskTemplate(
            title="Research user's active project context",
            description="Investigate the user's current project for relevant new information.",
            expected_desire_effects={"curiosity": 2.0, "user_helpfulness": 0.5},
            required_capabilities=["web_search", "read_file"],
            risk_level=RiskLevel.LOW,
            requires_user_approval=False,
            cooldown_seconds=7200,
        ),
    ],
    "social_connection": [
        _TaskTemplate(
            title="Send progress report to user",
            description="Draft a brief progress update for the user.",
            expected_desire_effects={"social_connection": 2.0, "user_helpfulness": 0.5},
            required_capabilities=["notify_user"],
            risk_level=RiskLevel.LOW,
            requires_user_approval=False,
            cooldown_seconds=14400,
        ),
    ],
    "maintenance": [
        _TaskTemplate(
            title="Run health check",
            description="Check disk usage, memory, service health, and stale data.",
            expected_desire_effects={"maintenance": 2.0, "reliability": 0.5},
            required_capabilities=["run_command"],
            risk_level=RiskLevel.LOW,
            requires_user_approval=False,
            cooldown_seconds=3600,
        ),
        _TaskTemplate(
            title="Clean up old logs and temp files",
            description="Remove stale log files and temporary data older than 7 days.",
            expected_desire_effects={"maintenance": 1.5},
            required_capabilities=["delete_file"],
            risk_level=RiskLevel.MEDIUM,
            requires_user_approval=True,
            cooldown_seconds=86400,
        ),
    ],
    "autonomy": [
        _TaskTemplate(
            title="Pick a low-risk improvement task",
            description="Select and propose an autonomous improvement that requires no approval.",
            expected_desire_effects={"autonomy": 2.0, "purpose": 0.5},
            required_capabilities=[],
            risk_level=RiskLevel.LOW,
            requires_user_approval=False,
            cooldown_seconds=3600,
        ),
    ],
    "user_helpfulness": [
        _TaskTemplate(
            title="Review user's pending TODOs",
            description="Scan recent conversations and tasks for unfinished user requests.",
            expected_desire_effects={"user_helpfulness": 2.0, "social_connection": 0.5},
            required_capabilities=["read_file"],
            risk_level=RiskLevel.NONE,
            requires_user_approval=False,
            cooldown_seconds=3600,
        ),
    ],
    "creativity": [
        _TaskTemplate(
            title="Propose a new feature idea",
            description="Brainstorm a new feature or UI improvement based on recent usage patterns.",
            expected_desire_effects={"creativity": 2.0, "purpose": 0.5},
            required_capabilities=[],
            risk_level=RiskLevel.NONE,
            requires_user_approval=False,
            cooldown_seconds=7200,
        ),
    ],
    "purpose": [
        _TaskTemplate(
            title="Review long-term goals and next steps",
            description="Reflect on current objectives and outline concrete next actions.",
            expected_desire_effects={"purpose": 2.0, "learning_progress": 0.5},
            required_capabilities=[],
            risk_level=RiskLevel.NONE,
            requires_user_approval=False,
            cooldown_seconds=14400,
        ),
    ],
}

# Minimum frustration to consider generating a task for a desire.
_DEFAULT_FRUSTRATION_THRESHOLD: float = 2.0


def _fingerprint(source_desire: str, title: str) -> str:
    raw = f"{source_desire}:{title}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class IntrinsicTaskGenerator:
    """Generates IntrinsicTask candidates from a DesireSnapshot.

    Parameters
    ----------
    frustration_threshold:
        Minimum frustration for a desire to produce task candidates.
    available_capabilities:
        Set of capability IDs the system can currently execute.
        Tasks whose required_capabilities are not a subset are downgraded
        to ``requires_user_approval=True`` proposals.
    now_ms:
        Override clock (epoch-ms). Defaults to wall-clock.
    """

    def __init__(
        self,
        frustration_threshold: float = _DEFAULT_FRUSTRATION_THRESHOLD,
        available_capabilities: set[str] | None = None,
        now_ms: int | None = None,
    ) -> None:
        self._threshold = frustration_threshold
        self._caps = available_capabilities if available_capabilities is not None else set()
        self._now = now_ms

        # fingerprint → last-execution epoch-ms
        self._cooldown_map: dict[str, int] = {}

    # ── Public API ───────────────────────────────────────────────────────

    def generate(self, snapshot: DesireSnapshot) -> list[IntrinsicTask]:
        """Return task candidates ordered by priority (descending)."""
        now = self._now if self._now is not None else int(time.time() * 1000)
        candidates: list[IntrinsicTask] = []

        for desire_name in snapshot.top_unsatisfied_desires:
            desire_info = snapshot.desires.get(desire_name)
            if desire_info is None:
                continue
            frustration = desire_info.get("frustration", 0.0)
            if frustration < self._threshold:
                continue

            templates = _TASK_TEMPLATES.get(desire_name, [])
            for tpl in templates:
                fp = _fingerprint(desire_name, tpl.title)
                last_run = self._cooldown_map.get(fp, 0)
                if now - last_run < tpl.cooldown_seconds * 1000:
                    continue

                caps_available = set(tpl.required_capabilities).issubset(self._caps)
                needs_approval = tpl.requires_user_approval
                risk = tpl.risk_level

                if not caps_available and tpl.required_capabilities:
                    needs_approval = True
                    risk = RiskLevel.MEDIUM

                if risk in (RiskLevel.HIGH, RiskLevel.FORBIDDEN):
                    needs_approval = True

                priority = round(frustration / 10.0, 4)

                task = IntrinsicTask(
                    task_id=uuid.uuid4().hex[:12],
                    source_desire=desire_name,
                    title=tpl.title,
                    description=tpl.description,
                    priority=priority,
                    expected_desire_effects=dict(tpl.expected_desire_effects),
                    required_capabilities=list(tpl.required_capabilities),
                    risk_level=risk,
                    requires_user_approval=needs_approval,
                    cooldown_seconds=tpl.cooldown_seconds,
                    created_at=now,
                    reason=f"{desire_name} frustration={frustration:.1f} >= threshold {self._threshold}",
                    fingerprint=fp,
                )
                candidates.append(task)

        candidates.sort(key=lambda t: t.priority, reverse=True)
        return candidates

    def record_execution(self, task: IntrinsicTask, now_ms: int | None = None) -> None:
        """Mark a task as executed (starts its cooldown)."""
        ts = now_ms if now_ms is not None else int(time.time() * 1000)
        self._cooldown_map[task.fingerprint] = ts

    def is_cooling_down(self, task: IntrinsicTask, now_ms: int | None = None) -> bool:
        now = now_ms if now_ms is not None else int(time.time() * 1000)
        last = self._cooldown_map.get(task.fingerprint, 0)
        return now - last < task.cooldown_seconds * 1000

    def set_available_capabilities(self, caps: set[str]) -> None:
        self._caps = caps
