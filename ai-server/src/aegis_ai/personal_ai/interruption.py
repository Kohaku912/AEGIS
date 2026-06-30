"""Notification interruption control."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aegis_ai.personal_ai.storage import JsonStateFile, now_ms


class InterruptionController:
    """Decides when notifications should be delivered or batched."""

    EXCEPTION_CATEGORIES = {"approval_required", "safety_warning", "deadline", "commitment_due", "recovery_needs_user"}

    def __init__(
        self,
        data_dir: str = "data/personal_ai",
        situation_model: Any = None,
        user_model_store: Any = None,
        commitment_manager: Any = None,
        audit_manager: Any = None,
    ) -> None:
        self._state_file = JsonStateFile(Path(data_dir) / "interruption.json", {"batched": [], "emergency_stop": False})
        self._situation_model = situation_model
        self._user_model_store = user_model_store
        self._commitment_manager = commitment_manager
        self._audit_manager = audit_manager
        self._state = self._state_file.load()

    def decide(self, notification: dict[str, Any]) -> dict[str, Any]:
        if self._state.get("emergency_stop"):
            return {"decision": "emergency_stop", "reason": "Emergency stop is active."}
        category = str(notification.get("category") or "general")
        severity = str(notification.get("severity") or "info")
        if category in self.EXCEPTION_CATEGORIES or severity in {"critical", "error"}:
            return {"decision": "send_now", "reason": "Important notification bypasses suppression."}
        model = self._user_model_store.get() if self._user_model_store is not None and hasattr(self._user_model_store, "get") else None
        if model is not None:
            try:
                import time

                if model.is_quiet_now(time.localtime().tm_hour):
                    return {"decision": "batch_later", "reason": "Quiet hours are active."}
                if not model.allows_proactive(category):
                    return {"decision": "suppress", "reason": "UserModel does not allow this proactive category."}
            except Exception:
                pass
        situation = self._situation_model.get_state() if self._situation_model is not None else {}
        mode = situation.get("interruptibility", "unknown")
        if mode == "suppress":
            return {"decision": "batch_later", "reason": f"Situation is {situation.get('state')}."}
        if mode == "important_only":
            return {"decision": "batch_later", "reason": f"Situation allows important notifications only: {situation.get('state')}."}
        return {"decision": "send_now", "reason": "Notification is allowed."}

    def before_send(self, notification: dict[str, Any]) -> dict[str, Any]:
        decision = self.decide(notification)
        if decision["decision"] in {"batch_later", "suppress"}:
            self._state.setdefault("batched", []).append({"notification": notification, "decision": decision, "batched_at": now_ms()})
            self._save()
        self._audit("interruption_decision", {"notification_id": notification.get("notification_id"), **decision})
        return decision

    def flush_batch(self) -> list[dict[str, Any]]:
        items = list(self._state.get("batched", []))
        self._state["batched"] = []
        self._save()
        return items

    def set_emergency_stop(self, active: bool) -> dict[str, Any]:
        self._state["emergency_stop"] = bool(active)
        self._state["updated_at"] = now_ms()
        self._save()
        return self.get_status()

    def get_status(self) -> dict[str, Any]:
        return {
            "emergency_stop": bool(self._state.get("emergency_stop", False)),
            "batched_count": len(self._state.get("batched", [])),
            "batched": list(self._state.get("batched", []))[-20:],
        }

    def _save(self) -> None:
        self._state_file.save(self._state)

    def _audit(self, action: str, detail: dict[str, Any]) -> None:
        if self._audit_manager is None:
            return
        try:
            self._audit_manager.log_decision(action=action, actor="interruption_controller", decision="success", reason=action, detail=detail)
        except Exception:
            pass
