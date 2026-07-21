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
        elif disposition == CapabilityDisposition.DEFER:
            decision = InitiativeDecision.OBSERVE_MORE
            reason = "The event was evaluated immediately and queued for bounded reasoning."
            self._increment("candidates_filtered")
        elif not candidate.candidate_capabilities:
            decision = InitiativeDecision.ASK_USER
            reason = "No manifest-backed capability can complete the candidate."
            self._increment("candidates_filtered")
        elif candidate.uncertainty >= 0.8 and candidate.urgency < 0.8:
            decision = InitiativeDecision.OBSERVE_MORE
            reason = "Uncertainty is high and urgency does not justify acting yet."
            self._increment("candidates_filtered")
        elif score < 0.25:
            decision = InitiativeDecision.IGNORE_WITH_REASON
            reason = f"Expected utility is too low ({score:.2f})."
            self._increment("candidates_filtered")
        elif score < 0.75:
            decision = InitiativeDecision.SAVE_FOR_LATER
            reason = f"Candidate is useful but not timely enough ({score:.2f})."
            self._increment("candidates_filtered")
        elif candidate.requires_approval or disposition == CapabilityDisposition.PROPOSE_FOR_APPROVAL:
            decision = InitiativeDecision.PROPOSE_APPROVAL
            reason = "The candidate is worthwhile, but policy requires explicit approval."
            self._increment("approval_proposals_selected")
        elif disposition == CapabilityDisposition.ASK_USER:
            decision = InitiativeDecision.ASK_USER
            reason = "Required context must be supplied by the user."
            self._increment("candidates_filtered")
        else:
            decision = InitiativeDecision.EXECUTE_NOW
            reason = f"Expected utility justifies a safe action now ({score:.2f})."
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

    def diagnostics(self) -> dict[str, Any]:
        records = list(self._state.get("records", []))
        reasons = Counter(
            str(item.get("reason") or "unspecified")
            for item in records
            if item.get("record_type") == "candidate_decision"
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
