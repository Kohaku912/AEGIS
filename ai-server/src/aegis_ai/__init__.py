"""AEGIS Core — Central brain of the AEGIS platform.

Package structure:
- aegis_ai.grpc_server: gRPC server with HealthCheck + AIServer service
- aegis_ai.config: Configuration management
- aegis_ai.event_bus: Event ingestion and distribution (→ src/event_bus.py)
- aegis_ai.trigger_engine: Trigger rules → TaskRequest (→ src/trigger_engine.py)
- aegis_ai.policy_engine: Safety enforcement (→ src/policy_engine.py)
- aegis_ai.tool_broker: Capability invocation (→ src/tool_broker.py)
- aegis_ai.tool_registry: Capability/server registration (→ src/tool_registry.py)
- aegis_ai.approval: Approval lifecycle (→ src/approval.py)
- aegis_ai.context_builder: Context assembly for LLM
- aegis_ai.autonomous_loop: Observe→Think→Plan→Act→Verify→Reflect
- aegis_ai.planner: Task decomposition
- aegis_ai.audit: Append-only audit log
- aegis_ai.scheduler: Cron-like scheduled tasks
- aegis_ai.agents: Research, Support, SelfDev agents
- aegis_ai.memory: Episodic, Semantic, Procedural, Reflection memory
- aegis_ai.mind: Identity, Desire, Emotion, Goals
"""

from importlib import import_module


def _optional_reexport(module_name: str, names: tuple[str, ...]) -> None:
    try:
        module = import_module(module_name)
    except (ModuleNotFoundError, ImportError):
        for name in names:
            globals()[name] = None
        return

    try:
        for name in names:
            globals()[name] = getattr(module, name)
    except ImportError:
        for name in names:
            globals()[name] = None


# Re-export core public APIs from existing implementations when their
# runtime dependencies are available.
_optional_reexport("aegis_ai.approval", ("ApprovalRequest", "ApprovalStatus", "ApprovalStore", "ApprovalType"))
_optional_reexport("aegis_ai.audit", ("AuditEntry", "AuditLog"))
_optional_reexport("aegis_ai.capability_registry", ("CapabilityRegistry",))
_optional_reexport("aegis_ai.config", ("Config",))
_optional_reexport("aegis_ai.event_bus", ("EventBus", "EventBusStats"))
_optional_reexport("aegis_ai.grpc_server", ("serve",))
_optional_reexport("aegis_ai.policy_engine", ("PolicyDecision", "PolicyEngine", "PolicyResult"))
_optional_reexport("aegis_ai.tool_broker", ("InvokeResult", "InvokeStatus", "ToolBroker"))
_optional_reexport("aegis_ai.tool_registry", ("ToolRegistry",))
_optional_reexport("aegis_ai.trigger_engine", ("ActionType", "TaskRequest", "TriggerEngine", "TriggerRule"))
