"""Cycle 18 pin: the eight *bare-absence* swallows in `web/ui_overview.py` name themselves.

Why eight, and not twenty-two
-----------------------------
`ui_overview.py` has **twenty-six** `except` handlers.  Before this cycle **four** named
themselves (all added by cycle 11: the two in `_operations`, `_autonomous_logs`, and
`_pending_approvals`).  The other **twenty-two** record nothing, but they are not one thing:

  * **8 are deliberate coercion / signature fallbacks** that still produce a value --
    `_number`, `_as_wire_text`, `_json_preview`, `_call_with_limit`, `_humanize_event_message`,
    `_causal_chain_from_operation` (an optional `ImportError`), and the two `except TypeError`
    retries that call a method with a narrower signature.  Naming these would misdescribe a
    handled conversion;
  * **5 already put the exception into the returned payload** -- `_section`, `_agent_state`,
    `_user_understanding`, `_initiative`, `_behavioral_reports` all return
    ``{"summary": f"... unavailable: {exc}"}`` (or an ``error`` key), so the failure is visible
    in the response, not swallowed;
  * **1 is a documented deliberate fallback** -- the `_errors` merge whose own comment says the
    raw StatusManager data "remains a usable fallback";
  * **8 are bare-absence swallows**: the read fails and the section silently shows nothing,
    which is indistinguishable from a legitimately empty state.

This pin covers those **eight**.  Reachability was measured first: all five enclosing
functions are live (`_mind_summary` / `_usage` / `_errors` are registered as sections at
`:38` / `:69` / `:70`; `_server_list` is called at `:725`/`:769`/`:848`/`:1651`;
`_recent_ui_events` at `:905`/`:939`/`:964`).
"""
from __future__ import annotations

import ast
import logging
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from aegis_ai.web import ui_overview as ui

_LOGGER = "aegis_ai.web.ui_overview"
_AI_SERVER = Path(__file__).resolve().parents[1]
_MODULE = _AI_SERVER / "src" / "aegis_ai" / "web" / "ui_overview.py"

# label -> a phrase only that site's warning contains.
_NAMED: dict[str, str] = {
    "autonomy": "looks like a loop with nothing to report",
    "desires": "looks like a calm one",
    "usage": "reported as an available service",
    "server_snapshot": "looks like servers with nothing to report",
    "repair_status": "looks like a healthy one",
    "android": "looks like an offline device",
    "events": "looks like a quiet system",
    "event_row": "indistinguishable from an event that never happened",
}

# Functions whose handlers are *deliberate* conversions/signature retries -- they must stay unnamed.
_COERCION = {
    "_number",
    "_as_wire_text",
    "_json_preview",
    "_call_with_limit",
    "_humanize_event_message",
    "_causal_chain_from_operation",
}
# Functions whose handlers already put the error into the payload -- no record needed.
_SURFACING = {"_section", "_agent_state", "_user_understanding", "_initiative", "_behavioral_reports"}

_TYPE_SHAPE = re.compile(r"\([A-Za-z_][A-Za-z0-9_]*(Error|Exception):")


# -- doubles ----------------------------------------------------------------


class _RaisingLoop:
    def get_status(self):
        raise RuntimeError("loop unavailable")


class _RaisingDesire:
    def apply_decay(self):
        raise RuntimeError("desire system unavailable")


class _RaisingSnapshot:
    def get_snapshot(self):
        raise RuntimeError("status manager unavailable")


class _RaisingRepair:
    def get_status(self):
        raise RuntimeError("repair manager unavailable")


class _RaisingAndroid:
    def get_status(self):
        raise RuntimeError("android manager unavailable")


class _RaisingEvents:
    def list_recent(self, *_a, **_k):
        raise RuntimeError("event manager unavailable")


class _OneBadEvent:
    def list_recent(self, *_a, **_k):
        return [{"event_type": "x"}]


def _runtime(**kw) -> SimpleNamespace:
    return SimpleNamespace(**kw)


def _make(label: str) -> SimpleNamespace:
    return {
        "autonomy": lambda: _runtime(autonomous_loop=_RaisingLoop()),
        "desires": lambda: _runtime(desire_system=_RaisingDesire()),
        "usage": lambda: _runtime(),
        "server_snapshot": lambda: _runtime(status_manager=_RaisingSnapshot()),
        "repair_status": lambda: _runtime(repair_manager=_RaisingRepair()),
        "android": lambda: _runtime(android_manager=_RaisingAndroid()),
        "events": lambda: _runtime(event_manager=_RaisingEvents()),
        "event_row": lambda: _runtime(event_manager=_OneBadEvent()),
    }[label]()


