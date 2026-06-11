"""Tests for ContextBuilder and Memory systems."""

from __future__ import annotations

import pytest

from aegis_ai.context_builder import Context, ContextBuilder, MAX_TOTAL_CHARS
from aegis_ai.memory.episodic import EpisodicMemory, Episode
from aegis_ai.memory.procedural import ProceduralMemory, Procedure
from aegis_ai.memory.reflection import ReflectionLog, Reflection
from aegis_ai.memory.semantic import Fact, SemanticMemory
from aegis_schema.models import Event, EventPriority, ServerType


def _make_event(event_id: str = "evt-001", event_type: str = "pc.screen_changed",
                server_type: ServerType = ServerType.PC, severity: int = 3) -> Event:
    return Event(event_id=event_id, event_type=event_type,
                 source_server_type=server_type, source_server_id="test",
                 severity=severity, priority=EventPriority.NORMAL)


# ═══════════════════════════════════════════════════════════════
# ContextBuilder Tests
# ═══════════════════════════════════════════════════════════════

class TestContextBuilder:
    def test_build_basic_context(self):
        builder = ContextBuilder(identity="AEGIS Test")
        ctx = builder.build()
        assert ctx.identity == "AEGIS Test"
        assert ctx.context_id.startswith("ctx_")
        assert ctx.built_at_ms > 0

    def test_build_with_triggering_events(self):
        builder = ContextBuilder()
        events = [_make_event("evt-1"), _make_event("evt-2", event_type="dev.test_failed")]
        ctx = builder.build(triggering_events=events)
        assert len(ctx.recent_events) >= 2

    def test_build_with_goals(self):
        builder = ContextBuilder()
        builder.set_goals(["Help user", "Learn", "Stay safe"])
        ctx = builder.build()
        assert "Help user" in ctx.current_goals

    def test_build_with_memories(self):
        episodic = EpisodicMemory(path="data/test_episodic_cb.jsonl")
        episodic.add(Episode(summary="User asked about weather", category="conversation"))
        episodic.add(Episode(summary="Checked temperature via room server", category="action_result"))

        semantic = SemanticMemory(path="data/test_semantic_cb.jsonl")
        semantic.add(Fact(content="User lives in Tokyo", category="user_info", source="user"))
        semantic.add(Fact(content="Weather forecast shows rain tomorrow", category="knowledge", source="inference"))

        builder = ContextBuilder(episodic_memory=episodic, semantic_memory=semantic)
        ctx = builder.build(triggering_query="weather")
        assert len(ctx.recent_episodes) > 0
        assert any("rain" in f for f in ctx.relevant_facts)

    def test_context_size_limit(self):
        """Context should be truncated if it exceeds the character budget."""
        episodic = EpisodicMemory(path="data/test_episodic_size.jsonl")
        for i in range(100):
            episodic.add(Episode(summary=f"Episode {i}: " + "x" * 200, category="general"))

        builder = ContextBuilder(episodic_memory=episodic)
        ctx = builder.build()
        assert ctx.total_chars > 0
        if ctx.truncated:
            assert len(ctx.recent_events) <= 3 or len(ctx.relevant_facts) <= 1

    def test_last_context(self):
        builder = ContextBuilder()
        ctx1 = builder.build()
        assert builder.last_context is ctx1

    def test_empty_builder_works(self):
        builder = ContextBuilder()
        ctx = builder.build()
        assert ctx.identity == "AEGIS — autonomous multi-device AI assistant"


# ═══════════════════════════════════════════════════════════════
# Memory System Tests
# ═══════════════════════════════════════════════════════════════

class TestEpisodicMemory:
    def test_add_and_list(self):
        mem = EpisodicMemory(path="data/test_ep.jsonl")
        mem.add(Episode(summary="Hello", category="conversation"))
        mem.add(Episode(summary="World", category="action_result"))
        recent = mem.list_recent(10)
        assert len(recent) == 2

    def test_filter_by_category(self):
        mem = EpisodicMemory(path="data/test_ep_cat.jsonl")
        mem.add(Episode(summary="Chat 1", category="conversation"))
        mem.add(Episode(summary="Event 1", category="event"))
        convs = mem.list_recent(10, category="conversation")
        assert len(convs) == 1
        assert convs[0].summary == "Chat 1"

    def test_search(self):
        mem = EpisodicMemory(path="data/test_ep_search.jsonl")
        mem.add(Episode(summary="User asked about weather", category="conversation",
                       detail={"topic": "weather"}))
        mem.add(Episode(summary="Checked file status", category="action_result"))
        results = mem.search("weather")
        assert len(results) == 1

    def test_timestamp_auto_set(self):
        mem = EpisodicMemory(path="data/test_ep_ts.jsonl")
        ep = Episode(summary="Test")
        mem.add(ep)
        assert ep.timestamp_ms > 0
        assert ep.episode_id != ""


