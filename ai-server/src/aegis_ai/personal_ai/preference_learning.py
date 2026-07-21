"""Conditional preference evidence learned from explicit user feedback."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from aegis_ai.personal_ai.storage import JsonStateFile, now_ms


class ConditionalPreferenceStore:
    """Retain feedback evidence without turning one response into a permanent rule."""

    VALID_FEEDBACK = {"approved", "rejected", "ignored", "edited", "opened", "dismissed"}

    def __init__(self, data_dir: str) -> None:
        self._state_file = JsonStateFile(Path(data_dir) / "conditional_preferences.json", {"evidence": []})
        self._state = self._state_file.load()

    def record(
        self,
        feedback: str,
        *,
        target: str = "",
        time_bucket: str = "",
        person: str = "",
        content_type: str = "",
        risk_level: str = "",
        surface: str = "",
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if feedback not in self.VALID_FEEDBACK:
            raise ValueError(f"Unsupported preference feedback: {feedback}")
        evidence = {
            "evidence_id": f"pref_{uuid.uuid4().hex[:12]}",
            "feedback": feedback,
            "conditions": {
                "target": target,
                "time_bucket": time_bucket,
                "person": person,
                "content_type": content_type,
                "risk_level": risk_level,
                "surface": surface,
            },
            "context": context or {},
            "created_at": now_ms(),
            "confidence": 0.2,
        }
        items = self._state.setdefault("evidence", [])
        items.append(evidence)
        if len(items) > 5000:
            del items[:-5000]
        self._state_file.save(self._state)
        return evidence

    def list(self, limit: int = 200) -> list[dict[str, Any]]:
        return list(self._state.get("evidence", []))[-limit:]

    def handle_approval_event(self, event: dict[str, Any]) -> None:
        event_type = str(event.get("event_type") or "")
        feedback = {
            "approved": "approved",
            "rejected": "rejected",
            "surface_rejected": "rejected",
            "modified": "edited",
        }.get(event_type)
        if feedback is None:
            return
        request = event.get("request")
        if request is None:
            return
        self.record(
            feedback,
            target=str(getattr(request, "capability_id", "") or ""),
            content_type=str(getattr(request, "tool_name", "") or ""),
            risk_level=str(getattr(request, "risk_level", "") or ""),
            surface=str(event.get("channel") or getattr(request, "approved_by_surface", "") or ""),
            context={
                "approval_id": getattr(request, "approval_id", ""),
                "source": getattr(request, "source", ""),
                "source_desire": getattr(request, "source_desire", ""),
            },
        )
