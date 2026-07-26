"""Advanced Memory System — Zep-inspired human-like memory.

Features:
- Entity Memory: Tracks people, places, things with relationships
- Fact Extraction: Automatically extracts facts from conversations
- Temporal Awareness: Tracks when facts were valid/invalid
- Graph Relationships: Links between entities
- Importance Scoring: More important memories are recalled more easily
- Consolidation: Periodic memory cleanup and summarization

Usage:
    memory = AdvancedMemory(llm_provider=llm)
    memory.add_conversation(user_msg, bot_response)
    context = memory.get_context("What do you know about Taro?")
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aegis_ai.llm.json_utils import extract_json_object

logger = logging.getLogger("aegis_ai.memory.advanced")


@dataclass
class Entity:
    """A tracked entity (person, place, thing)."""
    entity_id: str = ""
    name: str = ""
    entity_type: str = "person"  # person, place, thing, concept
    attributes: dict[str, Any] = field(default_factory=dict)
    relationships: list[dict[str, str]] = field(default_factory=list)  # [{type, target_id}]
    first_seen_ms: int = 0
    last_seen_ms: int = 0
    mention_count: int = 0
    importance: float = 0.5  # 0.0 = low, 1.0 = high


@dataclass
class Fact:
    """A fact extracted from conversation."""
    fact_id: str = ""
    content: str = ""
    subject: str = ""  # Entity name or "user"
    predicate: str = ""  # Relationship type
    object: str = ""  # Value or entity name
    source: str = "conversation"
    valid_at_ms: int = 0  # When fact became true
    invalid_at_ms: int = 0  # When fact became false (0 = still valid)
    confidence: float = 1.0
    importance: float = 0.5


@dataclass
class ConversationEntry:
    """A conversation entry."""
    entry_id: str = ""
    user_msg: str = ""
    bot_msg: str = ""
    timestamp_ms: int = 0
    entities_mentioned: list[str] = field(default_factory=list)
    facts_extracted: list[str] = field(default_factory=list)


class AdvancedMemory:
    """Zep-inspired advanced memory system.

    Combines:
    - Entity tracking (people, places, things)
    - Fact extraction from conversations
    - Temporal awareness
    - Importance scoring
    - ChromaDB vector search for semantic retrieval
    """

    def __init__(
        self,
        data_dir: str = "data/memory",
        llm_provider: Any = None,
    ) -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._llm = llm_provider

        self._entities: dict[str, Entity] = {}
        self._facts: dict[str, Fact] = {}
        self._conversations: list[ConversationEntry] = []

        self._load()

    def _load(self) -> None:
        """Load memory from disk."""
        # Load entities
        entities_path = self._data_dir / "entities.jsonl"
        if entities_path.exists():
            with open(entities_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        e = Entity(**data)
                        self._entities[e.entity_id] = e
                    except Exception:
                        pass

        # Load facts
        facts_path = self._data_dir / "facts.jsonl"
        if facts_path.exists():
            with open(facts_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        fact = Fact(**data)
                        self._facts[fact.fact_id] = fact
                    except Exception:
                        pass

        # Load conversations
        conv_path = self._data_dir / "conversations.jsonl"
        if conv_path.exists():
            with open(conv_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        self._conversations.append(ConversationEntry(**data))
                    except Exception:
                        pass

    def _save_entity(self, entity: Entity) -> None:
        """Save entity to disk."""
        path = self._data_dir / "entities.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entity.__dict__, ensure_ascii=False) + "\n")

    def _save_fact(self, fact: Fact) -> None:
        """Save fact to disk."""
        path = self._data_dir / "facts.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(fact.__dict__, ensure_ascii=False) + "\n")

    def _save_conversation(self, entry: ConversationEntry) -> None:
        """Save conversation to disk."""
        path = self._data_dir / "conversations.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry.__dict__, ensure_ascii=False) + "\n")

    def add_conversation(self, user_msg: str, bot_msg: str) -> None:
        """Process a conversation and extract entities/facts."""
        now = int(time.time() * 1000)

        # Use LLM to extract entities and facts
        if self._llm:
            try:
                extraction = self._extract_with_llm(user_msg, bot_msg)
                entities = extraction.get("entities", [])
                facts = extraction.get("facts", [])
            except Exception as e:
                logger.warning("LLM extraction failed: %s", e)
                entities = []
                facts = []
        else:
            entities = []
            facts = []

        # Save entities
        entity_ids = []
        for e_data in entities:
            name = e_data.get("name", "")
            if not name:
                continue
            
            aliases = e_data.get("aliases", [])
            existing_entity = None
            
            for alias in [name] + aliases:
                for eid, ent in self._entities.items():
                    if ent.name.lower() == alias.lower():
                        existing_entity = ent
                        break
                if existing_entity:
                    break
            
            if existing_entity:
                entity = existing_entity
                if name.lower() != entity.name.lower():
                    for alias in aliases:
                        if alias.lower() not in [a.lower() for a in entity.attributes.get("aliases", [])]:
                            entity.attributes.setdefault("aliases", []).append(alias)
            else:
                entity = self._get_or_create_entity(name, e_data.get("type", "person"))
                if aliases:
                    entity.attributes["aliases"] = aliases
            
            entity.mention_count += 1
            entity.last_seen_ms = now
            if e_data.get("attributes"):
                entity.attributes.update(e_data["attributes"])
            entity_ids.append(entity.entity_id)
            self._save_entity(entity)

        # Save facts
        fact_ids = []
        for f_data in facts:
            content = f_data.get("content", "")
            if not content:
                continue
            fact = Fact(
                fact_id=f"fact_{now}_{len(self._facts)}",
                content=content,
                subject=f_data.get("subject", "user"),
                predicate=f_data.get("predicate", "is"),
                object=f_data.get("object", ""),
                valid_at_ms=now,
                confidence=f_data.get("confidence", 0.8),
                importance=f_data.get("importance", 0.5),
            )
            self._facts[fact.fact_id] = fact
            fact_ids.append(fact.fact_id)
            self._save_fact(fact)

        # Save conversation
        entry = ConversationEntry(
            entry_id=f"conv_{now}",
            user_msg=user_msg[:500],
            bot_msg=bot_msg[:500],
            timestamp_ms=now,
            entities_mentioned=entity_ids,
            facts_extracted=fact_ids,
        )
        self._conversations.append(entry)
        self._save_conversation(entry)

        logger.info("Processed conversation: %d entities, %d facts", len(entity_ids), len(fact_ids))

    def _get_or_create_entity(self, name: str, entity_type: str = "person") -> Entity:
        """Get existing entity or create new one."""
        # Check for existing entity by name
        for entity in self._entities.values():
            if entity.name.lower() == name.lower():
                return entity

        # Create new
        entity = Entity(
            entity_id=f"entity_{int(time.time() * 1000)}_{len(self._entities)}",
            name=name,
            entity_type=entity_type,
            first_seen_ms=int(time.time() * 1000),
            last_seen_ms=int(time.time() * 1000),
        )
        self._entities[entity.entity_id] = entity
        return entity

    def _extract_with_llm(self, user_msg: str, bot_msg: str) -> dict[str, Any]:
        """Use LLM to extract entities and facts from conversation."""
        prompt = f"""Analyze this conversation and extract entities and facts.

