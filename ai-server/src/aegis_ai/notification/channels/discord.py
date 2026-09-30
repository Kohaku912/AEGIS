"""Discord notification channel — webhook POST, through the egress gate.

**The webhook URL contains the token**, so :meth:`destination` reports only the origin
(``https://discord.com``) and the full URL never reaches a result, a log line, or the audit
trail — those are all reported to the caller and persisted. The gate's permission is per-host,
which is the granularity the rest of AEGIS uses, so asking about the origin loses no
enforcement.

A webhook on the LAN (``http://192.168.x.x/hook``) is a **local** destination by the gate's
own definition and needs no permission; anything public does.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from aegis_ai.notification.channels.outbound import OutboundChannel, Transport
from aegis_ai.notification.models import Notification

#: Discord caps webhook content at 2000 characters.
_MAX_BODY = 2000

WEBHOOK_ENV = "AEGIS_DISCORD_WEBHOOK_URL"


def _discord_post(
    url: str, notification: Notification, *, timeout: float
) -> tuple[bool, int, str]:
    """POST one message to the Discord webhook. Returns ``(success, status_code, error)``."""
    import httpx

    response = httpx.post(
        url,
        json={"content": notification.body[:_MAX_BODY]},
        timeout=timeout,
    )
    ok = 200 <= response.status_code < 300
    return ok, response.status_code, "" if ok else f"HTTP {response.status_code}"


class DiscordNotificationChannel(OutboundChannel):
    """Sends notifications to Discord through a channel webhook.

    Usage:
        channel = DiscordNotificationChannel()
        result = channel.send(notification)   # refused unless the gate permits the host
    """

    purpose = "messaging.discord"
    label = "discord"
    required_env = (WEBHOOK_ENV,)

    def __init__(self, *, timeout_seconds: float = 15.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._timeout = timeout_seconds

    def destination(self) -> str:
        """The webhook's origin only — never the full URL, which carries the token."""
        url = self.setting(WEBHOOK_ENV)
        if not url:
            return ""
        parts = urlsplit(url)
        if not parts.scheme or not parts.hostname:
            return ""
        return f"{parts.scheme}://{parts.hostname}"

    def _default_transport(self) -> Transport | None:
        return lambda _destination, notification: _discord_post(
            self.setting(WEBHOOK_ENV), notification, timeout=self._timeout
        )
