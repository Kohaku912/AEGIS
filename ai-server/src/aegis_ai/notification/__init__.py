"""Notification Gateway — outbound communication for AEGIS.

Provides:
- Notification: Notification model
- NotificationRouter: Routes notifications to channels
- NotificationPreferences: User-configurable preferences
- QuietHoursManager: Quiet hours management
- NotificationDigest: Deferred notification batching
- DashboardNotificationChannel: Dashboard notifications
- WebChatNotificationChannel: Web chat notifications
- CLINotificationChannel: CLI notifications
"""

from aegis_ai.notification.channels.cli import CLINotificationChannel  # noqa: F401
from aegis_ai.notification.channels.dashboard import DashboardNotificationChannel  # noqa: F401
from aegis_ai.notification.channels.web_chat import WebChatNotificationChannel  # noqa: F401
from aegis_ai.notification.digest import NotificationDigest  # noqa: F401
from aegis_ai.notification.models import (  # noqa: F401
    Notification,
    NotificationChannel,
    NotificationSeverity,
    NotificationType,
)
from aegis_ai.notification.preferences import NotificationPreferences  # noqa: F401
from aegis_ai.notification.quiet_hours import QuietHoursManager  # noqa: F401
from aegis_ai.notification.router import NotificationRouter  # noqa: F401
