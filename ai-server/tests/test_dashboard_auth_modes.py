"""The dashboard's authentication resolves to one of three modes — and the default installs none.

`docs/operations.md` §認証（既定の状態） documents this table; this pin is what keeps the code and
the document agreeing. The safety-critical direction — production rejects the token mode — is
already pinned by `test_passkey_auth.py::test_production_token_mode_is_rejected`. What was
unpinned is the **default**, and the default is the surprising one.

Measured 2026-10-02: with `AEGIS_RUNTIME_MODE` unset, `AEGIS_AUTH_MODE` unset and no
`AEGIS_DASHBOARD_ACCESS_TOKEN`, `install_dashboard_token_auth` resolves to **`disabled`** and
installs **nothing** — while `dashboard.py:24` and `docker_entrypoint.py:54` both bind `0.0.0.0`
by default, and `docs/operations.md` tells the reader to open `http://0.0.0.0:8090`.

That combination is deliberate: `BUG_REPORT.md` item 7 moved the development escape hatch into
`web/auth.py`. So it is pinned **as recorded** rather than changed — a future edit that quietly
makes the default authenticated, or quietly makes production unauthenticated, fails here instead
of shipping.

The three modes are told apart by which `before_request` hook gets installed, because that is
what actually decides whether a request is checked — not the env var.
"""

from __future__ import annotations

from flask import Flask

from aegis_ai.web.auth import install_dashboard_token_auth

#: Env vars that select the mode. Every case starts from all of them unset, then applies its own.
_MODE_ENV = (
    "AEGIS_RUNTIME_MODE",
    "AEGIS_AUTH_MODE",
    "AEGIS_DASHBOARD_ACCESS_TOKEN",
    "AEGIS_SESSION_SECRET",
)

#: The hook each mode installs. `disabled` installs neither.
_PASSKEY_HOOK = "_load_and_require_auth"
_TOKEN_HOOK = "_require_dashboard_token"


def _install(tmp_path, monkeypatch, **env) -> set[str]:
    """Install auth on a bare app under ``env`` and return the `before_request` hook names."""
    for name in _MODE_ENV:
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    # `install_passkey_auth` defaults `data_dir` to the relative path `data/auth`; chdir so a test
    # run never writes that directory into the repository.
    monkeypatch.chdir(tmp_path)
    app = Flask(__name__)
    install_dashboard_token_auth(app)
    return {getattr(fn, "__name__", "") for fn in app.before_request_funcs.get(None, [])}


def test_production_installs_the_passkey_hook(tmp_path, monkeypatch):
    hooks = _install(
        tmp_path, monkeypatch, AEGIS_RUNTIME_MODE="production", AEGIS_SESSION_SECRET="secret"
    )
    assert _PASSKEY_HOOK in hooks, (
        f"production resolved to no passkey middleware (hooks: {sorted(hooks)}) — every route, "
        "including /api/*, would be public"
    )


def test_the_bare_default_installs_no_auth_hook(tmp_path, monkeypatch):
    """The recorded default. If this ever fails, `docs/operations.md` is now wrong.

    No non-vacuity floor is needed here: the `disabled` branch installs nothing, so the hook set is
    legitimately empty. `test_production_installs_the_passkey_hook` is the guard that the detector
    can see hooks at all — if the hook names ever change, that test fails rather than this one
    passing for the wrong reason.
    """
    hooks = _install(tmp_path, monkeypatch)
    installed = hooks & {_PASSKEY_HOOK, _TOKEN_HOOK}
    assert installed == set(), (
        f"the bare default now installs {sorted(installed)}. That may be an improvement, but "
        "docs/operations.md §認証（既定の状態） documents the default as unauthenticated — update "
        "it in the same change."
    )


def test_a_configured_token_installs_the_token_hook(tmp_path, monkeypatch):
    hooks = _install(tmp_path, monkeypatch, AEGIS_DASHBOARD_ACCESS_TOKEN="tok")
    assert _TOKEN_HOOK in hooks, (
        f"a configured token did not install the token middleware (hooks: {sorted(hooks)})"
    )
    assert _PASSKEY_HOOK not in hooks, "token mode must not also install passkey auth"
