"""Tests for Memory Store, Memory Types, and Reflection Engine."""

from __future__ import annotations

import shutil
import tempfile
import time

import pytest

from aegis_ai.memory.memory_types import (
    FailureType,
    MemoryRecord,
    MemorySource,
    MemoryType,
    ReflectionResult,
    Sensitivity,
    Visibility,
    _mask_sensitive,
    _score_for_context,
)
from aegis_ai.memory.memory_store import MemoryStore
from aegis_ai.reflection.reflection_engine import ReflectionEngine


@pytest.fixture()
def tmpdir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture()
def store(tmpdir):
    return MemoryStore(data_dir=tmpdir)


@pytest.fixture()
def engine(store):
    return ReflectionEngine(memory_store=store)


class TestMemoryRecord:
    def test_create_record(self):
        r = MemoryRecord(memory_type=MemoryType.EPISODIC.value, title="test", content="hello")
        assert r.memory_type == "episodic"
        assert not r.is_expired()

    def test_expired(self):
        r = MemoryRecord(expires_at=int(time.time() * 1000) - 1000)
        assert r.is_expired()

    def test_to_context_string(self):
        r = MemoryRecord(memory_type="episodic", title="Task 1", content="Did something")
        s = r.to_context_string()
        assert "episodic" in s
        assert "Task 1" in s

    def test_to_dict(self):
        r = MemoryRecord(memory_id="m1", title="test")
        d = r.to_dict()
        assert d["memory_id"] == "m1"

    def test_mask_sensitive_content(self):
        r = MemoryRecord(title="api_key test", content="my secret api_key=sk-abc123def456ghi789jkl0")
        assert "sk-***" in r.content or "***MASKED***" in r.content


class TestMasking:
    def test_mask_key(self):
        assert _mask_sensitive("secret", "api_key") == "***MASKED***"

    def test_mask_bearer(self):
        assert "Bearer ***" in _mask_sensitive("Bearer abc123token")

    def test_mask_sk(self):
        result = _mask_sensitive("key is sk-abcdefghijklmnopqrstu")
        assert "sk-***" in result


class TestScoreForContext:
    def test_high_importance_high_score(self):
        r = MemoryRecord(importance=1.0, confidence=1.0, created_at=int(time.time() * 1000))
        assert _score_for_context(r) > 0.8

    def test_low_importance_low_score(self):
        r = MemoryRecord(importance=0.1, confidence=0.1, created_at=int(time.time() * 1000) - 7 * 24 * 3600 * 1000)
        assert _score_for_context(r) < 0.3


