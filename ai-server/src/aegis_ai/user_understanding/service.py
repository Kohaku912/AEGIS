"""Builds a compact, evidence-backed user-understanding snapshot."""

from __future__ import annotations

import time
from typing import Any

from aegis_ai.user_understanding.models import UnderstandingItem, UserUnderstandingSnapshot
from aegis_ai.user_understanding.store import UserUnderstandingStore


def _now_ms() -> int:
    return int(time.time() * 1000)


class UserUnderstandingService:
    """Aggregates durable profile, current state, and open work into one snapshot."""

    def __init__(
        self,
        *,
        data_dir: str = "data/user_understanding",
        user_model_store: Any = None,
        user_state_manager: Any = None,
        commitment_manager: Any = None,
        delegation_policy: Any = None,
        person_memory: Any = None,
        personal_data_core: Any = None,
        task_manager: Any = None,
        repair_manager: Any = None,
    ) -> None:
        self._store = UserUnderstandingStore(data_dir)
        self._user_model_store = user_model_store
        self._user_state_manager = user_state_manager
        self._commitment_manager = commitment_manager
        self._delegation_policy = delegation_policy
        self._person_memory = person_memory
        self._personal_data_core = personal_data_core
        self._task_manager = task_manager
        self._repair_manager = repair_manager
        self._cache: dict[str, Any] = {}
        self._cache_at_ms = 0
        self._cache_ttl_ms = 30_000

    def get_latest_snapshot(self) -> dict[str, Any]:
        if self._cache:
            return dict(self._cache)
        stored = self._store.load()
        if stored:
            self._cache = dict(stored)
            self._cache_at_ms = int(stored.get("generated_at_ms") or _now_ms())
        return dict(stored)

    def build_snapshot(self, triggering_query: str = "") -> UserUnderstandingSnapshot:
        now_ms = _now_ms()
        if self._cache and now_ms - self._cache_at_ms <= self._cache_ttl_ms:
            return self._from_dict(self._cache)

        user_model = self._user_model()
        user_state = self._user_state()
        commitments = self._commitments()
        relationships = self._relationships()
        resources = self._resources()
        delegation = self._delegation()
        tasks = self._tasks()
        repairs = self._repairs()

        short_horizon = self._short_horizon(commitments, tasks, repairs)
        medium_horizon = self._medium_horizon(commitments, user_model)
        long_horizon = self._long_horizon(user_model)
        life_horizon = self._life_horizon(user_model)
        next_actions = self._likely_next_actions(commitments, tasks, repairs, triggering_query)
        deficits = self._predicted_deficits(commitments, tasks, repairs, user_model)
        burden = self._burden_reduction_opportunities(commitments, tasks, repairs)
        self_improvement = self._self_improvement_queue(tasks, repairs)
        evidence_log = self._evidence_log(user_state, commitments, relationships, resources, delegation)

        summary_bits = [
            f"attention={user_state.get('attention', {}).get('device', 'unknown')}",
            f"activity={user_state.get('activity', {}).get('label', 'unknown')}",
            f"open_commitments={len(commitments)}",
            f"next_actions={len(next_actions)}",
            f"deficits={len(deficits)}",
        ]
        snapshot = UserUnderstandingSnapshot(
            generated_at_ms=now_ms,
            summary=", ".join(summary_bits),
            identity_profile={
                "preferred_language": user_model.get("preferred_language", "ja"),
                "preferred_tone": user_model.get("preferred_tone", "polite"),
                "trust_score": user_model.get("trust_score", 0.5),
                "annoyance_score": user_model.get("annoyance_score", 0.0),
                "attention_device": user_state.get("attention", {}).get("device", ""),
                "current_activity": user_state.get("activity", {}).get("label", ""),
            },
            preferences={
                "detail_level": user_model.get("detail_level", "normal"),
                "autonomy_level": user_model.get("autonomy_level", "medium"),
                "notification_preference": user_model.get("notification_preference", "normal"),
                "common_apps": list(user_model.get("common_apps") or [])[:8],
                "preferences": dict(user_model.get("preferences") or {}),
                "work_patterns": dict(user_model.get("work_patterns") or {}),
            },
            constraints={
                "approval_strictness": user_model.get("approval_strictness", "normal"),
                "focus_mode": bool(user_model.get("focus_mode", False)),
                "quiet_hours": dict(user_model.get("quiet_hours") or {}),
                "disallowed_proactive_categories": list(
                    user_model.get("disallowed_proactive_categories") or []
                ),
            },
            commitments=commitments[:12],
            relationships=relationships[:10],
            resources=resources[:10],
            short_horizon=short_horizon[:6],
            medium_horizon=medium_horizon[:6],
            long_horizon=long_horizon[:6],
            life_horizon=life_horizon[:4],
            likely_next_actions=next_actions[:6],
            predicted_deficits=deficits[:6],
            burden_reduction_opportunities=burden[:6],
            self_improvement_queue=self_improvement[:6],
            delegated_authority_state=delegation,
            evidence_log=evidence_log[:20],
        )
        payload = snapshot.to_dict()
        self._store.save(payload)
        self._cache = payload
        self._cache_at_ms = now_ms
        return snapshot

    def to_context_string(self, triggering_query: str = "") -> str:
        return self.build_snapshot(triggering_query).to_context_string()

    def _user_model(self) -> dict[str, Any]:
        model = getattr(self._user_model_store, "get", lambda: None)()
        if model is None:
            return {}
        if hasattr(model, "to_dict"):
            return dict(model.to_dict())
        if isinstance(model, dict):
            return dict(model)
        return {}

    def _user_state(self) -> dict[str, Any]:
        if self._user_state_manager is None or not hasattr(
            self._user_state_manager, "get_current_user_state"
        ):
            return {}
        try:
            return dict(self._user_state_manager.get_current_user_state() or {})
        except Exception:
            return {}

    def _commitments(self) -> list[dict[str, Any]]:
        if self._commitment_manager is None or not hasattr(
            self._commitment_manager, "list_commitments"
        ):
            return []
        try:
            return list(self._commitment_manager.list_commitments(status="open") or [])
        except Exception:
            return []

    def _relationships(self) -> list[dict[str, Any]]:
        if self._person_memory is None or not hasattr(self._person_memory, "list_all"):
            return []
        records = []
        for item in self._person_memory.list_all() or []:
            if hasattr(item, "to_dict"):
                records.append(item.to_dict())
            elif isinstance(item, dict):
                records.append(dict(item))
        return records

    def _resources(self) -> list[dict[str, Any]]:
        if self._personal_data_core is None or not hasattr(self._personal_data_core, "recent_facts"):
            return []
        try:
            facts = list(self._personal_data_core.recent_facts(limit=8) or [])
        except Exception:
            return []
        return [
            {
                "id": str(item.get("id") or ""),
                "statement": str(item.get("statement") or ""),
                "confidence": float(item.get("confidence") or 0.0),
                "timestamp_ms": int(item.get("timestamp_ms") or 0),
            }
            for item in facts
            if item
        ]

    def _delegation(self) -> dict[str, Any]:
        if self._delegation_policy is None or not hasattr(self._delegation_policy, "get_summary"):
            return {
                "counts": {},
                "rules": [],
                "blocked_categories": ["payment"],
                "summary": "No personal delegation policy is configured.",
            }
        try:
            summary = dict(self._delegation_policy.get_summary() or {})
        except Exception:
            summary = {}
        counts = dict(summary.get("counts") or {})
        summary["blocked_categories"] = ["payment"]
        summary["summary"] = (
            f"{counts.get('auto_allowed', 0)} auto-allowed, "
            f"{counts.get('approval_required', 0)} approval-required, "
            f"{counts.get('forbidden', 0)} forbidden rules"
        )
        return summary

    def _tasks(self) -> list[dict[str, Any]]:
        if self._task_manager is None or not hasattr(self._task_manager, "list_tasks"):
            return []
        try:
            return list(self._task_manager.list_tasks(limit=40) or [])
        except Exception:
            return []

    def _repairs(self) -> list[dict[str, Any]]:
        if self._repair_manager is None or not hasattr(self._repair_manager, "list_history"):
            return []
        try:
            return list(self._repair_manager.list_history(limit=40) or [])
        except Exception:
            return []

    def _short_horizon(
        self,
        commitments: list[dict[str, Any]],
        tasks: list[dict[str, Any]],
        repairs: list[dict[str, Any]],
    ) -> list[UnderstandingItem]:
        items: list[UnderstandingItem] = []
        for item in commitments:
            due_at_ms = int(item.get("due_at_ms") or 0)
            if due_at_ms and due_at_ms <= _now_ms() + 24 * 60 * 60 * 1000:
                items.append(
                    UnderstandingItem(
                        title=str(item.get("title") or "Commitment"),
                        summary=str(item.get("next_action") or "Needs follow-through soon."),
                        confidence=0.85,
                        timestamp_ms=due_at_ms,
                        sources=["commitment_manager"],
                        detail={"kind": "commitment", "commitment_id": item.get("commitment_id")},
                    )
                )
        for item in tasks:
            status = str(item.get("status") or "")
            if status in {"running", "waiting_approval", "paused", "failed"}:
                items.append(
                    UnderstandingItem(
                        title=str(item.get("title") or item.get("goal") or "Task"),
                        summary=str(
                            item.get("next_action")
                            or item.get("blocked_reason")
                            or f"Task is {status}."
                        ),
                        confidence=0.7,
                        timestamp_ms=int(item.get("updated_at") or item.get("created_at") or 0),
                        sources=["task_manager"],
                        detail={"kind": "task", "task_id": item.get("task_id"), "status": status},
                    )
                )
        for item in repairs:
            final_result = str(item.get("final_result") or "")
            if final_result in {"recovered", "dismissed", "infra_noise", "rolled_back"}:
                continue
            items.append(
                UnderstandingItem(
                    title=str(item.get("capability_id") or item.get("category") or "Repair item"),
                    summary=str(item.get("error") or item.get("final_result") or "Needs follow-up."),
                    confidence=0.65,
                    timestamp_ms=int(item.get("timestamp") or 0),
                    sources=["repair_manager"],
                    detail={"kind": "repair", "repair_id": item.get("repair_id")},
                )
            )
        items.sort(key=lambda item: (item.timestamp_ms or 2**63, -item.confidence))
        return items

    def _medium_horizon(
        self, commitments: list[dict[str, Any]], user_model: dict[str, Any]
    ) -> list[UnderstandingItem]:
        items: list[UnderstandingItem] = []
        for item in commitments:
            due_at_ms = int(item.get("due_at_ms") or 0)
            if due_at_ms > _now_ms() + 24 * 60 * 60 * 1000:
                items.append(
                    UnderstandingItem(
                        title=str(item.get("title") or "Commitment"),
                        summary="Scheduled follow-through that should stay visible in planning.",
                        confidence=0.7,
                        timestamp_ms=due_at_ms,
                        sources=["commitment_manager"],
                    )
                )
        for goal in list(user_model.get("long_term_goals") or [])[:4]:
            title = str(goal.get("title") or goal.get("goal") or goal)
            if title:
                items.append(
                    UnderstandingItem(
                        title=title,
                        summary="Medium-horizon planning target from durable profile.",
                        confidence=0.6,
                        timestamp_ms=int(goal.get("updated_at") or 0),
                        sources=["user_model_store"],
                    )
                )
        return items

    def _long_horizon(self, user_model: dict[str, Any]) -> list[UnderstandingItem]:
        items = []
        for goal in list(user_model.get("long_term_goals") or [])[:6]:
            title = str(goal.get("title") or goal.get("goal") or goal)
            if not title:
                continue
            items.append(
                UnderstandingItem(
                    title=title,
                    summary=str(goal.get("success_condition") or "Long-horizon goal retained in profile."),
                    confidence=0.55,
                    timestamp_ms=int(goal.get("updated_at") or 0),
                    sources=["user_model_store"],
                )
            )
        return items

    def _life_horizon(self, user_model: dict[str, Any]) -> list[UnderstandingItem]:
        values = dict(user_model.get("preferences") or {})
        items = []
        if values:
            items.append(
                UnderstandingItem(
                    title="Durable preference map",
                    summary="Stable preferences should keep shaping burden-reduction choices.",
                    confidence=0.5,
                    timestamp_ms=int(user_model.get("updated_at") or 0),
                    sources=["user_model_store"],
                    detail={"keys": list(values.keys())[:8]},
                )
            )
        if user_model.get("long_term_goals"):
            items.append(
                UnderstandingItem(
                    title="Life-scale support direction",
                    summary="Long-term goals exist and should influence future delegation expansion.",
                    confidence=0.55,
                    timestamp_ms=int(user_model.get("updated_at") or 0),
                    sources=["user_model_store"],
                )
            )
        return items

    def _likely_next_actions(
        self,
        commitments: list[dict[str, Any]],
        tasks: list[dict[str, Any]],
        repairs: list[dict[str, Any]],
        triggering_query: str,
    ) -> list[UnderstandingItem]:
        items: list[UnderstandingItem] = []
        if triggering_query:
            items.append(
                UnderstandingItem(
                    title="Respond to current user intent",
                    summary=triggering_query[:180],
                    confidence=0.9,
                    timestamp_ms=_now_ms(),
                    sources=["current_query"],
                )
            )
        for item in commitments[:4]:
            next_action = str(item.get("next_action") or "")
            if next_action:
                items.append(
                    UnderstandingItem(
                        title=next_action,
                        summary=str(item.get("title") or "Next commitment step"),
                        confidence=0.8,
                        timestamp_ms=int(item.get("updated_at") or item.get("due_at_ms") or 0),
                        sources=["commitment_manager"],
                    )
                )
        for item in tasks[:4]:
            next_action = str(item.get("next_action") or item.get("blocked_reason") or "")
            if next_action:
                items.append(
                    UnderstandingItem(
                        title=next_action,
                        summary=str(item.get("title") or item.get("goal") or "Task"),
                        confidence=0.65,
                        timestamp_ms=int(item.get("updated_at") or 0),
                        sources=["task_manager"],
                    )
                )
        for item in repairs[:2]:
            if str(item.get("final_result") or "") in {"recovered", "dismissed", "rolled_back"}:
                continue
            items.append(
                UnderstandingItem(
                    title="Investigate unresolved failure",
                    summary=str(item.get("error") or item.get("category") or "Repair issue"),
                    confidence=0.6,
                    timestamp_ms=int(item.get("timestamp") or 0),
                    sources=["repair_manager"],
                )
            )
        return items

    def _predicted_deficits(
        self,
        commitments: list[dict[str, Any]],
        tasks: list[dict[str, Any]],
        repairs: list[dict[str, Any]],
        user_model: dict[str, Any],
    ) -> list[UnderstandingItem]:
        items: list[UnderstandingItem] = []
        if any(int(item.get("due_at_ms") or 0) <= _now_ms() for item in commitments if item.get("due_at_ms")):
            items.append(
                UnderstandingItem(
                    title="Follow-through gap",
                    summary="There are open or overdue commitments that still need execution evidence.",
                    confidence=0.8,
                    timestamp_ms=_now_ms(),
                    sources=["commitment_manager"],
                    detail={"horizon": "short"},
                )
            )
        if any(str(item.get("status") or "") == "failed" for item in tasks) or repairs:
            items.append(
                UnderstandingItem(
                    title="Reliability gap",
                    summary="Recent failed tasks or repair items suggest system stabilization work is needed.",
                    confidence=0.7,
                    timestamp_ms=_now_ms(),
                    sources=["task_manager", "repair_manager"],
                    detail={"horizon": "short"},
                )
            )
        if user_model.get("long_term_goals"):
            items.append(
                UnderstandingItem(
                    title="Planning support gap",
                    summary="Long-term goals exist but require recurring decomposition into actionable plans.",
                    confidence=0.55,
                    timestamp_ms=int(user_model.get("updated_at") or 0),
                    sources=["user_model_store"],
                    detail={"horizon": "medium"},
                )
            )
        return items

    def _burden_reduction_opportunities(
        self,
        commitments: list[dict[str, Any]],
        tasks: list[dict[str, Any]],
        repairs: list[dict[str, Any]],
    ) -> list[UnderstandingItem]:
        items: list[UnderstandingItem] = []
        for item in commitments[:4]:
            next_action = str(item.get("next_action") or "")
            if not next_action:
                continue
            items.append(
                UnderstandingItem(
                    title=str(item.get("title") or "Commitment"),
                    summary=f"Delegate or prepare the next step: {next_action}",
                    confidence=0.75,
                    timestamp_ms=int(item.get("updated_at") or item.get("due_at_ms") or 0),
                    sources=["commitment_manager"],
                )
            )
        if repairs:
            items.append(
                UnderstandingItem(
                    title="Reduce repeated repair churn",
                    summary="Convert unresolved failures into tracked improvement work.",
                    confidence=0.65,
                    timestamp_ms=_now_ms(),
                    sources=["repair_manager"],
                )
            )
        if any(str(item.get("status") or "") == "waiting_approval" for item in tasks):
            items.append(
                UnderstandingItem(
                    title="Compress approval friction",
                    summary="Waiting approvals are delaying work that may need better previews or batching.",
                    confidence=0.6,
                    timestamp_ms=_now_ms(),
                    sources=["task_manager"],
                )
            )
        return items

    def _self_improvement_queue(
        self, tasks: list[dict[str, Any]], repairs: list[dict[str, Any]]
    ) -> list[UnderstandingItem]:
        items: list[UnderstandingItem] = []
        for item in repairs[:4]:
            final_result = str(item.get("final_result") or "")
            if final_result in {"recovered", "dismissed", "infra_noise", "rolled_back"}:
                continue
            items.append(
                UnderstandingItem(
                    title=str(item.get("category") or "repair"),
                    summary=str(item.get("error") or "Persistent repair item."),
                    confidence=0.7,
                    timestamp_ms=int(item.get("timestamp") or 0),
                    sources=["repair_manager"],
                )
            )
        for item in tasks[:4]:
            if str(item.get("status") or "") != "failed":
                continue
            items.append(
                UnderstandingItem(
                    title=str(item.get("title") or item.get("goal") or "Failed task"),
                    summary="Investigate and improve the execution path for this failed task.",
                    confidence=0.6,
                    timestamp_ms=int(item.get("updated_at") or 0),
                    sources=["task_manager"],
                )
            )
        return items

    def _evidence_log(
        self,
        user_state: dict[str, Any],
        commitments: list[dict[str, Any]],
        relationships: list[dict[str, Any]],
        resources: list[dict[str, Any]],
        delegation: dict[str, Any],
    ) -> list[dict[str, Any]]:
        evidence: list[dict[str, Any]] = []
        if user_state:
            evidence.append(
                {
                    "source": "user_state_manager",
                    "kind": "live_state",
                    "summary": str(user_state.get("activity", {}).get("label") or "unknown"),
                    "timestamp_ms": int(user_state.get("updated_at_ms") or 0),
                }
            )
        evidence.extend(
            {
                "source": "commitment_manager",
                "kind": "commitment",
                "summary": str(item.get("title") or "Commitment"),
                "timestamp_ms": int(item.get("updated_at") or item.get("due_at_ms") or 0),
            }
            for item in commitments[:6]
        )
        evidence.extend(
            {
                "source": "person_memory",
                "kind": "relationship",
                "summary": str(item.get("name") or "Relationship"),
                "timestamp_ms": int(item.get("last_seen_ms") or 0),
            }
            for item in relationships[:6]
        )
        evidence.extend(
            {
                "source": "personal_data_core",
                "kind": "fact",
                "summary": str(item.get("statement") or ""),
                "timestamp_ms": int(item.get("timestamp_ms") or 0),
            }
            for item in resources[:6]
        )
        if delegation:
            evidence.append(
                {
                    "source": "delegation_policy",
                    "kind": "authority_state",
                    "summary": str(delegation.get("summary") or ""),
                    "timestamp_ms": _now_ms(),
                }
            )
        return evidence

    @staticmethod
    def _from_dict(data: dict[str, Any]) -> UserUnderstandingSnapshot:
        def _items(key: str) -> list[UnderstandingItem]:
            return [
                UnderstandingItem(
                    title=str(item.get("title") or ""),
                    summary=str(item.get("summary") or ""),
                    confidence=float(item.get("confidence") or 0.0),
                    timestamp_ms=int(item.get("timestamp_ms") or 0),
                    sources=list(item.get("sources") or []),
                    detail=dict(item.get("detail") or {}),
                )
                for item in list(data.get(key) or [])
                if item
            ]

        return UserUnderstandingSnapshot(
            generated_at_ms=int(data.get("generated_at_ms") or _now_ms()),
            summary=str(data.get("summary") or ""),
            identity_profile=dict(data.get("identity_profile") or {}),
            preferences=dict(data.get("preferences") or {}),
            constraints=dict(data.get("constraints") or {}),
            commitments=list(data.get("commitments") or []),
            relationships=list(data.get("relationships") or []),
            resources=list(data.get("resources") or []),
            short_horizon=_items("short_horizon"),
            medium_horizon=_items("medium_horizon"),
            long_horizon=_items("long_horizon"),
            life_horizon=_items("life_horizon"),
            likely_next_actions=_items("likely_next_actions"),
            predicted_deficits=_items("predicted_deficits"),
            burden_reduction_opportunities=_items("burden_reduction_opportunities"),
            self_improvement_queue=_items("self_improvement_queue"),
            delegated_authority_state=dict(data.get("delegated_authority_state") or {}),
            evidence_log=list(data.get("evidence_log") or []),
        )
