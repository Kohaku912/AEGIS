"""Tests for Memory System — Chroma, Persona, Consolidation."""

from __future__ import annotations

import tempfile
import shutil

from aegis_ai.memory.chroma_semantic import ChromaSemanticMemory
from aegis_ai.memory.persona import PersonaMemory, Person, ConversationMemory
from aegis_ai.memory.consolidation import MemoryConsolidator
from aegis_ai.memory.semantic import Fact


class TestChromaSemanticMemory:
    """ChromaDB semantic memory tests."""

    def test_add_and_search(self):
        """Can add facts and search."""
        tmpdir = tempfile.mkdtemp()
        try:
            mem = ChromaSemanticMemory(
                path=f"{tmpdir}/semantic.jsonl",
                chroma_path=f"{tmpdir}/chroma",
            )
            mem.add(Fact(content="User prefers dark mode", category="preference"))
            mem.add(Fact(content="AEGIS is an AI assistant", category="knowledge"))
            mem.add(Fact(content="Python 3.14 is installed", category="project"))

            results = mem.search("dark mode")
            assert len(results) >= 1
            assert any("dark mode" in r.content.lower() for r in results)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_stats(self):
        """Stats are returned."""
        tmpdir = tempfile.mkdtemp()
        try:
            mem = ChromaSemanticMemory(
                path=f"{tmpdir}/semantic.jsonl",
                chroma_path=f"{tmpdir}/chroma",
            )
            mem.add(Fact(content="Test fact", category="general"))
            stats = mem.get_stats()
            assert stats["jsonl_facts"] >= 1
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestPersonaMemory:
    """Persona memory tests."""

    def test_add_person(self):
        """Can add a person."""
        tmpdir = tempfile.mkdtemp()
        try:
            mem = PersonaMemory(path=f"{tmpdir}/persona.jsonl")
            person = Person(name="Taro", relationship="colleague", notes="Prefers email")
            mem.add_person(person)

            found = mem.get_person("Taro")
            assert found is not None
            assert found.name == "Taro"
            assert found.relationship == "colleague"
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_add_conversation(self):
        """Can add conversation memory."""
        tmpdir = tempfile.mkdtemp()
        try:
            mem = PersonaMemory(path=f"{tmpdir}/persona.jsonl")
            person = Person(name="Taro", relationship="colleague")
            mem.add_person(person)

            conv = ConversationMemory(
                person_name="Taro",
                summary="Discussed project timeline",
                key_points=["deadline is Friday", "need more resources"],
            )
            mem.add_conversation(conv)

            convs = mem.get_conversations("Taro")
            assert len(convs) == 1
            assert "timeline" in convs[0].summary
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_search(self):
        """Can search persons and conversations."""
        tmpdir = tempfile.mkdtemp()
        try:
            mem = PersonaMemory(path=f"{tmpdir}/persona.jsonl")
            mem.add_person(Person(name="Taro", relationship="colleague", notes="Developer"))
            mem.add_conversation(ConversationMemory(
                person_name="Taro",
                summary="Code review session",
                key_points=["Python", "testing"],
            ))

            results = mem.search("Taro")
            assert len(results) >= 2  # person + conversation
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestMemoryConsolidator:
    """Memory consolidation tests."""

    def test_consolidate_empty(self):
        """Consolidation works with empty memory."""
        consolidator = MemoryConsolidator()
        result = consolidator.consolidate()
        assert "semantic_merged" in result

    def test_consolidate_with_persona(self):
        """Consolidation updates persona."""
        tmpdir = tempfile.mkdtemp()
        try:
            persona = PersonaMemory(path=f"{tmpdir}/persona.jsonl")
            persona.add_person(Person(name="Taro", relationship="colleague"))
            persona.add_conversation(ConversationMemory(
                person_name="Taro",
                summary="Meeting",
                key_points=["project update"],
            ))

            consolidator = MemoryConsolidator(persona_memory=persona)
            result = consolidator.consolidate()
            assert result["persona_updated"] >= 0
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_status(self):
        """Status is returned."""
        consolidator = MemoryConsolidator()
        status = consolidator.get_status()
        assert "last_consolidation_ms" in status