def _drive(label: str, runtime, monkeypatch) -> None:
    if label in ("autonomy", "desires"):
        ui._mind_summary(runtime)
    elif label == "usage":
        from aegis_ai.observability.llm_usage.service import LLMUsageService

        def _boom(self, *_a, **_k):
            raise RuntimeError("usage service unavailable")

        monkeypatch.setattr(LLMUsageService, "get_summary", _boom)
        ui._usage(runtime)
    elif label in ("server_snapshot", "repair_status"):
        ui._errors(runtime)
    elif label == "android":
        # `_server_list` calls `_runtime_server_status`, which reads
        # `runtime.status_manager` with **no** getattr default; patch it so this test
        # exercises only the android block.
        import aegis_ai.web.dashboard_legacy as legacy

        monkeypatch.setattr(legacy, "_runtime_server_status", lambda **_k: {"servers": []})
        ui._server_list(runtime)
    elif label == "events":
        ui._recent_ui_events(runtime, limit=5)
    elif label == "event_row":

        def _boom(_raw):
            raise RuntimeError("normalisation unavailable")

        monkeypatch.setattr(ui, "normalize_ui_event", _boom)
        ui._recent_ui_events(runtime, limit=5)
    else:  # pragma: no cover
        raise AssertionError(f"unknown label {label!r}")


# -- the pin ----------------------------------------------------------------


@pytest.mark.parametrize("label", sorted(_NAMED))
def test_a_bare_absence_swallow_is_named(label, monkeypatch, caplog) -> None:
    runtime = _make(label)
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        _drive(label, runtime, monkeypatch)

    messages = [r.getMessage() for r in caplog.records if r.name == _LOGGER]
    assert any(_NAMED[label] in m for m in messages), (
        f"{label}: the failure left no record naming its consequence; got {messages}"
    )
    assert any(_TYPE_SHAPE.search(m) for m in messages), (
        f"{label}: no record named the exception type; got {messages}"
    )


def test_a_legitimate_absence_stays_silent(monkeypatch, caplog) -> None:
    """A section with nothing configured is *empty*, not *broken* -- it must not warn."""
    import aegis_ai.web.dashboard_legacy as legacy

    monkeypatch.setattr(legacy, "_runtime_server_status", lambda **_k: {"servers": []})
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        assert ui._recent_ui_events(_runtime(), limit=5) == []
        ui._mind_summary(_runtime())
        ui._errors(_runtime())
        ui._server_list(_runtime())
    assert [r for r in caplog.records if r.name == _LOGGER] == []


# -- structural: the deliberate handlers must stay unnamed ------------------


def _handlers() -> list[tuple[str, int, bool, bool]]:
    """(enclosing function, lineno, calls logger, mentions `exc`) per handler."""
    out: list[tuple[str, int, bool, bool]] = []
    stack: list[str] = []

    class V(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_ExceptHandler(self, node):
            calls = any(
                isinstance(s, ast.Call)
                and isinstance(s.func, ast.Attribute)
                and isinstance(s.func.value, ast.Name)
                and s.func.value.id == "logger"
                for s in ast.walk(node)
            )
            uses_exc = any(isinstance(s, ast.Name) and s.id == "exc" for s in ast.walk(node))
            out.append((stack[-1] if stack else "", node.lineno, calls, uses_exc))
            self.generic_visit(node)

    V().visit(ast.parse(_MODULE.read_text(encoding="utf-8")))
    return out


def test_the_module_still_has_twenty_six_handlers_and_twelve_named() -> None:
    """Non-vacuity: 26 handlers, 4 pre-existing + these 8 = 12 named, 14 unnamed."""
    handlers = _handlers()
    named = [h for h in handlers if h[2]]
    assert len(handlers) == 26, f"expected 26 handlers, found {len(handlers)}"
    assert len(named) == 12, f"expected 12 named handlers, found {len(named)}"


def test_the_coercion_guards_stay_unnamed() -> None:
    """These convert a value or retry a narrower signature -- a record would misdescribe them."""
    handlers = _handlers()
    for func in sorted(_COERCION):
        offenders = [h for h in handlers if h[0] == func and h[2]]
        assert not offenders, f"{func}: a deliberate fallback gained a record at {offenders}"


def test_the_already_surfacing_handlers_need_no_record() -> None:
    """These already return the error in the payload, so the failure is visible."""
    handlers = _handlers()
    for func in sorted(_SURFACING):
        mine = [h for h in handlers if h[0] == func]
        assert mine, f"{func}: no handler found (the scan is not reading the tree)"
        for _fn, lineno, calls, uses_exc in mine:
            assert not calls, f"{func}:{lineno} gained a record although it surfaces the error"
            assert uses_exc, f"{func}:{lineno} does not put the exception into the payload"


def test_the_errors_surface_names_exactly_two_handlers() -> None:
    """`_errors` has three `except Exception` blocks; only the two bare absences are named."""
    handlers = _handlers()
    assert len([h for h in handlers if h[0] == "_errors" and h[2]]) == 2