User: {user_msg}
AEGIS: {bot_msg}

Respond with JSON:
{{
  "entities": [
    {{"name": "...", "type": "person|place|thing|concept", "attributes": {{"key": "value"}}, "aliases": ["alias1", "alias2"]}}
  ],
  "facts": [
    {{"content": "...", "subject": "...", "predicate": "...", "object": "...", "confidence": 0.9, "importance": 0.5}}
  ]
}}

Extract:
- People mentioned (name, relationship, preferences)
- If someone says "call me X" or "my name is X, Y", X is an ALIAS for the same person, NOT a separate entity
- Places mentioned
- Important facts, preferences, decisions
- Action items or commitments

IMPORTANT RULES:
- If a user introduces themselves with a name AND a nickname/title (e.g., "I'm たつき, call me Master"), create ONE entity with the name as primary and the nickname as an alias
- Do NOT create separate entities for the same person's name and nickname
- "Master", "Sir", "Boss" etc. are titles/aliases, not separate people

Only extract meaningful information. If nothing noteworthy, return empty arrays."""

        result = self._llm.generate(
            prompt=prompt,
            system_prompt="You are a memory extraction system. Extract entities and facts from conversations. Output only JSON.",
            max_tokens=1000,
            json_mode=True,
        )

        if not result.success:
            return {"entities": [], "facts": []}

        try:
            return extract_json_object(result.content)
        except Exception:
            return {"entities": [], "facts": []}

    def get_context(self, query: str, max_tokens: int = 2000) -> str:
        """Get relevant memory context for a query."""
        parts = []

        # Get relevant entities
        entities = self._search_entities(query)
        if entities:
            parts.append("People and entities I know:")
            for e in entities[:5]:
                attrs = ", ".join(f"{k}: {v}" for k, v in e.attributes.items() if v)
                rels = ", ".join(r.get("type", "") + " " + r.get("target", "") for r in e.relationships if r)
                desc = f"  - {e.name} ({e.entity_type})"
                if attrs:
                    desc += f" [{attrs}]"
                if rels:
                    desc += f" relationships: {rels}"
                parts.append(desc)

        # Get relevant facts
        facts = self._search_facts(query)
        if facts:
            parts.append("\nThings I know:")
            for f in facts[:10]:
                if f.invalid_at_ms == 0:  # Only valid facts
                    parts.append(f"  - {f.content}")

        # Get recent conversations mentioning query
        recent = self._search_conversations(query)
        if recent:
            parts.append("\nRecent conversations:")
            for c in recent[:3]:
                parts.append(f"  User: {c.user_msg[:100]}")
                parts.append(f"  AEGIS: {c.bot_msg[:100]}")

        return "\n".join(parts) if parts else ""

    def _search_entities(self, query: str) -> list[Entity]:
        """Search entities by name or attributes."""
        query_lower = query.lower()
        results = []
        for entity in self._entities.values():
            if (query_lower in entity.name.lower() or
                any(query_lower in str(v).lower() for v in entity.attributes.values())):
                results.append(entity)
        return sorted(results, key=lambda e: e.importance, reverse=True)

    def _search_facts(self, query: str) -> list[Fact]:
        """Search facts by content."""
        query_lower = query.lower()
        results = []
        for fact in self._facts.values():
            if query_lower in fact.content.lower() or query_lower in fact.subject.lower():
                results.append(fact)
        return sorted(results, key=lambda f: f.importance, reverse=True)

    def _search_conversations(self, query: str) -> list[ConversationEntry]:
        """Search conversations by content."""
        query_lower = query.lower()
        results = []
        for conv in self._conversations:
            if query_lower in conv.user_msg.lower() or query_lower in conv.bot_msg.lower():
                results.append(conv)
        return results[-5:]  # Most recent

    def get_all_entities(self) -> list[Entity]:
        """Get all tracked entities."""
        return list(self._entities.values())

    def get_all_facts(self) -> list[Fact]:
        """Get all facts."""
        return list(self._facts.values())

    def get_recent_conversations(self, limit: int = 10) -> list[ConversationEntry]:
        """Return recent conversations without interpreting user text in code."""
        return list(self._conversations[-limit:])

    def delete_entity(self, name: str) -> bool:
        """Delete an entity by name."""
        for eid, entity in list(self._entities.items()):
            if entity.name.lower() == name.lower():
                del self._entities[eid]
                self._rewrite_entities_file()
                return True
        return False

    def delete_fact(self, content_substring: str) -> int:
        """Delete facts matching content."""
        to_delete = [fid for fid, f in self._facts.items() if content_substring.lower() in f.content.lower()]
        for fid in to_delete:
            del self._facts[fid]
        if to_delete:
            self._rewrite_facts_file()
        return len(to_delete)

    def clear_all(self) -> None:
        """Clear all memory."""
        self._entities.clear()
        self._facts.clear()
        self._conversations.clear()
        for f in self._data_dir.glob("*.jsonl"):
            f.unlink()

    def _rewrite_entities_file(self) -> None:
        """Rewrite entities file from memory."""
        path = self._data_dir / "entities.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for entity in self._entities.values():
                f.write(json.dumps(entity.__dict__, ensure_ascii=False) + "\n")

    def _rewrite_facts_file(self) -> None:
        """Rewrite facts file from memory."""
        path = self._data_dir / "facts.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for fact in self._facts.values():
                f.write(json.dumps(fact.__dict__, ensure_ascii=False) + "\n")

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        return {
            "entities": len(self._entities),
            "facts": len(self._facts),
            "conversations": len(self._conversations),
            "valid_facts": sum(1 for f in self._facts.values() if f.invalid_at_ms == 0),
        }
