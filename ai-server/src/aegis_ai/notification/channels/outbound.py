"""Shared machinery for notification channels that send **outside** the local environment.

LINE, Discord and Email all carry the same two obligations, and they are enforced here
rather than re-implemented three times:

1. **The egress gate decides.** A channel never calls its transport before the gate has
   allowed the destination, and the gate is always consulted with
   ``carries_user_information=True`` — a notification body is the user's own content, so it
   is never a "connection carrying no user information". There is no parameter that skips
   the check, and no channel overrides :meth:`OutboundChannel.send`.

2. **Secrets stay in the process.** Credentials are read from the environment at send time
   and are never placed in a result, a log line, or an exception message. This is why
   :meth:`OutboundChannel.destination` returns the *origin* and not the full webhook URL for
   Discord: the URL contains the token, and the destination is reported to the caller and
   written to the audit trail.

The transport is injectable so that the *decision* can be tested without a network call —
in particular so a test can assert the transport was **not** called when the gate refused.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from aegis_ai.notification.models import Notification

logger = logging.getLogger("aegis_ai.notification.channels.outbound")

#: A transport takes ``(destination, notification)`` and returns
#: ``(success, status_code, error)``. It must not raise for an ordinary failure.
Transport = Callable[[str, Notification], "tuple[bool, int, str]"]


@dataclass
class OutboundSendResult:
    """What happened to one outbound notification."""

    channel: str = ""
    destination: str = ""
    success: bool = False
    status_code: int = 0
    error: str = ""
    duration_ms: float = 0.0
    #: True when the egress gate refused, so the transport was never called.
    refused_by_gate: bool = False

    @property
    def attempted(self) -> bool:
        """False when the gate refused — nothing left the process."""
        return not self.refused_by_gate


class OutboundChannel:
    """Base for LINE / Discord / Email notification channels.

    Subclasses supply :attr:`purpose`, :attr:`label`, :attr:`required_env`, a
    :meth:`destination`, and a default transport.
    """

    #: Egress purpose. The gate maps the head (before the first dot) to a settings flag,
    #: so every outbound channel here must use a ``messaging.*`` purpose.
    purpose: str = ""
    #: Short label used in results and logs.
    label: str = ""
    #: Environment variables that must be set before a send is attempted.
    required_env: tuple[str, ...] = ()

    def __init__(
        self,
        *,
        env: Mapping[str, str] | None = None,
        transport: Transport | None = None,
        egress_gate: Any = None,
    ) -> None:
        self._env: Mapping[str, str] = os.environ if env is None else env
        self._transport = transport
        self._gate = egress_gate

    # ── Configuration ────────────────────────────────────────────────────────

    def setting(self, name: str) -> str:
        """Read a configuration value. Subclasses use this instead of ``os.environ``."""
        return str(self._env.get(name) or "").strip()

    def missing_configuration(self) -> list[str]:
        """Names of the environment variables this channel still needs."""
        return [name for name in self.required_env if not self.setting(name)]

    def destination(self) -> str:
        """The destination the gate is asked about. ``""`` when unconfigured.

        Must be the origin/host, never a URL carrying a credential.
        """
        raise NotImplementedError

    # ── The decision ─────────────────────────────────────────────────────────

    def _egress_allows(self, destination: str) -> bool:
        """Ask the gate. Anything unreadable denies — the gate itself fails closed."""
        from aegis_ai.egress import EgressRequest

        gate = self._gate
        if gate is None:
            from aegis_ai.egress import get_egress_gate

            gate = get_egress_gate()
        return bool(
            gate.allow(
                EgressRequest(
                    destination=destination,
                    purpose=self.purpose,
                    component=f"notification.channels.{self.label}",
                    data_summary="notification body (the user's own content)",
                    # Strict, and deliberately not a parameter of this method.
                    carries_user_information=True,
                )
            )
        )

    # ── Send ─────────────────────────────────────────────────────────────────

    def send(self, notification: Notification) -> OutboundSendResult:
        """Check the gate, then hand the notification to the transport.

        Returns a result rather than raising: the router calls ``send`` in a loop and one
        channel's failure must not abort the others.
        """
        missing = self.missing_configuration()
        if missing:
            return OutboundSendResult(
                channel=self.label,
                error=f"not configured: {', '.join(missing)} is not set",
            )

        destination = self.destination()
        if not destination:
            return OutboundSendResult(channel=self.label, error="no destination is configured")

        if not self._egress_allows(destination):
            logger.warning(
                "Outbound %s notification refused by the egress gate (body withheld)", self.label
            )
            return OutboundSendResult(
                channel=self.label,
                destination=destination,
                refused_by_gate=True,
                error=(
                    f"refused by the egress gate: '{destination}' is not permitted for "
                    f"'{self.purpose}'. Permit it (settings or a recorded grant), or use a "
                    "local channel."
                ),
            )

        started = time.perf_counter()
        try:
            success, status_code, error = self._deliver(destination, notification)
        except Exception as exc:
            # A transport exception can carry a credential in its message, so only the
            # exception's *type* is reported.
            logger.warning("Outbound %s transport raised %s", self.label, type(exc).__name__)
            success, status_code, error = False, 0, f"{type(exc).__name__} while sending"
        return OutboundSendResult(
            channel=self.label,
            destination=destination,
            success=success,
            status_code=status_code,
            error=error,
            duration_ms=(time.perf_counter() - started) * 1000.0,
        )

    def _deliver(self, destination: str, notification: Notification) -> tuple[bool, int, str]:
        """Run the transport.

        Deliberately **not** overridable in practice: subclasses supply
        :meth:`_default_transport` instead, so no channel can reorder the gate check ahead
        of the network call. ``test_external_messaging.py`` pins that none of them overrides
        this method.
        """
        transport = self._transport
        if transport is None:
            transport = self._default_transport()
        if transport is None:
            raise NotImplementedError(f"{self.label} has no transport configured")
        return transport(destination, notification)

    def _default_transport(self) -> Transport | None:
        """The real network transport, or ``None`` when the subclass supplies none."""
        return None
