"""`PresentationManager.dismiss` prefers a name that only a test double defines.

Measured 2026-10-01. `PresentationManager.dismiss` resolves its dismissal target by preference,
then by fallback:

    dismiss_notification = getattr(self._notification_manager, "dismiss_notification", None)
    if dismiss_notification is None:
        dismiss_notification = getattr(self._notification_manager, "dismiss", None)

Production passes a real `NotificationManager`, which defines `dismiss` and **not**
`dismiss_notification` — so production **always takes the fallback**. The preferred name is defined
by exactly one class in the whole repository, and it is a **test double**
(`FakeNotificationManager` in `tests/test_presentation_engine.py`) — which is what the single test
covering this path passes. So **the test takes the branch production never takes, and the branch
production always takes is covered by nothing.**

The hazard is measured rather than inferred: deleting the fallback — the obvious "this is dead
code" cleanup — leaves the suite at **1923 passed / 8 skipped** (full suite, 407.74s, measured
2026-10-01). Production would silently stop dismissing notifications and no test would fail.

This pin makes that deletion a deliberate, loud edit instead of a silent one. Which name is
canonical is a judgment — rename the manager's method to match the route handler and the double,
make the double faithful to the real class, or delete the dead lookup — so it is recorded rather
than decided, in `DELEGATION.md` §4 item 21.
"""

from __future__ import annotations

import ast
from functools import lru_cache
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SERVER = _REPO / "ai-server"
_SRC = _SERVER / "src"
_TESTS = _SERVER / "tests"

_PRESENTATION_MANAGER = _SRC / "aegis_ai" / "presentation" / "manager.py"
_NOTIFICATION_MANAGER = _SRC / "aegis_ai" / "notification" / "notification_manager.py"

# The name `PresentationManager.dismiss` looks up first, and the name it falls back to. Production's
# manager defines only the second, so the first lookup is always `None` there.
_PREFERRED = "dismiss_notification"
_FALLBACK = "dismiss"

# The classes that define the preferred name. Recorded by equality — the point being that the list
# is exactly one entry long, and that entry is a **test double**, not a manager.
_RECORDED_CLASSES_DEFINING_PREFERRED: frozenset[str] = frozenset(
    {"ai-server/tests/test_presentation_engine.py"}
)

# The upstream floor for the repository scan: `src/` + `tests/` hold 550 `.py` files (measured
# 2026-10-01). Strictly below that, so it fires on a blinded scan rather than on a real change.
_MIN_FILES = 400


def _rel(path: Path) -> str:
    return path.resolve().relative_to(_REPO).as_posix()


@lru_cache(maxsize=1)
def _scan_files() -> tuple[Path, ...]:
    return tuple(sorted([*_SRC.rglob("*.py"), *_TESTS.rglob("*.py")]))


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _classes_defining(name: str) -> dict[str, list[str]]:
    """Map file -> the classes whose body defines a method called `name`."""
    out: dict[str, list[str]] = {}
    for path in _scan_files():
        found = sorted(
            node.name
            for node in ast.walk(_parse(path))
            if isinstance(node, ast.ClassDef)
            and any(isinstance(body, ast.FunctionDef) and body.name == name for body in node.body)
        )
        if found:
            out[_rel(path)] = found
    return out


def _getattr_names(path: Path, method: str) -> list[str] | None:
    """The names passed to `getattr(..., <name>, ...)` inside `method`, in source order.

    `None` if the method does not exist.
    """
    node = next(
        (
            n
            for n in ast.walk(_parse(path))
            if isinstance(n, ast.FunctionDef) and n.name == method
        ),
        None,
    )
    if node is None:
        return None
    calls = sorted(
        (
            n
            for n in ast.walk(node)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == "getattr"
            and len(n.args) >= 2
        ),
        key=lambda n: n.lineno,
    )
    return [
        arg.value
        for call in calls
        for arg in [call.args[1]]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
    ]


def test_the_class_production_passes_defines_only_the_fallback() -> None:
    """Why the first lookup is always `None` where it matters."""
    names = {
        node.name
        for node in ast.walk(_parse(_NOTIFICATION_MANAGER))
        if isinstance(node, ast.FunctionDef)
    }
    assert _FALLBACK in names, (
        f"`NotificationManager` no longer defines `{_FALLBACK}` — the fallback production relies on "
        "has been renamed, so `PresentationManager.dismiss` would resolve nothing at all"
    )
    assert _PREFERRED not in names, (
        f"`NotificationManager` now defines `{_PREFERRED}` — production would take the preferred "
        "branch instead of the fallback, so the coverage note in this pin's docstring is stale"
    )


def test_the_preferred_name_is_defined_by_one_test_double_only() -> None:
    """The crux: the branch the test takes is the branch production cannot take."""
    files = _scan_files()
    assert len(files) >= _MIN_FILES, (
        f"the scan found only {len(files)} Python files under src/ + tests/ — it is not reading the "
        "tree, so the equality below would pass vacuously"
    )
    observed = frozenset(_classes_defining(_PREFERRED))
    assert observed == _RECORDED_CLASSES_DEFINING_PREFERRED, (
        f"the set of classes defining `{_PREFERRED}` changed.\n"
        f"  recorded: {sorted(_RECORDED_CLASSES_DEFINING_PREFERRED)}\n"
        f"  observed: {sorted(observed)}\n"
        "A production class now defining it means production takes the preferred branch, so this "
        "pin's premise is stale. The double being made faithful — or removed — means the branch "
        "production uses is now covered. Either way, revisit `DELEGATION.md` §4 item 21."
    )


def test_the_dismiss_path_prefers_then_falls_back() -> None:
    """Deleting the fallback must be a deliberate edit — nothing else would notice."""
    names = _getattr_names(_PRESENTATION_MANAGER, "dismiss")
    assert names is not None, (
        f"{_rel(_PRESENTATION_MANAGER)} no longer defines `dismiss` — this pin's subject is gone"
    )
    assert names == [_PREFERRED, _FALLBACK], (
        f"`PresentationManager.dismiss` now resolves {names} — expected "
        f"[{_PREFERRED!r}, {_FALLBACK!r}] in that order.\n"
        "Deleting the fallback leaves the whole suite green (measured 2026-10-01: 1923 passed / "
        "8 skipped), because the only test covering this path passes a double that defines the "
        "preferred name — so nothing would fail while production silently stopped dismissing "
        "notifications."
    )
