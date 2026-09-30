"""LINE notification channel — LINE Messaging API push, through the egress gate.

A message body is the user's own content, so it may only leave with the user's permission.
Two paths exist, both enforced by the gate: the **standing** one needs
``privacy.external_messaging_allowed`` **and** ``api.line.me`` in
``privacy.egress_allowed_hosts``; the narrower one is a recorded
``(api.line.me, messaging.line)`` grant. Neither is checked here — this module asks the gate
and obeys it. See :mod:`aegis_ai.notification.channels.outbound`.
"""

from __future__ import annotations

from typing import Any

from aegis_ai.notification.channels.outbound import OutboundChannel, Transport
from aegis_ai.notification.models import Notification

#: The origin the gate is asked about. The path is not part of the permission.
LINE_ORIGIN = "https://api.line.me"

_PUSH_PATH = "/v2/bot/message/push"

#: LINE caps a single text message at 5000 characters.
_MAX_BODY = 5000

TOKEN_ENV = "AEGIS_LINE_CHANNEL_ACCESS_TOKEN"
TO_ENV = "AEGIS_LINE_TO"


def _line_push(
    origin: str, notification: Notification, *, token: str, to: str, timeout: float
) -> tuple[bool, int, str]:
    """POST one text message to LINE. Returns ``(success, status_code, error)``."""
    import httpx

    response = httpx.post(
        f"{origin}{_PUSH_PATH}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "to": to,
            "messages": [{"type": "text", "text": notification.body[:_MAX_BODY]}],
        },
        timeout=timeout,
    )
    ok = 200 <= response.status_code < 300
    return ok, response.status_code, "" if ok else f"HTTP {response.status_code}"


class LineNotificationChannel(OutboundChannel):
    """Sends notifications to LINE via the Messaging API push endpoint.

    Usage:
        channel = LineNotificationChannel()
        result = channel.send(notification)   # refused unless the gate permits the host
    """

    purpose = "messaging.line"
    label = "line"
    required_env = (TOKEN_ENV, TO_ENV)

    def __init__(self, *, timeout_seconds: float = 15.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._timeout = timeout_seconds

    def destination(self) -> str:
        return LINE_ORIGIN

    def _default_transport(self) -> Transport | None:
        return lambda destination, notification: _line_push(
            destination,
            notification,
            token=self.setting(TOKEN_ENV),
            to=self.setting(TO_ENV),
            timeout=self._timeout,
        )
