"""TaskPlan — structured representation of what AEGIS should do.

A TaskPlan is produced by LLMTaskInterpreter from user's natural language.
It is validated by Planner against PolicyEngine and CapabilityRegistry
before execution through ToolBroker.

Architecture: docs/beta-architecture.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class RiskCategory(Enum):
    """Risk categories for task actions."""
    READ = auto()              # Read-only, no side effects
    DRAFT = auto()             # Create content locally, no external send
    OBSERVE = auto()           # Device observation (screenshot, window list)
    EXTERNAL_SEND = auto()     # Send/post/publish externally
    DEVICE_ACTION = auto()     # Physical device control
    PAYMENT = auto()           # Financial operations
    BLOCKED = auto()           # Always blocked


class StepStatus(Enum):
    """Execution status of a plan step."""
    PENDING = auto()
    APPROVED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()
    BLOCKED = auto()
    NEEDS_APPROVAL = auto()


@dataclass
class PlanStep:
    """A single step in a TaskPlan."""
    step_id: str = ""
    description: str = ""
    action_type: str = ""                  # "browser_open", "browser_read", "tool_invoke", etc.
    capability_id: str = ""                # For ToolBroker
    params: dict[str, Any] = field(default_factory=dict)
    risk_category: RiskCategory = RiskCategory.READ
    requires_approval: bool = False
    expected_result: str = ""
    depends_on: list[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: str = ""


@dataclass
class TaskPlan:
    """Structured task plan produced by LLMTaskInterpreter.

    This is the central data structure for Beta's natural language execution.
    The LLM interprets user intent and produces this plan.
    Planner validates it. ToolBroker executes it.
    """
    plan_id: str = ""

    # What the user wants
    user_goal: str = ""
    interpreted_request: str = ""

    # Planning
    assumptions: list[str] = field(default_factory=list)
    required_context: list[str] = field(default_factory=list)
    steps: list[PlanStep] = field(default_factory=list)

    # Capabilities
    required_capabilities: list[str] = field(default_factory=list)

    # Safety
    risk_notes: list[str] = field(default_factory=list)
    approval_needed: bool = False
    stop_conditions: list[str] = field(default_factory=list)

    # Verification
    expected_result: str = ""
    verification_plan: str = ""

    # Metadata
    needs_browser: bool = False
    needs_device: bool = False
    raw_llm_response: str = ""

    def has_approval_required_steps(self) -> bool:
        """Check if any step requires approval."""
        return any(s.requires_approval for s in self.steps)

    def has_blocked_steps(self) -> bool:
        """Check if any step is blocked."""
        return any(s.risk_category == RiskCategory.BLOCKED for s in self.steps)

    def get_pending_steps(self) -> list[PlanStep]:
        """Get steps that are pending execution."""
        return [s for s in self.steps if s.status == StepStatus.PENDING]

    def get_approval_steps(self) -> list[PlanStep]:
        """Get steps that need approval."""
        return [s for s in self.steps if s.status == StepStatus.NEEDS_APPROVAL]

    def mark_step_complete(self, step_id: str, result: Any = None) -> None:
        """Mark a step as completed."""
        for step in self.steps:
            if step.step_id == step_id:
                step.status = StepStatus.COMPLETED
                step.result = result
                break

    def mark_step_failed(self, step_id: str, error: str) -> None:
        """Mark a step as failed."""
        for step in self.steps:
            if step.step_id == step_id:
                step.status = StepStatus.FAILED
                step.error = error
                break

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "plan_id": self.plan_id,
            "user_goal": self.user_goal,
            "interpreted_request": self.interpreted_request,
            "assumptions": self.assumptions,
            "steps": [
                {
                    "step_id": s.step_id,
                    "description": s.description,
                    "action_type": s.action_type,
                    "capability_id": s.capability_id,
                    "risk_category": s.risk_category.name,
                    "requires_approval": s.requires_approval,
                    "status": s.status.name,
                }
                for s in self.steps
            ],
            "risk_notes": self.risk_notes,
            "approval_needed": self.approval_needed,
            "expected_result": self.expected_result,
        }
