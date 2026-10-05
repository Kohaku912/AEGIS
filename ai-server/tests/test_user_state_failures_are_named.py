"""The user-state manager names its failures.

Measured 2026-10-06
-------------------
``user_state/manager.py`` had **no logger at all** and **four** handlers whose whole
body was ``pass`` -- every one of them on a live path (the composition root builds the
manager at ``runtime.py:1086`` and starts the poller at ``:1422``):

* ``__init__`` -- ``event_manager.subscribe(self.on_event)``. A manager that could not
  subscribe is **constructed and looks healthy, but deaf**: it will never receive an
  event. Nothing distinguished it from a quiet system.
* ``_offer_raw_to_pdc`` -- the user-activity offer to the personal-data core was dropped
  in silence.
* ``start_pc_poller`` -- the poller thread swallows a per-iteration failure, so a poller
  whose every poll fails **looks like a healthy, quiet poller** and spins forever.
* ``_home_wifi_bssids`` -- a failed settings read yields a **partial** home-Wi-Fi set,
  silently changing presence detection ("is the user home?").

This cycle names all four at DEBUG (behaviour-preserving: a record only) and adds the
module's logger.

Scope
-----
The unit is cycle 16's: **no handler in this module may be a bare ``pass``**. Seven
further handlers are *not* bare ``pass`` and stay out of scope -- they produce a value
the caller receives (``_safe_float`` / ``_safe_int`` return the default; ``on_event``
falls back to ``{}``; ``_pc_poll_allowed`` fails open) or skip one bad line while
iterating (``query_recent`` / ``list_days`` / ``list_archives``). Those are a different,
milder class; naming them would change what "silent" means here.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from aegis_ai.user_state.manager import UserStateManager

_LOGGER = "aegis_ai.user_state.manager"
_MODULE = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "aegis_ai"
    / "user_state"
    / "manager.py"
)


# ── doubles ────────────────────────────────────────────────────────────────


class _RaisingSubscriber:
    def subscribe(self, handler):
        raise RuntimeError("event bus unavailable")


class _OkSubscriber:
    def subscribe(self, handler):
        self.handler = handler


class _RaisingPDC:
    def ingest_bus_event(self, event):
        raise RuntimeError("personal-data core unavailable")


class _RaisingSettings:
    def get_all(self):
        raise RuntimeError("settings unavailable")


class _OkSettings:
    def get_all(self):
        return {}


def _manager(tmp_path, **kw) -> UserStateManager:
    # `data_dir` is redirected so the archive key never lands in the repo's data/.
    return UserStateManager(data_dir=str(tmp_path / "user_state"), **kw)


# ── structural: no bare `pass` survives in the module ──────────────────────


def _all_pass_handlers() -> list[int]:
    tree = ast.parse(_MODULE.read_text(encoding="utf-8"))
    return [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.ExceptHandler)
        and node.body
        and all(isinstance(stmt, ast.Pass) for stmt in node.body)
    ]


def test_no_handler_in_the_manager_swallows_without_a_record() -> None:
    silent = _all_pass_handlers()
    assert silent == [], f"handler(s) still swallow with a bare `pass`: {silent}"


def test_the_scan_is_not_vacuous() -> None:
    """The module must have a logger, and the walk must see its handlers."""
    source = _MODULE.read_text(encoding="utf-8")
    assert 'logger = logging.getLogger("aegis_ai.user_state.manager")' in source
    tree = ast.parse(source)
    handlers = [n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)]
    assert len(handlers) >= 10, f"only {len(handlers)} handlers found -- the walk is broken"
    logging_handlers = [
        n
        for n in handlers
        if any(
            isinstance(s, ast.Call)
            and isinstance(s.func, ast.Attribute)
            and isinstance(s.func.value, ast.Name)
            and s.func.value.id == "logger"
            for s in ast.walk(n)
        )
    ]
    assert len(logging_handlers) >= 4, (
        f"only {len(logging_handlers)} handlers log -- the four named sites are gone"
    )


def test_the_poller_handler_names_its_failure() -> None:
    """The poller loop lives in a thread closure, so pin its handler structurally."""
    tree = ast.parse(_MODULE.read_text(encoding="utf-8"))
    poller = next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "start_pc_poller"
    )
    handlers = [n for n in ast.walk(poller) if isinstance(n, ast.ExceptHandler)]
    assert handlers, "start_pc_poller has no handler -- the scan is measuring the wrong thing"
    assert all(
        any(
            isinstance(s, ast.Call)
            and isinstance(s.func, ast.Attribute)
            and isinstance(s.func.value, ast.Name)
            and s.func.value.id == "logger"
            for s in ast.walk(h)
        )
        for h in handlers
    ), "a poller-loop handler swallows without a record"


# ── behavioural: the failure really reaches a record ───────────────────────


def test_a_failed_subscribe_is_named(tmp_path, caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        _manager(tmp_path, event_manager=_RaisingSubscriber())

    messages = [r.getMessage() for r in caplog.records if r.name == _LOGGER]
    assert any("subscribe" in m for m in messages), (
        f"a failed subscribe left no record; got {messages}"
    )


def test_a_successful_subscribe_stays_silent(tmp_path, caplog) -> None:
    """Control: a working subscription must not warn."""
    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        manager = _manager(tmp_path, event_manager=_OkSubscriber())

    assert manager._event_manager is not None
    assert [r for r in caplog.records if r.name == _LOGGER] == []


def test_a_failed_pdc_offer_is_named(tmp_path, caplog) -> None:
    manager = _manager(tmp_path)
    manager._event_manager = SimpleNamespace(_personal_data_core=_RaisingPDC())

    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        manager._offer_raw_to_pdc("pc.user_activity.snapshot", {})

    messages = [r.getMessage() for r in caplog.records if r.name == _LOGGER]
    assert any("pc.user_activity.snapshot" in m for m in messages), (
        f"a dropped personal-data offer left no record; got {messages}"
    )


def test_an_absent_pdc_stays_silent(tmp_path, caplog) -> None:
    """Control: no personal-data core at all is a legitimate absence, not a failure."""
    manager = _manager(tmp_path)
    manager._event_manager = SimpleNamespace(_personal_data_core=None)

    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        manager._offer_raw_to_pdc("pc.user_activity.snapshot", {})

    assert [r for r in caplog.records if r.name == _LOGGER] == []


def test_a_failed_home_wifi_read_is_named(tmp_path, caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        _manager(tmp_path, settings_store=_RaisingSettings())

    messages = [r.getMessage() for r in caplog.records if r.name == _LOGGER]
    assert any("home_wifi_bssids" in m for m in messages), (
        f"a failed home-Wi-Fi settings read left no record; got {messages}"
    )


def test_a_readable_settings_store_stays_silent(tmp_path, caplog) -> None:
    """Control: a settings store that answers must not warn."""
    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        _manager(tmp_path, settings_store=_OkSettings())

    assert [r for r in caplog.records if r.name == _LOGGER] == []


@pytest.mark.parametrize("store", [None, _OkSettings()], ids=["no_store", "ok_store"])
def test_home_wifi_defaults_do_not_warn(tmp_path, caplog, store) -> None:
    """Control: the two legitimate shapes (no store / an empty store) are silent."""
    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        manager = _manager(tmp_path, settings_store=store)

    assert manager._ingest is not None
    assert [r for r in caplog.records if r.name == _LOGGER] == []
