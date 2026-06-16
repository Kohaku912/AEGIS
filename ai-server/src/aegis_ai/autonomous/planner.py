"""Autonomous Planner — goal-driven task decomposition and execution.

Converts high-level goals into executable subtasks with:
- Subtask decomposition
- Tool requirement detection
- State observation before execution
- Post-execution verification
- Failure replanning
- Permission checking
- "Don't do" decisions
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from aegis_ai.llm.json_utils import extract_json_object
from aegis_ai.llm.memory_context import build_shared_memory_context

logger = logging.getLogger("aegis_ai.autonomous.planner")


class SubtaskStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"
    WAITING_APPROVAL = "waiting_approval"


class PlanStatus(Enum):
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REPLANNING = "replanning"


@dataclass
class Subtask:
    subtask_id: str = ""
    description: str = ""
    capability_id: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    status: SubtaskStatus = SubtaskStatus.PENDING
    output: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    verification_status: str = "pending"
    retry_count: int = 0
    max_retries: int = 2
    created_at: int = 0


@dataclass
class ExecutionPlan:
    plan_id: str = ""
    goal: str = ""
    subtasks: list[Subtask] = field(default_factory=list)
    status: PlanStatus = PlanStatus.PLANNING
    current_step: int = 0
    replan_count: int = 0
    max_replans: int = 3
    created_at: int = 0
    completed_at: int = 0
    result_summary: str = ""

    def next_pending(self) -> Subtask | None:
        for st in self.subtasks:
            if st.status == SubtaskStatus.PENDING:
                deps_met = all(
                    any(s.subtask_id == dep and s.status == SubtaskStatus.SUCCESS for s in self.subtasks)
                    for dep in st.depends_on
                )
                if deps_met:
                    return st
        return None

    def is_complete(self) -> bool:
        return all(s.status in (SubtaskStatus.SUCCESS, SubtaskStatus.SKIPPED) for s in self.subtasks)

    def has_failures(self) -> bool:
        return any(s.status == SubtaskStatus.FAILED for s in self.subtasks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "goal": self.goal,
            "status": self.status.value,
            "current_step": self.current_step,
            "replan_count": self.replan_count,
            "subtasks": [
                {
                    "subtask_id": s.subtask_id,
                    "description": s.description,
                    "capability_id": s.capability_id,
                    "status": s.status.value,
                    "verification_status": s.verification_status,
                    "retry_count": s.retry_count,
                    "error": s.error[:200] if s.error else "",
                }
                for s in self.subtasks
            ],
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "result_summary": self.result_summary,
        }


class AutonomousPlanner:
    """Plans and executes multi-step goals with safety enforcement."""

    def __init__(
        self,
        llm_provider: Any = None,
        tool_broker: Any = None,
        world_state_store: Any = None,
        memory_store: Any = None,
        policy_engine: Any = None,
        data_dir: str = "data/autonomous/plans",
    ) -> None:
        self._llm = llm_provider
        self._broker = tool_broker
        self._world = world_state_store
        self._memory = memory_store
        self._policy = policy_engine
        self._data_dir = data_dir

    def _memory_root(self) -> Path:
        data_path = Path(self._data_dir)
        if data_path.name == "plans":
            return data_path.parent.parent
        return data_path.parent

    def plan(self, goal: str, context: str = "") -> ExecutionPlan:
        plan = ExecutionPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:10]}",
            goal=goal,
            created_at=int(time.time() * 1000),
        )

        if not self._llm:
            plan.subtasks = self._default_decompose(goal)
            plan.status = PlanStatus.EXECUTING
            return plan

        world_context = ""
        if self._world:
            world_context = self._world.state.to_context_string(max_chars=500)

        prompt = f"""You are AEGIS's autonomous planner. Decompose this goal into subtasks.

Goal: {goal}
{f"Context: {context}" if context else ""}

Current world state:
{world_context}

Available capabilities (examples):
- agora.read_posts, agora.read_mentions, agora.create_post
- memory.save, memory.search
- pc.get_screenshot, pc.get_active_window

Rules:
- Each subtask must have a capability_id or be an observation/reflection step
- Mark dependencies between subtasks
- External sends (agora.create_post, email.send) require approval
- Never include destructive actions without explicit user request
- If a goal is unsafe or impossible, return {{"cancel": true, "reason": "..."}}

Respond with JSON:
{{
  "subtasks": [
    {{
      "description": "what to do",
      "capability_id": "agora.read_posts or empty for internal",
      "arguments": {{}},
      "depends_on": []
    }}
  ]
}}

