"""Phase 6 E2E — Mind Layer, Advanced Memory, Scheduler, Reflection Loop.

Tests the full integration:
  Mind Layer (identity/desire/emotion/goals) → ContextBuilder
  Scheduler → due tasks → ContextBuilder
  Reflection Loop → ReflectionLog → Mind state update
  Memory (episodic/semantic/procedural) → ContextBuilder

CI uses JSONL-based memory (no Chroma dependency for basic tests).
Architecture reference: docs/architecture.md §5, §6
"""

from __future__ import annotations

import time

from aegis_ai.context_builder import ContextBuilder
from aegis_ai.memory.episodic import Episode, EpisodicMemory
from aegis_ai.memory.procedural import ProceduralMemory, Procedure
from aegis_ai.memory.reflection import ReflectionLog
from aegis_ai.memory.semantic import Fact, SemanticMemory
from aegis_ai.mind.desire import Desire
from aegis_ai.mind.emotion import Emotion
from aegis_ai.mind.goals import Goal, GoalManager, GoalStatus, GoalType
from aegis_ai.mind.identity import Identity
from aegis_ai.mind.priorities import PriorityEngine
from aegis_ai.reflection_loop import ReflectionLoop
from aegis_ai.scheduler import ScheduledTask, Scheduler, TaskType
from aegis_schema.models import Event, EventPriority, ServerType

# ── Helpers ──────────────────────────────────────────────────


def _make_event(event_type: str = "android.notification_received", severity: int = 3) -> Event:
    return Event(
        event_id=f"evt_{int(time.time() * 1000)}",
        event_type=event_type,
        source_server_type=ServerType.ANDROID,
        source_server_id="test-server",
        timestamp_ms=int(time.time() * 1000),
        payload_json='{"test": true}',
        severity=severity,
        priority=EventPriority.NORMAL,
    )


# ═══════════════════════════════════════════════════════════════
# 1. Identity
# ═══════════════════════════════════════════════════════════════


class TestIdentity:
    """Identity persistence and context generation."""

    def test_identity_defaults(self):
        """Identity has correct default values."""
        identity = Identity(path="data/test_mind_identity.jsonl")
        assert identity.name == "AEGIS"
        assert "Autonomous" in identity.role
        assert len(identity.values) >= 4

    def test_identity_describe(self):
        """Identity.describe() returns human-readable string."""
        identity = Identity(path="data/test_mind_identity.jsonl")
        desc = identity.describe()
        assert "AEGIS" in desc

    def test_identity_to_context_string(self):
        """Identity.to_context_string() returns structured string."""
        identity = Identity(path="data/test_mind_identity.jsonl")
        ctx_str = identity.to_context_string()
        assert "Identity:" in ctx_str
        assert "Values:" in ctx_str
        assert "Safety:" in ctx_str

    def test_identity_persistence(self):
        """Identity values persist across instances."""
        path = "data/test_mind_identity_persist.jsonl"
        id1 = Identity(path=path)
        id1.update_values(["custom_value_1", "custom_value_2"])

        id2 = Identity(path=path)
        assert "custom_value_1" in id2.values


# ═══════════════════════════════════════════════════════════════
# 2. Desire
# ═══════════════════════════════════════════════════════════════


class TestDesire:
    """Desire priorities and persistence."""

    def test_desire_defaults(self):
        """Desire has correct default priorities."""
        desire = Desire(path="data/test_mind_desire.jsonl")
        assert desire.top_priority() == "help_user"
        assert desire.get_weight("stay_safe") > 0.9

    def test_desire_to_context_string(self):
        """Desire.to_context_string() returns structured string."""
        desire = Desire(path="data/test_mind_desire.jsonl")
        ctx_str = desire.to_context_string()
        assert "Priorities:" in ctx_str
        assert "help_user" in ctx_str

    def test_desire_update_weight(self):
        """Desire weight update persists."""
        path = "data/test_mind_desire_persist.jsonl"
        d1 = Desire(path=path)
        d1.update_weight("learn", 0.95)

        d2 = Desire(path=path)
        assert d2.get_weight("learn") == 0.95


