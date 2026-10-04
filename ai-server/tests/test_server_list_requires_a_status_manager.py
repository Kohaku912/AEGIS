"""`_server_list` inherits an unguarded read: `_runtime_server_status` does
`runtime.status_manager.get_snapshot()` with **no** getattr default, so a runtime
that has no `status_manager` makes `_server_list` raise `AttributeError` -- while
the sibling `_errors` guards the same value with `getattr(..., None)` and
survives (DELEGATION.md section 4 item 44).

Measured 2026-10-05:
  - `dashboard_legacy._runtime_server_status(runtime=<bare object>)` raises
    AttributeError (dashboard_legacy.py:226);
  - `ui_overview._server_list(<bare object>)` raises AttributeError (line 2604);
  - `ui_overview._errors(<bare object>)` returns a dict -- it reads
    `getattr(runtime, "status_manager", None)` and then checks `hasattr`
    (line 1952), and so does `_status_snapshot` (line 2672).

Cycle 18's pin had to monkeypatch `_runtime_server_status` to isolate the Android
path (`tests/test_ui_overview_failures_are_named.py:140-145`); this pin records
the *reason* instead of leaving it in a comment. Cases:
  - the bare runtime really lacks `status_manager` (so the raise is about the
    missing attribute and not something else);
  - `_runtime_server_status` raises AttributeError;
  - `_server_list` raises AttributeError;
  - control: with a `status_manager` present, `_server_list` returns a list;
  - the asymmetry: `_errors` does not raise on the same bare runtime.
"""

from __future__ import annotations

import pytest

from aegis_ai.web import dashboard_legacy as legacy
from aegis_ai.web import ui_overview as ui


class _Bare:
    """A minimal runtime: no dashboard managers at all."""


class _StatusManager:
    def get_snapshot(self) -> dict:
        return {}


class _WithStatus:
    def __init__(self) -> None:
        self.status_manager = _StatusManager()


def test_the_bare_runtime_really_lacks_a_status_manager() -> None:
    assert not hasattr(_Bare(), "status_manager")


def test_runtime_server_status_raises_without_a_status_manager() -> None:
    with pytest.raises(AttributeError):
        legacy._runtime_server_status(runtime=_Bare())


def test_server_list_raises_without_a_status_manager() -> None:
    with pytest.raises(AttributeError):
        ui._server_list(_Bare())


def test_server_list_returns_a_list_with_a_status_manager() -> None:
    """Control: the raise above is caused by the missing attribute."""
    assert isinstance(ui._server_list(_WithStatus()), list)


def test_errors_survives_without_a_status_manager() -> None:
    """The asymmetry: `_errors` guards the same value, `_server_list` does not."""
    assert isinstance(ui._errors(_Bare()), dict)
