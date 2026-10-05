"""The notification/ package names its failures.

Measured 2026-10-06 (cycle 49)
-----------------------------
Five handlers under ``notification/`` had a body that was exactly ``pass``, in five
modules. Two of those modules (``preferences``, ``quiet_hours``) had **no logger at all**
-- so the package gained two.

Four of the five are on the delivery path, and two of those change **behaviour**, not just
visibility:

- ``NotificationPreferences._load_from_settings`` -- the settings store is read to *disable*
  the types the user turned off. Swallowing the read leaves every type **enabled**:
  ``_load_from_settings`` runs in ``__init__`` and its whole effect is to flip flags to
  ``False``, so a failure means the user's "off" is silently ignored. Measured: the flags
  stay at ``DEFAULT_ENABLED``.
- ``QuietHoursManager._load_from_settings`` -- same shape: the failure leaves quiet hours
  un-applied, so non-critical notifications fire during the period the user asked to be
  left alone.
- ``OsNotificationProvider.is_available`` -- the probe returned ``False`` either way, so
  *"the probe failed"* and *"OS notifications are unavailable"* were the same answer. The
  value is unchanged; the reason is now in the log.
- ``NotificationManager.send`` -- the ``notification.sent`` event was dropped silently, so
  the rest of the system did not learn a notification had gone out.
- ``channels/email.py::_smtp_send`` -- the ``finally: client.quit()`` cleanup. The message
  had already been submitted, so the failure is benign -- but a *benign* failure is still a
  failure, and the send result does not mention it.

All five now log at DEBUG (behaviour-preserving: a record only). The two ``_load_from_settings``
methods are the *same shape* (guard, ``settings.get()``, map fields) in two modules and remain
two copies -- consolidation is a separate change with a different blast radius, recorded in
``DELEGATION.md`` section 4.

Scope
-----
Cycle 16's unit, applied to a package: **no handler under ``notification/`` has a body that
is exactly ``pass``**. Handlers that produce a value the caller receives stay out (a
different, milder class) -- ``_parse_time``'s ``except (ValueError, IndexError): return 0``
is one of those and is not touched.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

from aegis_ai.notification.channels.email import _smtp_send
from aegis_ai.notification.models import Notification, NotificationType
from aegis_ai.notification.notification_manager import NotificationManager
from aegis_ai.notification.os_provider import OsNotificationProvider
from aegis_ai.notification.preferences import NotificationPreferences
from aegis_ai.notification.quiet_hours import QuietHoursManager

_PKG = Path(__file__).resolve().parents[1] / "src" / "aegis_ai" / "notification"

_PREFS = "aegis_ai.notification.preferences"
_QUIET = "aegis_ai.notification.quiet_hours"
_MANAGER = "aegis_ai.notification.notification_manager"
_OS = "aegis_ai.notification.os_provider"
_EMAIL = "aegis_ai.notification.channels.email"

# (module path relative to the package, enclosing function) -> the logger that must name it.
_NAMED_SITES = {
    ("preferences.py", "_load_from_settings"): _PREFS,
    ("quiet_hours.py", "_load_from_settings"): _QUIET,
    ("notification_manager.py", "send"): _MANAGER,
    ("os_provider.py", "is_available"): _OS,
    ("channels/email.py", "_smtp_send"): _EMAIL,
}

#: The two loggers this cycle added (the other three modules already had one).
_NEW_LOGGERS = {_PREFS: "preferences.py", _QUIET: "quiet_hours.py"}


# ── helpers ────────────────────────────────────────────────────────────────


def _modules() -> list[Path]:
    return sorted(_PKG.rglob("*.py"))


def _handlers(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            yield tree, node


def _body_without_docstring(handler: ast.ExceptHandler) -> list[ast.stmt]:
    return [
        s
        for s in handler.body
        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)
                and isinstance(s.value.value, str))
    ]


def _is_bare_pass(handler: ast.ExceptHandler) -> bool:
    body = _body_without_docstring(handler)
    return len(body) == 1 and isinstance(body[0], ast.Pass)


def _enclosing_function(tree: ast.AST, target: ast.AST) -> str:
    best = "<module>"
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in ast.walk(node):
                if sub is target:
                    best = node.name
    return best


def _names_a_logger(handler: ast.ExceptHandler) -> bool:
    for stmt in _body_without_docstring(handler):
        for sub in ast.walk(stmt):
            if isinstance(sub, ast.Attribute) and sub.attr in (
                "debug", "info", "warning", "error", "exception", "critical", "log",
            ):
                if isinstance(sub.value, ast.Name) and "log" in sub.value.id:
                    return True
    return False


# ── structural ─────────────────────────────────────────────────────────────


def test_no_handler_in_notification_is_a_bare_pass():
    offenders = []
    for path in _modules():
        for _tree, handler in _handlers(path):
            if _is_bare_pass(handler):
                offenders.append(f"{path.name}:{handler.lineno}")
    assert offenders == [], f"bare `pass` handlers remain in notification/: {offenders}"


def test_the_census_is_not_vacuous():
    """Measured 2026-10-06: 17 modules, 18 handlers. The floors catch a wrong root.

    ⚠️ The first version of this control used a guessed floor (25) and failed on a
    *correct* tree -- the package is smaller than the ``memory/`` one. Floors are
    measurements, not round numbers.
    """
    files = _modules()
    total = sum(1 for path in files for _ in _handlers(path))
    assert len(files) >= 15, f"only {len(files)} files under notification/ -- wrong root?"
    assert total >= 15, f"only {total} handlers found -- the scanner is not seeing them"


def test_each_named_site_calls_a_logger():
    seen = {}
    for path in _modules():
        for tree, handler in _handlers(path):
            key = (path.relative_to(_PKG).as_posix(), _enclosing_function(tree, handler))
            if key in _NAMED_SITES:
                seen[key] = _names_a_logger(handler)
    assert set(seen) == set(_NAMED_SITES), (
        f"missing sites: {sorted(set(_NAMED_SITES) - set(seen))}"
    )
    unnamed = sorted(k for k, ok in seen.items() if not ok)
    assert unnamed == [], f"these sites no longer log their failure: {unnamed}"


def test_the_two_new_loggers_exist():
    for name, rel in _NEW_LOGGERS.items():
        text = (_PKG / rel).read_text(encoding="utf-8")
        assert f'getLogger("{name}")' in text, f"{rel} lost its logger {name}"


# ── behavioural: the two that silently ignore the user's settings ──────────


class _RaisingSettings:
    def get(self):
        raise RuntimeError("settings store unavailable")


def test_preferences_names_a_failed_settings_read(caplog):
    with caplog.at_level(logging.DEBUG, logger=_PREFS):
        prefs = NotificationPreferences(settings_store=_RaisingSettings())
    assert any("Failed to load notification preferences" in r.getMessage() for r in caplog.records), (
        "a failed settings read left the user's disabled types looking enabled, silently"
    )
    assert any(r.exc_info for r in caplog.records), "the traceback was not attached"
    # Behaviour preserved, and this is *why* the silence mattered: the whole effect of
    # `_load_from_settings` is to flip flags to False, so a failure leaves the defaults --
    # every type enabled, including the ones the user turned off.
    assert prefs.is_type_enabled(NotificationType.APPROVAL_REQUIRED) is True


def test_preferences_without_a_store_is_quiet(caplog):
    """Control: no settings store configured is not a failure.

    Also documents the fallback the *failing* case leaves behind: the built-in defaults.
    """
    with caplog.at_level(logging.DEBUG, logger=_PREFS):
        prefs = NotificationPreferences(settings_store=None)
    assert prefs.is_type_enabled(NotificationType.APPROVAL_REQUIRED) is True
    assert [r for r in caplog.records if r.name == _PREFS] == []


def test_quiet_hours_names_a_failed_settings_read(caplog):
    with caplog.at_level(logging.DEBUG, logger=_QUIET):
        QuietHoursManager(settings_store=_RaisingSettings())
    assert any("Failed to load quiet hours" in r.getMessage() for r in caplog.records)


def test_quiet_hours_without_a_store_is_quiet(caplog):
    """Control: the guard's early return is a deliberate non-logging path."""
    with caplog.at_level(logging.DEBUG, logger=_QUIET):
        QuietHoursManager(settings_store=None)
    assert [r for r in caplog.records if r.name == _QUIET] == []