class TestSemanticMemory:
    def test_add_and_search(self):
        mem = SemanticMemory(path="data/test_sem.jsonl")
        mem.add(Fact(content="User prefers dark mode", category="preference", source="user"))
        mem.add(Fact(content="Project uses Python 3.12", category="design", source="inference"))
        results = mem.search("dark mode")
        assert len(results) == 1

    def test_filter_by_category(self):
        mem = SemanticMemory(path="data/test_sem_cat.jsonl")
        mem.add(Fact(content="User is in Tokyo", category="user_info", source="user"))
        mem.add(Fact(content="Architecture uses gRPC", category="design", source="docs"))
        facts = mem.list_by_category("user_info")
        assert len(facts) == 1

    def test_source_field(self):
        mem = SemanticMemory(path="data/test_sem_src.jsonl")
        mem.add(Fact(content="Test", source="user", tags=["important"]))
        results = mem.search("Test")
        assert results[0].source == "user"


class TestProceduralMemory:
    def test_add_and_find(self):
        mem = ProceduralMemory(path="data/test_proc.jsonl")
        mem.add(Procedure(goal="Check weather", steps=["browser.open_page", "browser.extract_page_text"],
                         tags=["successful"], success_count=3))
        results = mem.find_for_goal("weather")
        assert len(results) == 1

    def test_confidence_calculation(self):
        mem = ProceduralMemory(path="data/test_proc_conf.jsonl")
        proc = Procedure(goal="Test", steps=["pc.screenshot"], success_count=7, failure_count=3)
        mem.add(proc)  # triggers confidence calculation via add()
        assert proc.total_attempts == 10
        assert proc.success_rate == 0.7
        assert proc.confidence == 0.7

    def test_successful_and_failure_patterns(self):
        mem = ProceduralMemory(path="data/test_proc_split.jsonl")
        mem.add(Procedure(goal="Good pattern", steps=["a"], success_count=5, tags=["successful"]))
        mem.add(Procedure(goal="Bad pattern", steps=["b"], failure_count=3, tags=["failed"]))
        assert len(mem.get_successful()) == 1
        assert len(mem.get_failure_patterns()) == 1

    def test_tool_tips(self):
        mem = ProceduralMemory(path="data/test_proc_tips.jsonl")
        mem.add(Procedure(goal="Tip: use selector", steps=["browser.extract_page_text"],
                         tags=["tool_tip"], success_count=10))
        tips = mem.get_tool_tips()
        assert len(tips) == 1


class TestReflectionLog:
    def test_add_and_list(self):
        log = ReflectionLog(path="data/test_refl.jsonl")
        log.add(Reflection(summary="Screenshot worked well", what_worked=["fast response"],
                          what_failed=["blurry image"], improvement_ideas=["increase quality"],
                          linked_event_ids=["evt-001"]))
        recent = log.list_recent(10)
        assert len(recent) == 1

    def test_improvement_ideas(self):
        log = ReflectionLog(path="data/test_refl_ideas.jsonl")
        log.add(Reflection(summary="Test 1", improvement_ideas=["Use faster selector"]))
        log.add(Reflection(summary="Test 2", improvement_ideas=["Cache results"]))
        ideas = log.get_improvement_ideas()
        assert len(ideas) == 2

    def test_find_by_event(self):
        log = ReflectionLog(path="data/test_refl_event.jsonl")
        log.add(Reflection(summary="Event reflection", linked_event_ids=["evt-abc"]))
        log.add(Reflection(summary="Other", linked_event_ids=["evt-xyz"]))
        results = log.find_by_event("evt-abc")
        assert len(results) == 1
