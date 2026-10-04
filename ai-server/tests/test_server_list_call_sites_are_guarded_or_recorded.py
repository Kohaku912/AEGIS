"""The exposure of `_server_list` is 4 of 5 call sites, not 1
(DELEGATION.md section 4 item 51, extending item 44).

Measured 2026-10-05 by AST: `web/ui_overview.py` calls `_server_list` from five
enclosing functions, and only one of them wraps the call in a `try` with an
`except`:

    _core (725)        unguarded
    _attention (769)   unguarded
    _connection (848)  unguarded
    _servers (1651)    unguarded
    _errors (1977)     guarded   <- `except Exception: pass`, with a comment
                                      saying minimal runtimes must keep working

All four unguarded callers are registered sections in the `sections` dict
(`:41`, `:42`, `:56`, `:57`), so they are reachable. `_server_list` reaches
`dashboard_legacy._runtime_server_status`, which reads `runtime.status_manager`
with no getattr default (`dashboard_legacy.py:226`) -- so a runtime without a
`status_manager` raises `AttributeError` in four sections, while `_errors`
survives on the same runtime.

The pin records the *exposure map* rather than one call: guarding a site, or
adding a new unguarded one, turns it red so the record moves with the code.
`_errors`' guard is the control that the detector is not vacuous -- if the guard
detector always returned False, `_errors` would be reported unguarded and the
equality below would fail.
"""

from __future__ import annotations

import ast
from pathlib import Path

UI = Path(__file__).resolve().parents[1] / "src" / "aegis_ai" / "web" / "ui_overview.py"

_CALLEE = "_server_list"

# Recorded exposure: the enclosing functions whose call is NOT inside a try/except.
_UNGUARDED = frozenset({"_core", "_attention", "_connection", "_servers"})

# The one guarded site -- also the control for the guard detector.
_GUARDED = frozenset({"_errors"})


def _call_sites(source: str) -> list[tuple[str, bool]]:
    """(enclosing function, guarded?) for every `_server_list(...)` call."""
    tree = ast.parse(source)
    parent: dict[ast.AST, ast.AST] = {
        child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)
    }

    def enclosing(node: ast.AST) -> str:
        n: ast.AST | None = node
        while n is not None:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return n.name
            n = parent.get(n)
        return "<module>"

    def guarded(node: ast.AST) -> bool:
        """True if an ancestor `try` *with handlers* contains this node."""
        n: ast.AST | None = node
        while n is not None:
            par = parent.get(n)
            if isinstance(par, ast.Try) and par.handlers:
                if any(n is stmt or n in ast.walk(stmt) for stmt in par.body):
                    return True
            n = par
        return False

    return [
        (enclosing(node), guarded(node))
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == _CALLEE
    ]


def test_the_scan_finds_the_known_call_sites() -> None:
    names = {fn for fn, _ in _call_sites(UI.read_text(encoding="utf-8"))}
    missing = sorted((_UNGUARDED | _GUARDED) - names)
    assert not missing, (
        f"{missing} no longer calls {_CALLEE} -- the site was moved or removed; update "
        f"DELEGATION.md section 4 item 51 (found {sorted(names)})"
    )


def test_the_unguarded_sites_are_exactly_the_recorded_ones() -> None:
    unguarded = {
        fn for fn, is_guarded in _call_sites(UI.read_text(encoding="utf-8")) if not is_guarded
    }
    assert unguarded == set(_UNGUARDED), (
        f"the unguarded {_CALLEE} call sites changed: now {sorted(unguarded)}, recorded "
        f"{sorted(_UNGUARDED)} -- if a site was guarded, or a new one added, update "
        "DELEGATION.md section 4 item 51"
    )


def test_the_guard_detector_recognises_a_try_block() -> None:
    """Control: the detector is not vacuous."""
    synthetic = (
        "def guarded(r):\n"
        "    try:\n"
        f"        return {_CALLEE}(r)\n"
        "    except Exception:\n"
        "        return []\n"
        "\n"
        "def bare(r):\n"
        f"    return {_CALLEE}(r)\n"
        "\n"
        "def finally_only(r):\n"
        "    try:\n"
        f"        return {_CALLEE}(r)\n"
        "    finally:\n"
        "        pass\n"
    )
    got = dict(_call_sites(synthetic))
    assert got == {"guarded": True, "bare": False, "finally_only": False}, got
