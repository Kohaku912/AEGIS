"""Test that all ellie_ai modules are importable and basic instances can be created."""

from __future__ import annotations


class TestImports:
    """Verify all ellie_ai modules import without errors."""

    def test_import_core(self):
        import ellie_ai  # noqa: F401

    def test_import_config(self):
        from ellie_ai.config import Config, get_config  # noqa: F401

        cfg = Config()
        assert cfg.grpc_port == 50051
        assert cfg.policy_default_deny is True

    def test_import_event_bus(self):
        from ellie_ai.event_bus import EventBus  # noqa: F401

        bus = EventBus()
        assert bus.stats.total_published == 0

    def test_import_policy_engine(self):
        from ellie_ai.policy_engine import PolicyDecision, PolicyEngine  # noqa: F401

        assert PolicyEngine is not None
        assert PolicyDecision.ALLOW is not None

    def test_import_tool_broker(self):
        from ellie_ai.tool_broker import ToolBroker  # noqa: F401
        from ellie_ai.tool_registry import ToolRegistry  # noqa: F401

        registry = ToolRegistry()
        broker = ToolBroker(registry)
        assert broker is not None

    def test_import_trigger_engine(self):
        from ellie_ai.trigger_engine import TriggerEngine, TriggerRule  # noqa: F401

        engine = TriggerEngine()
        assert engine.stats.events_received == 0

    def test_import_approval(self):
        from ellie_ai.approval import ApprovalStore  # noqa: F401

        store = ApprovalStore()
        assert len(store.get_pending_requests()) == 0

    def test_import_context_builder(self):
        from ellie_ai.context_builder import ContextBuilder  # noqa: F401

        builder = ContextBuilder()
        ctx = builder.build()
        assert ctx.identity == "Ellie — autonomous multi-device AI assistant"

    def test_import_autonomous_loop(self):
        from ellie_ai.autonomous_loop import AutonomousLoop, LoopPhase  # noqa: F401

        loop = AutonomousLoop()
        result = loop.iterate()
        assert result.phase == LoopPhase.IDLE

    def test_import_planner(self):
        from ellie_ai.planner import Plan, Planner  # noqa: F401

        planner = Planner()
        plan = planner.create_plan("test goal")
        assert plan.goal == "test goal"

    def test_import_audit(self):
        from ellie_ai.audit import AuditEntry, AuditLog  # noqa: F401

        log = AuditLog(path="data/test_audit.jsonl")
        entry = log.log_decision("test", "pc.test", "ALLOW")
        assert entry.decision == "ALLOW"
        log.clear()

    def test_import_scheduler(self):
        from ellie_ai.scheduler import ScheduledTask, Scheduler  # noqa: F401

        sched = Scheduler()
        task = ScheduledTask(task_id="test", name="Test")
        sched.add_task(task)
        assert len(sched.list_tasks()) == 1

    def test_import_agents(self):
        from ellie_ai.agents import ResearchAgent, SelfDevAgent, SupportAgent  # noqa: F401

        assert ResearchAgent() is not None
        assert SupportAgent() is not None
        assert SelfDevAgent() is not None

    def test_import_memory(self):
        from ellie_ai.memory import (  # noqa: F401
            EpisodicMemory,
            ProceduralMemory,
            ReflectionLog,
            SemanticMemory,
        )

        assert EpisodicMemory() is not None
        assert SemanticMemory() is not None
        assert ProceduralMemory() is not None
        assert ReflectionLog() is not None

    def test_import_mind(self):
        from ellie_ai.mind import Desire, Emotion, GoalManager, Identity  # noqa: F401

        assert Identity() is not None
        assert Desire() is not None
        assert Emotion() is not None
        assert GoalManager() is not None


class TestReExports:
    """Verify ellie_ai.__init__ re-exports the public API."""

    def test_event_bus_export(self):
        from ellie_ai import EventBus  # noqa: F401

    def test_policy_engine_export(self):
        from ellie_ai import PolicyDecision, PolicyEngine  # noqa: F401

    def test_tool_broker_export(self):
        from ellie_ai import ToolBroker  # noqa: F401

    def test_tool_registry_export(self):
        from ellie_ai import ToolRegistry  # noqa: F401

    def test_trigger_engine_export(self):
        from ellie_ai import TriggerEngine  # noqa: F401

    def test_approval_export(self):
        from ellie_ai import ApprovalStore  # noqa: F401

    def test_audit_export(self):
        from ellie_ai import AuditLog  # noqa: F401

    def test_config_export(self):
        from ellie_ai import Config  # noqa: F401
