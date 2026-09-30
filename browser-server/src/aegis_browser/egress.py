"""Egress gate for the Browser Server — the single constraint, enforced locally.

The only constraint is user-information egress — **re-scoped 2026-09-30** (owner) to
*unpermitted* disclosure, with outbound connections and user-permitted disclosure
allowed. This module is the Browser Server's enforcement point; it currently implements
the pre-re-scope deny-all form, and the permission wiring is open work.

Why this is duplicated rather than imported
-------------------------------------------
``aegis-browser-server`` is a standalone distribution (see ``pyproject.toml``) that
does not depend on ``aegis_ai``. It therefore carries its own copy of the
classification rules. The semantics are deliberately identical to
``ai-server/src/aegis_ai/egress/gate.py`` — see ``docs/egress-gate.md``. If you
change one, change the other.

Design (mirrors the AI Server gate)
-----------------------------------
1. **Deny by default.** External egress requires an explicit opt-in.
2. **Local is always allowed.** Loopback / RFC1918 / CGNAT / ULA / ``.local`` /
   single-label LAN hostnames never leave the environment.
3. **Fail closed.** A destination that cannot be classified is treated as external.
4. **Two locks for external egress.** The master switch *and* a host allowlist entry.

Configuration (environment variables)
-------------------------------------
``AEGIS_EXTERNAL_EGRESS_ALLOWED``  ``1``/``true`` to permit external egress (default off)
``AEGIS_EGRESS_ALLOWED_HOSTS``     comma-separated host allowlist
"""

from __future__ import annotations

import ipaddress
import logging
import os
from dataclasses import dataclass
from urllib.parse import urlsplit

logger = logging.getLogger("aegis_browser.egress")

__all__ = [
    "EgressDenied",
    "EgressRequest",
    "classify_destination",
    "egress_allowed",
    "external_egress_enabled",
    "is_local_destination",
    "navigation_allowlist",
    "require_egress",
]

# Single-label hostnames (no dot) cannot be public DNS names, so they are treated
# as LAN-local. ``.local`` is mDNS. Both are inside the environment.
_LOCAL_HOST_SUFFIXES = (".local", ".localhost", ".internal", ".lan", ".home")
_LOCAL_HOSTNAMES = frozenset({"localhost", "localhost.localdomain", "ip6-localhost"})

#: Local destinations restated as ``BrowserProfile.allowed_domains`` patterns.
#:
#: Why this exists: the pre-flight check in ``browser_use_agent`` only inspects the
#: targets a task *declares*. Once the browser is running, the agent can follow a link
#: or a redirect anywhere. browser-use's ``SecurityWatchdog`` blocks exactly that —
#: it vetoes ``NavigateToUrlEvent`` before navigation, re-checks on
#: ``NavigationCompleteEvent`` (redirects) and closes offending tabs — but it only
#: understands the patterns in ``allowed_domains``.
#:
#: So this tuple is the per-navigation half of the egress gate, and
#: :func:`is_local_destination` is the authority it must not contradict. The safety
#: direction is one-way: **no pattern here may admit a host the predicate calls
#: external.** Being *coarser* — blocking a local host the predicate would allow — is
#: accepted and documented; being looser is a breach of the single constraint.
#:
#: Hence every entry is an exact hostname, an exact IP literal, or a non-public suffix
#: (``.local`` is mDNS; ``.lan``/``.home``/``.internal`` are private-use TLDs that public
#: DNS does not resolve). **Private IP ranges are deliberately absent**: browser-use
#: matches with ``fnmatch``, and ``192.168.*`` also matches the publicly resolvable
#: ``192.168.evil.com``. A glob cannot express "the remaining labels are numeric", so a
#: private-IP destination is admitted only when the task *declares* it —
#: :func:`navigation_allowlist` appends declared targets as exact patterns.
#:
#: Keep this under ``DOMAIN_OPTIMIZATION_THRESHOLD`` (100): at 100 entries browser-use
#: converts the list to a set and **glob matching stops working** — ``*.local`` would
#: silently stop matching. ``tests/test_navigation_allowlist.py`` asserts the budget.
_LOCAL_NAVIGATION_PATTERNS: tuple[str, ...] = (
    # Local hostnames. Exact, and all three are in _LOCAL_HOSTNAMES.
    "localhost",
    "localhost.localdomain",
    "ip6-localhost",
    # mDNS and private-use TLDs — glob form, because the predicate matches the suffix.
    "*.localhost",
    "*.local",
    "*.internal",
    "*.lan",
    "*.home",
    # Loopback and "this network" literals. Exact: a numeric-range glob would also
    # admit *.evil.com, and the predicate would call that external.
    "::1",
    "127.0.0.1",
    "0.0.0.0",
)

