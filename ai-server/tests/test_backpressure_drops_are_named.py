"""Cycle 56 pin: a deliberate back-pressure drop is named -- at DEBUG, with no traceback.

Measured 2026-10-06 (HEAD 639fad7). The unit is the same bare-discard family the previous cycles
used, but the *conclusion is different*: ``except queue.Full`` guards a **bounded queue in front of a
slow client**, so the drop is **deliberate policy**, not an unexpected failure. Three sites swallowed
it with ``pass``:

* ``grpc_server.StreamUiEvents._handler`` -- the gRPC ``UiEvent`` stream client falls behind.
* ``web/manager_routes.presentation_stream._on_event`` -- the presentation SSE client falls behind.
* ``web/routes/ui.ui_stream._handler`` -- the ``/api/ui/stream`` SSE client falls behind.

The fourth site, ``web/routes/approval.approval_events``, **already named it** and thereby fixed the
convention:

    except queue.Full:
        logger.debug("Dropped a confirmation event for a slow client")

Two things are pinned here, and the second is the point of the cycle:

1. **Presence.** Silence makes "my stream is missing events" undebuggable; the drop is now named.
2. **Shape.** ``logger.debug`` **without** ``exc_info``. This is where the family's usual convention
   (cycles 53-55: name it *with* a traceback) is deliberately **not** applied: the condition is
   expected, and a traceback per drop would flood the log *exactly when the client is already behind*.
   ``test_no_drop_records_a_traceback`` pins the absence, so a later "make it consistent" edit that
   adds ``exc_info=True`` is red rather than quietly wrong.

``web/routes/ui.py`` had **no module-level logger**; one was added. ``test_the_ui_module_has_a_logger``
pins the *resolved* name (cycle 55's lesson: the logger name is not always the module path).
"""

from __future__ import annotations

import ast
import importlib
import logging
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"

FAMILY_TYPE = "queue.Full"

# (path relative to src/, a unique fragment of the drop message) -> expected handler count
_NAMED_DROPS: dict[str, list[str]] = {
    "aegis_ai/grpc_server.py": ["slow gRPC stream client"],
    "aegis_ai/web/manager_routes.py": ["slow SSE client"],
    "aegis_ai/web/routes/ui.py": ["slow SSE client"],
    "aegis_ai/web/routes/approval.py": ["slow client"],
}

# ── ast helpers ────────────────────────────────────────────────────────────


def _modules() -> list[Path]:
    return sorted(_SRC.rglob("*.py"))


def _handlers(tree: ast.AST) -> list[ast.ExceptHandler]:
    return [n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)]


def _except_types(handler: ast.ExceptHandler) -> set[str]:
    t = handler.type
    if t is None:
        return {"bare"}
    if isinstance(t, ast.Tuple):
        return {ast.unparse(e) for e in t.elts}
    return {ast.unparse(t)}


def _is_bare_discard(handler: ast.ExceptHandler) -> str | None:
    if len(handler.body) != 1:
        return None
    stmt = handler.body[0]
    if isinstance(stmt, ast.Pass):
        return "pass"
    if isinstance(stmt, ast.Continue):
        return "continue"
    if isinstance(stmt, ast.Break):
        return "break"
    return None


def _in_family(handler: ast.ExceptHandler) -> bool:
    return _is_bare_discard(handler) is not None and FAMILY_TYPE in _except_types(handler)


def _logger_calls(handler: ast.ExceptHandler) -> list[ast.Call]:
    out: list[ast.Call] = []
    for node in ast.walk(handler):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if getattr(node.func.value, "id", "") == "logger":
                out.append(node)
    return out


def _message_of(call: ast.Call) -> str:
    if call.args and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str):
        return call.args[0].value
    return ""


def _has_exc_info(call: ast.Call) -> bool:
    return any(kw.arg == "exc_info" for kw in call.keywords)


def _tree_of(rel: str) -> ast.AST:
    return ast.parse((_SRC / rel).read_text(encoding="utf-8"))


def _drops_in(rel: str) -> list[ast.ExceptHandler]:
    return [h for h in _handlers(_tree_of(rel)) if FAMILY_TYPE in _except_types(h)]


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


def test_no_handler_skips_a_queue_full_drop_in_silence() -> None:
    offenders = _family_sites()
    assert offenders == [], f"these handlers drop an event on back-pressure with a bare discard: {offenders}"


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
    tree = ast.parse(
        "def f():\n"
        "    for x in items:\n"
        "        try:\n"
        "            pass\n"
        "        except queue.Full:\n"
        "            pass\n"  # in the family
        "        except queue.Full:\n"
        "            continue\n"  # in the family (other shape)
        "        except queue.Full:\n"
        "            logger.debug('named')\n"  # named
        "        except queue.Empty:\n"
        "            pass\n"  # different type
    )
    hits = [h.lineno for h in _handlers(tree) if _in_family(h)]
    assert len(hits) == 2, f"the family detector fired {len(hits)} times, expected 2: {hits}"


