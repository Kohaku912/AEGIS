"""Persona Memory — DEPRECATED.

Use ``aegis_ai.memory.person_memory.PersonMemory`` (`data/memory/persons.jsonl`)
instead. This module is retained only for reading legacy `data/persona.jsonl`
exports and must not be wired into runtime.
"""

from __future__ import annotations

import json
import logging
import os
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.memory.persona")


@dataclass
class Person:
    """A person the user knows."""
    person_id: str = ""
    name: str = ""
    relationship: str = ""  # colleague, friend, family, client, etc.
    notes: str = ""
    preferences: dict[str, Any] = field(default_factory=dict)
    topics_discussed: list[str] = field(default_factory=list)
    last_seen_ms: int = 0
    interaction_count: int = 0
    emotional_context: str = ""  # positive, neutral, negative


@dataclass
class ConversationMemory:
    """Memory of a conversation with a person."""
    conversation_id: str = ""
    person_id: str = ""
    person_name: str = ""
    summary: str = ""
    key_points: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    timestamp_ms: int = 0


class PersonaMemory:
    """Stores and retrieves information about people.

    Usage:
        mem = PersonaMemory()
        mem.add_person(Person(name="Taro", relationship="colleague"))
        mem.add_conversation(ConversationMemory(person_name="Taro", summary="Discussed project"))
        results = mem.search("Taro")
    """

    def __init__(self, path: str = "data/persona.jsonl") -> None:
        warnings.warn(
            "PersonaMemory is deprecated; use PersonMemory (data/memory/persons.jsonl).",
            DeprecationWarning,
            stacklevel=2,
        )
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._persons: dict[str, Person] = {}
        self._conversations: list[ConversationMemory] = []
        self._load()

    def _load(self) -> None:
        """Load persona data from file."""
        if not self._path.exists():
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line.strip())
                    if data.get("type") == "person":
                        p = Person(**data["data"])
                        self._persons[p.person_id] = p
                    elif data.get("type") == "conversation":
                        self._conversations.append(ConversationMemory(**data["data"]))
        except Exception as e:
            logger.warning("Failed to load persona data: %s", e)

    def _save_person(self, person: Person) -> None:
        """Save a person to file."""
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "person", "data": person.__dict__}, ensure_ascii=False) + "\n")

    def _save_conversation(self, conv: ConversationMemory) -> None:
        """Save a conversation to file."""
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "conversation", "data": conv.__dict__}, ensure_ascii=False) + "\n")

    def add_person(self, person: Person) -> None:
        """Add or update a person."""
        if not person.person_id:
            person.person_id = f"person_{int(time.time() * 1000)}"
        if not person.last_seen_ms:
            person.last_seen_ms = int(time.time() * 1000)
        self._persons[person.person_id] = person
        self._save_person(person)
        logger.info("Persona added: %s (%s)", person.name, person.relationship)

    def add_conversation(self, conv: ConversationMemory) -> None:
        """Add a conversation memory."""
        if not conv.conversation_id:
            conv.conversation_id = f"conv_{int(time.time() * 1000)}"
        if not conv.timestamp_ms:
            conv.timestamp_ms = int(time.time() * 1000)

        # Update person's interaction count
        for person in self._persons.values():
            if person.name == conv.person_name or person.person_id == conv.person_id:
                person.interaction_count += 1
                person.last_seen_ms = conv.timestamp_ms
                if conv.key_points:
                    person.topics_discussed.extend(conv.key_points)
                    person.topics_discussed = list(set(person.topics_discussed))[-20:]
                break

        self._conversations.append(conv)
        self._save_conversation(conv)
        logger.info("Conversation memory added: with %s", conv.person_name)

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search for people and conversations."""
        query_lower = query.lower()
        results = []

        # Search persons
        for person in self._persons.values():
            if (query_lower in person.name.lower() or
                query_lower in person.relationship.lower() or
                query_lower in person.notes.lower() or
                any(query_lower in t.lower() for t in person.topics_discussed)):
                results.append({"type": "person", "data": person.__dict__})

        # Search conversations
        for conv in self._conversations:
            if (query_lower in conv.person_name.lower() or
                query_lower in conv.summary.lower() or
                any(query_lower in kp.lower() for kp in conv.key_points)):
                results.append({"type": "conversation", "data": conv.__dict__})

        return results

    def get_person(self, name: str) -> Person | None:
        """Get a person by name."""
        for person in self._persons.values():
            if person.name.lower() == name.lower():
                return person
        return None

    def get_all_persons(self) -> list[Person]:
        """Get all persons."""
        return list(self._persons.values())

    def get_conversations(self, person_name: str = "") -> list[ConversationMemory]:
        """Get conversations, optionally filtered by person."""
        if person_name:
            return [c for c in self._conversations if c.person_name.lower() == person_name.lower()]
        return self._conversations
