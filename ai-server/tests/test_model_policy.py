"""Tests for Model Policy — model profiles and task-to-model mapping."""

from __future__ import annotations

from aegis_ai.llm.model_policy import DEFAULT_TASK_MODEL_MAP, ModelPolicy, ModelProfile
from aegis_ai.llm.router import PrivacyLevel, TaskType


class TestModelPolicy:
    """Model policy manages model profiles and routing."""

    def test_default_profiles(self):
        """Default profiles include mock and local."""
        policy = ModelPolicy()
        profiles = policy.list_profiles()
        assert "mock" in profiles
        assert "local" in profiles

    def test_get_profile_for_task(self):
        """get_profile_for_task returns correct profile."""
        policy = ModelPolicy()
        profile = policy.get_profile_for_task(TaskType.PLANNING)
        assert profile.provider == "mock"

    def test_set_task_model(self):
        """set_task_model changes routing."""
        policy = ModelPolicy()
        policy.add_profile("custom", ModelProfile(provider="custom", model="custom-model"))
        policy.set_task_model(TaskType.PLANNING, "custom")

        profile = policy.get_profile_for_task(TaskType.PLANNING)
        assert profile.provider == "custom"

    def test_add_profile(self):
        """add_profile adds a new profile."""
        policy = ModelPolicy()
        policy.add_profile("openai", ModelProfile(
            provider="openai",
            model="gpt-4",
            cost_per_1k_tokens=0.03,
        ))
        profile = policy.get_profile("openai")
        assert profile is not None
        assert profile.model == "gpt-4"

    def test_list_task_mappings(self):
        """list_task_mappings returns all mappings."""
        policy = ModelPolicy()
        mappings = policy.list_task_mappings()
        assert len(mappings) == len(TaskType)

    def test_default_task_map(self):
        """Default task map maps all task types to mock."""
        for task_type, profile_name in DEFAULT_TASK_MODEL_MAP.items():
            assert profile_name == "mock"


class TestModelProfile:
    """Model profile has correct defaults."""

    def test_default_profile(self):
        """Default profile has safe values."""
        profile = ModelProfile()
        assert profile.provider == "mock"
        assert profile.privacy_level == PrivacyLevel.INTERNAL
        assert profile.disallowed_for_sensitive_data is False
        assert profile.requires_user_confirmation is False

    def test_sensitive_data_flag(self):
        """Sensitive data flag can be set."""
        profile = ModelProfile(disallowed_for_sensitive_data=True)
        assert profile.disallowed_for_sensitive_data is True