# ── presence: every drop names its reason ──────────────────────────────────


def test_every_queue_full_handler_in_the_recorded_files_names_its_drop() -> None:
    for rel, fragments in _NAMED_DROPS.items():
        handlers = _drops_in(rel)
        assert handlers, f"{rel} no longer handles queue.Full — re-measure"
        messages = [m for h in handlers for m in (_message_of(c) for c in _logger_calls(h))]
        for fragment in fragments:
            matches = [m for m in messages if fragment in m]
            assert len(matches) == 1, (
                f"{rel}: expected exactly one drop message containing {fragment!r}, "
                f"found {len(matches)} among {messages}"
            )


def test_the_site_map_covers_four_files_and_four_handlers() -> None:
    assert len(_NAMED_DROPS) == 4
    assert sum(len(v) for v in _NAMED_DROPS.values()) == 4
    assert sum(len(_drops_in(rel)) for rel in _NAMED_DROPS) == 4


# ── shape: DEBUG, and no traceback (the point of the cycle) ────────────────


def test_no_drop_records_a_traceback() -> None:
    """A traceback per drop would flood the log exactly when the client is already behind.

    The family convention for cycles 53-55 is the opposite (``exc_info=True``); this test pins the
    deliberate *difference* so a later "make it consistent" edit is red instead of quietly wrong.
    """
    offenders = []
    for rel in _NAMED_DROPS:
        for handler in _drops_in(rel):
            for call in _logger_calls(handler):
                if _has_exc_info(call):
                    offenders.append(f"{rel}:{handler.lineno}")
    assert offenders == [], f"a back-pressure drop now records a traceback: {offenders}"


def test_every_drop_names_the_reason_at_debug() -> None:
    offenders = []
    for rel in _NAMED_DROPS:
        for handler in _drops_in(rel):
            calls = _logger_calls(handler)
            if len(calls) != 1:
                offenders.append(f"{rel}:{handler.lineno} has {len(calls)} logger calls, expected 1")
                continue
            if calls[0].func.attr != "debug":
                offenders.append(f"{rel}:{handler.lineno} logs at {calls[0].func.attr}, expected debug")
            if len(_message_of(calls[0])) < 10:
                offenders.append(f"{rel}:{handler.lineno} has no readable message")
    assert offenders == [], offenders


def test_the_shape_detector_is_not_vacuous() -> None:
    """Self-test: the DEBUG/no-exc_info detector must fire on a named-but-wrong handler."""
    tree = ast.parse(
        "def f():\n"
        "    try:\n"
        "        pass\n"
        "    except queue.Full:\n"
        "        logger.debug('dropped', exc_info=True)\n"  # traceback -> offender
        "    except queue.Full:\n"
        "        logger.warning('dropped')\n"  # wrong level -> offender
        "    except queue.Full:\n"
        "        logger.debug('dropped for a slow client')\n"  # correct
    )
    offenders = []
    for handler in [h for h in _handlers(tree) if FAMILY_TYPE in _except_types(h)]:
        calls = _logger_calls(handler)
        if len(calls) != 1 or calls[0].func.attr != "debug" or _has_exc_info(calls[0]):
            offenders.append(handler.lineno)
    assert len(offenders) == 2, f"the shape detector found {len(offenders)} offenders, expected 2: {offenders}"


# ── the logger that had to be added ────────────────────────────────────────


def test_the_ui_module_has_a_logger() -> None:
    """``web/routes/ui.py`` had no module-level logger; the resolved name is what the records carry."""
    module = importlib.import_module("aegis_ai.web.routes.ui")
    resolved = getattr(module, "logger", None)
    assert resolved is not None, "web/routes/ui.py lost its module-level `logger`"
    assert resolved.name == "aegis_ai.web.routes.ui", f"resolves to {resolved.name!r}"


def test_the_three_edited_modules_each_resolve_their_logger() -> None:
    for rel, expected in (
        ("aegis_ai/grpc_server.py", "aegis_ai.grpc_server"),
        ("aegis_ai/web/manager_routes.py", "aegis_ai.web.manager_routes"),
        ("aegis_ai/web/routes/ui.py", "aegis_ai.web.routes.ui"),
    ):
        module = importlib.import_module(rel.removesuffix(".py").replace("/", "."))
        assert module.logger.name == expected, f"{rel}'s logger resolves to {module.logger.name!r}"


def test_the_record_detector_is_not_vacuous(caplog) -> None:
    caplog.set_level(logging.DEBUG, logger="aegis_ai.web.routes.ui")
    logging.getLogger("aegis_ai.web.routes.ui").debug("control")
    assert [r for r in caplog.records if r.name == "aegis_ai.web.routes.ui"] != [], (
        "the record detector is blind; the shape assertions above prove nothing"
    )