# ═══════════════════════════════════════════════════════════════
# 3. Emotion
# ═══════════════════════════════════════════════════════════════


class TestEmotion:
    """Emotion state and persistence."""

    def test_emotion_defaults(self):
        """Emotion has correct default state."""
        emotion = Emotion(path="data/test_mind_emotion.jsonl")
        assert emotion.urgency == 0
        assert emotion.confidence == 0.5
        assert emotion.is_urgent() is False

    def test_emotion_update(self):
        """Emotion update persists."""
        path = "data/test_mind_emotion_persist.jsonl"
        e1 = Emotion(path=path)
        e1.update(urgency=8, confidence=0.9)

        e2 = Emotion(path=path)
        assert e2.urgency == 8
        assert e2.confidence == 0.9
        assert e2.is_urgent() is True

    def test_emotion_to_context_string(self):
        """Emotion.to_context_string() returns structured string."""
        emotion = Emotion(path="data/test_mind_emotion.jsonl")
        ctx_str = emotion.to_context_string()
        assert "urgency=" in ctx_str
        assert "confidence=" in ctx_str


# ═══════════════════════════════════════════════════════════════
# 4. Goals
# ═══════════════════════════════════════════════════════════════


class TestGoals:
    """Goal management and persistence."""

    def test_add_goal(self):
        """Goals can be added and listed."""
        gm = GoalManager(path="data/test_mind_goals.jsonl")
        gm.add(Goal(description="Test goal", priority=3))
        active = gm.list_active()
        assert len(active) >= 1
        assert active[0].description == "Test goal"

    def test_goal_progress(self):
        """Goal progress can be updated."""
        path = "data/test_mind_goals_progress.jsonl"
        gm = GoalManager(path=path)
        gm.add(Goal(goal_id="g1", description="Test", priority=3))
        gm.update_progress("g1", 0.5, "halfway")

        gm2 = GoalManager(path=path)
        g = gm2.get("g1")
        assert g is not None
        assert g.progress == 0.5

    def test_goal_completion(self):
        """Goal completion sets status and timestamp."""
        gm = GoalManager(path="data/test_mind_goals_complete.jsonl")
        gm.add(Goal(goal_id="g2", description="Complete me"))
        gm.complete("g2")

        g = gm.get("g2")
        assert g is not None
        assert g.status == GoalStatus.COMPLETED
        assert g.completed_at_ms > 0

    def test_goal_types(self):
        """Goals support different types."""
        gm = GoalManager(path="data/test_mind_goals_types.jsonl")
        gm.add(Goal(description="Short", goal_type=GoalType.SHORT_TERM))
        gm.add(Goal(description="Long", goal_type=GoalType.LONG_TERM))
        gm.add(Goal(description="Recurring", goal_type=GoalType.RECURRING))

        all_goals = gm.list_all()
        types = {g.goal_type for g in all_goals}
        assert GoalType.SHORT_TERM in types
        assert GoalType.LONG_TERM in types
        assert GoalType.RECURRING in types


# ═══════════════════════════════════════════════════════════════
# 5. PriorityEngine
# ═══════════════════════════════════════════════════════════════


class TestPriorityEngine:
    """Priority calculation based on Mind state."""

    def test_score_action_baseline(self):
        """Baseline priority score is around 0.5."""
        engine = PriorityEngine()
        score = engine.score_action("test_action")
        assert 0.3 <= score.score <= 0.7

    def test_score_with_desire(self):
        """Desire weight influences priority score."""
        desire = Desire(path="data/test_mind_priority_desire.jsonl")
        engine = PriorityEngine(desire=desire)
        score = engine.score_action("help_user")
        assert score.score > 0.5

    def test_should_defer_when_fatigued(self):
        """Fatigued state causes deferral."""
        emotion = Emotion(path="data/test_mind_priority_fatigue.jsonl")
        emotion.update(fatigue_proxy=0.9)
        engine = PriorityEngine(emotion=emotion)
        assert engine.should_defer("test_action") is True