class TestMemoryStore:
    def test_add_and_get(self, store):
        r = MemoryRecord(memory_type="episodic", title="t", content="c")
        added = store.add_memory(r)
        assert added.memory_id
        assert store.get_memory(added.memory_id).title == "t"

    def test_search_by_type(self, store):
        store.add_memory(MemoryRecord(memory_type="episodic", title="ep", content="c"))
        store.add_memory(MemoryRecord(memory_type="failure_lesson", title="fl", content="c"))
        results = store.search_memories(memory_type="episodic")
        assert len(results) == 1
        assert results[0].memory_type == "episodic"

    def test_search_by_desire(self, store):
        store.add_memory(MemoryRecord(related_desire="curiosity", title="t", content="c"))
        store.add_memory(MemoryRecord(related_desire="autonomy", title="t2", content="c"))
        results = store.search_memories(related_desire="curiosity")
        assert len(results) == 1

    def test_list_recent(self, store):
        for i in range(5):
            store.add_memory(MemoryRecord(memory_type="episodic", title=f"t{i}", content="c"))
        recent = store.list_recent(limit=3)
        assert len(recent) == 3

    def test_list_by_task(self, store):
        store.add_memory(MemoryRecord(related_task_id="t1", title="a", content="c"))
        store.add_memory(MemoryRecord(related_task_id="t2", title="b", content="c"))
        assert len(store.list_by_task("t1")) == 1

    def test_list_by_desire(self, store):
        store.add_memory(MemoryRecord(related_desire="curiosity", title="a", content="c"))
        assert len(store.list_by_desire("curiosity")) == 1

    def test_update_memory(self, store):
        r = store.add_memory(MemoryRecord(title="old", content="c"))
        updated = store.update_memory(r.memory_id, {"title": "new"})
        assert updated.title == "new"

    def test_mark_superseded(self, store):
        old = store.add_memory(MemoryRecord(title="old", content="c"))
        new = store.add_memory(MemoryRecord(title="new", content="c"))
        assert store.mark_superseded(old.memory_id, new.memory_id)
        assert store.get_memory(old.memory_id).superseded_by == new.memory_id

    def test_superseded_excluded_from_search(self, store):
        old = store.add_memory(MemoryRecord(title="old", content="c"))
        new = store.add_memory(MemoryRecord(title="new", content="c"))
        store.mark_superseded(old.memory_id, new.memory_id)
        results = store.search_memories()
        ids = [r.memory_id for r in results]
        assert old.memory_id not in ids

    def test_forget_memory(self, store):
        r = store.add_memory(MemoryRecord(title="t", content="c"))
        assert store.forget_memory(r.memory_id)
        assert store.get_memory(r.memory_id) is None

    def test_prune_expired(self, store):
        r = store.add_memory(MemoryRecord(title="t", content="c", expires_at=int(time.time() * 1000) - 1000))
        count = store.prune_expired()
        assert count == 1
        assert store.get_memory(r.memory_id) is None

    def test_summarize_for_context(self, store):
        store.add_memory(MemoryRecord(memory_type="episodic", title="t1", content="hello world"))
        summary = store.summarize_for_context(memory_type="episodic")
        assert "t1" in summary or "hello" in summary

    def test_hidden_excluded_from_context(self, store):
        store.add_memory(MemoryRecord(title="secret", content="hidden", visibility=Visibility.HIDDEN.value))
        summary = store.summarize_for_context()
        assert "hidden" not in summary

    def test_secret_excluded_from_context(self, store):
        store.add_memory(MemoryRecord(title="key", content="password123", sensitivity=Sensitivity.SECRET.value))
        summary = store.summarize_for_context()
        assert "password123" not in summary

    def test_persistence(self, tmpdir):
        s1 = MemoryStore(data_dir=tmpdir)
        s1.add_memory(MemoryRecord(title="persist", content="me"))
        s2 = MemoryStore(data_dir=tmpdir)
        assert s2.count() == 1

    def test_count(self, store):
        assert store.count() == 0
        store.add_memory(MemoryRecord(title="t", content="c"))
        assert store.count() == 1

    def test_merge_similar_lessons(self, store):
        store.add_memory(MemoryRecord(memory_type="failure_lesson", title="Same Title", content="c1"))
        store.add_memory(MemoryRecord(memory_type="failure_lesson", title="Same Title", content="c2"))
        merged = store.merge_similar_lessons("failure_lesson")
        assert len(merged) == 1

    def test_confidence_filter(self, store):
        store.add_memory(MemoryRecord(title="high", content="c", confidence=0.9))
        store.add_memory(MemoryRecord(title="low", content="c", confidence=0.1))
        results = store.search_memories(min_confidence=0.5)
        assert len(results) == 1


