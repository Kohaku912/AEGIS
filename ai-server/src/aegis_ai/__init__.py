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

# Re-export core public APIs from existing implementations
from aegis_ai.approval import (  # noqa: F401
    ApprovalRequest,
    ApprovalStatus,
    ApprovalStore,
    ApprovalType,
)
from aegis_ai.audit import AuditEntry, AuditLog  # noqa: F401
from aegis_ai.capability_registry import CapabilityRegistry  # noqa: F401
from aegis_ai.config import Config  # noqa: F401
from aegis_ai.event_bus import EventBus, EventBusStats  # noqa: F401
from aegis_ai.grpc_server import serve  # noqa: F401
from aegis_ai.policy_engine import PolicyDecision, PolicyEngine, PolicyResult  # noqa: F401
from aegis_ai.tool_broker import InvokeResult, InvokeStatus, ToolBroker  # noqa: F401
from aegis_ai.tool_registry import ToolRegistry  # noqa: F401
from aegis_ai.trigger_engine import (  # noqa: F401
    ActionType,
    TaskRequest,
    TriggerEngine,
    TriggerRule,
)