# ── behavioural: the delivery path ────────────────────────────────────────


class _RaisingEventManager:
    def publish(self, *_a, **_kw):
        raise RuntimeError("event bus down")

    def publish_event(self, *_a, **_kw):
        raise RuntimeError("event bus down")


def test_notification_manager_names_a_dropped_sent_event(caplog):
    manager = NotificationManager(event_manager=_RaisingEventManager())
    manager._notifications["n1"] = {
        "notification_id": "n1",
        "title": "t",
        "status": "",
        "delivery_status": {},
    }
    with caplog.at_level(logging.DEBUG, logger=_MANAGER):
        sent = manager.send("n1")
    assert sent is not None and sent["status"] == "sent", "the send itself changed"
    assert any("Failed to publish notification.sent" in r.getMessage() for r in caplog.records)


def test_notification_manager_without_an_event_manager_is_quiet(caplog):
    """Control: no event manager configured is not a failure."""
    manager = NotificationManager(event_manager=None)
    manager._notifications["n1"] = {
        "notification_id": "n1",
        "title": "t",
        "status": "",
        "delivery_status": {},
    }
    with caplog.at_level(logging.DEBUG, logger=_MANAGER):
        manager.send("n1")
    assert [r for r in caplog.records if r.name == _MANAGER] == []