class TestReflectionEngine:
    def test_success_reflection(self, engine, store):
        result = engine.reflect(
            task_id="t1",
            task_description="Click button",
            tool_results=[{"status": "success", "capability_id": "pc.click"}],
            verification_results=[{"status": "verified"}],
        )
        assert result.outcome == "success"
        assert result.task_id == "t1"
        assert not result.should_retry

    def test_failure_reflection(self, engine, store):
        result = engine.reflect(
            task_id="t2",
            task_description="Send message",
            tool_results=[{"status": "failed", "error": "timeout", "capability_id": "browser.click"}],
        )
        assert result.outcome == "failure"
        assert result.should_retry
        assert len(result.lessons) > 0

    def test_denied_reflection(self, engine, store):
        result = engine.reflect(
            task_id="t3",
            task_description="Delete file",
            tool_results=[{"status": "denied", "error": "Policy denied"}],
        )
        assert result.outcome == "denied"
        assert not result.should_retry

    def test_rejected_reflection(self, engine, store):
        result = engine.reflect(
            task_id="t4",
            task_description="Post to SNS",
            approval_decisions=[{"status": "rejected", "reason": "too risky", "approval_id": "a1"}],
        )
        assert result.outcome == "rejected"
        assert not result.should_retry

    def test_memory_records_created(self, engine, store):
        engine.reflect(
            task_id="t5",
            task_description="Click",
            tool_results=[{"status": "success", "capability_id": "pc.click"}],
        )
        assert store.count() >= 1

    def test_failure_lesson_created(self, engine, store):
        engine.reflect(
            task_id="t6",
            task_description="Fail",
            tool_results=[{"status": "failed", "error": "timeout"}],
        )
        lessons = store.search_memories(memory_type="failure_lesson")
        assert len(lessons) >= 1

    def test_approval_lesson_created(self, engine, store):
        engine.reflect(
            task_id="t7",
            task_description="Post",
            approval_decisions=[{"status": "rejected", "reason": "no", "approval_id": "a1", "capability_id": "browser.post"}],
        )
        lessons = store.search_memories(memory_type="approval_lesson")
        assert len(lessons) >= 1

    def test_desire_lesson_created(self, engine, store):
        engine.reflect(
            task_id="t8",
            task_description="Learn",
            tool_results=[{"status": "success"}],
            source_desire="curiosity",
            frustration=7.0,
            desire_before={"curiosity": 3.0},
            desire_after={"curiosity": 6.0},
        )
        lessons = store.search_memories(memory_type="desire_lesson")
        assert len(lessons) >= 1

    def test_failure_type_classification(self, engine):
        result = engine.reflect(
            task_id="t9",
            task_description="Auth",
            tool_results=[{"status": "failed", "error": "authentication required"}],
        )
        assert any("authentication" in h.lower() for h in result.planner_hints)

    def test_no_memory_store(self):
        engine = ReflectionEngine(memory_store=None)
        result = engine.reflect(task_id="t10", tool_results=[{"status": "success"}])
        assert result.outcome == "success"

    def test_desire_update_hints_on_success(self, engine):
        result = engine.reflect(
            task_id="t11",
            tool_results=[{"status": "success"}],
            source_desire="curiosity",
        )
        assert "curiosity" in result.desire_update_hints
        assert result.desire_update_hints["curiosity"] > 0

    def test_suppress_repeated_loop(self, engine):
        result = engine.reflect(
            task_id="t12",
            tool_results=[{"status": "failed", "error": "repeated loop detected"}],
        )
        assert result.should_suppress_similar_task

    def test_reflection_to_dict(self, engine):
        result = engine.reflect(task_id="t13", tool_results=[{"status": "success"}])
        d = result.to_dict()
        assert d["task_id"] == "t13"
        assert d["outcome"] == "success"


class TestFailureType:
    def test_all_types_exist(self):
        types = [ft.value for ft in FailureType]
        assert "policy_denied" in types
        assert "approval_rejected" in types
        assert "timeout" in types
        assert "verification_failed" in types
        assert "unknown" in types


class TestMemoryType:
    def test_all_types_exist(self):
        types = [mt.value for mt in MemoryType]
        assert "episodic" in types
        assert "semantic" in types
        assert "procedural" in types
        assert "user_preference" in types
        assert "safety_lesson" in types
        assert "failure_lesson" in types
        assert "approval_lesson" in types
        assert "desire_lesson" in types
        assert "project_context" in types


class TestVisibilitySensitivity:
    def test_hidden_not_in_context(self, store):
        store.add_memory(MemoryRecord(title="h", content="secret", visibility="hidden"))
        assert store.summarize_for_context() == ""

    def test_secret_not_in_context(self, store):
        store.add_memory(MemoryRecord(title="s", content="key", sensitivity="secret"))
        assert store.summarize_for_context() == ""

    def test_normal_in_context(self, store):
        store.add_memory(MemoryRecord(title="n", content="visible", visibility="llm_visible"))
        assert "visible" in store.summarize_for_context()
