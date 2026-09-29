"""AEGIS specialized agents (research, support, self-dev) and agent runtime.

Public API (instruction.md §8):
- `runtime.interface.AgentBackend` — AEGIS ↔ Agent 境界 Protocol
- `runtime.models.AgentTask / AgentResult / ...` — 境界をまたぐ dataclass
- `runtime.router.AgentRouter` — Profile 選択ロジック (Phase 5)
- `profiles.models.AgentProfile` — declarative profile
- `profiles.registry.AgentProfileRegistry` — YAML loader
- `backends.local.LocalBackend` — Phase 1 ローカル subprocess backend

import 境界の不変条件 (instruction.md §8):
- OpenHands / 外部 SDK はこのパッケージの **外側** に置かない.
- AEGIS 本体からは `from aegis_ai.agents.runtime.interface import AgentBackend` のみ.
"""
from aegis_ai.agents.backends import (
    get_backend,
    list_backends,
    register_backend,
)
from aegis_ai.agents.profiles import (
    AgentProfile,
    AgentProfileRegistry,
    AgentRiskCeiling,
    RoutingDecision,
    WorkspaceKind,
)
from aegis_ai.agents.runtime.interface import AgentBackend
from aegis_ai.agents.runtime.models import (
    AgentAction,
    AgentError,
    AgentProgress,
    AgentResult,
    AgentTask,
    Artifact,
    MemoryCandidate,
    UsageMetrics,
)
from aegis_ai.agents.runtime.router import AgentRouter

__all__ = [
    "AgentAction",
    "AgentBackend",
    "AgentError",
    "AgentProfile",
    "AgentProfileRegistry",
    "AgentProgress",
    "AgentResult",
    "AgentRiskCeiling",
    "AgentRouter",
    "AgentTask",
    "Artifact",
    "MemoryCandidate",
    "RoutingDecision",
    "UsageMetrics",
    "WorkspaceKind",
    "get_backend",
    "list_backends",
    "register_backend",
]
