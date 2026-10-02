"""Egress Gate — control for all outbound transmission.

The gate is the *single* structural enforcement point for AEGIS's single constraint.
**Re-scoped 2026-09-30** (owner):

    **Unpermitted** user information must never leave the local environment. Outbound
    connections are allowed, and user information may be sent externally **with the
    user's permission**.

The gate now implements that rule with **two permission paths**:

1. **Standing configuration** — the master switch, the per-purpose feature flag and the
   host allowlist (principles 1-4 below). Unchanged from before the re-scope.
2. **A permission the user gave about a specific destination** — read from
   ``aegis_ai.egress.permissions``, which adapts the confirmation store. The gate
   **consults** it and never asks; raising the question is the *voluntary* ask's job, so
   the retired forced gate stays retired (pinned by
   ``tests/test_forced_gate_stays_retired.py``).

A request that carries **no user information** may connect out without either path,
because the constraint is about user information, not connectivity.
``EgressRequest.carries_user_information`` defaults to ``True``, so a caller that has not
reasoned about it gets the gated path rather than the open one.

Design principles
-----------------
1. **Deny by default.** External destinations are refused unless explicitly allowed
   by an operator-configured allowlist *and* a matching feature flag.
2. **Local is allowed.** AEGIS is a multi-device system; its own LAN *is* the local
   environment. Loopback, RFC1918, link-local, Tailscale CGNAT and IPv6 ULA are local.
3. **Fail closed.** If a destination cannot be classified, the request is denied.
4. **Permission, not a wall** (re-scoped 2026-09-30). The old "must be explicitly configured"
   escape hatch is gone, and the constraint is now *unpermitted* egress — so the intended
   mechanism is the **voluntary ask**, not an absolute refusal. **Two** paths can permit a
   destination: the standing configuration (master switch **and** feature flag **and** an
   allowlist entry — a flag alone never permits egress), or a **recorded user grant** for that
   host and purpose, consulted on every check via :meth:`_user_grant`. ⚠️ The grant path only
   answers when a ``permission_source`` was supplied, and the composition root does not pass
   one — so in the running system it always returns "no grant" and only the configuration path
   can permit. That wiring is the open work, not the check.
5. **Auditable.** Every decision is recorded so the constraint can be verified after
   the fact (post-hoc visibility, Phase 3).

Usage
-----
::

    from aegis_ai.egress import EgressGate, EgressRequest, EgressDenied

    gate = EgressGate(settings_store=store, audit=audit_manager)
    gate.require(EgressRequest(
        destination="https://api.deepseek.com/v1/chat/completions",
        purpose="llm.chat",
        component="llm.router",
        data_summary="chat prompt (user message + memory context)",
    ))  # raises EgressDenied while egress is closed
"""

from __future__ import annotations

import ipaddress
import logging
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable
from urllib.parse import urlsplit

logger = logging.getLogger("aegis_ai.egress.gate")


class EgressDenied(RuntimeError):
    """Raised when an outbound transmission is refused by the egress gate."""

    def __init__(self, request: "EgressRequest", reason: str) -> None:
        self.request = request
        self.reason = reason
        super().__init__(
            f"Egress denied for {request.component} -> {request.destination} "
            f"(purpose={request.purpose}): {reason}"
        )


class EgressDecision(str, Enum):
    """Outcome of an egress check."""

    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class EgressRequest:
    """A request to transmit data outside the process.

    Attributes:
        destination: URL, ``host:port``, or bare host. Must be classifiable.
        purpose: Stable purpose id, e.g. ``llm.chat``, ``web.search``, ``voice.tts``.
            Used to look up the matching feature flag.
        component: The code path making the request, e.g. ``llm.router``.
        data_summary: Human-readable description of what would be transmitted.
            Never contains the payload itself — only a summary, for audit.
        carries_user_information: Whether the request would transmit anything about the
            user. **Defaults to True — the strict reading**, so a caller that has not
            reasoned about it gets the permission-gated path rather than the open one.
            The re-scoped constraint is about *user information*, not connectivity, so a
            caller that genuinely sends nothing user-specific may say so; the claim is
            recorded in the audit. It is the caller's explicit claim, not an inference —
            AEGIS does not scan payloads to decide this (that would be a prose scanner).
    """

    destination: str
    purpose: str
    component: str = "unknown"
    data_summary: str = ""
    carries_user_information: bool = True


