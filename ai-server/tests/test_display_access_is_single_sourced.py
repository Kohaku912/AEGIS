"""The display-read rule lives in exactly one place, and the three guards still use it.

``auth/display_access.py`` is the single home of "may this request read the display?"
(``docs/improvement-review.md`` §S-2). Three modules used to spell it out, carrying three
copies of the host parse and three copies of the loopback host set, and ``presentation``
additionally narrowed it in three ways. This pin holds that consolidation in place in both
directions:

* the *host set* is declared once and the *credential* is named once — an ``ast`` scan of
  production source, so a mention in a docstring or a comment is not a declaration;
* each guard still reaches the shared rule, and ``presentation`` still passes its three
  narrowings — observed by spying on the name each module bound;
* the rule admits exactly the recorded callers, including the precedence cases that make
  the narrowings observable.

Scope is a rule, not a list: the scan covers ``src/aegis_ai/**/*.py`` — production source.
Tests set these env vars deliberately, and ``127.0.0.1`` appears in seven unrelated modules
(Ollama URLs, the gRPC bind default, the passkey origin), which is why the scan looks for
the *set of three hosts together* rather than for the substring. ``web/dashboard_legacy.
_is_local_request_host`` accepts ``""``/``0.0.0.0``/any loopback IP, so it is a different
fact and is deliberately not folded in — and, being uncalled, it does not declare this set.
"""

from __future__ import annotations

import ast
from collections.abc import Callable
from pathlib import Path

from flask import Flask

import aegis_ai
from aegis_ai.auth import session_middleware
from aegis_ai.auth.display_access import is_display_read_allowed
from aegis_ai.web.routes import presentation, ui_v2

_LOOPBACK_DECLARATION = {"127.0.0.1", "localhost", "::1"}
_CREDENTIAL_NAMES = {"AEGIS_DISPLAY_TOKEN", "AEGIS_DISPLAY_READ_TOKEN"}
_SOLE_DECLARER = "auth/display_access.py"

_CTX = Flask(__name__)
_TOKEN = "s3cret"


def _files_where(matches: Callable[[ast.AST], bool]) -> set[str]:
    root = Path(aegis_ai.__file__).resolve().parent
    found = set()
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if matches(tree):
            found.add(path.relative_to(root).as_posix())
    return found


def _declares_loopback_set(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Set):
            continue
        values = {e.value for e in node.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)}
        if _LOOPBACK_DECLARATION <= values:
            return True
    return False


