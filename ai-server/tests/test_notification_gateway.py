"""Tests for Notification Gateway — models, router, channels, preferences, quiet hours, digest."""

from __future__ import annotations

import time

from aegis_ai.notification.channels.cli import CLINotificationChannel
from aegis_ai.notification.channels.dashboard import DashboardNotificationChannel
from aegis_ai.notification.channels.web_chat import WebChatNotificationChannel
from aegis_ai.notification.digest import NotificationDigest
from aegis_ai.notification.models import Notification, NotificationChannel, NotificationSeverity, NotificationType
from aegis_ai.notification.preferences import NotificationPreferences
from aegis_ai.notification.quiet_hours import QuietHoursManager
from aegis_ai.notification.router import NotificationRouter

# ── Helpers ──────────────────────────────────────────────────


def _make_notification(
    ntype: NotificationType = NotificationType.SUPPORT_SUGGESTION,
    severity: NotificationSeverity = NotificationSeverity.NORMAL,
    channels: list[NotificationChannel] | None = None,
) -> Notification:
    return Notification(
        notification_id=f"notif_{int(time.time() * 1000)}",
        type=ntype,
        title=f"Test {ntype.name}",
        body="Test body",
        severity=severity,
        channels=channels or [NotificationChannel.DASHBOARD],
        created_at_ms=int(time.time() * 1000),
    )


# ═══════════════════════════════════════════════════════════════
# 1. Notification Model
# ═══════════════════════════════════════════════════════════════


class TestNotificationModel:
    """Notification model has correct fields."""

    def test_notification_creation(self):
        """Notification can be created."""
        n = _make_notification()
        assert n.title != ""
        assert n.severity == NotificationSeverity.NORMAL

    def test_severity_map(self):
        """Default severity map covers all types."""
        from aegis_ai.notification.models import DEFAULT_SEVERITY_MAP
        for ntype in NotificationType:
            assert ntype in DEFAULT_SEVERITY_MAP

    def test_channel_map(self):
        """Default channel map covers all severities."""
        from aegis_ai.notification.models import DEFAULT_CHANNEL_MAP
        for sev in NotificationSeverity:
            assert sev in DEFAULT_CHANNEL_MAP


# ═══════════════════════════════════════════════════════════════
# 2. Notification Router
# ═══════════════════════════════════════════════════════════════


class TestNotificationRouter:
    """Router sends notifications to channels."""

    def test_send_to_dashboard(self):
        """Notification is sent to dashboard channel."""
        dashboard = DashboardNotificationChannel()
        router = NotificationRouter(dashboard_channel=dashboard)
        n = _make_notification(channels=[NotificationChannel.DASHBOARD])
        assert router.send(n) is True
        assert len(dashboard.get_recent()) == 1

    def test_send_to_web_chat(self):
        """Notification is sent to web chat channel."""
        web_chat = WebChatNotificationChannel()
        router = NotificationRouter(web_chat_channel=web_chat)
        n = _make_notification(channels=[NotificationChannel.WEB_CHAT])
        assert router.send(n) is True
        assert len(web_chat.get_sent()) == 1

    def test_send_to_cli(self):
        """Notification is sent to CLI channel."""
        cli = CLINotificationChannel()
        router = NotificationRouter(cli_channel=cli)
        n = _make_notification(channels=[NotificationChannel.CLI])
        assert router.send(n) is True
        assert len(cli.get_sent()) == 1

    def test_disabled_type_not_sent(self):
        """Disabled notification type is not sent."""
        dashboard = DashboardNotificationChannel()
        prefs = NotificationPreferences()
        prefs.set_enabled(NotificationType.SUPPORT_SUGGESTION, False)
        router = NotificationRouter(dashboard_channel=dashboard, preferences=prefs)
        n = _make_notification(ntype=NotificationType.SUPPORT_SUGGESTION)
        assert router.send(n) is False
        assert len(dashboard.get_recent()) == 0

    def test_severity_routing(self):
        """Critical notifications go to all channels."""
        dashboard = DashboardNotificationChannel()
        web_chat = WebChatNotificationChannel()
        cli = CLINotificationChannel()
        router = NotificationRouter(
            dashboard_channel=dashboard,
            web_chat_channel=web_chat,
            cli_channel=cli,
        )
        n = _make_notification(severity=NotificationSeverity.CRITICAL)
        n.channels = []  # Use default routing
        router.send(n)
        assert len(dashboard.get_recent()) == 1
        assert len(web_chat.get_sent()) == 1
        assert len(cli.get_sent()) == 1

    def test_sent_count_tracked(self):
        """Sent counts are tracked."""
        dashboard = DashboardNotificationChannel()
        router = NotificationRouter(dashboard_channel=dashboard)
        n = _make_notification(channels=[NotificationChannel.DASHBOARD])
        router.send(n)
        router.send(n)
        assert router.get_sent_count(NotificationType.SUPPORT_SUGGESTION) == 2


