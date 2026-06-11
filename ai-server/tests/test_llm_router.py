"""Tests for LLM Router — routing, privacy, provider selection."""

from __future__ import annotations

from aegis_ai.llm.providers.mock import MockLLMProvider
from aegis_ai.llm.router import LLMRequest, LLMRouter, PrivacyLevel, TaskType
from aegis_ai.settings.store import SettingsStore

# ═══════════════════════════════════════════════════════════════
# 1. Mock Provider
# ═══════════════════════════════════════════════════════════════


class TestMockProvider:
    """Mock LLM provider returns deterministic responses."""

    def test_generate_returns_response(self):
        """Mock provider returns a valid response."""
        provider = MockLLMProvider()
        response = provider.generate(prompt="Hello")
        assert response.success is True
        assert response.provider_used == "mock"
        assert response.tokens_used > 0

    def test_generate_research_keyword(self):
        """Research keyword triggers research response."""
        provider = MockLLMProvider()
        response = provider.generate(prompt="Research the latest AI news")
        assert "summary" in response.content.lower() or "findings" in response.content.lower()

    def test_generate_plan_keyword(self):
        """Plan keyword triggers planning response."""
        provider = MockLLMProvider()
        response = provider.generate(prompt="Plan the next steps")
        assert "goal" in response.content.lower() or "steps" in response.content.lower()

    def test_call_log(self):
        """Provider logs all calls."""
        provider = MockLLMProvider()
        provider.generate(prompt="Test 1")
        provider.generate(prompt="Test 2")
        assert len(provider.call_log) == 2


# ═══════════════════════════════════════════════════════════════
# 2. Router
# ═══════════════════════════════════════════════════════════════


class TestLLMRouter:
    """LLM Router routes requests to providers."""

    def test_route_to_mock(self):
        """Router routes to mock provider by default."""
        router = LLMRouter()
        router.register_provider("mock", MockLLMProvider())

        request = LLMRequest(
            task_type=TaskType.PLANNING,
            prompt="Plan the next steps",
        )
        response = router.route(request)
        assert response.success is True
        assert response.provider_used == "mock"

    def test_route_local_only(self):
        """LOCAL_ONLY requests only use local/mock providers."""
        router = LLMRouter()
        router.register_provider("mock", MockLLMProvider())

        request = LLMRequest(
            task_type=TaskType.PLANNING,
            prompt="Plan with sensitive data",
            privacy_level=PrivacyLevel.LOCAL_ONLY,
        )
        response = router.route(request)
        assert response.success is True

    def test_route_local_only_no_provider(self):
        """LOCAL_ONLY fails if no local provider available."""
        router = LLMRouter()
        # No mock/local provider registered

        request = LLMRequest(
            task_type=TaskType.PLANNING,
            prompt="Plan",
            privacy_level=PrivacyLevel.LOCAL_ONLY,
        )
        response = router.route(request)
        assert response.success is False
        assert "local" in response.error.lower()

    def test_route_unknown_provider(self):
        """Router returns error for unknown provider."""
        router = LLMRouter()
        router.set_default_provider("nonexistent")

        request = LLMRequest(
            task_type=TaskType.PLANNING,
            prompt="Plan",
        )
        response = router.route(request)
        assert response.success is False

    def test_route_external_disabled(self):
        """External LLM disabled routes to local provider."""
        settings_store = SettingsStore(
            path="data/test_llm_router_settings.json",
            audit_path="data/test_llm_router_settings_audit.jsonl",
        )
        settings = settings_store.get()
        settings.privacy.external_llm_allowed = False
        settings_store.update(settings)

        router = LLMRouter(settings_store=settings_store)
        router.register_provider("mock", MockLLMProvider())
        router.register_provider("openai", MockLLMProvider())  # External

        request = LLMRequest(
            task_type=TaskType.PLANNING,
            prompt="Plan",
        )
        response = router.route(request)
        assert response.success is True
        assert response.provider_used == "mock"  # Should use local


# ═══════════════════════════════════════════════════════════════
# 3. Task Type Routing
# ═══════════════════════════════════════════════════════════════


class TestTaskTypeRouting:
    """Router routes different task types correctly."""

    def test_research_summary(self):
        """Research summary routes correctly."""
        router = LLMRouter()
        router.register_provider("mock", MockLLMProvider())

        request = LLMRequest(task_type=TaskType.RESEARCH_SUMMARY, prompt="Summarize research")
        response = router.route(request)
        assert response.success is True

    def test_planning(self):
        """Planning routes correctly."""
        router = LLMRouter()
        router.register_provider("mock", MockLLMProvider())

        request = LLMRequest(task_type=TaskType.PLANNING, prompt="Plan next steps")
        response = router.route(request)
        assert response.success is True

    def test_code_generation(self):
        """Code generation routes correctly."""
        router = LLMRouter()
        router.register_provider("mock", MockLLMProvider())

        request = LLMRequest(task_type=TaskType.CODE_GENERATION, prompt="Generate code")
        response = router.route(request)
        assert response.success is True

    def test_reflection(self):
        """Reflection routes correctly."""
        router = LLMRouter()
        router.register_provider("mock", MockLLMProvider())

        request = LLMRequest(task_type=TaskType.REFLECTION, prompt="Reflect on results")
        response = router.route(request)
        assert response.success is True