# A well-formed host is an IPv6 literal, an IPv4 literal, or a DNS name. Anything
# else (spaces, stray punctuation) is unclassifiable and must fail closed.
_HOSTNAME_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789-._")


def _is_wellformed_host(host: str) -> bool:
    if not host:
        return False
    if ":" in host:  # IPv6 literal
        return True
    return all(c in _HOSTNAME_CHARS for c in host)


@dataclass(frozen=True)
class EgressRequest:
    """A single outbound transmission to be evaluated."""

    destination: str
    purpose: str
    component: str = "unknown"
    data_summary: str = ""


class EgressDenied(RuntimeError):
    """Raised when the egress gate refuses a destination."""


def _extract_host(destination: str) -> str:
    """Extract the host from a URL, ``host:port`` pair, bare host, or unix path."""
    raw = (destination or "").strip()
    if not raw:
        return ""
    if raw.startswith("/"):  # unix socket path
        return raw
    if "://" not in raw:
        # Not a URL: strip any path, then parse the authority by hand. ``urlsplit``
        # cannot parse a bare IPv6 literal — ``urlsplit("//::1")`` has no hostname —
        # so the literal forms are recognised before it is consulted. Ported from
        # ``ai-server/src/aegis_ai/egress/gate.py``: this copy had drifted, and was
        # classifying ``::1`` as external while ``http://[::1]/`` was classified
        # local. See ``docs/egress-gate.md``.
        authority = raw.split("/", 1)[0]
        if authority.startswith("["):  # [::1] or [::1]:50051
            end = authority.find("]")
            return authority[1:end].strip().lower() if end != -1 else ""
        if authority.count(":") > 1:  # bare IPv6 literal, no port
            return authority.strip().lower()
        if ":" in authority:  # host:port
            return authority.split(":", 1)[0].strip().lower()
        return authority.strip().lower()
    try:
        parts = urlsplit(raw)
    except ValueError:
        return ""
    return (parts.hostname or "").strip().lower()


def _is_local_ip(host: str) -> bool:
    """Return True when ``host`` is an IP inside the local environment."""
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    if ip.is_loopback or ip.is_link_local or ip.is_private:
        return True
    # Tailscale / CGNAT range 100.64.0.0/10 — a private mesh, not the public internet.
    if isinstance(ip, ipaddress.IPv4Address) and ip in ipaddress.ip_network("100.64.0.0/10"):
        return True
    # IPv6 unique-local addresses fc00::/7.
    return bool(isinstance(ip, ipaddress.IPv6Address) and ip in ipaddress.ip_network("fc00::/7"))


def is_local_destination(destination: str) -> bool:
    """Return True when ``destination`` stays inside the local environment."""
    raw = (destination or "").strip()
    if not raw:
        return False
    if raw.startswith("/"):  # unix socket
        return True

    host = _extract_host(destination)
    if not host or not _is_wellformed_host(host):
        return False
    if host in _LOCAL_HOSTNAMES:
        return True
    if host.endswith(_LOCAL_HOST_SUFFIXES):
        return True
    if _is_local_ip(host):
        return True
    # A single-label hostname cannot be resolved by public DNS. Not applied to IPv6
    # literals: "::2" contains no dot but is a globally routable address, so the
    # heuristic alone would call it local. Matches ai-server's
    # ``"." not in host and ":" not in host``.
    return ":" not in host and "." not in host


