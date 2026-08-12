from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class CapabilityManifestModel(BaseModel):
    """Strict-ish runtime representation for a capability manifest JSON.

    Note: we validate presence/types that we control (shape), but we do not fully
    validate JSON Schema correctness here to avoid rejecting permissive manifests.
    """

    capability_id: str
    title: str = ""
    description: str = ""
    server_id: str
    app_id: str
    action: str
    operation_category: str
    origin: str = ""
    version: str = "1.0.0"
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    risk_level: str = "low"
    requires_approval: bool = False
    side_effects: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    completion: dict[str, Any] = Field(default_factory=dict)
    tcp_command: str = ""
    tcp_command_json: str = ""
    extra: dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "extra": "allow",
    }


class JournalEvent(BaseModel):
    """Append-only event for an event journal (Phase 2)."""

    sequence: int = Field(ge=0)
    event_type: str
    aggregate_type: str
    aggregate_id: str
    timestamp_ms: int = 0
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str = ""
    causation_id: str = ""

    model_config = {
        "extra": "allow",
    }


class PlanStepModel(BaseModel):
    """Typed view of a single step in `TaskPlan` (for schema enforcement)."""

    step_id: str
    action: str
    capability_id: str = ""
    arguments: dict[str, Any] = Field(default_factory=dict)
    success_criteria: dict[str, Any] = Field(default_factory=dict)


class TaskRecord(BaseModel):
    """Typed view of a persisted task record (Phase 2/5)."""

    task_id: str
    status: Literal["planning", "running", "paused", "completed", "failed", "blocked", "awaiting_approval"]
    created_at_ms: int = 0
    updated_at_ms: int = 0
    plan_json: str = ""
    root_task_id: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "CapabilityManifestModel",
    "JournalEvent",
    "PlanStepModel",
    "TaskRecord",
]

