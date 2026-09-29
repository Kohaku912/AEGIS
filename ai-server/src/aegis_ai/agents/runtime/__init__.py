"""Agent Runtime — AEGIS ↔ Agent 境界層のコア型と Protocol.

Layer 役割:
- `interface.py`: バックエンド共通 Protocol (AgentBackend)
- `models.py`:    AEGIS 内部表現の dataclass (AgentTask / AgentResult / ...)
- `lifecycle.py`: TaskStatus ↔ AgentStatus 変換 (Phase 3)
- `executor.py`:  PlanStep → AgentTask 変換 + AgentBackend 呼び出し (Phase 3)
- `router.py`:    profile → backend 選択 (Phase 5 で実装)

import 境界の不変条件 (instruction.md §8):
- このパッケージは OpenHands / 外部 SDK を一切 import しない。
- バックエンド具象は `aegis_ai/agents/backends/<name>/` 配下に閉じ込める。
- AEGIS 側からは `from aegis_ai.agents.runtime.interface import AgentBackend` のみが許可される。
"""

from aegis_ai.agents.runtime.executor import (  # noqa: F401
    AGENT_CAPABILITY_PREFIX,
    apply_result_to_step,
    build_agent_task,
    build_task_result_summary,
    is_agent_capability,
    run_agent_step,
)
from aegis_ai.agents.runtime.interface import AgentBackend  # noqa: F401
from aegis_ai.agents.runtime.lifecycle import (  # noqa: F401
    agent_result_to_step_results,
    agent_result_to_task_summary,
    backend_status_to_task,
    is_terminal,
    task_status_to_backend,
    validate_transition,
)
from aegis_ai.agents.runtime.models import (  # noqa: F401
    AgentAction,
    AgentError,
    AgentProgress,
    AgentResult,
    AgentTask,
    Artifact,
    MemoryCandidate,
    UsageMetrics,
)
