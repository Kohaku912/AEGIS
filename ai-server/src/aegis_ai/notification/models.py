"""Notification models — defines notification types and structure."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class NotificationType(Enum):
    """Types of notifications AEGIS can send."""
    APPROVAL_REQUIRED = auto()
    SUPPORT_SUGGESTION = auto()
    RESEARCH_COMPLETED = auto()
    RESEARCH_FAILED = auto()
    SERVER_DISCONNECTED = auto()
    PERMISSION_MISSING = auto()
    SELF_DEV_PROPOSAL = auto()
    SELF_DEV_TEST_FAILED = auto()
    ROOM_ALERT = auto()
    SECURITY_ALERT = auto()
    DAILY_BRIEFING = auto()
    BUDGET_WARNING = auto()


class NotificationSeverity(Enum):
    """Notification severity levels."""
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    CRITICAL = auto()


class NotificationChannel(Enum):
    """Channels for delivering notifications."""
    DASHBOARD = auto()
    WEB_CHAT = auto()
    CLI = auto()
    LINE = auto()        # Stub only
    DISCORD = auto()     # Stub only
    EMAIL = auto()       # Stub only
    OS_NOTIFICATION = auto()  # Stub only


@dataclass
class Notification:
    """A notification to send to the user."""
    notification_id: str = ""
    type: NotificationType = NotificationType.SUPPORT_SUGGESTION
    title: str = ""
    body: str = ""
    severity: NotificationSeverity = NotificationSeverity.NORMAL
    source: str = ""
    related_task_id: str = ""
    related_approval_id: str = ""
    created_at_ms: int = 0
    expires_at_ms: int = 0
    channels: list[NotificationChannel] = field(default_factory=list)
    requires_user_action: bool = False
    privacy_level: str = "internal"
    metadata: dict[str, Any] = field(default_factory=dict)


# Default severity mapping
DEFAULT_SEVERITY_MAP: dict[NotificationType, NotificationSeverity] = {
    NotificationType.APPROVAL_REQUIRED: NotificationSeverity.HIGH,
    NotificationType.SUPPORT_SUGGESTION: NotificationSeverity.NORMAL,
    NotificationType.RESEARCH_COMPLETED: NotificationSeverity.LOW,
    NotificationType.RESEARCH_FAILED: NotificationSeverity.HIGH,
    NotificationType.SERVER_DISCONNECTED: NotificationSeverity.HIGH,
    NotificationType.PERMISSION_MISSING: NotificationSeverity.HIGH,
    NotificationType.SELF_DEV_PROPOSAL: NotificationSeverity.NORMAL,
    NotificationType.SELF_DEV_TEST_FAILED: NotificationSeverity.HIGH,
    NotificationType.ROOM_ALERT: NotificationSeverity.CRITICAL,
    NotificationType.SECURITY_ALERT: NotificationSeverity.CRITICAL,
    NotificationType.DAILY_BRIEFING: NotificationSeverity.LOW,
    NotificationType.BUDGET_WARNING: NotificationSeverity.HIGH,
}

_CRITICAL_CHANNELS = [
    NotificationChannel.DASHBOARD,
    NotificationChannel.WEB_CHAT,
    NotificationChannel.CLI,
]

# Default channel routing by severity
DEFAULT_CHANNEL_MAP: dict[NotificationSeverity, list[NotificationChannel]] = {
    NotificationSeverity.LOW: [NotificationChannel.DASHBOARD],
    NotificationSeverity.NORMAL: [NotificationChannel.DASHBOARD, NotificationChannel.WEB_CHAT],
    NotificationSeverity.HIGH: [NotificationChannel.DASHBOARD, NotificationChannel.WEB_CHAT, NotificationChannel.CLI],
    NotificationSeverity.CRITICAL: _CRITICAL_CHANNELS,
}
