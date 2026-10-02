"""Every dashboard route must be refused to an unauthenticated client, or recorded here as public.

The passkey middleware (``auth/session_middleware._load_and_require_auth``) protects a **positive**
prefix list — ``/``, ``/dashboard``, ``/settings``, ``/chat``, ``/api/``, SSE/WS — plus a handful of
named exemptions (``/health``, ``/static/``, ``/auth/*``, ``/login``, the display reads). A path that
matches none of them falls through to ``return None``: **allowed**. The middleware is therefore not
default-deny, and a route added under a new prefix is public until somebody notices.

This pin turns that invisible default into an asserted set. It drives the *real* app in the passkey
configuration (``AEGIS_RUNTIME_MODE=production``, ``AEGIS_UI_VERSION=v2`` — the configuration the
docs tell operators to run) with an unauthenticated client, and requires every declared
``(rule, method)`` to be refused unless it appears below, each with its reason.

There are two records because the answer depends on where the caller is:

* ``RECORDED_PUBLIC_REMOTE`` — served even to a non-loopback caller.
* ``RECORDED_LOCAL_ONLY`` — refused to a non-loopback caller, served from loopback.

Both are compared for **equality**, so this fails in both directions: a new unprotected route grows a
record, and a route that becomes protected shrinks one. The record is a *measurement*, so when it
changes the answer is to re-measure and update it deliberately — never to loosen the comparison.

Recorded gap, not an endorsement (``docs/improvement-review.md`` §S-1①): the two ``/display`` *shell*
routes are public because ``ui_v2_prefer_spa_shell`` serves the shell from a ``before_request`` hook
*before* the route's own ``_require_display_read()`` can run. Measured: that guard is invoked 0 times
for ``/display`` and ``/display/presentations``, and once each for ``/display/overview`` and
``/display/power-state``. The display *data* routes are still guarded; only the static shell leaks.
"""

from __future__ import annotations

import re
from types import SimpleNamespace
from typing import Any

from test_dashboard_routes import _runtime

from aegis_ai.web import dashboard_routes

_REMOTE_BASE = "http://aegis.example.com"
_REMOTE_ENV = {"REMOTE_ADDR": "203.0.113.5"}
_LOCAL_BASE = "http://localhost"
_LOCAL_ENV = {"REMOTE_ADDR": "127.0.0.1"}

_REFUSED_STATUS = {401, 403}
_REDIRECT_STATUS = {301, 302, 303, 307, 308}

# Dummy values for rule converters, so every rule can be turned into a requestable path.
_DUMMY = {
    "int": "1",
    "float": "1.0",
    "path": "x",
    "uuid": "00000000-0000-0000-0000-000000000000",
    "any": "x",
    "string": "x",
}

# (rule template, method) -> why serving this to an unauthenticated non-loopback client is intended.
RECORDED_PUBLIC_REMOTE = {
    ("/assets/<path:filename>", "GET"): (
        "the built SPA bundle. Public the same way /static/ is, except that /static/ is exempted by "
        "name in the middleware while this one is public only by omission from the prefix list."
    ),
    ("/static/<path:filename>", "GET"): "Flask's static route; exempted by name in the middleware.",
    ("/auth/bootstrap/start", "POST"): "pre-login probe; must be reachable before a passkey exists.",
    ("/auth/login", "GET"): "the login page itself.",
    ("/auth/me", "GET"): "the login page reads it to choose bootstrap-vs-login.",
    ("/auth/passkey/login/options", "POST"): "first leg of passkey login.",
    ("/display", "GET"): "SPA shell for the display surface; no data. See the module docstring.",
    ("/display/presentations", "GET"): "SPA shell for the display surface; no data. See the docstring.",
}

# (rule template, method) -> why this one is served to loopback only.
RECORDED_LOCAL_ONLY = {
    ("/health", "GET"): "local_exempt; production refuses it to a non-loopback caller.",
    ("/display/overview", "GET"): "ui_v2._require_display_read().",
    ("/display/power-state", "GET"): "ui_v2._require_display_read().",
    ("/display/presentations/data", "GET"): "presentation._require_local_display_request().",
}


def _concretise(template: str) -> str:
    def replace(match: re.Match[str]) -> str:
        inner = match.group(1)
        converter = inner.split(":", 1)[0] if ":" in inner else "string"
        return _DUMMY.get(converter, "x")

    return re.sub(r"<([^>]+)>", replace, template)


