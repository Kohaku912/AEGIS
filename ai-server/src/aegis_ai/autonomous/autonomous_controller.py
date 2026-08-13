"""Autonomous Controller — desire-driven task orchestration.

Connects DesireSystem, IntrinsicTaskGenerator, MotivationArbiter,
and DesireActionEvaluator into a single tick() cycle.

Safety:
- tick(dry_run=True) returns decision without executing.
- requires_user_approval tasks are never passed to AutonomousLoop.
- All execution goes through ToolBroker/PolicyEngine.
- Single task per tick — no batch execution.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aegis_ai.autonomous.motivation_arbiter import (
    ExternalTask,
    MotivationArbiter,
    MotivationDecision,
)
from aegis_ai.desire.desire_action_evaluator import DesireActionEvaluator, TaskEvaluation
from aegis_ai.desire.desire_system import DesireSnapshot, DesireSystem
from aegis_ai.desire.intrinsic_task_generator import IntrinsicTask, IntrinsicTaskGenerator
from trigger_engine import ActionType, EventPriority, TaskRequest

logger = logging.getLogger("aegis_ai.autonomous.autonomous_controller")


@dataclass
class TickResult:
    tick_id: str
    decision: MotivationDecision | None
    evaluations: list[TaskEvaluation]
    task_request: TaskRequest | None
    before_snapshot: DesireSnapshot | None
    after_snapshot: DesireSnapshot | None
    executed: bool
    dry_run: bool
    reason: str
    verification_status: str = "pending"


class AutonomousController:
    """Orchestrates desire-driven autonomous behavior.

    Parameters
    ----------
    desire_system:
        Manages desire state, decay, frustration.
    task_generator:
        Generates IntrinsicTask candidates from frustration.
    arbiter:
        Selects which task to execute.
    evaluator:
        Scores candidates before selection.
    tool_broker:
        Executes capabilities (via PolicyEngine).
    data_dir:
        Directory for audit/reflection logs.
    frustration_threshold:
        Minimum average frustration to trigger intrinsic tasks.
    now_ms:
        Override clock.
    """

    def __init__(
        self,
        desire_system: DesireSystem,
        task_generator: IntrinsicTaskGenerator | None = None,
        arbiter: MotivationArbiter | None = None,
        evaluator: DesireActionEvaluator | None = None,
        tool_broker: Any = None,
        data_dir: str = "data/autonomous",
        frustration_threshold: float = 5.0,
        now_ms: int | None = None,
    ) -> None:
        self._desire = desire_system
        self._generator = task_generator or IntrinsicTaskGenerator()
        self._arbiter = arbiter or MotivationArbiter()
        self._evaluator = evaluator or DesireActionEvaluator()
        self._tool_broker = tool_broker
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._threshold = frustration_threshold
        self._now = now_ms

        self._recent_task_ids: list[str] = []
        self._recent_failures: list[str] = []
        self._audit_log: list[dict[str, Any]] = []

    def tick(
        self,
        dry_run: bool = False,
        now_ms: int | None = None,
        user_tasks: list[ExternalTask] | None = None,
        scheduled_tasks: list[ExternalTask] | None = None,
        event_tasks: list[ExternalTask] | None = None,
    ) -> TickResult:
        """Execute one desire-driven cycle.

        Returns TickResult with decision, evaluations, and execution status.
        """
        now = now_ms or self._now or int(time.time() * 1000)
        tick_id = uuid.uuid4().hex[:12]

        # 1. Decay
        self._desire.apply_decay(now_ms=now)

        # 2. Snapshot
        before = self._desire.create_snapshot()

        # 3. Pressure threshold check
        max_pressure = max(
            (d.get("pressure", 0.0) for d in before.desires.values()),
            default=0.0,
        )
        if max_pressure < self._threshold and not user_tasks and not scheduled_tasks and not event_tasks:
            result = TickResult(
                tick_id=tick_id,
                decision=None,
                evaluations=[],
                task_request=None,
                before_snapshot=before,
                after_snapshot=before,
                executed=False,
                dry_run=dry_run,
                reason=f"Max pressure {max_pressure:.2f} < threshold {self._threshold}",
            )
            self._record_audit(result)
            return result

        # 4. Generate intrinsic candidates
        desire_tasks = self._generator.generate(before)

        # 5. Evaluate candidates
        evaluations = self._evaluator.score_candidates(desire_tasks, before)

        # 6. Arbiter selects
        decision = self._arbiter.decide(
            user_tasks=user_tasks,
            scheduled_tasks=scheduled_tasks,
            event_tasks=event_tasks,
            desire_tasks=desire_tasks,
        )

        # 7. Build task request if applicable
        task_request = None
        executed = False
        verification_status = "pending"

        if decision.selected_task is not None and not dry_run:
            if decision.requires_approval:
                logger.info(
                    "Task %s requires approval — not executing.",
                    getattr(decision.selected_task, "task_id", "?"),
                )
                verification_status = "approval_required"
            else:
                task_request = self._build_task_request(decision, now)
                if task_request:
                    executed = True
                    task_id = getattr(decision.selected_task, "task_id", "")
                    if task_id:
                        self._recent_task_ids.append(task_id)
                        fp = getattr(decision.selected_task, "fingerprint", "")
                        if fp:
                            self._generator.record_execution(decision.selected_task, now_ms=now)

        # 8. After snapshot
        after = self._desire.create_snapshot()

        result = TickResult(
            tick_id=tick_id,
            decision=decision,
            evaluations=evaluations,
            task_request=task_request,
            before_snapshot=before,
            after_snapshot=after,
            executed=executed,
            dry_run=dry_run,
            reason=decision.reason,
            verification_status=verification_status,
        )

        # 9. Audit
        self._record_audit(result)
        return result

    def should_trigger_intrinsic_task(self, now_ms: int | None = None) -> bool:
        """Check if any desire pressure exceeds threshold."""
        now = now_ms or self._now or int(time.time() * 1000)
        self._desire.apply_decay(now_ms=now)
        snap = self._desire.create_snapshot()
        max_pressure = max(
            (d.get("pressure", 0.0) for d in snap.desires.values()),
            default=0.0,
        )
        return max_pressure >= self._threshold

    def build_task_request_from_intrinsic_task(
        self,
        task: IntrinsicTask,
        now_ms: int | None = None,
    ) -> TaskRequest:
        """Convert an IntrinsicTask to a TaskRequest."""
        now = now_ms or self._now or int(time.time() * 1000)
        action_type = self._infer_action_type(task)
        return TaskRequest(
            task_id=f"intrinsic_{task.task_id}",
            action_type=action_type,
            triggered_by_event_id="",
            triggered_by_event_type="desire_driven",
            triggered_by_rule_id=f"desire:{task.source_desire}",
            context_summary=f"[{task.source_desire}] {task.title}: {task.description}",
            payload_snapshot=json.dumps({
                "source_desire": task.source_desire,
                "expected_desire_effects": task.expected_desire_effects,
                "risk_level": task.risk_level.name,
                "fingerprint": task.fingerprint,
            }),
            priority=EventPriority.NORMAL,
            created_at_ms=now,
            cooldown_until_ms=now + task.cooldown_seconds * 1000,
        )

    def record_motivation_decision(self, decision: MotivationDecision) -> None:
        """Record a motivation decision for audit."""
        self._audit_log.append({
            "ts": decision.created_at,
            "type": decision.decision_type.name,
            "score": decision.score,
            "reason": decision.reason,
            "risk": decision.risk_level.name,
            "approval": decision.requires_approval,
            "selected": getattr(decision.selected_task, "task_id", None),
        })

    def update_desires_after_task_result(
        self,
        task: IntrinsicTask,
        action: str,
        observation: str,
    ) -> dict[str, Any]:
        """Update desires after task execution."""
        result = self._desire.update_after_action(action, observation)
        self._desire.save()
        return result

    def handle_verification_result(
        self,
        task: IntrinsicTask,
        verification_status: str,
        reason: str = "",
    ) -> None:
        """Handle verification result — update desires based on outcome.

        Parameters
        ----------
        task:
            The intrinsic task that was executed.
        verification_status:
            One of: verified, failed, unverified, requires_observation, error.
        reason:
            Why the verification passed or failed.
        """
        source_desire = task.source_desire

        if verification_status == "verified":
            self._desire.update_value(
                source_desire,
                min(10.0, self._desire.get_desire(source_desire).value + 0.5),
                reason=f"Task verified: {task.title}",
            )
        elif verification_status in ("failed", "error"):
            self._desire.update_value(
                source_desire,
                max(0.0, self._desire.get_desire(source_desire).value - 0.3),
                reason=f"Task failed verification: {reason}",
            )
            self._recent_failures.append(task.task_id)

        self._desire.save()

        self._audit_log.append({
            "ts": int(time.time() * 1000),
            "type": "verification_result",
            "task_id": task.task_id,
            "source_desire": source_desire,
            "frustration": task.frustration if hasattr(task, "frustration") else 0.0,
            "verification_status": verification_status,
            "reason": reason[:200],
        })

    def _build_task_request(
        self,
        decision: MotivationDecision,
        now_ms: int,
    ) -> TaskRequest | None:
        task = decision.selected_task
        if task is None:
            return None
        if isinstance(task, IntrinsicTask):
            return self.build_task_request_from_intrinsic_task(task, now_ms=now_ms)
        if isinstance(task, ExternalTask):
            return TaskRequest(
                task_id=f"external_{task.task_id}",
                action_type=ActionType.ASSIST,
                context_summary=task.title,
                priority=EventPriority.NORMAL,
                created_at_ms=now_ms,
            )
        return None

    def _infer_action_type(self, task: IntrinsicTask) -> ActionType:
        if task.requires_user_approval:
            return ActionType.ASSIST
        if task.source_desire == "social":
            return ActionType.NOTIFY
        if task.source_desire == "growth":
            return ActionType.RESEARCH
        return ActionType.SELF_DEV

    def _record_audit(self, result: TickResult) -> None:
        entry = {
            "tick_id": result.tick_id,
            "ts": int(time.time() * 1000),
            "dry_run": result.dry_run,
            "executed": result.executed,
            "reason": result.reason,
        }
        if result.decision:
            entry["decision_type"] = result.decision.decision_type.name
            entry["score"] = result.decision.score
            entry["risk"] = result.decision.risk_level.name
        if result.task_request:
            entry["task_request_id"] = result.task_request.task_id
        self._audit_log.append(entry)

        log_path = self._data_dir / "controller_audit.jsonl"
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as exc:
            logger.warning("Failed to write audit log: %s", exc)
