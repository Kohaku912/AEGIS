"""Cycle 53 pin: a value-coercion failure is never skipped in silence.

Measured 2026-10-06 (HEAD 5f6df56). The unit is a *family defined by its exception type*,
the same boundary cycles 43-52 used: **a handler whose whole body is ``continue`` and whose
except-type is exactly ``(TypeError, ValueError)``** — i.e. "this value would not coerce, so
skip it". Repo-wide there were **7 such handlers in 7 modules**, and every one of them
silently changed a *result*, not just a log:

* ``autonomous_loop._burden_activity`` — a history entry with an unreadable ``timestamp_ms``
  is dropped from the activity window, so the **burden metric** (``docs/burden-metric.md``,
  §3.1 穴 3) counts fewer work items than the history holds.
* ``desire/fulfillment._sanitize_deltas`` — a delta that is not a number is omitted from the
  **sanitized** dict. Dropping is fail-closed for the *value*, but the omission is invisible:
  the result silently has one key fewer than the model proposed.
* ``agora_service._recent_post_events`` — a post whose ``at`` will not coerce is dropped from
  the recent/burst window, so the **anti-burst guard counts fewer posts than arrived**.
* ``android/manager.get_status`` and ``._publish_proto_event`` — the connection metric keeps
  its previous value, so a corrupt reading is indistinguishable from "unchanged".
* ``presentation/preferences._preferred`` — a skipped entry cannot win the argmax, so one
  corrupt score silently changes **which key is returned**.
* ``social/manager._advance_processed_cursor`` — the item is excluded from the ordered list,
  so the cursor can advance past a message this scan never considered.

The discriminator is *structural*, not textual: a ``continue`` **inside a ``try``** swallows a
failure; the ``continue`` statements beside it (``if not isinstance(entry, dict): continue``,
``if item.channel != channel: continue``) are ordinary filters and are deliberately **not**
touched. The rule below therefore keys on the *handler*, never on the statement.

Behaviour is unchanged — each site gains one DEBUG record with ``exc_info``.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

from aegis_ai.integrations.agora.agora_service import AgoraService
from aegis_ai.presentation.preferences import PresentationPreferences

_SRC = Path(__file__).resolve().parents[1] / "src"

_LOOP = "aegis_ai.autonomous.autonomous_loop"
_FULFILLMENT = "aegis_ai.desire.fulfillment"
_AGORA = "aegis_ai.integrations.agora.service"
_ANDROID = "aegis_ai.integrations.android.manager"
_PREFERENCES = "aegis_ai.presentation.preferences"
_SOCIAL = "aegis_ai.social.manager"

FAMILY_TYPE = "(TypeError, ValueError)"

# (path relative to src/, enclosing function) -> (logger name, handler count measured 2026-10-06)
_NAMED_SITES: dict[tuple[str, str], tuple[str, int]] = {
    ("aegis_ai/autonomous/autonomous_loop.py", "_burden_activity"): (_LOOP, 1),
    ("aegis_ai/desire/fulfillment.py", "_sanitize_deltas"): (_FULFILLMENT, 1),
    ("aegis_ai/integrations/agora/agora_service.py", "_recent_post_events"): (_AGORA, 1),
    ("aegis_ai/integrations/android/manager.py", "get_status"): (_ANDROID, 1),
    ("aegis_ai/integrations/android/manager.py", "_publish_proto_event"): (_ANDROID, 2),
    ("aegis_ai/presentation/preferences.py", "_preferred"): (_PREFERENCES, 1),
    ("aegis_ai/social/manager.py", "_advance_processed_cursor"): (_SOCIAL, 1),
}


# ── ast helpers ────────────────────────────────────────────────────────────


def _modules() -> list[Path]:
    return sorted(_SRC.rglob("*.py"))


def _handlers(tree: ast.AST) -> list[ast.ExceptHandler]:
    return [n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)]


def _own_handlers(fn: ast.AST) -> list[ast.ExceptHandler]:
    """Handlers belonging to ``fn`` itself, excluding nested function bodies."""
    out: list[ast.ExceptHandler] = []

    def visit(node: ast.AST) -> None:
        if node is not fn and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return
        if isinstance(node, ast.Try):
            out.extend(node.handlers)
        for child in ast.iter_child_nodes(node):
            visit(child)

    for child in ast.iter_child_nodes(fn):
        visit(child)
    return out


def _except_type(handler: ast.ExceptHandler) -> str:
    return ast.unparse(handler.type) if handler.type is not None else "bare"


def _is_bare_continue(handler: ast.ExceptHandler) -> bool:
    return len(handler.body) == 1 and isinstance(handler.body[0], ast.Continue)


def _in_family(handler: ast.ExceptHandler) -> bool:
    """The cycle-53 family: a bare ``continue`` guarding a coercion failure."""
    return _is_bare_continue(handler) and _except_type(handler) == FAMILY_TYPE


def _names_a_logger(handler: ast.ExceptHandler) -> bool:
    for node in ast.walk(handler):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and getattr(func.value, "id", "") == "logger":
                return True
    return False


def _function(tree: ast.AST, name: str) -> ast.AST:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"{name} not found — re-measure")


def _records(caplog, name: str) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.name == name]


# ── the family rule ────────────────────────────────────────────────────────


def _family_sites() -> list[str]:
    found = []
    for path in _modules():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:  # pragma: no cover - not expected in src/
            continue
        for handler in _handlers(tree):
            if _in_family(handler):
                found.append(f"{path.relative_to(_SRC).as_posix()}:{handler.lineno}")
    return found


def test_no_handler_skips_a_coercion_failure_in_silence() -> None:
    offenders = _family_sites()
    assert offenders == [], (
        "these handlers swallow a (TypeError, ValueError) with a bare `continue`: "
        f"{offenders} — name them with a logger call"
    )


def test_the_census_is_not_vacuous() -> None:
    """Floors are measurements, not round numbers.

    Re-measured 2026-10-08 (cycle 107): **391 files / 1098 handlers** -- the count had
    drifted *below* the previous record (399 / 1117, set by cycle 102) because cycles
    103-107 deleted more modules and nothing forced a re-measure; the handler floor
    (1100) is what finally caught it, since 1098 < 1100. The file floor had one unit
    of margin left. The floors now carry a real margin again.
    """
    files = _modules()
    total = sum(len(_handlers(ast.parse(p.read_text(encoding="utf-8")))) for p in files)
    assert len(files) >= 380, f"only {len(files)} modules scanned; the walk is not reaching src/"
    assert total >= 1080, f"only {total} handlers scanned; the walk is not reaching the handlers"


def test_the_detector_sees_the_family_and_not_its_siblings() -> None:
    """Detector self-test: the rule must fire on the family and stay silent on its neighbours."""
    tree = ast.parse(
        "def f():\n"
        "    for x in items:\n"
        "        try:\n"
        "            pass\n"
        "        except (TypeError, ValueError):\n"
        "            continue\n"          # in the family
        "        except (TypeError, ValueError):\n"
        "            pass\n"              # same type, different shape
        "        except ValueError:\n"
        "            continue\n"          # narrower type
        "        except (TypeError, ValueError):\n"
        "            logger.debug('named', exc_info=True)\n"
        "            continue\n"          # same type, but named
    )
    hits = [h.lineno for h in _handlers(tree) if _in_family(h)]
    assert len(hits) == 1, f"the family detector fired {len(hits)} times, expected 1: {hits}"
    assert not _in_family([h for h in _handlers(tree) if _except_type(h) == "ValueError"][0])


def test_the_seven_sites_still_name_their_failures() -> None:
    by_file: dict[str, ast.AST] = {}
    for (rel, func), (logger_name, expected_count) in _NAMED_SITES.items():
        if rel not in by_file:
            by_file[rel] = ast.parse((_SRC / rel).read_text(encoding="utf-8"))
        handlers = _own_handlers(_function(by_file[rel], func))
        where = f"{rel}::{func}"
        assert len(handlers) == expected_count, (
            f"{where} now has {len(handlers)} handlers, expected {expected_count} — re-measure "
            "and update the pin rather than the count"
        )
        family = [h for h in handlers if _except_type(h) == FAMILY_TYPE]
        assert family, f"{where} no longer has a {FAMILY_TYPE} handler — re-measure"
        for handler in family:
            assert _names_a_logger(handler), (
                f"{where}:{handler.lineno} swallows a {FAMILY_TYPE} without a logger call"
            )
        assert logger_name in (_SRC / rel).read_text(encoding="utf-8"), (
            f"{rel} lost its logger {logger_name}"
        )


def test_the_site_map_covers_exactly_seven_sites() -> None:
    assert len(_NAMED_SITES) == 7
    assert len({rel for rel, _fn in _NAMED_SITES}) == 6


def test_the_legitimate_filters_are_left_alone() -> None:
    """The control that keeps the rule honest: a `continue` outside a `try` is a filter.

    ``_recent_post_events`` has three: a non-dict event, a stale timestamp, and — in
    ``_advance_processed_cursor`` — a different channel. The rule keys on the *handler*, so
    none of them is a site, and a future edit that moved one into a `try` would be caught
    by the rule rather than by this test.
    """
    tree = ast.parse((_SRC / "aegis_ai/integrations/agora/agora_service.py").read_text(encoding="utf-8"))
    fn = _function(tree, "_recent_post_events")
    bare_continues = sum(
        1 for n in ast.walk(fn) if isinstance(n, ast.Continue)
    )
    assert bare_continues >= 3, (
        f"only {bare_continues} `continue` statements in _recent_post_events — re-measure"
    )
    assert len(_own_handlers(fn)) == 1, (
        "the number of *handlers* is what the rule counts; the `continue` filters are not handlers"
    )


# ── behavioural: _sanitize_deltas ──────────────────────────────────────────


def test_sanitize_deltas_names_a_value_it_could_not_coerce(caplog) -> None:
    from aegis_ai.desire.fulfillment import _sanitize_deltas

    with caplog.at_level(logging.DEBUG, logger=_FULFILLMENT):
        deltas = _sanitize_deltas({"user_support": "not-a-number"}, "user_support")
    assert deltas == {}, "the uncoercible delta is no longer dropped — re-measure"
    records = _records(caplog, _FULFILLMENT)
    assert len(records) == 1, f"the dropped delta is silent again: {records}"
    assert "user_support" in records[0].getMessage()
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"


def test_sanitize_deltas_is_quiet_for_a_coercible_value_and_for_a_filtered_key(caplog) -> None:
    """Two quiet controls in one call: a good value, and a key excluded by an ordinary filter.

    ``unknown_desire`` is filtered *before* the ``try`` (it is not in ``DESIRE_FULFILLMENT``),
    so it must not produce a record — that is the difference between a filter and a swallow.
    """
    from aegis_ai.desire.fulfillment import _sanitize_deltas

    with caplog.at_level(logging.DEBUG, logger=_FULFILLMENT):
        deltas = _sanitize_deltas(
            {"user_support": "0.5", "unknown_desire": 1, "social": 1}, "user_support"
        )
    assert deltas == {"user_support": 0.5}, deltas
    assert _records(caplog, _FULFILLMENT) == [], "a legitimate filter or a good value now logs"


# ── behavioural: _preferred ────────────────────────────────────────────────


def test_preferred_names_a_score_it_could_not_coerce(caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger=_PREFERENCES):
        chosen = PresentationPreferences._preferred({"a": "not-a-number", "b": "2"}, "a")
    assert chosen == "b", "the uncoercible score is no longer skipped — re-measure"
    records = _records(caplog, _PREFERENCES)
    assert len(records) == 1, f"the skipped score is silent again: {records}"
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"


def test_preferred_is_quiet_when_every_score_coerces(caplog) -> None:
    with caplog.at_level(logging.DEBUG, logger=_PREFERENCES):
        chosen = PresentationPreferences._preferred({"a": "1", "b": "2"}, "a")
    assert chosen == "b"
    assert _records(caplog, _PREFERENCES) == [], "the healthy argmax now logs"


# ── behavioural: _recent_post_events ───────────────────────────────────────


def _agora_with_events(events: list) -> AgoraService:
    service = object.__new__(AgoraService)
    service._guard = {"recent_post_events": events}
    return service


def test_recent_post_events_names_an_event_it_could_not_coerce(caplog) -> None:
    import time

    now = time.time()
    service = _agora_with_events([{"at": "not-a-number", "body": "x"}])
    with caplog.at_level(logging.DEBUG, logger=_AGORA):
        events = service._recent_post_events()
    assert events == [], "the uncoercible event is no longer dropped — re-measure"
    records = _records(caplog, _AGORA)
    assert len(records) == 1, f"the dropped event is silent again: {records}"
    assert isinstance(records[0].exc_info, tuple), "the record dropped the traceback"
    # and the timestamp really would have been usable had it coerced
    good = _agora_with_events([{"at": now, "body": "x"}])
    assert len(good._recent_post_events()) == 1


def test_recent_post_events_is_quiet_for_a_usable_event(caplog) -> None:
    import time

    service = _agora_with_events([{"at": time.time(), "body": "hello"}])
    with caplog.at_level(logging.DEBUG, logger=_AGORA):
        events = service._recent_post_events()
    assert len(events) == 1
    assert _records(caplog, _AGORA) == [], "the healthy window now logs"


def test_the_detector_is_not_vacuous(caplog) -> None:
    caplog.set_level(logging.DEBUG, logger=_AGORA)
    logging.getLogger(_AGORA).debug("control")
    assert len(_records(caplog, _AGORA)) == 1, (
        "the record detector is blind; every 'is quiet' assertion above proves nothing"
    )
