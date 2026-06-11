"""Ellie AI Server — Central brain of the AEGIS platform.

Package structure:
- ellie_ai.grpc_server: gRPC server with HealthCheck + AIServer service
- ellie_ai.config: Configuration management
- ellie_ai.event_bus: Event ingestion and distribution (→ src/event_bus.py)
- ellie_ai.trigger_engine: Trigger rules → TaskRequest (→ src/trigger_engine.py)
- ellie_ai.policy_engine: Safety enforcement (→ src/policy_engine.py)
- ellie_ai.tool_broker: Capability invocation (→ src/tool_broker.py)
- ellie_ai.tool_registry: Capability/server registration (→ src/tool_registry.py)
- ellie_ai.approval: Approval lifecycle (→ src/approval.py)
- ellie_ai.context_builder: Context assembly for LLM
- ellie_ai.autonomous_loop: Observe→Think→Plan→Act→Verify→Reflect
- ellie_ai.planner: Task decomposition
- ellie_ai.audit: Append-only audit log
- ellie_ai.scheduler: Cron-like scheduled tasks
- ellie_ai.agents: Research, Support, SelfDev agents
- ellie_ai.memory: Episodic, Semantic, Procedural, Reflection memory
- ellie_ai.mind: Identity, Desire, Emotion, Goals
"""

# Re-export core public APIs from existing implementations
from ellie_ai.approval import (  # noqa: F401
    ApprovalRequest,
    ApprovalStatus,
    ApprovalStore,
    ApprovalType,
)
from ellie_ai.audit import AuditEntry, AuditLog  # noqa: F401
from ellie_ai.config import Config  # noqa: F401
from ellie_ai.event_bus import EventBus, EventBusStats  # noqa: F401
from ellie_ai.grpc_server import serve  # noqa: F401
from ellie_ai.policy_engine import PolicyDecision, PolicyEngine, PolicyResult  # noqa: F401
from ellie_ai.tool_broker import InvokeResult, InvokeStatus, ToolBroker  # noqa: F401
from ellie_ai.tool_registry import ToolRegistry  # noqa: F401
from ellie_ai.trigger_engine import (  # noqa: F401
    ActionType,
    TaskRequest,
    TriggerEngine,
    TriggerRule,
)
