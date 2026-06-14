"""Action Trace Memory — Full trace of autonomous actions.

Records every autonomous action with complete context:
- Purpose and goal
- Context and trigger
- Plan and execution steps
- Tool calls and results
- Failure reasons
- Verification results
- User feedback

Inspired by ExpeL and Reflexion — learning from action trajectories.

Usage:
    atm = ActionTraceMemory()
    trace = atm.begin_trace(goal="Check AGORA", context="social_connection desire")
    atm.add_step(trace, tool_call="agora.read_posts", result="{posts: [...]}")
    atm.complete_trace(trace, success=True, verification="Posts read successfully")
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.memory.action_trace")


class TraceStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionStep:
    """A single step within an action trace."""
    step_id: str = ""
    step_number: int = 0
    description: str = ""
    tool_call: str = ""            # capability_id or "llm" or "internal"
    tool_args: dict[str, Any] = field(default_factory=dict)
    tool_result: str = ""
    success: bool = True
    error: str = ""
    duration_ms: int = 0
    timestamp_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id, "step_number": self.step_number,
            "description": self.description, "tool_call": self.tool_call,
            "tool_args": self.tool_args, "tool_result": self.tool_result[:500],
            "success": self.success, "error": self.error[:200],
            "duration_ms": self.duration_ms, "timestamp_ms": self.timestamp_ms,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExecutionStep:
        return cls(
            step_id=data.get("step_id", ""), step_number=int(data.get("step_number", 0)),
            description=data.get("description", ""), tool_call=data.get("tool_call", ""),
            tool_args=data.get("tool_args", {}), tool_result=data.get("tool_result", ""),
            success=bool(data.get("success", True)), error=data.get("error", ""),
            duration_ms=int(data.get("duration_ms", 0)), timestamp_ms=int(data.get("timestamp_ms", 0)),
        )


@dataclass
class ActionTrace:
    """Complete trace of an autonomous action."""
    trace_id: str = ""
    goal: str = ""
    context: str = ""              # What triggered this action
    desire_name: str = ""          # Related desire
    plan_description: str = ""     # High-level plan

    # Execution
    steps: list[ExecutionStep] = field(default_factory=list)
    status: TraceStatus = TraceStatus.RUNNING

    # Outcome
    success: bool = False
    result_summary: str = ""
    failure_reason: str = ""
    verification_result: str = ""

    # Feedback
    user_feedback: str = ""
    user_satisfaction: float = 0.0  # -1.0 to 1.0

    # Learning metadata
    difficulty: float = 0.5         # 0.0 (easy) to 1.0 (hard)
    novelty: float = 0.5           # 0.0 (routine) to 1.0 (novel)
    tags: list[str] = field(default_factory=list)

    # Timestamps
    started_at_ms: int = 0
    completed_at_ms: int = 0

    # Consolidation
    consolidated: bool = False
    lessons_extracted: bool = False

    @property
    def duration_ms(self) -> int:
        if self.completed_at_ms and self.started_at_ms:
            return self.completed_at_ms - self.started_at_ms
        return 0

    @property
    def success_rate(self) -> float:
        if not self.steps:
            return 0.0
        return sum(1 for s in self.steps if s.success) / len(self.steps)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id, "goal": self.goal, "context": self.context,
            "desire_name": self.desire_name, "plan_description": self.plan_description,
            "steps": [s.to_dict() for s in self.steps],
            "status": self.status.value, "success": self.success,
            "result_summary": self.result_summary, "failure_reason": self.failure_reason,
            "verification_result": self.verification_result,
            "user_feedback": self.user_feedback, "user_satisfaction": self.user_satisfaction,
            "difficulty": self.difficulty, "novelty": self.novelty, "tags": self.tags,
            "started_at_ms": self.started_at_ms, "completed_at_ms": self.completed_at_ms,
            "consolidated": self.consolidated, "lessons_extracted": self.lessons_extracted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ActionTrace:
        return cls(
            trace_id=data.get("trace_id", ""), goal=data.get("goal", ""),
            context=data.get("context", ""), desire_name=data.get("desire_name", ""),
            plan_description=data.get("plan_description", ""),
            steps=[ExecutionStep.from_dict(s) for s in data.get("steps", [])],
            status=TraceStatus(data.get("status", "running")),
            success=bool(data.get("success", False)),
            result_summary=data.get("result_summary", ""),
            failure_reason=data.get("failure_reason", ""),
            verification_result=data.get("verification_result", ""),
            user_feedback=data.get("user_feedback", ""),
            user_satisfaction=float(data.get("user_satisfaction", 0.0)),
            difficulty=float(data.get("difficulty", 0.5)),
            novelty=float(data.get("novelty", 0.5)),
            tags=data.get("tags", []),
            started_at_ms=int(data.get("started_at_ms", 0)),
            completed_at_ms=int(data.get("completed_at_ms", 0)),
            consolidated=bool(data.get("consolidated", False)),
            lessons_extracted=bool(data.get("lessons_extracted", False)),
        )


class ActionTraceMemory:
    """Stores and retrieves complete action traces.

    Central to the learning pipeline:
    ActionTrace → (consolidation) → Lesson / Workflow / Skill
    """

    MAX_TRACES = 500

    def __init__(self, path: str = "data/memory/action_traces.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._traces: dict[str, ActionTrace] = {}
        self._active: dict[str, ActionTrace] = {}  # Currently running
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            for line in self._path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    trace = ActionTrace.from_dict(json.loads(line))
                    self._traces[trace.trace_id] = trace
                    if trace.status == TraceStatus.RUNNING:
                        self._active[trace.trace_id] = trace
            logger.info("Loaded %d action traces", len(self._traces))
        except Exception as e:
            logger.warning("Failed to load action traces: %s", e)

    def _persist(self, trace: ActionTrace) -> None:
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace.to_dict(), ensure_ascii=False) + "\n")

    def begin_trace(
        self,
        goal: str,
        context: str = "",
        desire_name: str = "",
        plan_description: str = "",
        tags: list[str] | None = None,
    ) -> ActionTrace:
        """Begin a new action trace."""
        trace = ActionTrace(
            trace_id=f"trace_{os.urandom(6).hex()}",
            goal=goal, context=context, desire_name=desire_name,
            plan_description=plan_description, tags=tags or [],
            started_at_ms=int(time.time() * 1000),
        )
        self._active[trace.trace_id] = trace
        return trace

    def add_step(
        self,
        trace: ActionTrace,
        description: str,
        tool_call: str = "",
        tool_args: dict[str, Any] | None = None,
        tool_result: str = "",
        success: bool = True,
        error: str = "",
        duration_ms: int = 0,
    ) -> ExecutionStep:
        """Add an execution step to a trace."""
        step = ExecutionStep(
            step_id=f"step_{os.urandom(4).hex()}",
            step_number=len(trace.steps) + 1,
            description=description, tool_call=tool_call,
            tool_args=tool_args or {}, tool_result=tool_result,
            success=success, error=error, duration_ms=duration_ms,
            timestamp_ms=int(time.time() * 1000),
        )
        trace.steps.append(step)
        return step

    def complete_trace(
        self,
        trace: ActionTrace,
        success: bool,
        result_summary: str = "",
        failure_reason: str = "",
        verification_result: str = "",
        user_feedback: str = "",
        user_satisfaction: float = 0.0,
    ) -> None:
        """Complete an action trace."""
        trace.success = success
        trace.result_summary = result_summary
        trace.failure_reason = failure_reason
        trace.verification_result = verification_result
        trace.user_feedback = user_feedback
        trace.user_satisfaction = user_satisfaction
        trace.status = TraceStatus.COMPLETED if success else TraceStatus.FAILED
        trace.completed_at_ms = int(time.time() * 1000)

        self._traces[trace.trace_id] = trace
        self._active.pop(trace.trace_id, None)
        self._persist(trace)

        # Trim old traces
        if len(self._traces) > self.MAX_TRACES:
            oldest = sorted(self._traces.values(), key=lambda t: t.started_at_ms)[:len(self._traces) - self.MAX_TRACES]
            for t in oldest:
                self._traces.pop(t.trace_id, None)

    def get_unconsolidated(self, max_count: int = 50) -> list[ActionTrace]:
        """Get traces that haven't been consolidated yet."""
        return sorted(
            [t for t in self._traces.values() if not t.consolidated and t.status != TraceStatus.RUNNING],
            key=lambda t: t.started_at_ms,
        )[:max_count]

    def search_similar(self, goal: str, count: int = 5) -> list[ActionTrace]:
        """Search for traces with similar goals."""
        goal_words = set(goal.lower().split())
        scored: list[tuple[float, ActionTrace]] = []
        for trace in self._traces.values():
            if trace.status == TraceStatus.RUNNING:
                continue
            trace_words = set(trace.goal.lower().split())
            overlap = len(goal_words & trace_words)
            if overlap > 0:
                score = overlap / max(len(goal_words | trace_words), 1)
                # Boost successful traces
                if trace.success:
                    score *= 1.5
                scored.append((score, trace))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored[:count]]

    def get_successful(self, count: int = 20) -> list[ActionTrace]:
        return sorted(
            [t for t in self._traces.values() if t.success and t.status == TraceStatus.COMPLETED],
            key=lambda t: t.completed_at_ms, reverse=True,
        )[:count]

    def get_failed(self, count: int = 20) -> list[ActionTrace]:
        return sorted(
            [t for t in self._traces.values() if not t.success and t.status == TraceStatus.FAILED],
            key=lambda t: t.completed_at_ms, reverse=True,
        )[:count]

    def get_stats(self) -> dict[str, Any]:
        total = len(self._traces)
        completed = [t for t in self._traces.values() if t.status in (TraceStatus.COMPLETED, TraceStatus.FAILED)]
        return {
            "total_traces": total,
            "active": len(self._active),
            "completed": sum(1 for t in completed if t.success),
            "failed": sum(1 for t in completed if not t.success),
            "unconsolidated": sum(1 for t in self._traces.values() if not t.consolidated),
            "average_steps": sum(len(t.steps) for t in completed) / len(completed) if completed else 0,
        }
