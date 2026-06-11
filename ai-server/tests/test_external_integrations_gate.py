"""Tests for External Integrations Gate — policy, registry, stubs."""

from __future__ import annotations

from aegis_ai.integrations.discord_stub import DiscordStub
from aegis_ai.integrations.email_stub import EmailStub
from aegis_ai.integrations.line_stub import LINEStub
from aegis_ai.integrations.models import IntegrationConfig, IntegrationDirection, IntegrationStatus, IntegrationType
from aegis_ai.integrations.policy import IntegrationPolicy
from aegis_ai.integrations.registry import IntegrationRegistry
from aegis_ai.integrations.webhook_stub import WebhookStub

# ═══════════════════════════════════════════════════════════════
# 1. Integration Registry
# ═══════════════════════════════════════════════════════════════


class TestIntegrationRegistry:
    """Registry manages integration configurations."""

    def test_default_integrations_loaded(self):
        """Default stub integrations are loaded."""
        registry = IntegrationRegistry()
        assert registry.get("line") is not None
        assert registry.get("discord") is not None
        assert registry.get("email") is not None
        assert registry.get("webhook") is not None

    def test_default_disabled(self):
        """All default integrations are disabled."""
        registry = IntegrationRegistry()
        for config in registry.list_all():
            assert config.enabled is False

    def test_default_stub_status(self):
        """All default integrations have STUB status."""
        registry = IntegrationRegistry()
        for config in registry.list_all():
            assert config.status == IntegrationStatus.STUB

    def test_enable_integration(self):
        """Integration can be enabled."""
        registry = IntegrationRegistry()
        assert registry.enable("line") is True
        assert registry.is_enabled("line") is True

    def test_disable_integration(self):
        """Integration can be disabled."""
        registry = IntegrationRegistry()
        registry.enable("line")
        registry.disable("line")
        assert registry.is_enabled("line") is False

    def test_list_enabled(self):
        """list_enabled returns only enabled integrations."""
        registry = IntegrationRegistry()
        registry.enable("line")
        enabled = registry.list_enabled()
        assert len(enabled) == 1
        assert enabled[0].integration_id == "line"

    def test_register_custom(self):
        """Custom integration can be registered."""
        registry = IntegrationRegistry()
        config = IntegrationConfig(
            integration_id="custom",
            type=IntegrationType.WEBHOOK,
            enabled=False,
        )
        registry.register(config)
        assert registry.get("custom") is not None


# ═══════════════════════════════════════════════════════════════
# 2. Integration Policy
# ═══════════════════════════════════════════════════════════════


class TestIntegrationPolicy:
    """Policy enforces safety rules for external integrations."""

    def test_unknown_integration_denied(self):
        """Unknown integration is denied."""
        policy = IntegrationPolicy(registry=IntegrationRegistry())
        result = policy.check_outbound("nonexistent", "send_message")
        assert result["allowed"] is False

    def test_disabled_integration_denied(self):
        """Disabled integration is denied."""
        registry = IntegrationRegistry()
        policy = IntegrationPolicy(registry=registry)
        result = policy.check_outbound("line", "send_message")
        assert result["allowed"] is False

    def test_enabled_outbound_allowed(self):
        """Enabled outbound integration is allowed."""
        registry = IntegrationRegistry()
        registry.enable("line")
        policy = IntegrationPolicy(registry=registry)
        result = policy.check_outbound("line", "custom_action")
        assert result["allowed"] is True

    def test_send_message_requires_approval(self):
        """send_message requires approval."""
        registry = IntegrationRegistry()
        registry.enable("line")
        policy = IntegrationPolicy(registry=registry)
        result = policy.check_outbound("line", "send_message")
        assert result["requires_approval"] is True

    def test_deny_pattern_blocked(self):
        """Deny pattern blocks action."""
        registry = IntegrationRegistry()
        registry.enable("line")
        policy = IntegrationPolicy(registry=registry)
        result = policy.check_outbound("line", "send_dm")
        assert result["allowed"] is False

    def test_inbound_disabled_denied(self):
        """Inbound on disabled integration is denied."""
        policy = IntegrationPolicy(registry=IntegrationRegistry())
        result = policy.check_inbound("line")
        assert result["allowed"] is False

    def test_inbound_enabled_allowed(self):
        """Inbound on enabled integration with BOTH direction is allowed."""
        registry = IntegrationRegistry()
        registry.enable("line")  # LINE has direction=BOTH
        policy = IntegrationPolicy(registry=registry)
        result = policy.check_inbound("line")
        assert result["allowed"] is True


