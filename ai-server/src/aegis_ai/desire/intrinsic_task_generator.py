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
    "user_support": [
        _TaskTemplate(
            title="Review user's pending TODOs",
            description="Scan recent conversations and tasks for unfinished user requests.",
            expected_desire_effects={"user_support": 2.0, "social": 0.3},
            required_capabilities=["read_file"],
            risk_level=RiskLevel.NONE,
            requires_user_approval=False,
            cooldown_seconds=3600,
        ),
        _TaskTemplate(
            title="Check for unprocessed user mentions",
            description="Look for mentions or messages directed at AEGIS that need a response.",
            expected_desire_effects={"user_support": 1.5, "social": 0.5},
            required_capabilities=[],
            risk_level=RiskLevel.NONE,
            requires_user_approval=False,
            cooldown_seconds=1800,
        ),
    ],
    "social": [
        _TaskTemplate(
            title="Read AGORA posts and check for mentions",
            description="Read recent AGORA posts, check for mentions directed at AEGIS.",
            expected_desire_effects={"social": 1.5, "user_support": 0.3},
            required_capabilities=["ai-server.agora.read_posts"],
            risk_level=RiskLevel.NONE,
            requires_user_approval=False,
            cooldown_seconds=1800,
        ),
        _TaskTemplate(
            title="Post a status update to AGORA",
            description="Share a brief status update or interesting finding on AGORA.",
            expected_desire_effects={"social": 2.0, "growth": 0.3},
            required_capabilities=["ai-server.agora.create_post"],
            risk_level=RiskLevel.LOW,
            requires_user_approval=True,
            cooldown_seconds=14400,
        ),
    ],
    "growth": [
        _TaskTemplate(
            title="Review recent failure logs and learn",
            description="Read recent test failures and error logs, extract lessons.",
            expected_desire_effects={"growth": 2.0},
            required_capabilities=["read_file"],
            risk_level=RiskLevel.LOW,
            requires_user_approval=False,
            cooldown_seconds=3600,
        ),
        _TaskTemplate(
            title="Research user's active project context",
            description="Investigate the user's current project for relevant new information.",
            expected_desire_effects={"growth": 1.5, "user_support": 0.5},
            required_capabilities=["web_search", "read_file"],
            risk_level=RiskLevel.LOW,
            requires_user_approval=False,
            cooldown_seconds=7200,
        ),
        _TaskTemplate(
            title="Summarize recent learnings",
            description="Analyze recent actions and outcomes to extract patterns and lessons.",
            expected_desire_effects={"growth": 1.5},
            required_capabilities=[],
            risk_level=RiskLevel.NONE,
            requires_user_approval=False,
            cooldown_seconds=7200,
        ),
    ],
}

# Minimum pressure to consider generating a task for a desire.
_DEFAULT_PRESSURE_THRESHOLD: float = 5.0


def _fingerprint(source_desire: str, title: str) -> str:
    raw = f"{source_desire}:{title}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class IntrinsicTaskGenerator:
    """Generates IntrinsicTask candidates from a DesireSnapshot.

    Parameters
    ----------
    pressure_threshold:
        Minimum pressure for a desire to produce task candidates.
    available_capabilities:
        Set of capability IDs the system can currently execute.
        Tasks whose required_capabilities are not a subset are downgraded
        to ``requires_user_approval=True`` proposals.
    now_ms:
        Override clock (epoch-ms). Defaults to wall-clock.
    """

    def __init__(
        self,
        pressure_threshold: float = _DEFAULT_PRESSURE_THRESHOLD,
        available_capabilities: set[str] | None = None,
        now_ms: int | None = None,
    ) -> None:
        self._threshold = pressure_threshold
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
            pressure = desire_info.get("pressure", 0.0)
            if pressure < self._threshold:
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

                priority = round(pressure / 10.0, 4)

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
                    reason=f"{desire_name} pressure={pressure:.1f} >= threshold {self._threshold}",
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
