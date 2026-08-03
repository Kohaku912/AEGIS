"""Failure classification and conservative retry/repair tracking."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import time
import uuid

from tool_broker import ExecutionSource, InvokeStatus, ToolExecutionRequest

from aegis_ai.personal_ai.storage import JsonStateFile, append_jsonl, now_ms

# Failures AEGIS cannot recover from autonomously — learn + ask the user.
_UNREPAIRABLE_CATEGORIES = frozenset({"auth", "permission", "policy_denied", "validation"})
_INFRA_NOISE_CATEGORIES = frozenset({"transient", "server_down", "llm_failed"})
_PRESENT_COOLDOWN_MS = 3_600_000  # 1 hour per fingerprint


class RepairManager:
    """Classifies failures, retries safe operations, and records lessons."""

    def __init__(
        self,
        data_dir: str = "data/personal_ai",
        tool_broker: Any = None,
        audit_manager: Any = None,
        memory_manager: Any = None,
        presentation_manager: Any = None,
    ) -> None:
        self._state = JsonStateFile(Path(data_dir) / "repair.json", {"disabled": False})
        self._history = Path(data_dir) / "repair_history.jsonl"
        self._tool_broker = tool_broker
        self._audit_manager = audit_manager
        self._memory_manager = memory_manager
        self._presentation_manager = presentation_manager
        self._status = self._state.load()
        self._rollback_strategies: dict[str, dict[str, Any]] = dict(self._status.get("rollback_strategies", {}))
        self._agent_state: Any = None
        self._presented_fingerprints: dict[str, int] = dict(self._status.get("presented_fingerprints", {}) or {})

    def set_agent_state(self, agent_state: Any) -> None:
        """Use the shared state when selecting a recovery strategy."""
        self._agent_state = agent_state

    def set_presentation_manager(self, presentation_manager: Any) -> None:
        """Wire PresentationManager for unrepairable user reports."""
        self._presentation_manager = presentation_manager

    def classify_failure(self, *, error: str = "", status: str = "", capability_id: str = "") -> str:
        text = f"{error} {status} {capability_id}".lower()
        if "auth" in text or "token" in text or "credential" in text:
            return "auth"
        if "permission" in text or "denied" in text:
            return "permission"
        if "screen is locked" in text or ("locked" in text and "screen" in text):
            return "permission"
        if (
            "unreachable" in text
            or "connection" in text
            or "offline" in text
            or "unavailable" in text
        ):
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
        if category in _INFRA_NOISE_CATEGORIES:
            final_result = "infra_noise"
        elif category in _UNREPAIRABLE_CATEGORIES:
            final_result = "not_retryable"
        else:
            final_result = "recorded"
        entry = {
            "repair_id": f"repair_{now_ms()}",
            "capability_id": capability_id,
            "category": category,
            "error": error,
            "status": status,
            "timestamp": now_ms(),
            "attempts": [],
            "final_result": final_result,
        }
        append_jsonl(self._history, entry)
        self._audit("repair_failure_recorded", entry)
        self._record_lesson(entry)
        if final_result == "not_retryable":
            self._present_unrepairable(entry)
        return entry

    def maybe_retry(self, request: Any, result: Any, *, max_attempts: int = 2) -> dict[str, Any]:
        cap_id = getattr(request, "capability_id", "")
        status = getattr(getattr(result, "status", None), "value", str(getattr(result, "status", "")))
        error = getattr(result, "error", "")
        entry = self.record_failure(capability_id=cap_id, error=error, status=status, request=request, result=result)
        if entry.get("final_result") == "not_retryable":
            # Already classified as unrepairable and reported.
            return entry
        if self._status.get("disabled"):
            entry["final_result"] = "repair_disabled"
            append_jsonl(self._history, entry)
            self._present_unrepairable(entry)
            return entry
        if not self._is_safe_retry(request, result):
            entry["final_result"] = "not_retryable"
            append_jsonl(self._history, entry)
            self._record_lesson(entry)
            self._present_unrepairable(entry)
            return entry
        strategy = self.plan_strategy(request, result)
        entry["strategy"] = strategy
        attempts_allowed = min(max_attempts, 1)
        if strategy["method"] == "rollback_or_escalate":
            attempts_allowed = 0
        for attempt in range(1, attempts_allowed + 1):
            delay = min(8, 2 ** (attempt - 1))
            if delay > 0:
                time.sleep(min(delay, 0.05))
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
        self._audit("repair_attempted", entry)
        if entry["final_result"] != "recovered":
            rollback = self.rollback(request, result, reason=f"Retry failed: {strategy.get('category')}")
            if rollback.get("attempted"):
                entry["rollback"] = rollback
                entry["final_result"] = (
                    "rolled_back" if rollback.get("success") else "rollback_failed"
                )
            elif strategy["method"] == "rollback_or_escalate":
                entry["final_result"] = "needs_followup"
            self._record_lesson(entry)
            if entry["final_result"] in {"not_retryable", "repair_disabled", "needs_followup", "rollback_failed"}:
                self._present_unrepairable(entry)
        append_jsonl(self._history, entry)
        return entry

    def execute_with_repair(self, request: Any, *, max_attempts: int = 2) -> dict[str, Any]:
        """Execute via ToolBroker and apply retry/rollback strategy on failure."""
        if self._tool_broker is None:
            return {"ok": False, "error": "ToolBroker unavailable."}
        result = self._tool_broker.execute(request)
        if getattr(result, "success", False):
            return {"ok": True, "result": getattr(result, "output", {})}
        repair = self.maybe_retry(request, result, max_attempts=max_attempts)
        return {"ok": repair.get("final_result") == "recovered", "repair": repair}

    def plan_strategy(self, request: Any, result: Any) -> dict[str, Any]:
        category = self.classify_failure(
            error=getattr(result, "error", ""),
            status=getattr(getattr(result, "status", None), "value", ""),
            capability_id=getattr(request, "capability_id", ""),
        )
        retryable = self._is_safe_retry(request, result)
        capability_id = str(getattr(request, "capability_id", "") or "")
        prior_matches = {
            str(item.get("repair_id") or "")
            for item in self.list_history(limit=100)
            if str(item.get("capability_id") or "") == capability_id
            and str(item.get("category") or "") == category
            and str(item.get("final_result") or "") not in {"recovered", "rolled_back"}
        }
        method = "rollback_or_escalate" if len(prior_matches) > 1 else "retry_once"
        metadata = dict(getattr(request, "metadata", {}) or {})
        rollback_capability = metadata.get("rollback_capability_id") or self._rollback_strategies.get(getattr(request, "capability_id", ""), {}).get("capability_id", "")
        return {
            "category": category,
            "retryable": retryable,
            "method": method,
            "prior_matching_failures": max(0, len(prior_matches) - 1),
            "rollback_capability_id": rollback_capability,
            "requires_approval_for_rollback": bool(rollback_capability),
            "decision_context_id": (
                self._agent_state.snapshot(
                    f"repair {getattr(request, 'capability_id', '')}"
                ).context_id
                if self._agent_state is not None
                else ""
            ),
        }

    def register_rollback_strategy(self, capability_id: str, rollback_capability_id: str, rollback_arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        self._rollback_strategies[capability_id] = {
            "capability_id": rollback_capability_id,
            "arguments": rollback_arguments or {},
            "updated_at": now_ms(),
        }
        self._status["rollback_strategies"] = self._rollback_strategies
        self._state.save(self._status)
        return self._rollback_strategies[capability_id]

    def rollback(self, request: Any, result: Any = None, *, reason: str = "") -> dict[str, Any]:
        metadata = dict(getattr(request, "metadata", {}) or {})
        strategy = self._rollback_strategies.get(getattr(request, "capability_id", ""), {})
        rollback_capability = metadata.get("rollback_capability_id") or strategy.get("capability_id", "")
        if not rollback_capability:
            return {"attempted": False, "reason": "No rollback strategy configured."}
        rollback_args = dict(strategy.get("arguments") or {})
        rollback_args.update(dict(metadata.get("rollback_arguments") or {}))
        rollback_request = ToolExecutionRequest(
            request_id=f"repair_rb_{uuid.uuid4().hex[:10]}",
            capability_id=rollback_capability,
            arguments=rollback_args,
            source=ExecutionSource.SYSTEM,
            reason=f"Repair rollback: {reason}",
            metadata={"repair_for_request_id": getattr(request, "request_id", "")},
        )
        rollback_result = self._tool_broker.execute(rollback_request) if self._tool_broker is not None else None
        out = {
            "attempted": True,
            "capability_id": rollback_capability,
            "status": getattr(getattr(rollback_result, "status", None), "value", ""),
            "approval_id": getattr(rollback_result, "approval_id", ""),
            "success": bool(getattr(rollback_result, "success", False)),
            "error": getattr(rollback_result, "error", ""),
        }
        self._audit("repair_rollback_requested", out)
        return out

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

    def dismiss_matching(
        self,
        *,
        categories: set[str] | None = None,
        final_results: set[str] | None = None,
        error_substrings: list[str] | None = None,
        dry_run: bool = True,
        limit: int = 500,
    ) -> dict[str, Any]:
        """Append dismissed markers for old infra noise so obligations stay clean."""
        import json

        categories = categories or {"transient", "server_down", "llm_failed"}
        final_results = final_results or {
            "recorded",
            "needs_followup",
            "rollback_failed",
            "not_retryable",
        }
        needles = [s.lower() for s in (error_substrings or ["timeout", "browserstartevent", "connection"])]
        matched: list[dict[str, Any]] = []
        for item in self.list_history(limit=limit):
            category = str(item.get("category") or "")
            final_result = str(item.get("final_result") or "")
            error = str(item.get("error") or "").lower()
            if final_result in {"recovered", "dismissed", "infra_noise", "rolled_back"}:
                continue
            if category not in categories and not any(n in error for n in needles):
                continue
            if final_result and final_result not in final_results and category not in categories:
                continue
            matched.append(item)
            if not dry_run:
                dismiss = dict(item)
                dismiss["final_result"] = "dismissed"
                dismiss["dismissed_at"] = now_ms()
                dismiss["dismiss_reason"] = "goal_hygiene_infra_noise"
                append_jsonl(self._history, dismiss)
        return {"matched": len(matched), "dry_run": dry_run, "repair_ids": [m.get("repair_id") for m in matched]}

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
        """Persist a short failure lesson so future planning can avoid the same trap."""
        if self._memory_manager is None:
            return
        category = str(entry.get("category") or "")
        # Skip pure infra noise noise; keep actionable lessons.
        if category in _INFRA_NOISE_CATEGORIES:
            return
        content = (
            f"Failure lesson [{category}] capability={entry.get('capability_id')}: "
            f"{entry.get('error')} (result={entry.get('final_result')})"
        )
        try:
            if hasattr(self._memory_manager, "write_memory"):
                self._memory_manager.write_memory(
                    content,
                    memory_type="lesson",
                    tags=["repair", category or "general"],
                    importance=0.6,
                )
            elif hasattr(self._memory_manager, "add_memory"):
                self._memory_manager.add_memory(
                    content,
                    memory_type="lesson",
                    tags=["repair", category or "general"],
                    importance=0.6,
                )
        except Exception:
            pass

    def _present_fingerprint(self, entry: dict[str, Any]) -> str:
        error = str(entry.get("error") or "")[:120]
        return f"{entry.get('capability_id')}|{entry.get('category')}|{error}"

    def _should_suppress_present(self, entry: dict[str, Any]) -> bool:
        fingerprint = self._present_fingerprint(entry)
        last = int(self._presented_fingerprints.get(fingerprint) or 0)
        return bool(last and now_ms() - last < _PRESENT_COOLDOWN_MS)

    def _user_guidance(self, entry: dict[str, Any]) -> str:
        category = str(entry.get("category") or "")
        error = str(entry.get("error") or "")
        if category == "permission":
            if "locked" in error.lower():
                return "端末の画面ロックを解除してから、同じ操作を再試行してください。"
            return "不足している権限を付与してから、同じ操作を再試行してください。"
        if category == "auth":
            return "認証情報の再設定または再ログインが必要です。"
        if category == "policy_denied":
            return "ポリシーにより自動実行できません。必要なら承認するか方針を見直してください。"
        if category == "validation":
            return "引数や入力内容を確認してから再試行してください。"
        if entry.get("final_result") == "repair_disabled":
            return "自動修復が無効です。設定を確認するか手動で対応してください。"
        return "AEGIS だけでは修復できないため、手動対応が必要です。"

    def _present_unrepairable(self, entry: dict[str, Any]) -> None:
        """Tell the user when AEGIS cannot recover from a failure."""
        if self._should_suppress_present(entry):
            return
        presentation_manager = self._presentation_manager
        if presentation_manager is None:
            try:
                from aegis_ai.runtime import get_runtime

                runtime = get_runtime()
                presentation_manager = getattr(runtime, "presentation_manager", None) if runtime else None
            except Exception:
                presentation_manager = None
        if presentation_manager is None or not hasattr(presentation_manager, "present"):
            return

        capability_id = str(entry.get("capability_id") or "unknown")
        error = str(entry.get("error") or "Unknown error")
        category = str(entry.get("category") or "tool_failed")
        guidance = self._user_guidance(entry)
        try:
            from aegis_ai.presentation.models import PresentationRequest

            request = PresentationRequest(
                source="repair_manager",
                intent="unrepairable_failure",
                importance="high",
                modality="text_card",
                title="修復できない問題があります",
                summary=f"{capability_id}: {error[:200]}",
                content={
                    "capability_id": capability_id,
                    "category": category,
                    "error": error[:500],
                    "final_result": entry.get("final_result"),
                    "repair_id": entry.get("repair_id"),
                    "guidance": guidance,
                    "body": f"{error}\n\n{guidance}",
                },
                targets=["dashboard"],
                metadata={
                    "repair_id": entry.get("repair_id"),
                    "category": category,
                },
            )
            presentation_manager.present(request)
            fingerprint = self._present_fingerprint(entry)
            self._presented_fingerprints[fingerprint] = now_ms()
            # Bound persisted dedupe map
            if len(self._presented_fingerprints) > 200:
                oldest = sorted(self._presented_fingerprints.items(), key=lambda item: item[1])[:50]
                for key, _ in oldest:
                    self._presented_fingerprints.pop(key, None)
            self._status["presented_fingerprints"] = self._presented_fingerprints
            self._state.save(self._status)
            self._audit("repair_unrepairable_presented", entry)
        except Exception:
            pass

    def _audit(self, action: str, detail: dict[str, Any]) -> None:
        if self._audit_manager is None:
            return
        try:
            self._audit_manager.log_decision(action=action, actor="repair_manager", decision="success", reason=action, detail=detail)
        except Exception:
            pass