OR if the goal should not be executed:
{{
  "cancel": true,
  "reason": "why not to do this"
}}"""
        memory_context = build_shared_memory_context(
            query=f"{goal}\n{context}".strip(),
            data_dir=str(self._memory_root()),
            profile="decision",
        )
        if memory_context.text:
            prompt = f"Shared memory context:\n{memory_context.text}\n\n{prompt}"

        result = self._llm.generate(
            prompt=prompt,
            system_prompt="You are AEGIS's autonomous planner. Output only JSON. Be safe and conservative.",
            max_tokens=1000,
            context_meta=memory_context.audit_detail(),
            json_mode=True,
        )

        if not result.success:
            plan.subtasks = self._default_decompose(goal)
            plan.status = PlanStatus.EXECUTING
            return plan

        try:
            data = extract_json_object(result.content)

            if data.get("cancel"):
                plan.status = PlanStatus.CANCELLED
                plan.result_summary = data.get("reason", "Goal cancelled by planner.")
                return plan

            subtasks_data = data.get("subtasks", data.get("steps", []))
            if not subtasks_data:
                plan.subtasks = self._default_decompose(goal)
                plan.status = PlanStatus.EXECUTING
                return plan

            for i, st in enumerate(subtasks_data):
                subtask = Subtask(
                    subtask_id=f"st_{i+1}",
                    description=st.get("description", ""),
                    capability_id=st.get("capability_id", ""),
                    arguments=st.get("arguments", {}),
                    depends_on=st.get("depends_on", []),
                    created_at=int(time.time() * 1000),
                )
                plan.subtasks.append(subtask)

            plan.status = PlanStatus.EXECUTING
            return plan

        except Exception as e:
            logger.warning("Planner LLM parse failed: %s", e)
            plan.subtasks = self._default_decompose(goal)
            plan.status = PlanStatus.EXECUTING
            return plan

    def execute_plan(self, plan: ExecutionPlan, dry_run: bool = False) -> ExecutionPlan:
        if plan.status == PlanStatus.CANCELLED:
            return plan

        if not plan.subtasks:
            plan.status = PlanStatus.COMPLETED
            plan.result_summary = "No subtasks to execute."
            plan.completed_at = int(time.time() * 1000)
            return plan

        max_steps = len(plan.subtasks) * 2
        step = 0

        while step < max_steps:
            step += 1
            subtask = plan.next_pending()

            if subtask is None:
                if plan.is_complete():
                    plan.status = PlanStatus.COMPLETED
                    plan.result_summary = f"Completed {len(plan.subtasks)} subtasks."
                elif plan.has_failures():
                    if plan.replan_count < plan.max_replans:
                        plan = self._replan(plan)
                        continue
                    plan.status = PlanStatus.FAILED
                    plan.result_summary = "Failed after max replans."
                break

            if dry_run:
                subtask.status = SubtaskStatus.SKIPPED
                continue

            result = self._execute_subtask(subtask)
            subtask.output = result.get("output", {})
            subtask.error = result.get("error", "")

            if result.get("success"):
                subtask.status = SubtaskStatus.SUCCESS
                subtask.verification_status = self._verify_subtask(subtask)
            elif result.get("needs_approval"):
                subtask.status = SubtaskStatus.WAITING_APPROVAL
            else:
                subtask.retry_count += 1
                if subtask.retry_count <= subtask.max_retries:
                    subtask.status = SubtaskStatus.PENDING
                else:
                    subtask.status = SubtaskStatus.FAILED

            plan.current_step += 1

        plan.completed_at = int(time.time() * 1000)
        self._save_plan(plan)
        return plan

    def _execute_subtask(self, subtask: Subtask) -> dict[str, Any]:
        if not subtask.capability_id:
            if self._llm:
                memory_context = build_shared_memory_context(
                    query=subtask.description,
                    data_dir=str(self._memory_root()),
                    profile="decision",
                )
                prompt = (
                    f"Execute this task and provide the result:\n\n{subtask.description}\n\n"
                    "Respond with the actual output or result."
                )
                if memory_context.text:
                    prompt = f"Shared memory context:\n{memory_context.text}\n\n{prompt}"
                result = self._llm.generate(
                    prompt=prompt,
                    system_prompt="You are AEGIS executing a task. Produce the actual result.",
                    max_tokens=500,
                    context_meta=memory_context.audit_detail(),
                )
                if result.success and result.content:
                    return {"success": True, "output": {"result": result.content.strip()}}
                return {"success": False, "error": "LLM execution failed"}
            return {"success": True, "output": {"result": subtask.description}}

        if not self._broker:
            return {"success": False, "error": "No ToolBroker configured."}

        from tool_broker import ToolExecutionRequest, ExecutionSource

        request = ToolExecutionRequest(
            capability_id=subtask.capability_id,
            arguments=subtask.arguments,
            source=ExecutionSource.AUTONOMOUS,
            reason=f"Autonomous plan subtask: {subtask.description[:100]}",
        )

        result = self._broker.execute(request)

        if result.status.value == "approval_required":
            return {"success": False, "needs_approval": True, "error": result.error}

        if result.status.value == "denied":
            return {"success": False, "error": f"Denied: {result.error}"}

        if result.success:
            return {"success": True, "output": result.output}

        return {"success": False, "error": result.error}

    def _verify_subtask(self, subtask: Subtask) -> str:
        if not subtask.output:
            return "no_output"

        if "error" in subtask.output:
            return "has_error"

        if subtask.capability_id.startswith("agora."):
            if "post_id" in subtask.output:
                return "verified"
            if "posts" in subtask.output or "mentions" in subtask.output:
                return "verified"

        return "passed"

    def _replan(self, plan: ExecutionPlan) -> ExecutionPlan:
        plan.replan_count += 1
        plan.status = PlanStatus.REPLANNING

        failed = [s for s in plan.subtasks if s.status == SubtaskStatus.FAILED]
        for s in failed:
            s.status = SubtaskStatus.PENDING
            s.retry_count = 0

        plan.status = PlanStatus.EXECUTING
        logger.info("Replan #%d: retrying %d failed subtasks", plan.replan_count, len(failed))
        return plan

    def _default_decompose(self, goal: str) -> list[Subtask]:
        return [Subtask(
            subtask_id="st_1",
            description=goal,
            created_at=int(time.time() * 1000),
        )]

    def _save_plan(self, plan: ExecutionPlan) -> None:
        import os
        os.makedirs(self._data_dir, exist_ok=True)
        path = os.path.join(self._data_dir, f"{plan.plan_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(plan.to_dict(), f, ensure_ascii=False, indent=2)
