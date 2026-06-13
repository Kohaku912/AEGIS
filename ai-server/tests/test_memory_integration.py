"""Tests for memory integration — ContextBuilder, MotivationArbiter, ApprovalQueue, AutonomousLoop."""

from __future__ import annotations

import shutil
import tempfile

import pytest

from aegis_ai.memory.memory_store import MemoryStore
from aegis_ai.memory.memory_types import (
    MemoryRecord,
    MemorySource,
    MemoryType,
    Sensitivity,
    Visibility,
)
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


class TestContextBuilderMemoryIntegration:
    def test_failure_lessons_in_context(self, store):
        from aegis_ai.context_builder import ContextBuilder

        store.add_memory(MemoryRecord(
            memory_type=MemoryType.FAILURE_LESSON.value,
            title="Timeout error",
            content="browser.click timed out after 30s",
            importance=0.8,
        ))
        builder = ContextBuilder(memory_store=store)
        ctx = builder.build()
        assert any("Timeout" in s or "timeout" in s for s in ctx.failure_lessons)

    def test_safety_lessons_in_context(self, store):
        from aegis_ai.context_builder import ContextBuilder

        store.add_memory(MemoryRecord(
            memory_type=MemoryType.SAFETY_LESSON.value,
            title="Dangerous delete",
            content="Never auto-delete production files",
            importance=0.9,
        ))
        builder = ContextBuilder(memory_store=store)
        ctx = builder.build()
        assert any("Dangerous" in s or "delete" in s for s in ctx.safety_lessons)

    def test_approval_lessons_in_context(self, store):
        from aegis_ai.context_builder import ContextBuilder

        store.add_memory(MemoryRecord(
            memory_type=MemoryType.APPROVAL_LESSON.value,
            title="SNS post rejected",
            content="User rejected SNS posting",
            importance=0.8,
        ))
        builder = ContextBuilder(memory_store=store)
        ctx = builder.build()
        assert any("SNS" in s or "rejected" in s for s in ctx.approval_lessons)

    def test_user_preferences_in_context(self, store):
        from aegis_ai.context_builder import ContextBuilder

        store.add_memory(MemoryRecord(
            memory_type=MemoryType.USER_PREFERENCE.value,
            title="Prefer concise",
            content="User prefers brief responses",
            importance=0.7,
        ))
        builder = ContextBuilder(memory_store=store)
        ctx = builder.build()
        assert any("concise" in s or "brief" in s for s in ctx.user_preferences)

    def test_hidden_excluded_from_context(self, store):
        from aegis_ai.context_builder import ContextBuilder

        store.add_memory(MemoryRecord(
            memory_type=MemoryType.FAILURE_LESSON.value,
            title="hidden failure",
            content="should not appear",
            visibility=Visibility.HIDDEN.value,
        ))
        builder = ContextBuilder(memory_store=store)
        ctx = builder.build()
        assert not any("should not appear" in s for s in ctx.failure_lessons)

    def test_secret_excluded_from_context(self, store):
        from aegis_ai.context_builder import ContextBuilder

        store.add_memory(MemoryRecord(
            memory_type=MemoryType.USER_PREFERENCE.value,
            title="api key",
            content="password123",
            sensitivity=Sensitivity.SECRET.value,
        ))
        builder = ContextBuilder(memory_store=store)
        ctx = builder.build()
        assert not any("password123" in s for s in ctx.user_preferences)


class TestMotivationArbiterMemoryIntegration:
    def test_memory_penalty_on_failure(self, store):
        from aegis_ai.autonomous.motivation_arbiter import MotivationArbiter

        store.add_memory(MemoryRecord(
            memory_type=MemoryType.FAILURE_LESSON.value,
            title="curiosity task failed",
            content="Failed curiosity task",
            related_desire="curiosity",
            importance=0.7,
        ))
        arbiter = MotivationArbiter(memory_store=store)
        penalty, reason = arbiter._check_memory_penalties("t1", "curiosity")
        assert penalty > 0
        assert "failure" in reason.lower()

    def test_memory_penalty_on_rejection(self, store):
        from aegis_ai.autonomous.motivation_arbiter import MotivationArbiter

        store.add_memory(MemoryRecord(
            memory_type=MemoryType.APPROVAL_LESSON.value,
            title="rejected social",
            content="User rejected social_connection notification",
            related_desire="social_connection",
            importance=0.8,
        ))
        arbiter = MotivationArbiter(memory_store=store)
        penalty, reason = arbiter._check_memory_penalties("t2", "social_connection")
        assert penalty > 0
        assert "rejection" in reason.lower() or "rejected" in reason.lower()

    def test_no_penalty_without_memory(self, store):
        from aegis_ai.autonomous.motivation_arbiter import MotivationArbiter

        arbiter = MotivationArbiter(memory_store=store)
        penalty, reason = arbiter._check_memory_penalties("t3", "curiosity")
        assert penalty == 0.0


