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
    ) -> None:
        self._initiative = initiative_engine
        self._continuations = continuation_manager
        self._social = social_manager

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
        return {
            "continuity": completed / max(1, terminal),
            "follow_through": terminal / max(1, len(records)),
            "restraint": filtered / max(1, selected + filtered),
            "social_reciprocity": social_terminal / max(1, int(social.get("total", 0) or 0)),
            "evidence": {
                "continuations": len(records),
                "terminal_continuations": terminal,
                "completed_continuations": completed,
                "initiative_funnel": funnel,
                "social_counts": social_counts,
            },
        }
