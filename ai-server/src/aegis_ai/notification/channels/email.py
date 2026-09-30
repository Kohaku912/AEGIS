"""Email notification channel — SMTP submission, through the egress gate.

The destination is ``smtp://host:port``. An SMTP server on the LAN (RFC1918, a single-label
hostname, ``.local``) is a **local** destination by the gate's own definition, so it needs no
permission — that is the constraint working as written, not a hole: the rule is about user
information leaving the *local environment*. A public mail host does need permission.

The password is read at send time and never placed in a result, a log line, or an error
string. See :mod:`aegis_ai.notification.channels.outbound`.
"""

from __future__ import annotations

import logging
from typing import Any

from aegis_ai.notification.channels.outbound import OutboundChannel, Transport
from aegis_ai.notification.models import Notification

logger = logging.getLogger("aegis_ai.notification.channels.email")

HOST_ENV = "AEGIS_SMTP_HOST"
PORT_ENV = "AEGIS_SMTP_PORT"
USER_ENV = "AEGIS_SMTP_USER"
PASSWORD_ENV = "AEGIS_SMTP_PASSWORD"
FROM_ENV = "AEGIS_SMTP_FROM"
TO_ENV = "AEGIS_SMTP_TO"

_DEFAULT_PORT = 587

#: Ports that already speak TLS, and so must not be upgraded with STARTTLS.
_IMPLICIT_TLS_PORTS = frozenset({465})
_NO_STARTTLS_PORTS = frozenset({25})


def _smtp_send(
    notification: Notification,
    *,
    host: str,
    port: int,
    user: str,
    password: str,
    sender: str,
    recipient: str,
    timeout: float,
) -> tuple[bool, int, str]:
    """Submit one message. Returns ``(success, status_code, error)``.

    ``status_code`` is SMTP's numeric reply, or 0 when the connection never got that far.
    """
    import smtplib
    from email.message import EmailMessage

    message = EmailMessage()
    message["Subject"] = notification.title or "(no subject)"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(notification.body or "")

    client: Any = None
    try:
        if port in _IMPLICIT_TLS_PORTS:
            client = smtplib.SMTP_SSL(host, port, timeout=timeout)
        else:
            client = smtplib.SMTP(host, port, timeout=timeout)
            if port not in _NO_STARTTLS_PORTS:
                client.starttls()
        if user:
            client.login(user, password)
        client.send_message(message)
        return True, 250, ""
    except smtplib.SMTPResponseException as exc:
        # `exc.smtp_error` is the server's reply text — no credentials in it.
        return False, int(exc.smtp_code or 0), f"SMTP {exc.smtp_code}"
    except smtplib.SMTPException as exc:
        return False, 0, f"SMTP failure: {type(exc).__name__}"
    except OSError as exc:
        return False, 0, f"connection failed: {type(exc).__name__}"
    finally:
        if client is not None:
            try:
                client.quit()
            except Exception:
                pass


class EmailNotificationChannel(OutboundChannel):
    """Sends notifications by email over SMTP.

    Usage:
        channel = EmailNotificationChannel()
        result = channel.send(notification)   # refused unless the gate permits the host
    """

    purpose = "messaging.email"
    label = "email"
    required_env = (HOST_ENV, TO_ENV)

    def __init__(self, *, timeout_seconds: float = 20.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._timeout = timeout_seconds

    def _port(self) -> int:
        raw = self.setting(PORT_ENV)
        try:
            return int(raw) if raw else _DEFAULT_PORT
        except ValueError:
            return _DEFAULT_PORT

    def destination(self) -> str:
        host = self.setting(HOST_ENV)
        if not host:
            return ""
        return f"smtp://{host}:{self._port()}"

    def _default_transport(self) -> Transport | None:
        return lambda _destination, notification: _smtp_send(
            notification,
            host=self.setting(HOST_ENV),
            port=self._port(),
            user=self.setting(USER_ENV),
            password=self.setting(PASSWORD_ENV),
            sender=self.setting(FROM_ENV) or self.setting(USER_ENV) or self.setting(TO_ENV),
            recipient=self.setting(TO_ENV),
            timeout=self._timeout,
        )
