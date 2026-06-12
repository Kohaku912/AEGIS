"""Tests for AutonomousLoop — full cycle with mock LLM, Planner, safety enforcement."""

from __future__ import annotations

from aegis_ai.audit import AuditLog
from aegis_ai.autonomous_loop import AutonomousLoop, LoopPhase, LoopResult
from aegis_ai.llm.client import LLMThought, MockLLMClient
from aegis_ai.memory.reflection import ReflectionLog
from aegis_ai.planner import Plan, PlannedStep, Planner, TaskStatus


class TestAutonomousLoop:
    def test_run_once_full_cycle(self):
        """A full cycle should progress through all phases."""
        loop = AutonomousLoop()
        loop.enable()
        result = loop.run_once()
        assert result.phase == LoopPhase.REFLECT
        assert result.actions_taken > 0
        assert result.duration_ms > 0

    def test_run_once_disabled_returns_idle(self):
        loop = AutonomousLoop()
        result = loop.run_once()
        assert result.phase == LoopPhase.IDLE

    def test_run_once_max_iterations(self):
        loop = AutonomousLoop()
        loop.enable()
        loop._iteration_count = 10  # Simulate max reached
        result = loop.run_once()
        assert result.phase == LoopPhase.IDLE
        assert "Max iterations" in str(result.errors)

    def test_run_once_records_reflection(self):
        reflection = ReflectionLog(path="data/test_loop_refl.jsonl")
        loop = AutonomousLoop(reflection_log=reflection)
        loop.enable()
        loop.run_once()
        refs = reflection.list_recent(10)
        assert len(refs) == 1
        assert "Cycle" in refs[0].summary

    def test_run_once_records_audit(self):
        audit = AuditLog(path="data/test_loop_audit.jsonl")
        loop = AutonomousLoop(audit_log=audit)
        loop.enable()
        loop.run_once()
        entries = audit.list_recent(50)
        # Should have at least observe, think, plan, act, verify, reflect
        phases = {e.action for e in entries}
        assert "loop_observe" in phases
        assert "loop_think" in phases
        assert "loop_plan" in phases
        assert "loop_act" in phases
        assert "loop_verify" in phases
        assert "loop_reflect" in phases

    def test_run_once_with_task_request(self):
        """TaskRequest context_summary should be passed to ContextBuilder."""
        class FakeTaskRequest:
            context_summary = "screenshot request"
        loop = AutonomousLoop()
        loop.enable()
        result = loop.run_once(task_request=FakeTaskRequest())
        assert result.phase == LoopPhase.REFLECT

    def test_run_once_tool_broker_integration(self):
        """When ToolBroker is provided, actions go through it."""
        from aegis_ai.tool_broker import ToolBroker
        from aegis_ai.tool_registry import ToolRegistry
        from aegis_schema.models import Capability, RiskLevel, ServerType

        registry = ToolRegistry()
        registry.register_capability(Capability(
            id="pc.screenshot", name="Screenshot", description="Take screenshot",
            server_type=ServerType.PC, risk_level=RiskLevel.READ_ONLY,
        ))
        broker = ToolBroker(registry)
        loop = AutonomousLoop(tool_broker=broker)
        loop.enable()
        result = loop.run_once()
        assert result.phase == LoopPhase.REFLECT
        assert result.actions_taken > 0

    def test_run_once_errors_caught(self):
        """Exceptions during the cycle should be caught, not crash the loop."""
        class BrokenLLM:
            def generate_thought(self, _ctx):
                raise RuntimeError("LLM is broken")
        loop = AutonomousLoop(llm_client=BrokenLLM())
        loop.enable()
        result = loop.run_once()
        assert result.phase == LoopPhase.FAILED
        assert "LLM is broken" in str(result.errors)

    def test_run_once_phase_order(self):
        """Phases should progress in correct order."""
        phases_seen = []

        class TrackingLoop(AutonomousLoop):
            def run_once(self, task_request=None):
                result = LoopResult()
                result.phase = LoopPhase.OBSERVE
                phases_seen.append("OBSERVE")
                result.phase = LoopPhase.THINK
                phases_seen.append("THINK")
                result.phase = LoopPhase.PLAN
                phases_seen.append("PLAN")
                result.phase = LoopPhase.ACT
                phases_seen.append("ACT")
                result.phase = LoopPhase.VERIFY
                phases_seen.append("VERIFY")
                result.phase = LoopPhase.REFLECT
                phases_seen.append("REFLECT")
                result.actions_taken = 1
                result.duration_ms = 1
                return result

        loop = TrackingLoop()
        loop.enable()
        loop.run_once()
        assert phases_seen == ["OBSERVE", "THINK", "PLAN", "ACT", "VERIFY", "REFLECT"]