# ═══════════════════════════════════════════════════════════════
# 6. Scheduler
# ═══════════════════════════════════════════════════════════════


class TestScheduler:
    """Scheduler task management and due detection."""

    def test_add_task(self):
        """Tasks can be added and listed."""
        scheduler = Scheduler()
        scheduler.add_task(ScheduledTask(
            task_id="test-1", name="Test", task_type=TaskType.DAILY_BRIEFING,
            interval_seconds=3600,
        ))
        assert len(scheduler.list_tasks()) == 1

    def test_get_due_tasks(self):
        """Tasks are due when interval has elapsed."""
        scheduler = Scheduler()
        scheduler.add_task(ScheduledTask(
            task_id="test-due", name="Due", task_type=TaskType.REFLECTION,
            interval_seconds=1, next_run_ms=int(time.time() * 1000) - 1000,
        ))
        due = scheduler.get_due_tasks()
        assert len(due) >= 1

    def test_cooldown_prevents_rapid_execution(self):
        """Cooldown prevents rapid task execution."""
        scheduler = Scheduler()
        task = ScheduledTask(
            task_id="test-cd", name="Cooldown", task_type=TaskType.REFLECTION,
            interval_seconds=1, cooldown_seconds=60,
        )
        scheduler.add_task(task)

        # First run
        scheduler.mark_started("test-cd")
        scheduler.mark_completed("test-cd")

        # Second run — should be blocked by cooldown
        due = scheduler.get_due_tasks()
        assert len(due) == 0

    def test_daily_budget(self):
        """Daily budget limits task runs."""
        scheduler = Scheduler()
        task = ScheduledTask(
            task_id="test-budget", name="Budget", task_type=TaskType.DAILY_BRIEFING,
            interval_seconds=1, daily_budget=2,
        )
        scheduler.add_task(task)

        # Run 2 times
        for _ in range(2):
            scheduler.mark_started("test-budget")
            scheduler.mark_completed("test-budget")
            task.next_run_ms = int(time.time() * 1000) - 1000

        # Third run — should be blocked by budget
        due = scheduler.get_due_tasks()
        assert len(due) == 0

    def test_default_tasks(self):
        """Default tasks are created."""
        scheduler = Scheduler()
        scheduler._default_tasks_created = False  # Reset for test
        scheduler.create_default_tasks()
        tasks = scheduler.list_tasks()
        assert len(tasks) >= 5

        task_ids = {t.task_id for t in tasks}
        assert "daily-briefing" in task_ids
        assert "reflection-interval" in task_ids
        assert "self-dev-scan" in task_ids

    def test_mark_completed_schedules_next(self):
        """Completed task schedules next run."""
        scheduler = Scheduler()
        scheduler.add_task(ScheduledTask(
            task_id="test-next", name="Next", task_type=TaskType.REFLECTION,
            interval_seconds=3600,
        ))
        scheduler.mark_started("test-next")
        scheduler.mark_completed("test-next")

        task = scheduler.get_task("test-next")
        assert task is not None
        assert task.run_count == 1
        assert task.next_run_ms > task.last_run_ms


# ═══════════════════════════════════════════════════════════════
# 7. Reflection Loop
# ═══════════════════════════════════════════════════════════════


