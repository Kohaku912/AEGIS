"""Tests for OS Notification Provider."""

from __future__ import annotations

import pytest

from aegis_ai.notification.os_provider import OsNotificationProvider


class TestOsNotificationProvider:
    """OS notification provider tests."""

    def test_provider_creation(self):
        """Provider can be created."""
        provider = OsNotificationProvider()
        assert provider is not None

    def test_platform_detection(self):
        """Platform is detected."""
        provider = OsNotificationProvider()
        assert provider._platform in ("windows", "darwin", "linux")

    def test_send_logs_on_failure(self):
        """Falls back to logging when notification fails."""
        provider = OsNotificationProvider()
        # This should not raise even if notification fails
        result = provider.send("Test Title", "Test body")
        assert isinstance(result, bool)