class TestApprovalQueueMemoryIntegration:
    def test_approval_stores_memory_on_approve(self, store, tmpdir):
        from aegis_ai.approval.approval_queue import ApprovalQueue

        queue = ApprovalQueue(data_dir=f"{tmpdir}/approvals", memory_store=store)

        class FakeRequest:
            approval_id = "a1"
            request_id = "r1"
            task_id = "t1"
            source = "desire_driven"
            source_desire = "curiosity"
            frustration = 5.0
            capability_id = "browser.navigate"
            tool_name = "Navigate"
            arguments = {"url": "https://example.com"}
            arguments_summary = "url=https://example.com"
            risk_level = "medium"
            policy_decision = "ASK_APPROVAL"
            approval_reason = "External navigation"
            user_facing_summary = "Navigate to example.com"
            status = "pending"
            created_at = 1000
            expires_at = 9999999999999

            def is_expired(self, now_ms=None):
                return False

            def to_dict(self):
                return {
                    "approval_id": self.approval_id,
                    "request_id": self.request_id,
                    "task_id": self.task_id,
                    "source": self.source,
                    "source_desire": self.source_desire,
                    "frustration": self.frustration,
                    "capability_id": self.capability_id,
                    "tool_name": self.tool_name,
                    "arguments_summary": self.arguments_summary,
                    "risk_level": self.risk_level,
                    "policy_decision": self.policy_decision,
                    "approval_reason": self.approval_reason,
                    "user_facing_summary": self.user_facing_summary,
                    "created_at": self.created_at,
                    "expires_at": self.expires_at,
                    "status": self.status,
                }

        queue._requests["a1"] = FakeRequest()
        queue.approve("a1", user_note="ok")

        lessons = store.search_memories(memory_type=MemoryType.APPROVAL_LESSON.value)
        assert len(lessons) >= 1
        assert any("approved" in r.content.lower() for r in lessons)

    def test_rejection_stores_memory(self, store, tmpdir):
        from aegis_ai.approval.approval_queue import ApprovalQueue

        queue = ApprovalQueue(data_dir=f"{tmpdir}/approvals", memory_store=store)

        class FakeRequest:
            approval_id = "a2"
            request_id = "r2"
            task_id = "t2"
            source = "desire_driven"
            source_desire = "social_connection"
            frustration = 6.0
            capability_id = "browser.post_sns"
            tool_name = "Post SNS"
            arguments = {"message": "hello"}
            arguments_summary = "message=hello"
            risk_level = "high"
            policy_decision = "ASK_APPROVAL"
            approval_reason = "SNS posting"
            user_facing_summary = "Post to SNS"
            status = "pending"
            created_at = 1000
            expires_at = 9999999999999

            def is_expired(self, now_ms=None):
                return False

            def to_dict(self):
                return {
                    "approval_id": self.approval_id,
                    "request_id": self.request_id,
                    "task_id": self.task_id,
                    "source": self.source,
                    "source_desire": self.source_desire,
                    "frustration": self.frustration,
                    "capability_id": self.capability_id,
                    "tool_name": self.tool_name,
                    "arguments_summary": self.arguments_summary,
                    "risk_level": self.risk_level,
                    "policy_decision": self.policy_decision,
                    "approval_reason": self.approval_reason,
                    "user_facing_summary": self.user_facing_summary,
                    "created_at": self.created_at,
                    "expires_at": self.expires_at,
                    "status": self.status,
                }

        queue._requests["a2"] = FakeRequest()
        queue.reject("a2", reason="too risky")

        lessons = store.search_memories(memory_type=MemoryType.APPROVAL_LESSON.value)
        assert len(lessons) >= 1
        assert any("rejected" in r.content.lower() for r in lessons)