class TestReflectionLoop:
    """Reflection Loop analysis and Mind state updates."""

    def test_reflection_run(self):
        """Reflection loop runs and produces results."""
        reflection = ReflectionLog(path="data/test_reflection_loop.jsonl")
        emotion = Emotion(path="data/test_reflection_emotion.jsonl")
        episodic = EpisodicMemory(path="data/test_reflection_episodic.jsonl")

        loop = ReflectionLoop(
            reflection_log=reflection,
            emotion=emotion,
            episodic_memory=episodic,
        )
        result = loop.run()

        assert result.reflection_id != ""
        assert result.duration_ms > 0

    def test_reflection_with_failures(self):
        """Reflection detects failures and adjusts confidence."""
        reflection = ReflectionLog(path="data/test_reflection_fail.jsonl")
        emotion = Emotion(path="data/test_reflection_fail_emo.jsonl")
        episodic = EpisodicMemory(path="data/test_reflection_fail_ep.jsonl")

        # Add failure episodes
        episodic.add(Episode(
            summary="Test failed", category="action_result",
            detail={"success": False},
        ))
        episodic.add(Episode(
            summary="Another failure", category="action_result",
            detail={"success": False},
        ))

        loop = ReflectionLoop(
            reflection_log=reflection,
            emotion=emotion,
            episodic_memory=episodic,
        )
        result = loop.run()

        assert len(result.what_failed) >= 2
        assert result.confidence_change < 0

    def test_reflection_with_successes(self):
        """Reflection detects successes and improves confidence."""
        reflection = ReflectionLog(path="data/test_reflection_success.jsonl")
        emotion = Emotion(path="data/test_reflection_succ_emo.jsonl")
        episodic = EpisodicMemory(path="data/test_reflection_succ_ep.jsonl")

        # Add success episodes
        for i in range(5):
            episodic.add(Episode(
                summary=f"Success {i}", category="action_result",
                detail={"success": True},
            ))

        loop = ReflectionLoop(
            reflection_log=reflection,
            emotion=emotion,
            episodic_memory=episodic,
        )
        result = loop.run()

        assert len(result.what_worked) >= 5
        assert result.confidence_change > 0

    def test_reflection_writes_to_log(self):
        """Reflection writes to ReflectionLog."""
        reflection = ReflectionLog(path="data/test_reflection_write.jsonl")
        loop = ReflectionLoop(reflection_log=reflection)
        loop.run()

        recent = reflection.list_recent(5)
        assert len(recent) >= 1


# ═══════════════════════════════════════════════════════════════
# 8. ContextBuilder Integration
# ═══════════════════════════════════════════════════════════════


class TestContextBuilderIntegration:
    """ContextBuilder integrates Mind Layer, Memory, and Scheduler."""

    def test_context_includes_identity(self):
        """Context includes identity string."""
        identity = Identity(path="data/test_ctx_identity.jsonl")
        builder = ContextBuilder(identity=identity)
        ctx = builder.build()
        assert "AEGIS" in ctx.identity

    def test_context_includes_emotion(self):
        """Context includes emotional state."""
        emotion = Emotion(path="data/test_ctx_emotion.jsonl")
        emotion.update(urgency=5, confidence=0.8)
        builder = ContextBuilder(emotion=emotion)
        ctx = builder.build()
        assert "urgency=" in ctx.emotional_state

    def test_context_includes_goals(self):
        """Context includes active goals."""
        goals = GoalManager(path="data/test_ctx_goals.jsonl")
        goals.add(Goal(description="Help user with tasks", priority=1))
        builder = ContextBuilder(goal_manager=goals)
        ctx = builder.build()
        assert len(ctx.current_goals) >= 1

    def test_context_includes_desires(self):
        """Context includes desire priorities."""
        desire = Desire(path="data/test_ctx_desire.jsonl")
        builder = ContextBuilder(desire=desire)
        ctx = builder.build()
        assert "Priorities:" in ctx.desires

    def test_context_includes_scheduled_tasks(self):
        """Context includes pending scheduled tasks."""
        scheduler = Scheduler()
        scheduler.add_task(ScheduledTask(
            task_id="test-due", name="Test Task",
            task_type=TaskType.DAILY_BRIEFING,
            description="Test scheduled task",
            interval_seconds=1,
            next_run_ms=int(time.time() * 1000) - 1000,
        ))
        builder = ContextBuilder(scheduler=scheduler)
        ctx = builder.build()
        assert len(ctx.pending_tasks) >= 1

    def test_context_includes_memory(self):
        """Context includes episodic and semantic memory."""
        episodic = EpisodicMemory(path="data/test_ctx_episodic.jsonl")
        semantic = SemanticMemory(path="data/test_ctx_semantic.jsonl")

        episodic.add(Episode(summary="Test episode", category="event"))
        semantic.add(Fact(content="User prefers dark mode", category="preference"))

        builder = ContextBuilder(
            episodic_memory=episodic,
            semantic_memory=semantic,
        )
        ctx = builder.build(triggering_query="dark mode")
        assert len(ctx.recent_episodes) >= 1
        assert len(ctx.relevant_facts) >= 1

    def test_context_budget_truncation(self):
        """Context is truncated when exceeding budget."""
        episodic = EpisodicMemory(path="data/test_ctx_budget.jsonl")
        for i in range(100):
            episodic.add(Episode(summary=f"Episode {i} " + "x" * 200, category="event"))

        builder = ContextBuilder(episodic_memory=episodic)
        ctx = builder.build()
        assert ctx.total_chars <= 8000 or ctx.truncated is True