@dataclass
class EgressStatus:
    """Result of the startup egress configuration assertion."""

    ok: bool
    violations: list[str] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def raise_if_violated(self) -> None:
        """Raise ``EgressConfigurationError`` if the assertion failed."""
        if not self.ok:
            raise EgressConfigurationError(
                "Egress configuration is not structurally closed: " + "; ".join(self.violations)
            )


class EgressConfigurationError(RuntimeError):
    """Raised at startup when egress is not structurally closed."""


# ── Destination classification ────────────────────────────────────────────────

_LOOPBACK_HOSTNAMES = frozenset({"localhost", "localhost.localdomain", "ip6-localhost"})


def _extract_host(destination: str) -> str:
    """Extract the host from a URL, ``host:port``, or bare host string.

    Returns an empty string when nothing classifiable can be extracted.
    """
    if not destination:
        return ""
    text = destination.strip()
    if not text:
        return ""

    # Unix domain sockets are local by construction.
    if text.startswith("unix:") or text.startswith("/"):
        return ""

    if "://" in text:
        try:
            host = urlsplit(text).hostname or ""
        except ValueError:
            return ""
        return host.strip().lower()

    # host:port or bare host — strip a path/query if present.
    text = text.split("/", 1)[0]
    # Bracketed IPv6, e.g. [::1]:50051
    if text.startswith("["):
        end = text.find("]")
        if end != -1:
            return text[1:end].strip().lower()
        return ""
    # Bare IPv6 (multiple colons) — no port.
    if text.count(":") > 1:
        return text.strip().lower()
    if ":" in text:
        return text.split(":", 1)[0].strip().lower()
    return text.strip().lower()


# A well-formed host is an IPv6 literal, an IPv4 literal, or a DNS name. Anything
# else (spaces, stray punctuation) is unclassifiable and must fail closed rather
# than be mistaken for a single-label LAN hostname.
_HOSTNAME_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789-._")


def _is_wellformed_host(host: str) -> bool:
    """Return True when ``host`` looks like a real hostname or IP literal."""
    if not host:
        return False
    if ":" in host:  # IPv6 literal
        return True
    return all(c in _HOSTNAME_CHARS for c in host)


def _is_local_ip(host: str) -> bool:
    """Return True when ``host`` is a literal IP inside the local environment."""
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False

    if ip.is_loopback or ip.is_link_local or ip.is_unspecified:
        return True
    if ip.version == 4:
        # RFC1918 private ranges.
        if ip in ipaddress.ip_network("10.0.0.0/8"):
            return True
        if ip in ipaddress.ip_network("172.16.0.0/12"):
            return True
        if ip in ipaddress.ip_network("192.168.0.0/16"):
            return True
        # Tailscale / CGNAT.
        if ip in ipaddress.ip_network("100.64.0.0/10"):
            return True
        return False
    # IPv6 unique local addresses (fc00::/7).
    return ip in ipaddress.ip_network("fc00::/7")


def is_local_destination(destination: str) -> bool:
    """Return True when ``destination`` is inside the local environment.

    Local means: loopback, RFC1918 / link-local / Tailscale-CGNAT / IPv6-ULA, a
    loopback hostname, a single-label hostname (LAN mDNS / NetBIOS, which cannot be
    public DNS), a ``.local`` mDNS name, or a unix socket path.
    """
    if not destination:
        return False
    text = destination.strip()
    if not text:
        return False
    if text.startswith("unix:") or text.startswith("/"):
        return True

    host = _extract_host(text)
    if not host or not _is_wellformed_host(host):
        return False
    if host in _LOOPBACK_HOSTNAMES:
        return True
    if host.endswith(".local"):
        return True
    if _is_local_ip(host):
        return True
    # Single-label hostname — cannot be resolved by public DNS.
    if "." not in host and ":" not in host:
        return True
    return False


def classify_destination(destination: str) -> str:
    """Return ``"local"``, ``"external"``, or ``"unknown"`` for a destination."""
    if not destination or not destination.strip():
        return "unknown"
    text = destination.strip()
    if text.startswith("unix:") or text.startswith("/"):
        return "local"
    host = _extract_host(text)
    if not host:
        return "unknown"
    if is_local_destination(text):
        return "local"
    return "external"


