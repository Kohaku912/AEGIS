"""Model Policy — configuration for which LLM models to use per task type.

Defines model profiles with cost, privacy, and capability constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from aegis_ai.llm.router import PrivacyLevel, TaskType


@dataclass
class ModelProfile:
    """Configuration for a specific LLM model."""
    provider: str = "mock"
    model: str = "mock-model"
    max_tokens: int = 2000
    temperature: float = 0.7
    cost_per_1k_tokens: float = 0.0
    privacy_level: PrivacyLevel = PrivacyLevel.INTERNAL
    allowed_task_types: list[TaskType] = field(default_factory=lambda: list(TaskType))
    disallowed_for_sensitive_data: bool = False
    fallback_model: str = ""
    requires_user_confirmation: bool = False


# Default model profiles
DEFAULT_PROFILES: dict[str, ModelProfile] = {
    "mock": ModelProfile(
        provider="mock",
        model="mock-model",
        max_tokens=2000,
        temperature=0.7,
        cost_per_1k_tokens=0.0,
        privacy_level=PrivacyLevel.PUBLIC,
    ),
    "local": ModelProfile(
        provider="openai",
        model="qwen2.5:7b",
        max_tokens=2048,
        temperature=0.7,
        cost_per_1k_tokens=0.0,
        privacy_level=PrivacyLevel.LOCAL_ONLY,
    ),
}

# Task type → model profile mapping
DEFAULT_TASK_MODEL_MAP: dict[TaskType, str] = {
    TaskType.RESEARCH_SUMMARY: "mock",
    TaskType.PLANNING: "mock",
    TaskType.SUPPORT_SUGGESTION: "mock",
    TaskType.SELF_DEV_ANALYSIS: "mock",
    TaskType.CODE_GENERATION: "mock",
    TaskType.REFLECTION: "mock",
    TaskType.MEMORY_SUMMARIZATION: "mock",
    TaskType.CLASSIFICATION: "mock",
    TaskType.SMALL_FAST_TASK: "mock",
    TaskType.HIGH_REASONING_TASK: "mock",
}


class ModelPolicy:
    """Manages model profiles and task-to-model routing.

    Usage:
        policy = ModelPolicy()
        profile = policy.get_profile_for_task(TaskType.PLANNING)
    """

    def __init__(self) -> None:
        self._profiles: dict[str, ModelProfile] = dict(DEFAULT_PROFILES)
        self._task_map: dict[TaskType, str] = dict(DEFAULT_TASK_MODEL_MAP)

    def get_profile_for_task(self, task_type: TaskType) -> ModelProfile:
        """Get the model profile for a given task type."""
        profile_name = self._task_map.get(task_type, "mock")
        return self._profiles.get(profile_name, self._profiles["mock"])

    def set_task_model(self, task_type: TaskType, profile_name: str) -> None:
        """Set which model profile to use for a task type."""
        self._task_map[task_type] = profile_name

    def add_profile(self, name: str, profile: ModelProfile) -> None:
        """Add or update a model profile."""
        self._profiles[name] = profile

    def get_profile(self, name: str) -> ModelProfile | None:
        """Get a model profile by name."""
        return self._profiles.get(name)

    def list_profiles(self) -> dict[str, ModelProfile]:
        """List all model profiles."""
        return dict(self._profiles)

    def list_task_mappings(self) -> dict[TaskType, str]:
        """List all task-to-model mappings."""
        return dict(self._task_map)
