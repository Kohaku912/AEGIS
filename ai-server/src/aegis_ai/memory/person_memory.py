"""Person Memory — Remembers people with authority and trust system.

Stores person-centric information with:
- Authority levels (master > admin > user > guest)
- Trust levels and relationship tracking
- Alias resolution
- Authority-based command filtering

Usage:
    pm = PersonMemory()
    pm.upsert(PersonRecord(name="Kohaku", role="master", authority_level=100))
    pm.upsert(PersonRecord(name="Guest", role="guest", authority_level=10))
    person = pm.resolve("Kohaku-san")
    if pm.has_authority(person, required_level=50):
        execute_command()
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.memory.person")

# Authority level ranges
AUTHORITY_LEVELS = {
    "master": 100,
    "admin": 80,
    "user": 50,
    "guest": 10,
    "unknown": 0,
}


@dataclass
class PersonRecord:
    """A person with authority, trust, and relationship metadata."""
    person_id: str = ""
    name: str = ""
    aliases: list[str] = field(default_factory=list)
    role: str = "user"
    authority_level: int = 50
    trust_level: float = 0.5       # 0.0 (untrusted) to 1.0 (fully trusted)
    relationship: str = ""         # "master", "colleague", "friend", "client", etc.
    notes: str = ""
    preferences: dict[str, Any] = field(default_factory=dict)
    topics: list[str] = field(default_factory=list)
    first_seen_ms: int = 0
    last_seen_ms: int = 0
    interaction_count: int = 0
    last_context: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "person_id": self.person_id,
            "name": self.name,
            "aliases": self.aliases,
            "role": self.role,
            "authority_level": self.authority_level,
            "trust_level": self.trust_level,
            "relationship": self.relationship,
            "notes": self.notes,
            "preferences": self.preferences,
            "topics": self.topics,
            "first_seen_ms": self.first_seen_ms,
            "last_seen_ms": self.last_seen_ms,
            "interaction_count": self.interaction_count,
            "last_context": self.last_context,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PersonRecord:
        return cls(
            person_id=data.get("person_id", ""),
            name=data.get("name", ""),
            aliases=data.get("aliases", []),
            role=data.get("role", "user"),
            authority_level=int(data.get("authority_level", 50)),
            trust_level=float(data.get("trust_level", 0.5)),
            relationship=data.get("relationship", ""),
            notes=data.get("notes", ""),
            preferences=data.get("preferences", {}),
            topics=data.get("topics", []),
            first_seen_ms=int(data.get("first_seen_ms", 0)),
            last_seen_ms=int(data.get("last_seen_ms", 0)),
            interaction_count=int(data.get("interaction_count", 0)),
            last_context=data.get("last_context", ""),
            tags=data.get("tags", []),
        )


class PersonMemory:
    """Person-centric memory with authority-based access control.

    Features:
    - Resolve names and aliases to canonical person records
    - Authority-based command filtering (master > admin > user > guest)
    - Trust level tracking
    - Relationship and preference tracking

    Usage:
        pm = PersonMemory()
        pm.upsert(PersonRecord(name="Kohaku", role="master", authority_level=100))
        person = pm.resolve("Kohaku-san")
        if pm.has_authority(person, required_level=50):
            execute()
    """

    def __init__(self, path: str = "data/memory/persons.jsonl") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._persons: dict[str, PersonRecord] = {}
        self._alias_map: dict[str, str] = {}  # alias/name → person_id
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            for line in self._path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    data = json.loads(line)
                    if data.get("type") == "person":
                        person = PersonRecord.from_dict(data["data"])
                        self._persons[person.person_id] = person
                        self._rebuild_aliases(person)
            logger.info("Loaded %d persons", len(self._persons))
        except Exception as e:
            logger.warning("Failed to load persons: %s", e)

    def _rebuild_aliases(self, person: PersonRecord) -> None:
        """Register name and aliases in lookup map."""
        key = person.name.lower().strip()
        if key:
            self._alias_map[key] = person.person_id
        for alias in person.aliases:
            akey = alias.lower().strip()
            if akey:
                self._alias_map[akey] = person.person_id

    def _persist(self, person: PersonRecord) -> None:
        record = {"type": "person", "data": person.to_dict(), "timestamp_ms": int(time.time() * 1000)}
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def upsert(self, person: PersonRecord) -> PersonRecord:
        """Add or update a person. Returns the saved record."""
        now_ms = int(time.time() * 1000)

        # Check if person exists by name or alias
        existing = self.resolve(person.name)
        if existing:
            # Merge into existing
            existing.aliases = list(set(existing.aliases + person.aliases))
            if person.role and person.role != "user":
                existing.role = person.role
            if person.authority_level != 50:
                existing.authority_level = person.authority_level
            if person.trust_level != 0.5:
                existing.trust_level = person.trust_level
            if person.relationship:
                existing.relationship = person.relationship
            if person.notes:
                existing.notes = (existing.notes + "\n" + person.notes).strip()[-500:]
            if person.preferences:
                existing.preferences.update(person.preferences)
            if person.topics:
                existing.topics = list(set(existing.topics + person.topics))[-30:]
            if person.tags:
                existing.tags = list(set(existing.tags + person.tags))
            existing.last_seen_ms = now_ms
            existing.last_context = person.last_context or existing.last_context
            self._rebuild_aliases(existing)
            self._persist(existing)
            logger.info("Updated person: %s (role=%s, authority=%d)", existing.name, existing.role, existing.authority_level)
            return existing

        # New person
        if not person.person_id:
            person.person_id = f"person_{os.urandom(6).hex()}"
        if not person.first_seen_ms:
            person.first_seen_ms = now_ms
        if not person.last_seen_ms:
            person.last_seen_ms = now_ms
        if person.role in AUTHORITY_LEVELS and person.authority_level == 50:
            person.authority_level = AUTHORITY_LEVELS[person.role]

        self._persons[person.person_id] = person
        self._rebuild_aliases(person)
        self._persist(person)
        logger.info("Added person: %s (role=%s, authority=%d)", person.name, person.role, person.authority_level)
        return person

    def resolve(self, name_or_alias: str) -> PersonRecord | None:
        """Resolve a name or alias to a person record."""
        if not name_or_alias:
            return None
        key = name_or_alias.lower().strip()
        # Exact match
        pid = self._alias_map.get(key)
        if pid:
            return self._persons.get(pid)
        # Fuzzy match
        for person in self._persons.values():
            if key in person.name.lower() or person.name.lower() in key:
                return person
            for alias in person.aliases:
                if key in alias.lower() or alias.lower() in key:
                    return person
        return None

    def list_all(self) -> list[PersonRecord]:
        """Return all known relationships for shared decision context."""
        return list(self._persons.values())

    def has_authority(self, person: PersonRecord | None, required_level: int) -> bool:
        """Check if a person has sufficient authority level."""
        if person is None:
            return False
        return person.authority_level >= required_level

    def is_master(self, person: PersonRecord | None) -> bool:
        """Check if a person is the master."""
        if person is None:
            return False
        return person.role == "master" or person.authority_level >= 100

    def get_master(self) -> PersonRecord | None:
        """Get the master person record."""
        for person in self._persons.values():
            if person.role == "master":
                return person
        return None

    def record_interaction(self, person_id: str, context: str = "") -> None:
        """Record an interaction with a person."""
        person = self._persons.get(person_id)
        if person:
            person.interaction_count += 1
            person.last_seen_ms = int(time.time() * 1000)
            if context:
                person.last_context = context[:200]
            self._persist(person)

    def update_trust(self, person_id: str, delta: float, reason: str = "") -> None:
        """Update trust level for a person."""
        person = self._persons.get(person_id)
        if person:
            person.trust_level = max(0.0, min(1.0, person.trust_level + delta))
            if reason:
                person.notes = (person.notes + f"\n[trust {delta:+.2f}] {reason}").strip()[-500:]
            self._persist(person)

    def search(self, query: str) -> list[PersonRecord]:
        """Search persons by name, notes, topics, tags."""
        q = query.lower()
        results = []
        for person in self._persons.values():
            searchable = f"{person.name} {person.notes} {' '.join(person.topics)} {' '.join(person.tags)} {person.relationship}".lower()
            if q in searchable:
                results.append(person)
        return results

    def get_all(self) -> list[PersonRecord]:
        return list(self._persons.values())

    def get_context_string(self, max_chars: int = 500) -> str:
        """Get person context for LLM prompts."""
        lines = ["Known people:"]
        for p in sorted(self._persons.values(), key=lambda x: x.authority_level, reverse=True):
            role_tag = f"[{p.role}]" if p.role != "user" else ""
            trust_tag = f"trust={p.trust_level:.1f}"
            lines.append(f"  - {p.name} {role_tag} ({p.relationship}, {trust_tag}): {p.notes[:60]}")
        result = "\n".join(lines)
        return result[:max_chars]

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_persons": len(self._persons),
            "masters": sum(1 for p in self._persons.values() if p.role == "master"),
            "admins": sum(1 for p in self._persons.values() if p.role == "admin"),
            "users": sum(1 for p in self._persons.values() if p.role == "user"),
        }