def _app(tmp_path, monkeypatch) -> Any:
    monkeypatch.setenv("AEGIS_RUNTIME_MODE", "production")
    monkeypatch.setenv("AEGIS_SESSION_SECRET", "x" * 64)
    monkeypatch.setenv("AEGIS_UI_VERSION", "v2")
    for name in (
        "AEGIS_AUTH_MODE",
        "AEGIS_DASHBOARD_ACCESS_TOKEN",
        "AEGIS_DISPLAY_TOKEN",
        "AEGIS_DISPLAY_READ_TOKEN",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)  # never write data/auth into the repo
    monkeypatch.setattr(dashboard_routes, "_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(dashboard_routes.DashboardApp, "_start_autonomous_loop", lambda self: None)
    runtime = _runtime(tmp_path)
    # The shared test double omits presentation_manager, so /display/presentations/data would 500
    # (a gap in the double) instead of exercising its own host check.
    runtime.presentation_manager = SimpleNamespace(
        list_active=lambda limit=20: [], get_status=lambda: {}
    )
    app = dashboard_routes.DashboardApp(runtime=runtime).app
    app.config.update(TESTING=True)
    return app


def _measure(app: Any, base: str, environ: dict[str, str]) -> dict[tuple[str, str], tuple[bool, int]]:
    """Return {(rule template, method): (refused, status)} for every declared rule/method."""

    adapter = app.url_map.bind(base.split("//", 1)[1])
    client = app.test_client()
    observed: dict[tuple[str, str], tuple[bool, int]] = {}
    for rule in app.url_map.iter_rules():
        path = _concretise(rule.rule)
        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            try:
                adapter.match(path, method=method)
            except Exception as exc:  # the measurement itself is void if a rule is unreachable
                raise AssertionError(
                    f"cannot build a request for rule {rule.rule!r} ({method}): {exc}. "
                    "Add a dummy value for its converter."
                ) from exc
            response = client.open(path, method=method, base_url=base, environ_base=environ)
            refused = response.status_code in _REFUSED_STATUS or (
                response.status_code in _REDIRECT_STATUS
                and "/auth/login" in response.headers.get("Location", "")
            )
            observed[(rule.rule, method)] = (refused, response.status_code)
    return observed


def _public(observed: dict[tuple[str, str], tuple[bool, int]]) -> set[tuple[str, str]]:
    return {key for key, (refused, _) in observed.items() if not refused}


def _report(observed: set[tuple[str, str]], recorded: dict[tuple[str, str], str]) -> str:
    missing = sorted(observed - set(recorded))
    stale = sorted(set(recorded) - observed)
    lines = []
    if missing:
        lines.append("public but NOT recorded (add each with its reason, or protect it):")
        lines += [f"    {path}  {method}" for path, method in missing]
    if stale:
        lines.append("recorded as public but no longer public (delete the record):")
        lines += [f"    {path}  {method}  -- {recorded[(path, method)]}" for path, method in stale]
    return "\n".join(lines) or "no difference"


def test_a_remote_client_is_refused_every_route_but_the_recorded_public_set(tmp_path, monkeypatch) -> None:
    app = _app(tmp_path, monkeypatch)
    observed = _measure(app, _REMOTE_BASE, _REMOTE_ENV)

    assert len(observed) >= 180, f"the probe collapsed: only {len(observed)} rule/method pairs measured"

    public = _public(observed)
    assert public == set(RECORDED_PUBLIC_REMOTE), _report(public, RECORDED_PUBLIC_REMOTE)

    # A route that is "public" because it raised is not public by design; it is broken.
    broken = sorted(key for key, (refused, status) in observed.items() if not refused and status >= 500)
    assert broken == [], f"unauthenticated requests returned 5xx: {broken}"


def test_loopback_is_never_more_restrictive_than_a_remote_client(tmp_path, monkeypatch) -> None:
    app = _app(tmp_path, monkeypatch)
    remote = _measure(app, _REMOTE_BASE, _REMOTE_ENV)
    local = _measure(app, _LOCAL_BASE, _LOCAL_ENV)

    public_remote = _public(remote)
    public_local = _public(local)

    # Local access is a superset: the middleware's loopback branches can only add reads.
    assert public_remote <= public_local, sorted(public_remote - public_local)

    local_only = public_local - public_remote
    assert local_only == set(RECORDED_LOCAL_ONLY), _report(local_only, RECORDED_LOCAL_ONLY)