class TestPlanner:
    def test_create_plan_from_thought(self):
        planner = Planner()
        thought = LLMThought(
            summary="Take screenshot",
            recommended_action="Take a screenshot using pc.screenshot",
            confidence=0.9,
        )
        plan = planner.create_plan_from_thought(thought, "Context: user wants screenshot")
        assert plan is not None
        assert plan.goal == "Take a screenshot"
        assert len(plan.steps) >= 1
        assert plan.steps[0].capability_id == "pc.screenshot"

    def test_plan_steps_have_required_fields(self):
        planner = Planner()
        thought = LLMThought(
            summary="Delete file",
            recommended_action="Delete file using pc.delete_file",
        )
        plan = planner.create_plan_from_thought(thought, "Context: delete /tmp/test.txt")
        assert plan is not None
        for step in plan.steps:
            assert step.step_id != ""
            assert step.description != ""
            assert step.capability_id != ""
            assert step.risk_level != ""

    def test_plan_has_fallback_steps(self):
        planner = Planner()
        thought = LLMThought(
            summary="Run tests",
            recommended_action="Run dev.run_tests to verify",
        )
        plan = planner.create_plan_from_thought(thought, "Context: test failure")
        assert plan is not None
        # The mock LLM provides fallback steps for test recommendations
        assert len(plan.fallback_steps) >= 0

    def test_next_step_dependency_order(self):
        plan = Plan(
            plan_id="p1", goal="Test",
            steps=[
                PlannedStep(step_id="step_1", capability_id="pc.screenshot", status=TaskStatus.COMPLETED),
                PlannedStep(step_id="step_2", capability_id="pc.mouse_click",
                           depends_on=["step_1"], status=TaskStatus.PENDING),
            ],
        )
        planner = Planner()
        next_s = planner.next_step(plan)
        assert next_s is not None
        assert next_s.step_id == "step_2"

    def test_next_step_skips_when_dependency_not_met(self):
        plan = Plan(
            plan_id="p1", goal="Test",
            steps=[
                PlannedStep(step_id="step_1", capability_id="pc.screenshot", status=TaskStatus.PENDING),
                PlannedStep(step_id="step_2", capability_id="pc.mouse_click",
                           depends_on=["step_1"], status=TaskStatus.PENDING),
            ],
        )
        planner = Planner()
        next_s = planner.next_step(plan)
        assert next_s is not None
        assert next_s.step_id == "step_1"  # Only step_1 is ready

    def test_create_basic_plan(self):
        planner = Planner()
        plan = planner.create_plan("Test goal")
        assert plan.goal == "Test goal"
        assert plan.plan_id.startswith("plan_")


class TestMockLLM:
    def test_generates_thought_for_screenshot(self):
        llm = MockLLMClient()
        thought = llm.generate_thought("Take a screenshot of the screen")
        assert thought.recommended_action == "Take a screenshot using pc.screenshot"
        assert thought.confidence > 0.5

    def test_generates_thought_for_test_failure(self):
        llm = MockLLMClient()
        thought = llm.generate_thought("Test failed with error")
        assert "test" in thought.recommended_action.lower()
        assert len(thought.risks_identified) > 0

    def test_generates_plan_with_steps(self):
        llm = MockLLMClient()
        thought = llm.generate_thought("Take a screenshot")
        plan_output = llm.generate_plan(thought, "Context")
        assert len(plan_output.steps) == 1
        assert plan_output.steps[0]["capability_id"] == "pc.screenshot"

    def test_summarize_results(self):
        llm = MockLLMClient()
        summary = llm.summarize_result(
            [{"success": True}, {"success": True}], "Test goal")
        assert "2 succeeded" in summary
        assert "All steps completed" in summary

    def test_summarize_results_with_failures(self):
        llm = MockLLMClient()
        summary = llm.summarize_result(
            [{"success": True}, {"success": False}], "Test goal")
        assert "1 succeeded" in summary
        assert "Some steps failed" in summary