# ═══════════════════════════════════════════════════════════════
# 3. Notification Preferences
# ═══════════════════════════════════════════════════════════════


class TestNotificationPreferences:
    """Preferences control which notifications are enabled."""

    def test_default_all_enabled(self):
        """All notification types are enabled by default."""
        prefs = NotificationPreferences()
        for ntype in NotificationType:
            assert prefs.is_type_enabled(ntype) is True

    def test_disable_type(self):
        """Disabled type returns False."""
        prefs = NotificationPreferences()
        prefs.set_enabled(NotificationType.DAILY_BRIEFING, False)
        assert prefs.is_type_enabled(NotificationType.DAILY_BRIEFING) is False

    def test_re_enable_type(self):
        """Re-enabled type returns True."""
        prefs = NotificationPreferences()
        prefs.set_enabled(NotificationType.DAILY_BRIEFING, False)
        prefs.set_enabled(NotificationType.DAILY_BRIEFING, True)
        assert prefs.is_type_enabled(NotificationType.DAILY_BRIEFING) is True


# ═══════════════════════════════════════════════════════════════
# 4. Quiet Hours
# ═══════════════════════════════════════════════════════════════


class TestQuietHours:
    """Quiet hours defers non-critical notifications."""

    def test_quiet_hours_disabled(self):
        """When disabled, is_quiet returns False."""
        qh = QuietHoursManager(enabled=False)
        assert qh.is_quiet() is False

    def test_quiet_hours_enabled(self):
        """When enabled, is_quiet checks time."""
        qh = QuietHoursManager(enabled=True, start="00:00", end="23:59")
        assert qh.is_quiet() is True


# ═══════════════════════════════════════════════════════════════
# 5. Digest
# ═══════════════════════════════════════════════════════════════


class TestNotificationDigest:
    """Digest batches deferred notifications."""

    def test_defer_and_count(self):
        """Deferred notifications are counted."""
        digest = NotificationDigest()
        digest.defer(_make_notification())
        digest.defer(_make_notification())
        assert digest.count() == 2

    def test_generate_summary(self):
        """Summary includes counts by type."""
        digest = NotificationDigest()
        digest.defer(_make_notification(ntype=NotificationType.SUPPORT_SUGGESTION))
        digest.defer(_make_notification(ntype=NotificationType.RESEARCH_COMPLETED))
        summary = digest.generate_summary()
        assert summary["count"] == 2
        assert "SUPPORT_SUGGESTION" in summary["by_type"]

    def test_drain(self):
        """Drain returns and clears deferred notifications."""
        digest = NotificationDigest()
        digest.defer(_make_notification())
        items = digest.drain()
        assert len(items) == 1
        assert digest.count() == 0

    def test_empty_summary(self):
        """Empty digest returns no deferred message."""
        digest = NotificationDigest()
        summary = digest.generate_summary()
        assert summary["count"] == 0


# ═══════════════════════════════════════════════════════════════
# 6. Dashboard Channel
# ═══════════════════════════════════════════════════════════════


class TestDashboardChannel:
    """Dashboard channel stores notifications."""

    def test_send_and_get(self):
        """Notifications are stored and retrievable."""
        channel = DashboardNotificationChannel()
        channel.send(_make_notification())
        assert len(channel.get_recent()) == 1

    def test_clear(self):
        """Clear removes all notifications."""
        channel = DashboardNotificationChannel()
        channel.send(_make_notification())
        channel.clear()
        assert len(channel.get_recent()) == 0


# ═══════════════════════════════════════════════════════════════
# 7. Web Chat Channel
# ═══════════════════════════════════════════════════════════════


class TestWebChatChannel:
    """Web Chat channel sends notifications."""

    def test_send(self):
        """Notification is sent."""
        channel = WebChatNotificationChannel()
        channel.send(_make_notification())
        assert len(channel.get_sent()) == 1


# ═══════════════════════════════════════════════════════════════
# 8. CLI Channel
# ═══════════════════════════════════════════════════════════════


class TestCLIChannel:
    """CLI channel displays notifications."""

    def test_send(self):
        """Notification is sent."""
        channel = CLINotificationChannel()
        channel.send(_make_notification())
        assert len(channel.get_sent()) == 1