# ═══════════════════════════════════════════════════════════════
# 3. LINE Stub
# ═══════════════════════════════════════════════════════════════


class TestLINEStub:
    """LINE stub does not send real messages."""

    def test_send_returns_stub(self):
        """send_message returns stub response."""
        stub = LINEStub()
        result = stub.send_message("user1", "Hello")
        assert result["success"] is False
        assert result["stub"] is True

    def test_sent_logged(self):
        """Sent messages are logged."""
        stub = LINEStub()
        stub.send_message("user1", "Hello")
        assert len(stub.get_sent()) == 1


# ═══════════════════════════════════════════════════════════════
# 4. Discord Stub
# ═══════════════════════════════════════════════════════════════


class TestDiscordStub:
    """Discord stub does not send real messages."""

    def test_send_returns_stub(self):
        """send_message returns stub response."""
        stub = DiscordStub()
        result = stub.send_message("channel1", "Hello")
        assert result["success"] is False
        assert result["stub"] is True


# ═══════════════════════════════════════════════════════════════
# 5. Email Stub
# ═══════════════════════════════════════════════════════════════


class TestEmailStub:
    """Email stub does not send real emails."""

    def test_send_returns_stub(self):
        """send_email returns stub response."""
        stub = EmailStub()
        result = stub.send_email("test@example.com", "Subject", "Body")
        assert result["success"] is False
        assert result["stub"] is True


# ═══════════════════════════════════════════════════════════════
# 6. Webhook Stub
# ═══════════════════════════════════════════════════════════════


class TestWebhookStub:
    """Webhook stub does not send real webhooks."""

    def test_send_returns_stub(self):
        """send_webhook returns stub response."""
        stub = WebhookStub()
        result = stub.send_webhook("https://example.com/hook", {"data": "test"})
        assert result["success"] is False
        assert result["stub"] is True


# ═══════════════════════════════════════════════════════════════
# 7. E2E Scenarios
# ═══════════════════════════════════════════════════════════════


class TestE2EScenarios:
    """End-to-end integration scenarios."""

    def test_line_disabled_denies_send(self):
        """LINE disabled → send denied."""
        policy = IntegrationPolicy(registry=IntegrationRegistry())
        result = policy.check_outbound("line", "send_message")
        assert result["allowed"] is False

    def test_discord_enabled_outbound_false(self):
        """Discord enabled but outbound denied if direction is wrong."""
        registry = IntegrationRegistry()
        config = registry.get("discord")
        config.enabled = True
        config.direction = IntegrationDirection.INBOUND
        policy = IntegrationPolicy(registry=registry)
        result = policy.check_outbound("discord", "send_message")
        assert result["allowed"] is False

    def test_email_send_requires_approval(self):
        """Email send requires approval."""
        registry = IntegrationRegistry()
        registry.enable("email")
        policy = IntegrationPolicy(registry=registry)
        result = policy.check_outbound("email", "send_email")
        # send_email matches approval pattern
        assert result["allowed"] is True
        assert result["requires_approval"] is True

    def test_unknown_integration_denied(self):
        """Unknown integration is denied."""
        policy = IntegrationPolicy(registry=IntegrationRegistry())
        result = policy.check_outbound("unknown_service", "send_message")
        assert result["allowed"] is False

    def test_stub_integration_no_real_send(self):
        """Stub integration does not send real messages."""
        stub = LINEStub()
        result = stub.send_message("user1", "Hello")
        assert result["stub"] is True
        assert result["success"] is False
