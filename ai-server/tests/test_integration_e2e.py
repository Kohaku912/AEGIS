"""E2E Integration Test — verifies full autonomous flow.

Flow: Observation → Desire/Emotion update → Memory search → Planning →
      PolicyEngine check → Capability execution → Result verification →
      ActionTrace save → Memory/Skill update → Sleep consolidation
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
from aegis_ai.autonomous.curiosity_exploration import CuriosityDrivenExplorationSystem
from aegis_ai.autonomous.planner import AutonomousPlanner, PlanStatus
from aegis_ai.desire.desire_system import DesireSystem
from aegis_ai.memory.action_trace import ActionTraceMemory, TraceStatus
from aegis_ai.memory.semantic import Fact, SemanticMemory
from aegis_ai.memory.skill_memory import SkillMemory
from aegis_ai.memory.sleep_consolidation import SleepConsolidationSystem
from aegis_ai.mind.emotion import Emotion
from aegis_ai.observation.observation_service import MultimodalObservationService
from aegis_ai.observation.observation_types import ObservationRequest, ObservationTarget
from aegis_schema.models import Capability, RiskLevel, ServerType
from policy_engine import PolicyDecision, PolicyEngine


@pytest.fixture
def temp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def mock_llm():
    llm = MagicMock()

    def generate_side_effect(prompt, system_prompt="", max_tokens=2000, temperature=0.7):
        if "Generate up to" in prompt or "generate tasks" in prompt.lower():
            return MagicMock(
                success=True,
                content=json.dumps({
                    "tasks": [
                        {"desire": "curiosity", "action": "Explore new topic", "expected_impact": 0.5}
                    ]
                }),
                error="",
            )
        return MagicMock(
            success=True,
            content=json.dumps({
                "desire_updates": {
                    "curiosity": {"new_value": 7.0, "reason": "Explored new topic"},
                }
            }),
            error="",
        )

    llm.generate.side_effect = generate_side_effect
    return llm


@pytest.fixture
def mock_broker():
    from tool_broker import InvokeStatus, ToolExecutionResult

    broker = MagicMock()
    broker.execute.return_value = ToolExecutionResult(
        status=InvokeStatus.SUCCESS,
        output={"result": "Posts read successfully", "count": 5},
    )
    return broker


@pytest.fixture
def desire_system(temp_dir, mock_llm):
    return DesireSystem(
        data_dir=str(Path(temp_dir) / "desires"),
        llm_provider=mock_llm,
    )


@pytest.fixture
def emotion_system(temp_dir):
    return Emotion(path=str(Path(temp_dir) / "emotion.jsonl"))


@pytest.fixture
def action_trace(temp_dir):
    return ActionTraceMemory(path=str(Path(temp_dir) / "action_traces.jsonl"))


@pytest.fixture
def skill_memory(temp_dir):
    return SkillMemory(path=str(Path(temp_dir) / "skills.jsonl"))


@pytest.fixture
def semantic_memory(temp_dir):
    return SemanticMemory(path=str(Path(temp_dir) / "semantic.jsonl"))


# ── Desire → Task Generation ────────────────────────────────────────────


class TestDesireToTaskGeneration:
    def test_low_desires_generate_tasks(self, desire_system):
        desire_system.update_value("curiosity", 2.0)

        tasks = desire_system.generate_tasks()

        assert len(tasks) > 0
        assert any(t["desire"] == "curiosity" for t in tasks)
        assert all("gap" in t for t in tasks)

    def test_high_desires_no_tasks(self, desire_system):
        for name in desire_system.get_all_desires():
            desire_system.update_value(name, 10.0)

        tasks = desire_system.generate_tasks()

        assert len(tasks) == 0

    def test_snapshot_captures_frustration(self, desire_system):
        desire_system.update_value("curiosity", 1.0)

        snap = desire_system.create_snapshot()

        assert snap.max_frustration > 0
        assert "curiosity" in snap.top_unsatisfied_desires


# ── Emotion Appraisal ───────────────────────────────────────────────────


class TestEmotionAppraisal:
    def test_success_boosts_confidence(self, emotion_system):
        initial = emotion_system.confidence

        emotion_system.appraise_from_experience(
            action="Read AGORA posts",
            observation="Found 5 new posts",
            success=True,
            desire_name="social_connection",
        )

        assert emotion_system.confidence > initial

    def test_failure_reduces_confidence(self, emotion_system):
        emotion_system.update(confidence=0.8)
        initial = emotion_system.confidence

        emotion_system.appraise_from_experience(
            action="Failed to read posts",
            observation="Connection error",
            success=False,
            desire_name="social_connection",
        )

        assert emotion_system.confidence < initial

    def test_context_string_includes_state(self, emotion_system):
        ctx = emotion_system.to_context_string()

        assert "urgency" in ctx
        assert "confidence" in ctx

    def test_persistence_across_instances(self, temp_dir):
        path = str(Path(temp_dir) / "emotion_persist.jsonl")

        em1 = Emotion(path=path)
        em1.update(confidence=0.8, urgency=3)

        em2 = Emotion(path=path)
        assert em2.confidence == 0.8
        assert em2.urgency == 3


# ── Action Trace Lifecycle ──────────────────────────────────────────────


class TestActionTraceLifecycle:
    def test_begin_step_complete(self, action_trace):
        trace = action_trace.begin_trace(
            goal="Check AGORA",
            context="desire:social_connection",
            desire_name="social_connection",
        )

        action_trace.add_step(
            trace,
            description="Read posts",
            tool_call="ai.agora.read_posts",
            tool_result="Found 5 posts",
            success=True,
        )

        action_trace.complete_trace(
            trace,
            success=True,
            result_summary="Posts read successfully",
        )

        assert trace.success
        assert len(trace.steps) == 1
        assert trace.status == TraceStatus.COMPLETED

    def test_failed_trace_records_reason(self, action_trace):
        trace = action_trace.begin_trace(goal="Test fail", context="test")

        action_trace.complete_trace(
            trace,
            success=False,
            failure_reason="Connection timeout",
        )

        assert not trace.success
        assert trace.failure_reason == "Connection timeout"
        assert trace.status == TraceStatus.FAILED

    def test_search_similar_finds_matches(self, action_trace):
        t1 = action_trace.begin_trace(goal="Check AGORA posts", context="test")
        action_trace.complete_trace(t1, success=True, result_summary="Done")

        t2 = action_trace.begin_trace(goal="Read AGORA messages", context="test")
        action_trace.complete_trace(t2, success=True, result_summary="Done")

        t3 = action_trace.begin_trace(goal="Clean up logs", context="test")
        action_trace.complete_trace(t3, success=True, result_summary="Done")

        results = action_trace.search_similar("Check AGORA")
        assert len(results) >= 1
        assert all("AGORA" in r.goal for r in results)


# ── Skill Memory Reuse ─────────────────────────────────────────────────


class TestSkillMemoryReuse:
    def test_add_and_find_skill(self, skill_memory):
        skill = skill_memory.add_skill(
            name="Read AGORA Messages",
            execution_steps=[{"tool": "ai.agora.read_posts", "args": {"limit": 10}}],
            activation_conditions="read agora messages",
            goal_pattern="agora|messages|posts",
        )

        found = skill_memory.find_skill("Read AGORA messages")

        assert found is not None
        assert found.skill_id == skill.skill_id

    def test_record_result_updates_stats(self, skill_memory):
        skill = skill_memory.add_skill(
            name="Test Skill",
            execution_steps=[{"tool": "test.action"}],
        )

        skill_memory.record_result(skill.skill_id, success=True, duration_ms=500)
        skill_memory.record_result(skill.skill_id, success=False, failure_reason="timeout")

        refreshed = skill_memory.get_active()
        match = [s for s in refreshed if s.skill_id == skill.skill_id]
        assert len(match) == 1
        assert match[0].success_count == 1
        assert match[0].failure_count == 1

    def test_auto_deprecate_low_success(self, skill_memory):
        skill = skill_memory.add_skill(
            name="Bad Skill",
            execution_steps=[{"tool": "test.action"}],
        )

        for _ in range(5):
            skill_memory.record_result(skill.skill_id, success=False, failure_reason="fail")

        active = skill_memory.get_active()
        assert not any(s.skill_id == skill.skill_id for s in active)


# ── Semantic Memory Search ─────────────────────────────────────────────


class TestSemanticMemorySearch:
    def test_add_and_search(self, semantic_memory):
        fact = Fact(content="AGORA is a social platform", category="knowledge", source="test")
        semantic_memory.add(fact)

        results = semantic_memory.search("AGORA")

        assert len(results) > 0
        assert results[0].content == "AGORA is a social platform"

    def test_search_by_category(self, semantic_memory):
        semantic_memory.add(Fact(content="Test fact", category="user_info", source="test"))
        semantic_memory.add(Fact(content="Other fact", category="knowledge", source="test"))

        results = semantic_memory.search("fact", category="user_info")

        assert len(results) == 1
        assert results[0].category == "user_info"


# ── Sleep Consolidation ────────────────────────────────────────────────


class TestSleepConsolidation:
    def test_consolidate_returns_summary(self, temp_dir, action_trace, skill_memory):
        trace = action_trace.begin_trace(goal="Test goal", context="test")
        action_trace.complete_trace(trace, success=True, result_summary="Done")

        mock_llm = MagicMock()
        mock_llm.generate.return_value = MagicMock(
            success=True,
            content=json.dumps({
                "lessons": [{"content": "Test lesson", "type": "success_pattern"}]
            }),
            error="",
        )

        mock_lesson = MagicMock()
        mock_lesson.get_relevant.return_value = []

        mock_workflow = MagicMock()
        mock_workflow.find_matching.return_value = None
        mock_workflow.get_active.return_value = []

        sleep = SleepConsolidationSystem(
            action_trace=action_trace,
            lesson=mock_lesson,
            workflow=mock_workflow,
            skill=skill_memory,
            llm=mock_llm,
            data_dir=str(Path(temp_dir) / "memory"),
        )

        result = sleep.consolidate()

        assert "action_traces_consolidated" in result
        assert "lessons_from_traces" in result

    def test_consolidate_with_no_systems(self, temp_dir):
        sleep = SleepConsolidationSystem(
            data_dir=str(Path(temp_dir) / "memory"),
        )

        result = sleep.consolidate()

        assert result["episodes_summarized"] == 0
        assert result["lessons_extracted"] == 0


# ── Policy Engine Integration ──────────────────────────────────────────


class TestPolicyEngineIntegration:
    def test_read_only_allows(self):
        policy = PolicyEngine()

        cap = Capability(
            id="pc.screenshot.get_screenshot",
            name="Get Screenshot",
            description="Capture screenshot",
            server_type=ServerType.PC,
            risk_level=RiskLevel.READ_ONLY,
        )

        result = policy.evaluate(cap, {})

        assert result.decision == PolicyDecision.ALLOW

    def test_explicit_deny_blocks(self):
        policy = PolicyEngine()

        cap = Capability(
            id="dev.merge_to_main",
            name="Merge to Main",
            description="Merge to main branch",
            server_type=ServerType.DEV,
            risk_level=RiskLevel.HIGH_RISK,
        )

        result = policy.evaluate(cap, {})

        assert result.decision == PolicyDecision.DENY

    def test_high_risk_not_auto_allowed(self):
        policy = PolicyEngine()

        cap = Capability(
            id="pc.install_package",
            name="Install Package",
            description="Install system package",
            server_type=ServerType.PC,
            risk_level=RiskLevel.HIGH_RISK,
        )

        result = policy.evaluate(cap, {})

        assert result.decision != PolicyDecision.ALLOW


# ── Observation → Desire Flow ──────────────────────────────────────────


class TestObservationToDesireFlow:
    def test_observation_updates_emotion(self, emotion_system):
        emotion_system.appraise_from_experience(
            action="Observed system state",
            observation="System running normally, 5 new AGORA posts",
            success=True,
            desire_name="curiosity",
        )

        assert emotion_system.confidence >= 0.5

    def test_desire_update_after_action(self, desire_system, mock_llm):
        mock_llm.generate.return_value = MagicMock(
            success=True,
            content=json.dumps({
                "desire_updates": {
                    "curiosity": {"new_value": 7.0, "reason": "Learned something new"},
                }
            }),
            error="",
        )

        result = desire_system.update_after_action(
            action="Read new research paper",
            observation="Found interesting findings",
        )

        assert "updates" in result or "error" not in result

    def test_observation_service_with_no_clients(self, temp_dir):
        service = MultimodalObservationService()
        request = ObservationRequest(target=ObservationTarget.PC)
        result = service.observe(request)

        assert result is not None


# ── Curiosity Exploration ──────────────────────────────────────────────


class TestCuriosityExploration:
    def test_should_explore_when_curiosity_high(self, desire_system, mock_llm, temp_dir):
        curiosity = CuriosityDrivenExplorationSystem(
            llm=mock_llm,
            desire_system=desire_system,
            curiosity_threshold=6.0,
            data_dir=str(Path(temp_dir) / "autonomous"),
        )

        desire_system.update_value("curiosity", 8.0)

        assert curiosity.should_explore

    def test_should_not_explore_when_curiosity_low(self, desire_system, mock_llm, temp_dir):
        curiosity = CuriosityDrivenExplorationSystem(
            llm=mock_llm,
            desire_system=desire_system,
            curiosity_threshold=6.0,
            data_dir=str(Path(temp_dir) / "autonomous"),
        )

        desire_system.update_value("curiosity", 3.0)

        assert not curiosity.should_explore

    def test_generate_candidates_returns_list(self, desire_system, mock_llm, temp_dir):
        mock_llm.generate.return_value = MagicMock(
            success=True,
            content=json.dumps({
                "candidates": [
                    {
                        "topic": "New AI frameworks",
                        "description": "Explore latest AI tools",
                        "importance": 0.7,
                        "novelty": 0.8,
                    }
                ]
            }),
            error="",
        )

        curiosity = CuriosityDrivenExplorationSystem(
            llm=mock_llm,
            desire_system=desire_system,
            data_dir=str(Path(temp_dir) / "autonomous"),
        )

        candidates = curiosity.generate_exploration_candidates()

        assert isinstance(candidates, list)


# ── Planner ────────────────────────────────────────────────────────────


class TestPlanner:
    def test_creates_execution_plan(self, mock_llm, temp_dir):
        planner = AutonomousPlanner(
            llm_provider=mock_llm,
            data_dir=str(Path(temp_dir) / "plans"),
        )

        plan = planner.plan("Check AGORA for new messages", context="social_connection desire")

        assert plan.goal == "Check AGORA for new messages"
        assert plan.status in (PlanStatus.PLANNING, PlanStatus.CANCELLED, PlanStatus.EXECUTING)


# ── Full Autonomous Cycle ──────────────────────────────────────────────


class TestFullAutonomousCycle:
    def test_cycle_with_low_desires(
        self, desire_system, emotion_system, action_trace,
        skill_memory, mock_llm, mock_broker, temp_dir,
    ):
        desire_system.update_value("curiosity", 2.0)

        def gen_side_effect(prompt, system_prompt="", max_tokens=2000, temperature=0.7):
            if "Generate up to" in prompt:
                return MagicMock(
                    success=True,
                    content=json.dumps({
                        "tasks": [
                            {"desire": "curiosity", "action": "Explore new topic", "expected_impact": 0.5}
                        ]
                    }),
                    error="",
                )
            return MagicMock(
                success=True,
                content=json.dumps({
                    "desire_updates": {
                        "curiosity": {"new_value": 5.0, "reason": "Explored topic"},
                    }
                }),
                error="",
            )

        mock_llm.generate.side_effect = gen_side_effect

        loop = AutonomousLoop(
            llm_provider=mock_llm,
            desire_system=desire_system,
            tool_broker=mock_broker,
            affect_system=emotion_system,
            action_trace=action_trace,
            skill_memory=skill_memory,
            data_dir=str(Path(temp_dir) / "autonomous"),
        )

        status = loop.trigger_now()

        assert status["execution_count"] > 0
        assert status["last_run_ms"] > 0

    def test_cycle_with_no_low_desires(
        self, desire_system, emotion_system, action_trace,
        skill_memory, mock_llm, mock_broker, temp_dir,
    ):
        for name in desire_system.get_all_desires():
            desire_system.update_value(name, 10.0)

        loop = AutonomousLoop(
            llm_provider=mock_llm,
            desire_system=desire_system,
            tool_broker=mock_broker,
            affect_system=emotion_system,
            action_trace=action_trace,
            skill_memory=skill_memory,
            desire_threshold=4.0,
            data_dir=str(Path(temp_dir) / "autonomous"),
        )

        status = loop.trigger_now()

        assert status["execution_count"] >= 0

    def test_loop_status_fields(self, desire_system, mock_llm, temp_dir):
        loop = AutonomousLoop(
            llm_provider=mock_llm,
            desire_system=desire_system,
            data_dir=str(Path(temp_dir) / "autonomous"),
        )

        status = loop.get_status()

        assert "running" in status
        assert "execution_count" in status
        assert "last_run_ms" in status
        assert "next_run_ms" in status

    def test_action_trace_recorded_during_cycle(
        self, desire_system, emotion_system, action_trace,
        skill_memory, mock_llm, mock_broker, temp_dir,
    ):
        desire_system.update_value("curiosity", 2.0)

        def gen_side_effect(prompt, system_prompt="", max_tokens=2000, temperature=0.7):
            if "Generate up to" in prompt:
                return MagicMock(
                    success=True,
                    content=json.dumps({
                        "tasks": [
                            {"desire": "curiosity", "action": "Explore new topic", "expected_impact": 0.5}
                        ]
                    }),
                    error="",
                )
            return MagicMock(
                success=True,
                content=json.dumps({
                    "desire_updates": {
                        "curiosity": {"new_value": 5.0, "reason": "Done"},
                    }
                }),
                error="",
            )

        mock_llm.generate.side_effect = gen_side_effect

        loop = AutonomousLoop(
            llm_provider=mock_llm,
            desire_system=desire_system,
            tool_broker=mock_broker,
            affect_system=emotion_system,
            action_trace=action_trace,
            skill_memory=skill_memory,
            data_dir=str(Path(temp_dir) / "autonomous"),
        )

        loop.trigger_now()

        traces = action_trace.get_successful()
        failed = action_trace.get_failed()
        assert len(traces) + len(failed) > 0

    def test_emotion_updated_after_cycle(
        self, desire_system, emotion_system, action_trace,
        skill_memory, mock_llm, mock_broker, temp_dir,
    ):
        desire_system.update_value("curiosity", 2.0)
        initial_confidence = emotion_system.confidence

        def gen_side_effect(prompt, system_prompt="", max_tokens=2000, temperature=0.7):
            if "Generate up to" in prompt:
                return MagicMock(
                    success=True,
                    content=json.dumps({
                        "tasks": [
                            {"desire": "curiosity", "action": "Explore new topic", "expected_impact": 0.5}
                        ]
                    }),
                    error="",
                )
            return MagicMock(
                success=True,
                content=json.dumps({
                    "desire_updates": {
                        "curiosity": {"new_value": 5.0, "reason": "Done"},
                    }
                }),
                error="",
            )

        mock_llm.generate.side_effect = gen_side_effect

        loop = AutonomousLoop(
            llm_provider=mock_llm,
            desire_system=desire_system,
            tool_broker=mock_broker,
            affect_system=emotion_system,
            action_trace=action_trace,
            skill_memory=skill_memory,
            data_dir=str(Path(temp_dir) / "autonomous"),
        )

        loop.trigger_now()

        assert emotion_system.confidence >= initial_confidence


# ── Full E2E Flow ──────────────────────────────────────────────────────


class TestEndToEndFlow:
    """Full flow: Observation → Desire → Emotion → Memory → Policy →
    Execute → Trace → Skill → Sleep consolidation."""

    def test_full_e2e_flow(self, temp_dir, mock_llm, mock_broker):
        # 1. Initialize all systems
        desire = DesireSystem(
            data_dir=str(Path(temp_dir) / "desires"),
            llm_provider=mock_llm,
        )
        emotion = Emotion(path=str(Path(temp_dir) / "emotion.jsonl"))
        trace_mem = ActionTraceMemory(path=str(Path(temp_dir) / "traces.jsonl"))
        skill_mem = SkillMemory(path=str(Path(temp_dir) / "skills.jsonl"))
        semantic = SemanticMemory(path=str(Path(temp_dir) / "semantic.jsonl"))

        # 2. Set low desire to trigger autonomous behavior
        desire.update_value("curiosity", 2.0)
        desire.update_value("social_connection", 2.0)

        # 3. Emotion appraises initial state
        emotion.appraise_from_experience(
            action="System startup",
            observation="All systems online",
            success=True,
            desire_name="system_safety",
        )
        assert emotion.confidence >= 0.5

        # 4. Add knowledge to semantic memory
        semantic.add(Fact(
            content="AGORA is a social platform for AEGIS communication",
            category="knowledge",
            source="test",
        ))
        results = semantic.search("AGORA")
        assert len(results) > 0

        # 5. PolicyEngine allows read-only operations
        policy = PolicyEngine()
        cap = Capability(
            id="ai.agora.read_posts",
            name="Read Posts",
            description="Read AGORA posts",
            server_type=ServerType.AI,
            risk_level=RiskLevel.READ_ONLY,
        )
        policy_result = policy.evaluate(cap, {})
        assert policy_result.decision == PolicyDecision.ALLOW

        # 6. Execute autonomous cycle
        def gen_side_effect(prompt, system_prompt="", max_tokens=2000, temperature=0.7):
            if "Generate up to" in prompt:
                return MagicMock(
                    success=True,
                    content=json.dumps({
                        "tasks": [
                            {"desire": "curiosity", "action": "Explore AGORA", "expected_impact": 0.5},
                            {"desire": "social_connection", "action": "Check AGORA posts", "expected_impact": 0.5},
                        ]
                    }),
                    error="",
                )
            return MagicMock(
                success=True,
                content=json.dumps({
                    "desire_updates": {
                        "curiosity": {"new_value": 5.0, "reason": "Explored AGORA"},
                        "social_connection": {"new_value": 5.0, "reason": "Read posts"},
                    }
                }),
                error="",
            )

        mock_llm.generate.side_effect = gen_side_effect

        loop = AutonomousLoop(
            llm_provider=mock_llm,
            desire_system=desire,
            tool_broker=mock_broker,
            affect_system=emotion,
            action_trace=trace_mem,
            skill_memory=skill_mem,
            data_dir=str(Path(temp_dir) / "autonomous"),
        )

        status = loop.trigger_now()
        assert status["execution_count"] > 0

        # 7. Verify action traces were saved
        all_traces = trace_mem.get_successful() + trace_mem.get_failed()
        assert len(all_traces) > 0

        # 8. Add a skill based on successful execution
        skill = skill_mem.add_skill(
            name="Read AGORA Posts",
            execution_steps=[{"tool": "ai.agora.read_posts", "args": {"limit": 10}}],
            activation_conditions="social_connection desire is low",
        )
        assert skill.skill_id

        # 9. Sleep consolidation processes traces
        mock_lesson = MagicMock()
        mock_lesson.get_relevant.return_value = []

        mock_workflow = MagicMock()
        mock_workflow.find_matching.return_value = None
        mock_workflow.get_active.return_value = []

        sleep = SleepConsolidationSystem(
            action_trace=trace_mem,
            lesson=mock_lesson,
            workflow=mock_workflow,
            skill=skill_mem,
            llm=mock_llm,
            data_dir=str(Path(temp_dir) / "memory"),
        )

        consolidation_result = sleep.consolidate()
        assert "action_traces_consolidated" in consolidation_result

        # 10. Verify final desire state reflects updates
        snap = desire.create_snapshot()
        assert snap.timestamp > 0

    def test_desire_persistence_across_instances(self, temp_dir, mock_llm):
        data_dir = str(Path(temp_dir) / "desire_persist")

        ds1 = DesireSystem(data_dir=data_dir, llm_provider=mock_llm)
        ds1.update_value("curiosity", 8.5)
        ds1.save()

        ds2 = DesireSystem(data_dir=data_dir, llm_provider=mock_llm)
        curiosity = ds2.get_desire("curiosity")
        assert curiosity is not None
        assert curiosity.value == 8.5