def test_os_provider_names_a_failed_probe(monkeypatch, caplog):
    provider = OsNotificationProvider()
    provider._platform = "linux"

    def _boom(*_a, **_kw):
        raise OSError("no such binary")

    monkeypatch.setattr("aegis_ai.notification.os_provider.subprocess.run", _boom)
    with caplog.at_level(logging.DEBUG, logger=_OS):
        available = provider.is_available()
    assert available is False, "the reported value moved"
    assert any("OS notification probe failed" in r.getMessage() for r in caplog.records), (
        "a failed probe is still indistinguishable from 'unavailable'"
    )


def test_os_provider_on_an_unprobed_platform_is_quiet(caplog):
    """Control: ``darwin`` returns True without probing, so nothing should be reported."""
    provider = OsNotificationProvider()
    provider._platform = "darwin"
    with caplog.at_level(logging.DEBUG, logger=_OS):
        available = provider.is_available()
    assert available is True
    assert [r for r in caplog.records if r.name == _OS] == []


# ── behavioural: the cleanup failure in _smtp_send ────────────────────────


def test_smtp_send_names_a_failed_quit(monkeypatch, caplog):
    """The message is submitted; only the cleanup fails -- and that is now recorded."""

    class _Client:
        def starttls(self):
            return None

        def login(self, *_a, **_kw):
            return None

        def send_message(self, *_a, **_kw):
            return None

        def quit(self):
            raise OSError("connection already closed")

    monkeypatch.setattr("smtplib.SMTP", lambda *_a, **_kw: _Client())
    with caplog.at_level(logging.DEBUG, logger=_EMAIL):
        ok, code, err = _smtp_send(
            Notification(title="t", body="b"),
            host="127.0.0.1",
            port=587,
            user="",
            password="",
            sender="a@localhost",
            recipient="b@localhost",
            timeout=1.0,
        )
    assert (ok, code, err) == (True, 250, ""), "the send result moved"
    assert any("SMTP client quit failed" in r.getMessage() for r in caplog.records)


def test_smtp_send_with_a_clean_quit_is_quiet(monkeypatch, caplog):
    """Control: a normal quit must not be reported."""

    class _Client:
        def starttls(self):
            return None

        def login(self, *_a, **_kw):
            return None

        def send_message(self, *_a, **_kw):
            return None

        def quit(self):
            return None

    monkeypatch.setattr("smtplib.SMTP", lambda *_a, **_kw: _Client())
    with caplog.at_level(logging.DEBUG, logger=_EMAIL):
        ok, _code, _err = _smtp_send(
            Notification(title="t", body="b"),
            host="127.0.0.1",
            port=587,
            user="",
            password="",
            sender="a@localhost",
            recipient="b@localhost",
            timeout=1.0,
        )
    assert ok is True
    assert [r for r in caplog.records if r.name == _EMAIL] == []
