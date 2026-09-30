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
- LineNotificationChannel / DiscordNotificationChannel / EmailNotificationChannel: external
  channels, each refused by the egress gate unless the user has permitted its host
"""

from aegis_ai.notification.channels.cli import CLINotificationChannel  # noqa: F401
from aegis_ai.notification.channels.dashboard import DashboardNotificationChannel  # noqa: F401
from aegis_ai.notification.channels.discord import DiscordNotificationChannel  # noqa: F401
from aegis_ai.notification.channels.email import EmailNotificationChannel  # noqa: F401
from aegis_ai.notification.channels.line import LineNotificationChannel  # noqa: F401
from aegis_ai.notification.channels.outbound import (  # noqa: F401
    OutboundChannel,
    OutboundSendResult,
)
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