def _names_credential(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in _CREDENTIAL_NAMES:
            return True
    return False


def test_the_loopback_host_set_is_declared_in_exactly_one_module() -> None:
    found = _files_where(_declares_loopback_set)
    assert found == {_SOLE_DECLARER}, (
        f"the loopback host set must be declared once, in {_SOLE_DECLARER}; found in {sorted(found)}"
    )


def test_the_display_credential_is_named_in_exactly_one_module() -> None:
    found = _files_where(_names_credential)
    assert found == {_SOLE_DECLARER}, (
        f"the display credential must be named once, in {_SOLE_DECLARER}; found in {sorted(found)}"
    )


def test_every_display_guard_consults_the_shared_rule(monkeypatch) -> None:
    """All three guards delegate; only ``presentation`` narrows, and by exactly three flags."""

    calls: list[dict[str, object]] = []

    def spy(**kwargs: object) -> bool:
        calls.append(kwargs)
        return True  # allow, so we observe the delegation and nothing else

    for module in (session_middleware, ui_v2, presentation):
        monkeypatch.setattr(module, "is_display_read_allowed", spy)

    with _CTX.test_request_context("/display/overview", base_url="http://localhost"):
        assert session_middleware._display_read_allowed("/display/overview") is True
        assert ui_v2._require_display_read() is None
        assert presentation._require_local_display_request() is None

    assert calls == [
        {},
        {},
        {"allow_token": False, "allow_remote_addr": False, "trust_forwarded_host": False},
    ], f"guards no longer delegate as recorded: {calls}"


_DEFAULTS = {"allow_token": True, "allow_remote_addr": True, "trust_forwarded_host": True}
_NARROWED = {"allow_token": False, "allow_remote_addr": False, "trust_forwarded_host": False}

# (base_url, extra headers, REMOTE_ADDR, env, flags, expected, why)
_RULE_CASES = [
    (
        "http://localhost", {}, "203.0.113.5", {"AEGIS_DISPLAY_TOKEN": _TOKEN}, _DEFAULTS, True,
        "a loopback Host is enough, with no credential presented",
    ),
    (
        "http://aegis.example.com", {}, "203.0.113.5", {"AEGIS_DISPLAY_TOKEN": _TOKEN}, _DEFAULTS, False,
        "a remote Host and a remote peer, with no credential",
    ),
    (
        "http://aegis.example.com", {"X-AEGIS-Display-Token": _TOKEN}, "203.0.113.5",
        {"AEGIS_DISPLAY_TOKEN": _TOKEN}, _DEFAULTS, True,
        "the configured credential admits a remote caller",
    ),
    (
        "http://aegis.example.com", {"X-AEGIS-Display-Token": "wrong"}, "203.0.113.5",
        {"AEGIS_DISPLAY_TOKEN": _TOKEN}, _DEFAULTS, False,
        "a wrong credential does not",
    ),
    (
        "http://aegis.example.com", {"X-AEGIS-Display-Token": _TOKEN}, "203.0.113.5",
        {}, _DEFAULTS, False,
        "with no credential configured, a presented one admits nothing",
    ),
    (
        "http://aegis.example.com", {"X-AEGIS-Display-Token": _TOKEN}, "203.0.113.5",
        {"AEGIS_DISPLAY_READ_TOKEN": _TOKEN}, _DEFAULTS, True,
        "the second env var spelling is honoured",
    ),
    (
        "http://aegis.example.com", {}, "127.0.0.1", {"AEGIS_DISPLAY_TOKEN": _TOKEN}, _DEFAULTS, True,
        "a loopback peer admits a remote Host",
    ),
    (
        "http://aegis.example.com", {"X-Forwarded-Host": "localhost"}, "127.0.0.1",
        {"AEGIS_DISPLAY_TOKEN": _TOKEN}, _DEFAULTS, True,
        "a forwarded host of localhost is trusted and admits",
    ),
    (
        "http://aegis.example.com", {"X-Forwarded-Host": "evil.example"}, "127.0.0.1",
        {"AEGIS_DISPLAY_TOKEN": _TOKEN}, _DEFAULTS, False,
        "a forwarded host is not trusted: it refuses before the peer fallback",
    ),
    (
        "http://[::1]:8090", {}, "203.0.113.5", {"AEGIS_DISPLAY_TOKEN": _TOKEN}, _DEFAULTS, True,
        "an IPv6 bracket host is parsed to ::1",
    ),
    (
        "http://aegis.example.com", {"X-AEGIS-Display-Token": _TOKEN}, "127.0.0.1",
        {"AEGIS_DISPLAY_TOKEN": _TOKEN}, _NARROWED, False,
        "presentation accepts no remote credential and has no peer fallback",
    ),
    (
        "http://localhost", {"X-Forwarded-Host": "evil.example"}, "203.0.113.5",
        {"AEGIS_DISPLAY_TOKEN": _TOKEN}, _NARROWED, True,
        "presentation reads Host alone, so a forwarded header cannot move it",
    ),
    (
        "http://localhost", {"X-Forwarded-Host": "evil.example"}, "203.0.113.5",
        {"AEGIS_DISPLAY_TOKEN": _TOKEN}, _DEFAULTS, False,
        "the shared default DOES trust the forwarded header — the contrast that makes it observable",
    ),
]


def test_the_rule_admits_exactly_the_recorded_callers(monkeypatch) -> None:
    for base_url, headers, remote, env, flags, expected, why in _RULE_CASES:
        for name in _CREDENTIAL_NAMES:
            monkeypatch.delenv(name, raising=False)
        for name, value in env.items():
            monkeypatch.setenv(name, value)
        with _CTX.test_request_context(
            "/display/overview", base_url=base_url, headers=headers, environ_base={"REMOTE_ADDR": remote}
        ):
            got = is_display_read_allowed(**flags)
        assert got is expected, f"{why}: expected {expected}, got {got}"
