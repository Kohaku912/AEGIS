"""Self-Development — sandbox-based self-improvement for AEGIS."""

from aegis_ai.self_development.sandbox_manager import SandboxManager
from aegis_ai.self_development.self_development_controller import SelfDevelopmentController
from aegis_ai.self_development.self_development_types import (
    CommandPolicy,
    CommandRequest,
    CommandResult,
    SandboxInfo,
    SelfDevelopmentResult,
    SelfDevelopmentTask,
    SelfDevSource,
    SelfDevStatus,
    classify_command,
    is_secret_path,
)

__all__ = [
    "CommandPolicy",
    "CommandRequest",
    "CommandResult",
    "SandboxInfo",
    "SandboxManager",
    "SelfDevelopmentController",
    "SelfDevelopmentResult",
    "SelfDevelopmentTask",
    "SelfDevSource",
    "SelfDevStatus",
    "classify_command",
    "is_secret_path",
]
