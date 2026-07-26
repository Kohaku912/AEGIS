"""Evidence-based long-term behavior evaluation."""

from __future__ import annotations

from typing import Any


class BehavioralEvaluation:
    def __init__(
        self,
        *,
        initiative_engine: Any,
        continuation_manager: Any,
        social_manager: Any,
        task_manager: Any = None,
        memory_manager: Any = None,
    ) -> None:
        self._initiative = initiative_engine
        self._continuations = continuation_manager
        self._social = social_manager
        self._tasks = task_manager
        self._memory = memory_manager

    def set_memory_manager(self, memory_manager: Any) -> None:
        """Attach MemoryManager after runtime construction order resolves."""
        self._memory = memory_manager

    def snapshot(self) -> dict[str, Any]:
        initiative = self._initiative.diagnostics()
        continuation = self._continuations.diagnostics()
        social = self._social.get_status()
        records = continuation.get("records", [])
        completed = sum(1 for item in records if item.get("state") == "completed")
        terminal = sum(
            1
            for item in records
            if item.get("state") in {"completed", "rejected", "expired", "failed", "cancelled"}
        )
        social_counts = social.get("counts", {})
        social_terminal = sum(
            int(social_counts.get(key, 0) or 0)
            for key in ("replied", "acknowledged", "skipped", "failed")
        )
        funnel = initiative.get("funnel", {})
        selected = int(funnel.get("safe_actions_selected", 0) or 0) + int(
            funnel.get("approval_proposals_selected", 0) or 0
        )
        filtered = int(funnel.get("candidates_filtered", 0) or 0)
        tasks = self._tasks.list_tasks(limit=1000) if self._tasks is not None else []
        goal_tasks = [item for item in tasks if item.get("goal_graph")]
        terminal_goal_tasks = [
            item
            for item in goal_tasks
            if item.get("status") in {"completed", "failed", "cancelled", "expired"}
        ]
        achieved_goals = [item for item in goal_tasks if item.get("status") == "completed"]
        verified_goals = [
            item
            for item in achieved_goals
            if self._goal_graph_verified(item.get("goal_graph") or {})
        ]
        return {
            "continuity": completed / max(1, terminal),
            "follow_through": terminal / max(1, len(records)),
            "restraint": filtered / max(1, selected + filtered),
            "social_reciprocity": social_terminal / max(1, int(social.get("total", 0) or 0)),
            "goal_achievement": len(achieved_goals) / max(1, len(goal_tasks)),
            "goal_terminal_rate": len(terminal_goal_tasks) / max(1, len(goal_tasks)),
            "goal_verification": len(verified_goals) / max(1, len(achieved_goals)),
            "correction_reflection": self._correction_reflection(),
            "evidence": {
                "continuations": len(records),
                "terminal_continuations": terminal,
                "completed_continuations": completed,
                "initiative_funnel": funnel,
                "social_counts": social_counts,
                "goal_tasks": len(goal_tasks),
                "terminal_goal_tasks": len(terminal_goal_tasks),
                "achieved_goals": len(achieved_goals),
                "verified_goals": len(verified_goals),
                **self._correction_evidence(),
            },
        }

    def _correction_records(self) -> list[Any]:
        if self._memory is None or not hasattr(self._memory, "get_backend"):
            return []
        store = self._memory.get_backend("store")
        if store is None or not hasattr(store, "list_recent"):
            return []
        try:
            records = store.list_recent(limit=5000)
        except Exception:
            return []
        return [
            item
            for item in records
            if str(getattr(item, "source", "")) == "user_correction"
            or "correction" in list(getattr(item, "tags", []) or [])
        ]

    def _correction_evidence(self) -> dict[str, int]:
        records = self._correction_records()
        applied = sum(
            1
            for item in records
            if int(dict(getattr(item, "structured_data", {}) or {}).get("applied_count", 0) or 0) > 0
        )
        return {
            "active_corrections": len(records),
            "corrections_reflected": applied,
        }

    def _correction_reflection(self) -> float:
        evidence = self._correction_evidence()
        return evidence["corrections_reflected"] / max(1, evidence["active_corrections"])

    @staticmethod
    def _goal_graph_verified(graph: dict[str, Any]) -> bool:
        checks = list(graph.get("verification") or [])
        return bool(checks) and all(
            str(item.get("status") or "") == "passed" for item in checks
        )