# ── Purpose → feature-flag mapping ────────────────────────────────────────────

# Purpose prefix → (settings section, attribute). The flag must be True *and* the
# host must be allowlisted for external egress to be permitted.
_PURPOSE_FLAGS: dict[str, tuple[str, str]] = {
    "llm": ("privacy", "external_llm_allowed"),
    "web": ("privacy", "web_search_allowed"),
    "search": ("privacy", "web_search_allowed"),
    "voice": ("voice", "external_voice_api_allowed"),
    "messaging": ("privacy", "external_messaging_allowed"),
}


def _build_audit_entry(*, action: str, decision: str, reason: str, detail: dict[str, Any]) -> Any:
    """Build an audit entry the configured audit sink can accept.

    ``AuditLog`` and ``AuditManager`` both expect an ``AuditEntry``; older sinks
    accept plain dicts. Prefer the typed entry and fall back to a dict so that
    audit recording can never break the egress path.
    """
    try:
        from aegis_ai.audit import AuditEntry

        return AuditEntry(
            action=action,
            actor="egress_gate",
            decision=decision,
            reason=reason,
            detail=dict(detail),
        )
    except Exception:  # pragma: no cover - defensive
        return {"action": action, "decision": decision, "reason": reason, "detail": dict(detail)}


class EgressGate:
    """The single gate for all outbound transmission.

    Args:
        settings_store: Optional SettingsStore. When absent, all feature flags are
            treated as False (closed) and no allowlist is available.
        audit: Optional AuditManager (or any object with ``append``). Failures to
            record are logged but never mask the decision.
        allowed_hosts: Explicit external-host allowlist. Defaults to empty — external
            egress is refused even when a feature flag is on.
        strict: When True (default), unknown destinations are denied.
        permission_source: Optional object with ``grant_for(*, host, purpose,
            moment_ms)`` — the **second** permission path added by the 2026-09-30
            re-scope (see ``aegis_ai.egress.permissions``). Read-only: the gate asks it
            what the user has already permitted and never asks the user itself. When
            absent, only the standing configuration path exists, which is the
            pre-re-scope behaviour.
    """

    def __init__(
        self,
        *,
        settings_store: Any = None,
        audit: Any = None,
        allowed_hosts: Iterable[str] | None = None,
        strict: bool = True,
        permission_source: Any = None,
    ) -> None:
        self._settings = settings_store
        self._audit = audit
        self._lock = threading.Lock()
        self._strict = strict
        self._permission_source = permission_source
        self._allowed_hosts: frozenset[str] = frozenset(
            h.strip().lower() for h in (allowed_hosts or []) if h and h.strip()
        )

    # ── Configuration ────────────────────────────────────────────────────────

    def set_allowed_hosts(self, hosts: Iterable[str]) -> None:
        """Replace the explicit external allowlist."""
        with self._lock:
            self._allowed_hosts = frozenset(
                h.strip().lower() for h in hosts if h and h.strip()
            )

    def set_permission_source(self, permission_source: Any) -> None:
        """Attach (or clear) the read-only source of user egress permissions."""
        with self._lock:
            self._permission_source = permission_source

    def set_settings_store(self, settings_store: Any) -> None:
        with self._lock:
            self._settings = settings_store

    def set_audit(self, audit: Any) -> None:
        with self._lock:
            self._audit = audit

    @property
    def allowed_hosts(self) -> frozenset[str]:
        """The *effective* allowlist: explicit wiring plus the settings lock.

        Not just ``self._allowed_hosts`` — the composition root passes only a
        settings store, so a constructor-only view would ignore the lock the docs
        advertise. See :meth:`_settings_allowed_hosts`.
        """
        with self._lock:
            explicit = self._allowed_hosts
        return explicit | self._settings_allowed_hosts()

    # ── Policy reads ─────────────────────────────────────────────────────────

    def _privacy_setting(self, section: str, attribute: str, default: bool = False) -> bool:
        with self._lock:
            settings = self._settings
        if settings is None:
            return default
        try:
            resolved = settings.get()
            section_obj = getattr(resolved, section, None)
            if section_obj is None:
                return default
            value = getattr(section_obj, attribute, default)
            return bool(value)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Egress: failed to read %s.%s (%s) — treating as closed", section, attribute, exc)
            return default

    def _external_egress_enabled(self) -> bool:
        """Master switch for any external egress."""
        return self._privacy_setting("privacy", "external_egress_allowed", default=False)

    def _settings_allowed_hosts(self) -> frozenset[str]:
        """The allowlist declared in settings (``privacy.egress_allowed_hosts``).

        The third lock is read here rather than injected by the composition root,
        so that the lock the documentation advertises is the lock that actually
        applies. Before this existed the field had **no reader anywhere in
        ``src/``**: adding a host to ``settings.json`` did nothing at all, which is
        the "declared but ineffective" bug class (see
        ``tests/test_ineffective_flags.py``).

        A malformed or unreadable value degrades to empty — the safe direction,
        since an empty allowlist can never open egress on its own.
        """
        with self._lock:
            settings = self._settings
        if settings is None:
            return frozenset()
        try:
            privacy = getattr(settings.get(), "privacy", None)
            declared = getattr(privacy, "egress_allowed_hosts", None) or ()
            return frozenset(
                str(host).strip().lower() for host in declared if str(host).strip()
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(
                "Egress: failed to read privacy.egress_allowed_hosts (%s) — treating as empty",
                exc,
            )
            return frozenset()

    def _purpose_allowed(self, purpose: str) -> bool:
        """Whether the feature flag for this purpose is on."""
        if not purpose:
            return False
        head = purpose.split(".", 1)[0].strip().lower()
        mapping = _PURPOSE_FLAGS.get(head)
        if mapping is None:
            return False
        return self._privacy_setting(mapping[0], mapping[1], default=False)

    # ── Evaluation ───────────────────────────────────────────────────────────

    def check(self, request: EgressRequest) -> EgressDecision:
        """Evaluate a request and record the decision. Never raises."""
        decision, reason = self._evaluate(request)
        self._record(request, decision, reason)
        return decision

    def allow(self, request: EgressRequest) -> bool:
        """Return True when the request is permitted."""
        return self.check(request) is EgressDecision.ALLOW

    def require(self, request: EgressRequest) -> None:
        """Permit the request or raise :class:`EgressDenied`."""
        decision, reason = self._evaluate(request)
        self._record(request, decision, reason)
        if decision is EgressDecision.DENY:
            raise EgressDenied(request, reason)

    def _evaluate(self, request: EgressRequest) -> tuple[EgressDecision, str]:
        kind = classify_destination(request.destination)

        if kind == "local":
            return EgressDecision.ALLOW, "local destination"

        if kind == "unknown":
            # Fail closed.
            return EgressDecision.DENY, "destination could not be classified (fail closed)"

        # External.
        if not self._external_egress_enabled():
            return EgressDecision.DENY, "external egress is disabled (single constraint)"

        # The re-scoped constraint is about *user information*, not connectivity: a request
        # that carries none needs no permission. The claim is the caller's, and it is audited.
        if not request.carries_user_information:
            return EgressDecision.ALLOW, "external connection carrying no user information"

        host = _extract_host(request.destination)
        allowlisted = host in self.allowed_hosts
        purpose_allowed = self._purpose_allowed(request.purpose)
        if allowlisted and purpose_allowed:
            return EgressDecision.ALLOW, "explicitly allowlisted external destination"

        # Second path, added by the 2026-09-30 re-scope: permission the user gave about
        # this exact destination. Read-only — the gate consults, it never asks.
        grant = self._user_grant(host=host, purpose=request.purpose)
        if grant is not None:
            return EgressDecision.ALLOW, f"permitted by the user ({grant.grant_id})"

        if not allowlisted:
            return (
                EgressDecision.DENY,
                f"host '{host}' is not in the egress allowlist and the user has not permitted it",
            )
        return (
            EgressDecision.DENY,
            f"feature flag for purpose '{request.purpose}' is off and the user has not permitted it",
        )

    def _user_grant(self, *, host: str, purpose: str) -> Any:
        """The user's recorded permission for this destination, or ``None``. Never asks.

        A source that is missing, misconfigured, or raising yields ``None`` — i.e. the
        request falls back to the standing-configuration path and is denied. The failure
        mode is closed, never open.
        """
        with self._lock:
            source = self._permission_source
        lookup = getattr(source, "grant_for", None)
        if not callable(lookup):
            return None
        try:
            return lookup(host=host, purpose=purpose)
        except Exception as exc:  # pragma: no cover - defensive, exercised by the pin
            logger.warning("egress permission lookup failed (falling back to deny): %s", exc)
            return None

    # ── Audit ────────────────────────────────────────────────────────────────

    def _record(self, request: EgressRequest, decision: EgressDecision, reason: str) -> None:
        level = logging.INFO if decision is EgressDecision.ALLOW else logging.WARNING
        logger.log(
            level,
            "egress %s component=%s purpose=%s destination=%s reason=%s",
            decision.value,
            request.component,
            request.purpose,
            request.destination,
            reason,
        )
        with self._lock:
            audit = self._audit
        if audit is None:
            return
        try:
            append = getattr(audit, "append", None)
            if append is None:
                return
            append(
                _build_audit_entry(
                    action="egress_decision",
                    decision=decision.value,
                    reason=reason,
                    detail={
                        "component": request.component,
                        "purpose": request.purpose,
                        "destination": request.destination,
                        "data_summary": request.data_summary,
                    },
                )
            )
        except Exception as exc:  # pragma: no cover - audit must never break the path
            logger.warning("Egress: failed to record decision to audit: %s", exc)

    # ── Startup assertion ────────────────────────────────────────────────────

    def status(self) -> EgressStatus:
        """Return whether the egress **permission configuration** is coherent.

        **Re-scoped 2026-09-30** (canonical: ``docs/GOAL-CHANGE.md``). Outbound
        connections are allowed and user information may be sent externally *with the
        user's permission*, so an **opened** surface is no longer a defect by itself:
        this gate *is* the permission check, and it evaluates every request. Asserting
        "egress is closed" would now be asserting something the goal does not require —
        and it would make a permitted configuration unable to start.

        What this still has to catch is an opening that does not describe what it
        permits — the "declared but ineffective" class:

        - the master switch on with an **empty allowlist**: no destination is permitted,
          so the configuration claims an opening it does not implement;
        - an allowlist entry that can never match. :func:`_extract_host` reduces a
          destination to a bare hostname, so an entry containing ``/`` (a URL or a path)
          is dead — it looks like a permission and grants nothing.

        The purpose flags and a populated allowlist are the permission itself; they are
        reported in ``summary`` for the operator rather than as violations.
        """
        violations: list[str] = []

        hosts = self.allowed_hosts
        if self._external_egress_enabled() and not hosts:
            violations.append(
                "privacy.external_egress_allowed is True but privacy.egress_allowed_hosts "
                "is empty — external egress is enabled with no permitted destination"
            )

        dead = sorted(host for host in hosts if "/" in host)
        if dead:
            violations.append(
                f"egress allowlist entries can never match a bare hostname: {dead} "
                "(entries must be hosts, not URLs or paths)"
            )

        return EgressStatus(
            ok=not violations,
            violations=violations,
            summary={
                "allowed_hosts": sorted(hosts),
                "external_egress_allowed": self._external_egress_enabled(),
                "external_llm_allowed": self._privacy_setting(
                    "privacy", "external_llm_allowed", default=False
                ),
                "web_search_allowed": self._privacy_setting(
                    "privacy", "web_search_allowed", default=False
                ),
                "external_voice_api_allowed": self._privacy_setting(
                    "voice", "external_voice_api_allowed", default=False
                ),
            },
        )


# ── Process-wide singleton ────────────────────────────────────────────────────

_GATE: EgressGate | None = None
_GATE_LOCK = threading.Lock()


def get_egress_gate() -> EgressGate:
    """Return the process-wide egress gate, creating a closed one if needed."""
    global _GATE
    with _GATE_LOCK:
        if _GATE is None:
            _GATE = EgressGate()
        return _GATE


def configure_egress_gate(
    *,
    settings_store: Any = None,
    audit: Any = None,
    allowed_hosts: Iterable[str] | None = None,
    permission_source: Any = None,
) -> EgressGate:
    """Configure the process-wide egress gate. Called from the composition root."""
    global _GATE
    with _GATE_LOCK:
        _GATE = EgressGate(
            settings_store=settings_store,
            audit=audit,
            allowed_hosts=allowed_hosts,
            permission_source=permission_source,
        )
        return _GATE
