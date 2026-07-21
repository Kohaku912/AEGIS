"""Durable continuation and open-loop ownership."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from aegis_ai.personal_ai.storage import JsonStateFile, now_ms


@dataclass
class ContinuationRecord:
    continuation_id: str
    goal: str
    stage: str = "observed"
    state: str = "open"
    trigger: str = ""
    task_id: str = ""
    step_id: str = ""
    request_id: str = ""
    approval_id: str = ""
    capability_id: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    purpose: str = ""
    source_desire: str = ""
    conversation_id: str = ""
    waiting_for: str = ""
    follow_up_due_at: int = 0
    social_obligation_id: str = ""
    promised_action: str = ""
    unresolved_question: str = ""
    success_condition: str = ""
    stop_condition: str = ""
    rationale: str = ""
    created_at: int = 0
    updated_at: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ContinuationManager:
    """Persist one chain across propose, execute, verify, present, and learn."""

    TERMINAL_STATES = {"completed", "rejected", "expired", "failed", "cancelled"}

    def __init__(self, data_dir: str) -> None:
        self._state_file = JsonStateFile(Path(data_dir) / "continuations.json", {"records": {}})
        self._state = self._state_file.load()

    def create(self, goal: str, **fields: Any) -> ContinuationRecord:
        timestamp = now_ms()
        record = ContinuationRecord(
            continuation_id=str(fields.pop("continuation_id", "") or f"cont_{uuid.uuid4().hex[:12]}"),
            goal=goal,
            created_at=timestamp,
            updated_at=timestamp,
            **{key: value for key, value in fields.items() if key in ContinuationRecord.__dataclass_fields__},
        )
        record.history.append(
            {
                "stage": record.stage,
                "state": record.state,
                "at": timestamp,
                "reason": record.rationale,
            }
        )
        self._records()[record.continuation_id] = record.to_dict()
        self._save()
        return record

    def get(self, continuation_id: str) -> ContinuationRecord | None:
        raw = self._records().get(continuation_id)
        return ContinuationRecord(**raw) if isinstance(raw, dict) else None

    def find_by_approval(self, approval_id: str) -> ContinuationRecord | None:
        for raw in self._records().values():
            if str(raw.get("approval_id") or "") == approval_id:
                return ContinuationRecord(**raw)
        return None

    def advance(
        self,
        continuation_id: str,
        *,
        stage: str,
        state: str | None = None,
        reason: str = "",
        **updates: Any,
    ) -> ContinuationRecord:
        record = self.get(continuation_id)
        if record is None:
            raise KeyError(f"Continuation not found: {continuation_id}")
        record.stage = stage
        if state is not None:
            record.state = state
        if reason:
            record.rationale = reason
        for key, value in updates.items():
            if key in ContinuationRecord.__dataclass_fields__:
                setattr(record, key, value)
        record.updated_at = now_ms()
        record.history.append(
            {"stage": record.stage, "state": record.state, "at": record.updated_at, "reason": reason}
        )
        self._records()[continuation_id] = record.to_dict()
        self._save()
        return record

    def list_open(self) -> list[dict[str, Any]]:
        return [
            dict(raw)
            for raw in self._records().values()
            if str(raw.get("state") or "open") not in self.TERMINAL_STATES
        ]

    def due(self, at_ms: int | None = None) -> list[dict[str, Any]]:
        current = at_ms or now_ms()
        return [
            raw
            for raw in self.list_open()
            if int(raw.get("follow_up_due_at", 0) or 0) > 0
            and int(raw.get("follow_up_due_at", 0)) <= current
        ]

    def handle_approval_event(self, event: dict[str, Any]) -> None:
        approval_id = str(event.get("approval_id") or "")
        record = self.find_by_approval(approval_id)
        if record is None:
            request = event.get("request")
            metadata = getattr(request, "metadata", {}) if request is not None else {}
            continuation_id = str(metadata.get("continuation_id") or "")
            record = self.get(continuation_id) if continuation_id else None
        if record is None:
            return
        event_type = str(event.get("event_type") or "")
        transitions = {
            "approved": ("approved", "open"),
            "executing": ("executing", "open"),
            "executed": ("verifying", "open"),
            "rejected": ("approval_rejected", "rejected"),
            "cancelled": ("approval_cancelled", "cancelled"),
            "expired": ("approval_expired", "expired"),
            "failed": ("execution_failed", "failed"),
        }
        if event_type in transitions:
            stage, state = transitions[event_type]
            self.advance(record.continuation_id, stage=stage, state=state, reason=f"Approval {event_type}")

    def diagnostics(self) -> dict[str, Any]:
        records = list(self._records().values())
        return {
            "total": len(records),
            "open": len(self.list_open()),
            "due": len(self.due()),
            "waiting_for_user": sum(1 for item in records if item.get("waiting_for") == "user"),
            "waiting_for_external": sum(1 for item in records if item.get("waiting_for") == "external"),
            "records": sorted(records, key=lambda item: int(item.get("updated_at", 0) or 0), reverse=True)[:100],
        }

    def _records(self) -> dict[str, dict[str, Any]]:
        records = self._state.setdefault("records", {})
        if not isinstance(records, dict):
            records = {}
            self._state["records"] = records
        return records

    def _save(self) -> None:
        self._state_file.save(self._state)
