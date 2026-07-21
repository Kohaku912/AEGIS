"""Persistent, grounded browser exploration agenda."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from aegis_ai.personal_ai.storage import JsonStateFile, now_ms


@dataclass
class ExplorationAgendaItem:
    agenda_id: str
    topic: str
    source: str
    related_project: str = ""
    related_person: str = ""
    related_commitment: str = ""
    related_conversation: str = ""
    related_failure: str = ""
    question: str = ""
    expected_value: float = 0.0
    novelty: float = 0.0
    last_explored: int = 0
    sources_seen: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    status: str = "open"
    why_now: str = ""
    what_was_unknown: str = ""
    what_was_learned: str = ""
    source_quality: dict[str, Any] = field(default_factory=dict)
    what_changed: str = ""
    who_benefits: str = ""
    next_question: str = ""
    stop_reason: str = ""
    verification: dict[str, Any] = field(default_factory=dict)
    handoffs: list[dict[str, Any]] = field(default_factory=list)
    budgets: dict[str, Any] = field(default_factory=dict)
    created_at: int = 0
    updated_at: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ExplorationAgenda:
    """Own bounded exploration topics and their evidence across restarts."""

    VALID_SOURCES = {
        "project",
        "conversation",
        "question",
        "commitment",
        "social",
        "failure",
        "capability_improvement",
        "user_interest",
        "prior_finding",
    }

    def __init__(self, data_dir: str) -> None:
        self._state_file = JsonStateFile(Path(data_dir) / "exploration_agenda.json", {"items": {}})
        self._state = self._state_file.load()

    def add(self, topic: str, source: str, **context: Any) -> ExplorationAgendaItem:
        if source not in self.VALID_SOURCES:
            raise ValueError(f"Unsupported exploration source: {source}")
        if not any(
            str(context.get(key) or "")
            for key in (
                "related_project",
                "related_person",
                "related_commitment",
                "related_conversation",
                "related_failure",
                "question",
            )
        ):
            raise ValueError(
                "Exploration must be grounded in a project, person, commitment, "
                "conversation, failure, or question"
            )
        for raw in self._items().values():
            if (
                raw.get("topic") == topic
                and raw.get("source") == source
                and raw.get("status") in {"open", "needs_followup"}
            ):
                return ExplorationAgendaItem(**raw)
        timestamp = now_ms()
        item = ExplorationAgendaItem(
            agenda_id=f"agenda_{uuid.uuid4().hex[:12]}",
            topic=topic,
            source=source,
            created_at=timestamp,
            updated_at=timestamp,
            **{key: value for key, value in context.items() if key in ExplorationAgendaItem.__dataclass_fields__},
        )
        self._items()[item.agenda_id] = item.to_dict()
        self._save()
        return item

    def record_result(
        self,
        agenda_id: str,
        *,
        sources: list[str],
        what_was_learned: str,
        source_quality: dict[str, Any],
        what_changed: str,
        next_question: str,
        stop_reason: str,
        verification: dict[str, Any],
        budgets: dict[str, Any],
        handoff: dict[str, Any] | None = None,
    ) -> ExplorationAgendaItem:
        raw = self._items().get(agenda_id)
        if raw is None:
            raise KeyError(f"Exploration agenda item not found: {agenda_id}")
        if not 2 <= len(sources) <= 5:
            raise ValueError("A completed exploration must compare 2 to 5 sources")
        item = ExplorationAgendaItem(**raw)
        item.sources_seen = list(dict.fromkeys([*item.sources_seen, *sources]))
        item.what_was_learned = what_was_learned
        item.source_quality = source_quality
        item.what_changed = what_changed
        item.next_question = next_question
        item.stop_reason = stop_reason
        item.verification = verification
        item.budgets = budgets
        item.last_explored = now_ms()
        item.updated_at = item.last_explored
        item.status = "completed" if verification.get("passed") else "needs_followup"
        if next_question and next_question not in item.open_questions:
            item.open_questions.append(next_question)
        if handoff:
            item.handoffs.append(dict(handoff))
        self._items()[agenda_id] = item.to_dict()
        self._save()
        return item

    def record_attempt(
        self,
        agenda_id: str,
        *,
        sources: list[str],
        stop_reason: str,
        verification: dict[str, Any],
        budgets: dict[str, Any],
        handoff: dict[str, Any] | None = None,
    ) -> ExplorationAgendaItem:
        """Persist a bounded attempt that did not meet completion evidence."""
        raw = self._items().get(agenda_id)
        if raw is None:
            raise KeyError(f"Exploration agenda item not found: {agenda_id}")
        item = ExplorationAgendaItem(**raw)
        item.sources_seen = list(dict.fromkeys([*item.sources_seen, *sources]))
        item.stop_reason = stop_reason
        item.verification = dict(verification)
        item.budgets = dict(budgets)
        item.last_explored = now_ms()
        item.updated_at = item.last_explored
        item.status = "needs_followup"
        if handoff:
            item.handoffs.append(dict(handoff))
        self._items()[agenda_id] = item.to_dict()
        self._save()
        return item

    def list(self, status: str = "") -> list[dict[str, Any]]:
        items = list(self._items().values())
        if status:
            items = [item for item in items if item.get("status") == status]
        return sorted(items, key=lambda item: int(item.get("updated_at", 0) or 0), reverse=True)

    def diagnostics(self) -> dict[str, Any]:
        items = self.list()
        sessions = [item for item in items if item.get("last_explored")]
        return {
            "agenda_count": len(items),
            "private_sessions": len(sessions),
            "user_visible_handoffs": sum(len(item.get("handoffs", [])) for item in items),
            "current_topic": next((item.get("topic") for item in items if item.get("status") == "open"), ""),
            "sources_visited": sum(len(item.get("sources_seen", [])) for item in items),
            "recent": items[:50],
        }

    def _items(self) -> dict[str, dict[str, Any]]:
        return self._state.setdefault("items", {})

    def _save(self) -> None:
        self._state_file.save(self._state)
