"""Persistent mixed-initiative candidate evaluation and diagnostics."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from aegis_ai.autonomous.models import (
    ActionCandidate,
    CapabilityDisposition,
    InitiativeDecision,
)
from aegis_ai.personal_ai.storage import JsonStateFile, now_ms


class InitiativeEngine:
    """Evaluate structured candidates and retain action/non-action rationale."""

    def __init__(self, data_dir: str) -> None:
        self._state_file = JsonStateFile(
            Path(data_dir) / "initiative_state.json",
            {"records": [], "funnel": {}, "last_updated_at": 0},
        )
        self._state = self._state_file.load()

    def record_trigger(self, trigger: str, detail: dict[str, Any] | None = None) -> None:
        self._increment("triggers_observed")
        self._append(
            {
                "record_type": "trigger",
                "trigger": trigger,
                "detail": detail or {},
                "created_at": now_ms(),
            }
        )

    def evaluate(
        self,
        candidate: ActionCandidate,
        disposition: CapabilityDisposition,
    ) -> tuple[InitiativeDecision, str]:
        self._increment("candidates_generated")
        score = candidate.initiative_score

        if disposition in {CapabilityDisposition.FORBIDDEN, CapabilityDisposition.UNAVAILABLE}:
            decision = InitiativeDecision.IGNORE_WITH_REASON
            reason = f"Capability disposition is {disposition.value}."
            self._increment("candidates_filtered")
        elif not candidate.candidate_capabilities:
            decision = InitiativeDecision.ASK_USER
            reason = "No manifest-backed capability can complete the candidate."
            self._increment("candidates_filtered")
        else:
            decision = InitiativeDecision.EXECUTE_NOW
            reason = f"LLM selected this capability (score={score:.2f}; advisory only)."
            self._increment("safe_actions_selected")

        self._append(
            {
                "record_type": "candidate_decision",
                "candidate": candidate.to_dict(),
                "initiative_score": score,
                "capability_disposition": disposition.value,
                "decision": decision.value,
                "reason": reason,
                "created_at": now_ms(),
            }
        )
        return decision, reason

    def record_stage(self, stage: str, detail: dict[str, Any] | None = None) -> None:
        allowed = {
            "actions_executed",
            "actions_verified",
            "results_presented",
            "user_acknowledged",
        }
        if stage in allowed:
            self._increment(stage)
        self._append(
            {
                "record_type": "stage",
                "stage": stage,
                "detail": detail or {},
                "created_at": now_ms(),
            }
        )

    def record_non_action(self, reason: str, detail: dict[str, Any] | None = None) -> None:
        """Persist a deliberate non-action without classifying it as a failure."""
        self._increment("candidates_filtered")
        self._append(
            {
                "record_type": "non_action",
                "decision": InitiativeDecision.IGNORE_WITH_REASON.value,
                "reason": reason or "No action was justified.",
                "detail": detail or {},
                "created_at": now_ms(),
            }
        )

    def diagnostics(self) -> dict[str, Any]:
        records = list(self._state.get("records", []))
        reasons = Counter(
            str(item.get("reason") or "unspecified")
            for item in records
            if item.get("record_type") in {"candidate_decision", "non_action"}
            and item.get("decision") != InitiativeDecision.EXECUTE_NOW.value
        )
        return {
            "funnel": dict(self._state.get("funnel", {})),
            "no_action_reasons": dict(reasons.most_common(20)),
            "recent_decisions": records[-50:],
            "updated_at": int(self._state.get("last_updated_at", 0) or 0),
        }

    def _increment(self, key: str) -> None:
        funnel = self._state.setdefault("funnel", {})
        funnel[key] = int(funnel.get(key, 0) or 0) + 1
        self._save()

    def _append(self, record: dict[str, Any]) -> None:
        records = self._state.setdefault("records", [])
        records.append(record)
        if len(records) > 2000:
            del records[:-2000]
        self._save()

    def _save(self) -> None:
        self._state["last_updated_at"] = now_ms()
        self._state_file.save(self._state)
