"""Unified runtime state and DecisionContext assembly."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from aegis_ai.agency.mission import DEFAULT_MISSION_CONTRACT, MissionContract

_OBLIGATION_RANK = {
    "incident": 0,
    "commitment": 1,
    "social_obligation": 2,
    "user_goal": 3,
    "growth": 4,
}


@dataclass
class Obligation:
    """An unresolved real-world duty considered before optional desires."""

    obligation_id: str
    kind: str
    summary: str
    priority: int = 0
    due_at_ms: int = 0
    source: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def sort_key(self) -> tuple[int, int, int]:
        due = self.due_at_ms or 2**63
        return (_OBLIGATION_RANK.get(self.kind, 99), due, -self.priority)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class DecisionContext:
    """Immutable-by-convention snapshot consumed by every decision surface."""

    context_id: str
    built_at_ms: int
    triggering_query: str
    mission_version: str
    identity: str = ""
    situation: dict[str, Any] = field(default_factory=dict)
    relationships: list[dict[str, Any]] = field(default_factory=list)
    learnings: list[dict[str, Any]] = field(default_factory=list)
    opinions: list[dict[str, Any]] = field(default_factory=list)
    preferences: list[dict[str, Any]] = field(default_factory=list)
    conversations: list[dict[str, Any]] = field(default_factory=list)
    corrections: list[dict[str, Any]] = field(default_factory=list)
    decision_evidence: list[dict[str, Any]] = field(default_factory=list)
    obligations: list[Obligation] = field(default_factory=list)
    active_tasks: list[dict[str, Any]] = field(default_factory=list)
    daily_plan: dict[str, Any] = field(default_factory=dict)
    delegation: dict[str, Any] = field(default_factory=dict)
    repair_history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "built_at_ms": self.built_at_ms,
            "triggering_query": self.triggering_query,
            "mission_version": self.mission_version,
            "identity": self.identity,
            "situation": dict(self.situation),
            "relationships": list(self.relationships),
            "learnings": list(self.learnings),
            "opinions": list(self.opinions),
            "preferences": list(self.preferences),
            "conversations": list(self.conversations),
            "corrections": list(self.corrections),
            "decision_evidence": list(self.decision_evidence),
            "obligations": [item.to_dict() for item in self.obligations],
            "active_tasks": list(self.active_tasks),
            "daily_plan": dict(self.daily_plan),
            "delegation": dict(self.delegation),
            "repair_history": list(self.repair_history),
        }

    def to_context_string(self) -> str:
        lines = [f"Mission contract: {self.mission_version}"]
        if self.identity:
            lines.append(self.identity)
        if self.obligations:
            lines.append("Unresolved obligations, in required priority order:")
            lines.extend(f"- [{item.kind}] {item.summary} (id={item.obligation_id})" for item in self.obligations[:12])
        if self.repair_history:
            lines.append("Recent incidents must affect method selection:")
            lines.extend(
                f"- {item.get('category', 'failure')}: {item.get('error', '')}" for item in self.repair_history[-5:]
            )
        if self.corrections:
            lines.append("User corrections that supersede earlier information:")
            lines.extend(
                f"- {item.get('title', 'Correction')}: {item.get('content', '')}"
                for item in self.corrections[:10]
            )
        if self.learnings:
            lines.append("Relevant durable learning:")
            lines.extend(
                f"- {item.get('title', item.get('topic', 'Learning'))}: "
                f"{item.get('content', item.get('summary', ''))}"
                for item in self.learnings[:10]
            )
        if self.opinions:
            lines.append("Evidence-linked AEGIS opinions:")
            lines.extend(
                f"- {item.get('topic', '')}: {item.get('position', '')} "
                f"(evidence: {item.get('evidence', '')})"
                for item in self.opinions[:10]
            )
        if self.preferences:
            lines.append("Conditional user preference evidence:")
            lines.extend(
                f"- {item.get('feedback', '')}: {item.get('conditions', {})}"
                for item in self.preferences[:10]
            )
        if self.conversations:
            lines.append("Recent relationship and conversation continuity:")
            lines.extend(
                f"- User: {item.get('user_msg', item.get('content', ''))}; "
                f"AEGIS: {item.get('bot_msg', '')}"
                for item in self.conversations[:5]
            )
        return "\n".join(lines)


class AgentState:
    """Single state facade shared by chat, autonomy, social, repair, and planning."""

    def __init__(
        self,
        *,
        mission_contract: MissionContract = DEFAULT_MISSION_CONTRACT,
        identity: Any = None,
        situation_model: Any = None,
        commitment_manager: Any = None,
        social_manager: Any = None,
        task_manager: Any = None,
        repair_manager: Any = None,
        delegation_policy: Any = None,
        daily_planning_manager: Any = None,
        person_memory: Any = None,
        memory_manager: Any = None,
        preference_store: Any = None,
    ) -> None:
        self.mission_contract = mission_contract
        self._identity = identity
        self._situation = situation_model
        self._commitments = commitment_manager
        self._social = social_manager
        self._tasks = task_manager
        self._repair = repair_manager
        self._delegation = delegation_policy
        self._daily = daily_planning_manager
        self._persons = person_memory
        self._memory = memory_manager
        self._preferences = preference_store

    def snapshot(self, triggering_query: str = "") -> DecisionContext:
        """Build one coherent snapshot without interpreting the query in code."""
        now = int(time.time() * 1000)
        context_id = f"decision_{uuid.uuid4().hex[:12]}"
        memory = self._memory_context()
        identity_learning = self._safe_call(self._identity, "get_recent_learning", [], limit=20)
        opinions = self._safe_call(self._identity, "get_learned_opinions", [], limit=50)
        learnings = [*identity_learning, *memory["learnings"]]
        correction_ids = [
            str(item.get("memory_id") or "") for item in memory["corrections"] if item.get("memory_id")
        ]
        context = DecisionContext(
            context_id=context_id,
            built_at_ms=now,
            triggering_query=triggering_query,
            mission_version=self.mission_contract.version,
            identity=self._identity_text(),
            situation=self._safe_call(self._situation, "get_state", {}),
            relationships=self._relationships(),
            learnings=learnings[:30],
            opinions=opinions[:50],
            preferences=self._safe_call(self._preferences, "list", [], limit=50),
            conversations=memory["conversations"][:20],
            corrections=memory["corrections"][:20],
            decision_evidence=[
                {
                    "kind": "correction_applied",
                    "memory_id": memory_id,
                    "context_id": context_id,
                }
                for memory_id in correction_ids
            ],
            obligations=self._obligations(now),
            active_tasks=self._active_tasks(),
            daily_plan=self._safe_call(self._daily, "get", {}) or {},
            delegation=self._safe_call(self._delegation, "get_summary", {}),
            repair_history=self._safe_call(self._repair, "list_history", [], limit=20),
        )
        if correction_ids and self._memory is not None:
            self._safe_call(
                self._memory,
                "mark_corrections_applied",
                None,
                memory_ids=correction_ids,
                context_id=context_id,
            )
        return context

    def _memory_context(self) -> dict[str, list[dict[str, Any]]]:
        default = {"conversations": [], "corrections": [], "learnings": []}
        result = self._safe_call(self._memory, "get_decision_context_memory", default, limit=20)
        if not isinstance(result, dict):
            return default
        return {
            key: list(result.get(key, []) or [])
            for key in ("conversations", "corrections", "learnings")
        }

    def _obligations(self, now_ms: int) -> list[Obligation]:
        items: list[Obligation] = []
        commitments = self._safe_call(self._commitments, "list_commitments", [], status="open")
        for item in commitments:
            items.append(
                Obligation(
                    obligation_id=str(item.get("commitment_id") or ""),
                    kind="commitment",
                    summary=str(item.get("title") or item.get("description") or ""),
                    priority=self._priority_value(item.get("priority")),
                    due_at_ms=int(item.get("due_at_ms") or 0),
                    source=str(item.get("source") or "commitment_manager"),
                    evidence=dict(item),
                )
            )
        social_items = self._safe_call(self._social, "list_items", [], limit=200)
        for item in social_items:
            if str(item.get("status") or "") in {
                "replied",
                "acknowledged",
                "skipped",
                "failed",
            }:
                continue
            items.append(
                Obligation(
                    obligation_id=str(item.get("item_id") or ""),
                    kind="social_obligation",
                    summary=f"{item.get('author', '')}: {item.get('body', '')}".strip(),
                    priority=int(float(item.get("urgency") or 0) * 10),
                    due_at_ms=int(item.get("received_at") or now_ms),
                    source=str(item.get("channel") or "social_manager"),
                    evidence=dict(item),
                )
            )
        repair_items = self._safe_call(self._repair, "list_history", [], limit=50)
        noise_categories = {"transient", "server_down", "llm_failed"}
        noise_results = {
            "recovered",
            "infra_noise",
            "dismissed",
            "rolled_back",
            "repair_disabled",
            "not_retryable",
        }
        for item in repair_items:
            final_result = str(item.get("final_result") or "")
            category = str(item.get("category") or "")
            if final_result in noise_results:
                continue
            if category in noise_categories:
                # Browser timeouts / unreachable servers stay in repair history
                # for diagnostics but must not become user/goal obligations.
                continue
            items.append(
                Obligation(
                    obligation_id=str(item.get("repair_id") or ""),
                    kind="incident",
                    summary=str(item.get("error") or item.get("category") or "Unresolved incident"),
                    priority=10,
                    due_at_ms=int(item.get("timestamp") or now_ms),
                    source="repair_manager",
                    evidence=dict(item),
                )
            )
        task_items = self._safe_call(self._tasks, "list_tasks", [], limit=200)
        for item in task_items:
            if (
                str(item.get("status") or "") != "failed"
                or str(item.get("incident_status") or "") != "open"
            ):
                continue
            items.append(
                Obligation(
                    obligation_id=str(item.get("task_id") or ""),
                    kind="incident",
                    summary=str(item.get("error") or item.get("goal") or "Failed task"),
                    priority=max(8, int(item.get("priority") or 0)),
                    due_at_ms=int(item.get("updated_at") or now_ms),
                    source="task_manager",
                    evidence=dict(item),
                )
            )
        return sorted(items, key=Obligation.sort_key)

    def _active_tasks(self) -> list[dict[str, Any]]:
        tasks = self._safe_call(self._tasks, "list_tasks", [], limit=200)
        terminal = {"completed", "failed", "cancelled", "expired"}
        return [dict(item) for item in tasks if str(item.get("status")) not in terminal]

    def _relationships(self) -> list[dict[str, Any]]:
        persons = self._safe_call(self._persons, "list_all", [])
        return [item.to_dict() if hasattr(item, "to_dict") else dict(item) for item in persons[:50] if item is not None]

    def _identity_text(self) -> str:
        if self._identity is None:
            return ""
        if hasattr(self._identity, "to_context_string"):
            return str(self._identity.to_context_string())
        return str(self._identity)

    @staticmethod
    def _priority_value(value: Any) -> int:
        if isinstance(value, (int, float)):
            return int(value)
        return {"urgent": 10, "high": 8, "normal": 5, "low": 2}.get(str(value).lower(), 5)

    @staticmethod
    def _safe_call(target: Any, method: str, default: Any, **kwargs: Any) -> Any:
        if target is None or not hasattr(target, method):
            return default
        try:
            return getattr(target, method)(**kwargs)
        except Exception:
            return default