def classify_destination(destination: str) -> str:
    """Classify a destination as ``"local"``, ``"external"``, or ``"unknown"``."""
    raw = (destination or "").strip()
    if not raw:
        return "unknown"
    if is_local_destination(raw):
        return "local"
    host = _extract_host(raw)
    if not host:
        return "unknown"
    # Has a dot (or is a public IP) => a real external host.
    return "external"


def _external_egress_enabled() -> bool:
    return os.getenv("AEGIS_EXTERNAL_EGRESS_ALLOWED", "").strip().lower() in {"1", "true", "yes", "on"}


def external_egress_enabled() -> bool:
    """Public accessor for the master switch (default: disabled)."""
    return _external_egress_enabled()


def _allowed_hosts() -> list[str]:
    raw = os.getenv("AEGIS_EGRESS_ALLOWED_HOSTS", "")
    return [h.strip().lower() for h in raw.split(",") if h.strip()]


def _host_is_allowlisted(host: str) -> bool:
    for entry in _allowed_hosts():
        expected = entry.lstrip(".")
        if host == expected or host.endswith(f".{expected}"):
            return True
    return False


def egress_allowed(request: EgressRequest) -> bool:
    """Return True when ``request`` may leave the process.

    Local destinations are always permitted. External destinations require the
    master switch *and* an allowlist entry. Unknown destinations fail closed.
    """
    kind = classify_destination(request.destination)

    if kind == "local":
        _record(request, "allow", "local destination")
        return True

    if kind == "unknown":
        _record(request, "deny", "unclassifiable destination (fail closed)")
        return False

    if not _external_egress_enabled():
        _record(request, "deny", "external egress is disabled (single constraint)")
        return False

    host = _extract_host(request.destination)
    if not _host_is_allowlisted(host):
        _record(request, "deny", f"host not in allowlist: {host}")
        return False

    _record(request, "allow", "external egress explicitly enabled and allowlisted")
    return True


def _admissible_host(host: str) -> bool:
    """Return True when ``host`` may be navigated to, mirroring :func:`egress_allowed`.

    Split out so :func:`navigation_allowlist` can classify a host without emitting an
    egress log line per declared target — the pre-flight check already logs those.
    ``tests/test_navigation_allowlist.py`` asserts the two agree.
    """
    if not host:
        return False
    if is_local_destination(host):
        return True
    return external_egress_enabled() and _host_is_allowlisted(host)


def navigation_allowlist(declared_targets: list[str] | None = None) -> list[str]:
    """Patterns for ``BrowserProfile.allowed_domains`` — the per-navigation egress gate.

    Local patterns are always present. External hosts appear only when the master
    switch is on *and* the host is allowlisted, so an undeclared external navigation is
    refused by the browser itself rather than only by the pre-flight check.

    ``declared_targets`` are hosts or URLs the task declared. Each is admitted only if
    :func:`_admissible_host` clears it — the caller does not get to decide — which is how
    a declared private IP or single-label LAN host that the pattern list cannot express
    still gets through.
    """
    patterns: list[str] = list(_LOCAL_NAVIGATION_PATTERNS)

    if external_egress_enabled():
        patterns.extend(entry.lstrip(".") for entry in _allowed_hosts())

    for target in declared_targets or []:
        host = _extract_host(target)
        if _admissible_host(host):
            patterns.append(host)

    # Order-preserving de-duplication.
    seen: dict[str, None] = {}
    for pattern in patterns:
        seen.setdefault(pattern, None)
    return list(seen)


def require_egress(request: EgressRequest) -> None:
    """Raise :class:`EgressDenied` unless ``request`` is permitted."""
    if not egress_allowed(request):
        raise EgressDenied(
            f"Egress denied: {request.component} -> {request.destination} "
            f"(purpose={request.purpose}). "
            "The user's information must not leave the local environment."
        )


def _record(request: EgressRequest, decision: str, reason: str) -> None:
    """Log the decision. Audit belongs to the AI Server; this is visibility only."""
    level = logging.INFO if decision == "allow" else logging.WARNING
    logger.log(
        level,
        "egress %s component=%s purpose=%s destination=%s reason=%s",
        decision,
        request.component,
        request.purpose,
        request.destination,
        reason,
    )
