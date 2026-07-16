"""Tests for the OS notification channel."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

from aegis_ai.notification.channels.os_notification import OSNotificationChannel
from aegis_ai.notification.models import Notification, NotificationSeverity


class TestOSNotificationChannel:
    def test_send_logs_notification(self, caplog):
        caplog.set_level(logging.DEBUG)
        channel = OSNotificationChannel()
        notification = Notification(
            title="Test",
            body="Hello",
            severity=NotificationSeverity.NORMAL,
        )
        channel.send(notification)
        assert "Test" in caplog.text
        assert "Hello" in caplog.text

    def test_send_via_pc_overlay(self):
        mock_pc = MagicMock()
        channel = OSNotificationChannel(pc_server_client=mock_pc)
        notification = Notification(
            title="Alert",
            body="Something happened",
            severity=NotificationSeverity.HIGH,
        )
        channel.send(notification)
        mock_pc.show_overlay.assert_called_once()
        call_kwargs = mock_pc.show_overlay.call_args
        assert "Alert" in call_kwargs.kwargs.get("text", call_kwargs[1].get("text", ""))

    def test_send_no_body(self):
        mock_pc = MagicMock()
        channel = OSNotificationChannel(pc_server_client=mock_pc)
        notification = Notification(
            title="Simple",
            body="",
            severity=NotificationSeverity.LOW,
        )
        channel.send(notification)
        call_kwargs = mock_pc.show_overlay.call_args
        text = call_kwargs.kwargs.get("text", call_kwargs[1].get("text", ""))
        assert text == "Simple"

    def test_send_pc_failure_graceful(self, caplog):
        caplog.set_level(logging.DEBUG)
        mock_pc = MagicMock()
        mock_pc.show_overlay.side_effect = Exception("PC offline")
        channel = OSNotificationChannel(pc_server_client=mock_pc)
        notification = Notification(title="Test", body="Body", severity=NotificationSeverity.NORMAL)
        channel.send(notification)
        assert "PC overlay delivery failed" in caplog.text