# ═══════════════════════════════════════════════════════════════
# 9. Full E2E Flow
# ═══════════════════════════════════════════════════════════════


class TestFullE2EFlow:
    """Complete E2E: Mind + Memory + Scheduler + Reflection → ContextBuilder."""

    def test_full_flow(self):
        """Full flow from Mind/Memory/Scheduler to Context."""
        # Setup all components
        identity = Identity(path="data/test_e2e_identity.jsonl")
        desire = Desire(path="data/test_e2e_desire.jsonl")
        emotion = Emotion(path="data/test_e2e_emotion.jsonl")
        goals = GoalManager(path="data/test_e2e_goals.jsonl")
        episodic = EpisodicMemory(path="data/test_e2e_episodic.jsonl")
        semantic = SemanticMemory(path="data/test_e2e_semantic.jsonl")
        procedural = ProceduralMemory(path="data/test_e2e_procedural.jsonl")
        reflection = ReflectionLog(path="data/test_e2e_reflection.jsonl")
        scheduler = Scheduler()

        # Add data
        goals.add(Goal(description="Improve AEGIS reliability", priority=1))
        episodic.add(Episode(summary="User asked about temperature", category="event"))
        semantic.add(Fact(content="User prefers 22°C room temperature", category="preference"))
        procedural.add(Procedure(
            goal="research topic",
            steps=["browser.open_page", "browser.extract_text"],
            success_count=5,
            failure_count=1,
        ))
        scheduler = Scheduler()
        scheduler.add_task(ScheduledTask(
            task_id="test-due", name="Reflection",
            task_type=TaskType.REFLECTION,
            description="Run reflection",
            interval_seconds=1,
            next_run_ms=int(time.time() * 1000) - 1000,
        ))

        # Build context
        builder = ContextBuilder(
            identity=identity,
            desire=desire,
            emotion=emotion,
            goal_manager=goals,
            episodic_memory=episodic,
            semantic_memory=semantic,
            procedural_memory=procedural,
            reflection_log=reflection,
            scheduler=scheduler,
        )
        ctx = builder.build(triggering_query="temperature")

        # Verify all sections present
        assert "AEGIS" in ctx.identity
        assert "Priorities:" in ctx.desires
        assert "urgency=" in ctx.emotional_state
        assert len(ctx.current_goals) >= 1
        assert len(ctx.recent_episodes) >= 1
        assert len(ctx.relevant_facts) >= 1
        assert len(ctx.pending_tasks) >= 1

    def test_reflection_updates_mind(self):
        """Reflection loop updates Mind state based on outcomes."""
        reflection = ReflectionLog(path="data/test_e2e_refl_reflection.jsonl")
        emotion = Emotion(path="data/test_e2e_refl_emotion.jsonl")
        episodic = EpisodicMemory(path="data/test_e2e_refl_episodic.jsonl")

        # Add failures
        for i in range(5):
            episodic.add(Episode(
                summary=f"Failure {i}", category="action_result",
                detail={"success": False},
            ))

        loop = ReflectionLoop(
            reflection_log=reflection,
            emotion=emotion,
            episodic_memory=episodic,
        )
        result = loop.run()

        # Confidence should have decreased
        assert emotion.confidence < 0.5
        assert len(result.what_failed) >= 5
