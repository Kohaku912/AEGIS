"""The single home of the "may this request read the display?" rule.

Three modules used to spell this rule out independently, and each carried its own
copy of the host parse and of the loopback host set:

* ``auth/session_middleware._display_read_allowed`` — the passkey middleware's
  exemption for ``/display/overview`` and the display SSE stream;
* ``web/routes/ui_v2._require_display_read`` — the guard on the v2 display data
  routes;
* ``web/routes/presentation._require_local_display_request`` — the guard on the
  physical display's data route.

They agree on the core — a configured display token, or a loopback caller — but
each *narrowed* it, and those narrowings are deliberate, so the rule is
parameterised rather than merged. Every caller keeps the exact behaviour it had.

The rule, in order:

1. a configured display token, presented as ``?display_token=`` or
   ``X-AEGIS-Display-Token``, admits the request;
2. a loopback effective host admits it;
3. a forwarded host is **not trusted**: if ``X-Forwarded-Host`` is present and
   the host is not loopback, the request is refused rather than falling back;
4. otherwise a loopback peer address (``REMOTE_ADDR``) admits it.

``presentation`` guards the *physical* display, which is local by definition, so
it passes all three flags ``False``: it accepts no remote credential, does not
fall back to the peer address, and reads ``request.host`` alone rather than a
proxy header.

Not this rule — deliberately **not** folded in: ``web/dashboard_legacy.
_is_local_request_host`` accepts ``""``, ``0.0.0.0`` and any loopback IP via
``ipaddress``, so it is not determined by this host set. It answers a different
question ("is this *configured* host local?") and merging it would change
behaviour at its call sites. It also currently has no caller at all.

One unification, unobservable: the middleware compared ``REMOTE_ADDR`` verbatim
while ``ui_v2`` stripped and lower-cased it. ``remote_addr`` is the server's own
view of the peer and is never attacker-controlled, so the normalised form cannot
widen the surface, and one spelling is the point of this module.
"""

from __future__ import annotations

import os

from flask import request

#: The one loopback host set. Replaces three identical copies.
DISPLAY_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})

#: Environment variables that may configure the display credential, in order.
DISPLAY_TOKEN_ENV_VARS = ("AEGIS_DISPLAY_TOKEN", "AEGIS_DISPLAY_READ_TOKEN")

#: How a caller may present that credential.
DISPLAY_TOKEN_ARG = "display_token"
DISPLAY_TOKEN_HEADER = "X-AEGIS-Display-Token"


def request_host_without_port(*, trust_forwarded_host: bool = True) -> str:
    """The effective host, lower-cased, with the port and IPv6 brackets removed.

    ``trust_forwarded_host`` False reads ``request.host`` alone, so a caller that
    does not sit behind a proxy cannot be moved by a forwarded header.
    """

    if trust_forwarded_host:
        raw = request.headers.get("X-Forwarded-Host") or request.host or ""
    else:
        raw = request.host or ""
    host = raw.strip().lower()
    if host.startswith("["):
        return host.split("]", 1)[0].lstrip("[")
    return host.split(":", 1)[0]


def configured_display_token() -> str:
    """The configured display credential, or "" when none is configured."""

    for name in DISPLAY_TOKEN_ENV_VARS:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def presented_display_token() -> str:
    """The credential this request presents, or "" when it presents none."""

    return request.args.get(DISPLAY_TOKEN_ARG, "") or request.headers.get(DISPLAY_TOKEN_HEADER, "")


def is_loopback_peer() -> bool:
    """Whether the peer address (``REMOTE_ADDR``) is loopback."""

    return (request.remote_addr or "").strip().lower() in DISPLAY_LOOPBACK_HOSTS


def is_display_read_allowed(
    *,
    allow_token: bool = True,
    allow_remote_addr: bool = True,
    trust_forwarded_host: bool = True,
) -> bool:
    """Whether the current request may read display data. See the module docstring."""

    if allow_token:
        token = configured_display_token()
        if token and presented_display_token() == token:
            return True
    if request_host_without_port(trust_forwarded_host=trust_forwarded_host) in DISPLAY_LOOPBACK_HOSTS:
        return True
    if trust_forwarded_host and request.headers.get("X-Forwarded-Host"):
        return False
    if allow_remote_addr and is_loopback_peer():
        return True
    return False