class TestReflectionEngineMemoryIntegration:
    def test_reflection_creates_failure_lesson(self, engine, store):
        engine.reflect(
            task_id="t1",
            task_description="Click button",
            tool_results=[{"status": "failed", "error": "timeout", "capability_id": "pc.click"}],
        )
        lessons = store.search_memories(memory_type=MemoryType.FAILURE_LESSON.value)
        assert len(lessons) >= 1

    def test_reflection_creates_approval_lesson(self, engine, store):
        engine.reflect(
            task_id="t2",
            task_description="Post to SNS",
            approval_decisions=[{
                "status": "rejected", "reason": "too risky",
                "approval_id": "a1", "capability_id": "browser.post",
            }],
        )
        lessons = store.search_memories(memory_type=MemoryType.APPROVAL_LESSON.value)
        assert len(lessons) >= 1

    def test_reflection_creates_desire_lesson(self, engine, store):
        engine.reflect(
            task_id="t3",
            task_description="Learn",
            tool_results=[{"status": "success"}],
            source_desire="curiosity",
            frustration=7.0,
            desire_before={"curiosity": 3.0},
            desire_after={"curiosity": 6.0},
        )
        lessons = store.search_memories(memory_type=MemoryType.DESIRE_LESSON.value)
        assert len(lessons) >= 1

    def test_reflection_creates_episodic_memory(self, engine, store):
        engine.reflect(
            task_id="t4",
            task_description="Click button",
            tool_results=[{"status": "success", "capability_id": "pc.click"}],
        )
        episodes = store.search_memories(memory_type=MemoryType.EPISODIC.value)
        assert len(episodes) >= 1

    def test_reflection_failure_type_classified(self, engine):
        result = engine.reflect(
            task_id="t5",
            task_description="Auth",
            tool_results=[{"status": "failed", "error": "authentication required"}],
        )
        assert any("authentication" in h.lower() for h in result.planner_hints)


class TestMemoryCompression:
    def test_summarize_old_episodes(self, store):
        import time
        old_ms = int(time.time() * 1000) - 200 * 3600 * 1000
        store.add_memory(MemoryRecord(
            memory_type=MemoryType.EPISODIC.value,
            title="old episode",
            content="very old",
            created_at=old_ms,
        ))
        store.add_memory(MemoryRecord(
            memory_type=MemoryType.EPISODIC.value,
            title="new episode",
            content="recent",
        ))
        old = store.summarize_old_episodes(max_age_hours=168)
        assert len(old) >= 1
        assert any("old" in r.title for r in old)

    def test_merge_similar_lessons(self, store):
        store.add_memory(MemoryRecord(
            memory_type=MemoryType.FAILURE_LESSON.value,
            title="Same Title",
            content="v1",
        ))
        store.add_memory(MemoryRecord(
            memory_type=MemoryType.FAILURE_LESSON.value,
            title="Same Title",
            content="v2",
        ))
        merged = store.merge_similar_lessons(MemoryType.FAILURE_LESSON.value)
        assert len(merged) == 1

    def test_prune_expired(self, store):
        import time
        store.add_memory(MemoryRecord(
            title="expired",
            content="gone",
            expires_at=int(time.time() * 1000) - 1000,
        ))
        count = store.prune_expired()
        assert count == 1
        assert store.count() == 0


class TestAutonomousLoopReflection:
    def test_loop_accepts_reflection_engine(self):
        from aegis_ai.autonomous.autonomous_loop import AutonomousLoop

        loop = AutonomousLoop(reflection_engine=None)
        assert loop._reflection is None

        loop2 = AutonomousLoop(reflection_engine="mock")
        assert loop2._reflection == "mock"


class TestVerificationMemoryIntegration:
    def test_verification_result_storable(self, store):
        store.add_memory(MemoryRecord(
            memory_type=MemoryType.PROCEDURAL.value,
            title="Verified: pc.write_file",
            content="File write verified successfully",
            source=MemorySource.VERIFICATION_RESULT.value,
            related_verification_id="v1",
            confidence=0.9,
            importance=0.6,
        ))
        records = store.search_memories(memory_type=MemoryType.PROCEDURAL.value)
        assert len(records) >= 1
        assert any("Verified" in r.title for r in records)
