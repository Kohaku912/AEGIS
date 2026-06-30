"""Commitment manager for promises, pending tasks, and follow-ups."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aegis_ai.personal_ai.storage import JsonStateFile, now_ms


@dataclass
class Commitment:
    commitment_id: str
    title: str
    description: str = ""
    due_at_ms: int = 0
    priority: str = "normal"
    status: str = "open"  # open | completed | failed | postponed | cancelled
    next_action: str = ""
    source: str = ""
    related_hook_id: str = ""
    created_at: int = 0
    updated_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Commitment":
        return cls(
            commitment_id=str(data.get("commitment_id") or f"commit_{uuid.uuid4().hex[:10]}"),
            title=str(data.get("title") or "Commitment"),
            description=str(data.get("description") or ""),
            due_at_ms=int(data.get("due_at_ms") or 0),
            priority=str(data.get("priority") or "normal"),
            status=str(data.get("status") or "open"),
            next_action=str(data.get("next_action") or ""),
            source=str(data.get("source") or ""),
            related_hook_id=str(data.get("related_hook_id") or ""),
            created_at=int(data.get("created_at") or 0),
            updated_at=int(data.get("updated_at") or 0),
        )


class CommitmentManager:
    def __init__(self, data_dir: str = "data/personal_ai", audit_manager: Any = None, hook_engine: Any = None) -> None:
        self._state = JsonStateFile(Path(data_dir) / "commitments.json", {"commitments": []})
        self._audit_manager = audit_manager
        self._hook_engine = hook_engine
        self._items: dict[str, Commitment] = {}
        self._load()

    def list_commitments(self, status: str | None = None) -> list[dict[str, Any]]:
        items = list(self._items.values())
        if status:
            items = [c for c in items if c.status == status]
        items.sort(key=lambda c: (c.due_at_ms or 2**63, c.created_at))
        return [c.to_dict() for c in items]

    def get_commitment(self, commitment_id: str) -> dict[str, Any] | None:
        item = self._items.get(commitment_id)
        return item.to_dict() if item else None

    def upsert_commitment(self, patch: dict[str, Any]) -> dict[str, Any]:
        now = now_ms()
        cid = str(patch.get("commitment_id") or f"commit_{uuid.uuid4().hex[:10]}")
        item = self._items.get(cid)
        if item is None:
            item = Commitment(commitment_id=cid, title=str(patch.get("title") or "Commitment"), created_at=now, updated_at=now)
            self._items[cid] = item
        for key in ("title", "description", "due_at_ms", "priority", "status", "next_action", "source", "related_hook_id"):
            if key in patch:
                setattr(item, key, int(patch[key] or 0) if key == "due_at_ms" else str(patch[key]))
        item.updated_at = now
        self._save()
        self._ensure_due_hook(item)
        self._audit("commitment_upserted", item.to_dict())
        return item.to_dict()

    def transition(self, commitment_id: str, status: str, reason: str = "", postpone_until_ms: int = 0) -> dict[str, Any] | None:
        item = self._items.get(commitment_id)
        if item is None:
            return None
        old = item.status
        item.status = status
        if status == "postponed" and postpone_until_ms:
            item.due_at_ms = int(postpone_until_ms)
        item.updated_at = now_ms()
        self._save()
        self._ensure_due_hook(item)
        self._audit("commitment_transition", {"commitment_id": commitment_id, "from": old, "to": status, "reason": reason})
        return item.to_dict()

    def due_commitments(self, now: int | None = None) -> list[dict[str, Any]]:
        t = now or now_ms()
        return [c.to_dict() for c in self._items.values() if c.status == "open" and c.due_at_ms and c.due_at_ms <= t]

    def get_urgency(self, related_task_id: str = "") -> str:
        due = self.due_commitments()
        if any(c.get("priority") in {"high", "urgent"} for c in due):
            return "high"
        return "normal" if due else "low"

    def _ensure_due_hook(self, item: Commitment) -> None:
        if self._hook_engine is None or not item.due_at_ms or item.status != "open":
            return
        hook_id = item.related_hook_id or f"commitment_due_{item.commitment_id}"
        hook = self._hook_engine.upsert_hook({
            "hook_id": hook_id,
            "name": f"Commitment due: {item.title}",
            "kind": "schedule",
            "schedule_at_ms": item.due_at_ms,
            "capability_id": "ai-server.workspace.list_files",
            "arguments": {"relative_dir": ".", "max_entries": 1},
            "condition": {"path": "ok", "op": "eq", "value": True},
            "cooldown_seconds": 3600,
            "max_runs_per_hour": 1,
            "enabled": True,
        })
        item.related_hook_id = hook.get("hook_id", hook_id)
        self._save()

    def _load(self) -> None:
        data = self._state.load()
        self._items = {c.commitment_id: c for c in [Commitment.from_dict(x) for x in data.get("commitments", []) if isinstance(x, dict)]}

    def _save(self) -> None:
        self._state.save({"commitments": [c.to_dict() for c in self._items.values()], "updated_at": now_ms()})

    def _audit(self, action: str, detail: dict[str, Any]) -> None:
        if self._audit_manager is None:
            return
        try:
            self._audit_manager.log_decision(action=action, actor="commitment_manager", decision="success", reason=action, detail=detail)
        except Exception:
            pass
