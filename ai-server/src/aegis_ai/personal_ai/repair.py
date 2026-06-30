"""Failure classification and conservative retry/repair tracking."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tool_broker import InvokeStatus

from aegis_ai.personal_ai.storage import JsonStateFile, append_jsonl, now_ms


class RepairManager:
    """Classifies failures, retries safe operations, and records lessons."""

    def __init__(
        self,
        data_dir: str = "data/personal_ai",
        tool_broker: Any = None,
        audit_manager: Any = None,
        memory_manager: Any = None,
    ) -> None:
        self._state = JsonStateFile(Path(data_dir) / "repair.json", {"disabled": False})
        self._history = Path(data_dir) / "repair_history.jsonl"
        self._tool_broker = tool_broker
        self._audit_manager = audit_manager
        self._memory_manager = memory_manager
        self._status = self._state.load()

    def classify_failure(self, *, error: str = "", status: str = "", capability_id: str = "") -> str:
        text = f"{error} {status} {capability_id}".lower()
        if "auth" in text or "token" in text or "credential" in text:
            return "auth"
        if "permission" in text or "denied" in text:
            return "permission"
        if "unreachable" in text or "connection" in text or "offline" in text:
            return "server_down"
        if "validation" in text or "invalid argument" in text:
            return "validation"
        if "timeout" in text or "temporar" in text:
            return "transient"
        if "llm" in text or "provider" in text:
            return "llm_failed"
        if "policy" in text or "approval" in text:
            return "policy_denied"
        return "tool_failed"

    def record_failure(self, *, capability_id: str = "", error: str = "", status: str = "", request: Any = None, result: Any = None) -> dict[str, Any]:
        category = self.classify_failure(error=error, status=status, capability_id=capability_id)
        entry = {
            "repair_id": f"repair_{now_ms()}",
            "capability_id": capability_id,
            "category": category,
            "error": error,
            "status": status,
            "timestamp": now_ms(),
            "attempts": [],
            "final_result": "recorded",
        }
        append_jsonl(self._history, entry)
        self._audit("repair_failure_recorded", entry)
        if category in {"auth", "permission", "server_down"}:
            self._record_lesson(entry)
        return entry

    def maybe_retry(self, request: Any, result: Any, *, max_attempts: int = 2) -> dict[str, Any]:
        cap_id = getattr(request, "capability_id", "")
        status = getattr(getattr(result, "status", None), "value", str(getattr(result, "status", "")))
        error = getattr(result, "error", "")
        entry = self.record_failure(capability_id=cap_id, error=error, status=status, request=request, result=result)
        if self._status.get("disabled"):
            entry["final_result"] = "repair_disabled"
            return entry
        if not self._is_safe_retry(request, result):
            entry["final_result"] = "not_retryable"
            return entry
        for attempt in range(1, max_attempts + 1):
            retry = self._tool_broker.execute(request) if self._tool_broker is not None else None
            attempt_entry = {
                "attempt": attempt,
                "success": bool(getattr(retry, "success", False)),
                "status": getattr(getattr(retry, "status", None), "value", ""),
                "error": getattr(retry, "error", ""),
                "timestamp": now_ms(),
            }
            entry["attempts"].append(attempt_entry)
            if attempt_entry["success"]:
                entry["final_result"] = "recovered"
                break
        append_jsonl(self._history, entry)
        self._audit("repair_attempted", entry)
        if entry["final_result"] != "recovered":
            self._record_lesson(entry)
        return entry

    def list_history(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self._history.exists():
            return []
        import json

        lines = self._history.read_text(encoding="utf-8").splitlines()
        out = []
        for line in lines[-limit:]:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
        return out

    def set_disabled(self, disabled: bool) -> dict[str, Any]:
        self._status["disabled"] = bool(disabled)
        self._status["updated_at"] = now_ms()
        self._state.save(self._status)
        return self.get_status()

    def get_status(self) -> dict[str, Any]:
        return {"disabled": bool(self._status.get("disabled", False)), "recent": self.list_history(limit=10)}

    def _is_safe_retry(self, request: Any, result: Any) -> bool:
        if getattr(getattr(result, "status", None), "value", "") not in {InvokeStatus.TIMEOUT.value, InvokeStatus.UNAVAILABLE.value, InvokeStatus.EXECUTION_ERROR.value}:
            return False
        risk = getattr(getattr(request, "risk_level", None), "name", "").lower()
        return risk in {"read_only", "safe_action", ""}

    def _record_lesson(self, entry: dict[str, Any]) -> None:
        if self._memory_manager is None:
            return
        try:
            self._memory_manager.add_memory(
                f"Failure category {entry['category']} for {entry.get('capability_id')}: {entry.get('error')}",
                memory_type="lesson",
                tags=["repair", entry["category"]],
                importance=0.6,
            )
        except Exception:
            pass

    def _audit(self, action: str, detail: dict[str, Any]) -> None:
        if self._audit_manager is None:
            return
        try:
            self._audit_manager.log_decision(action=action, actor="repair_manager", decision="success", reason=action, detail=detail)
        except Exception:
            pass
