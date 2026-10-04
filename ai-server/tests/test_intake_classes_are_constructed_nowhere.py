"""The three intake classes are re-exported by `aegis_ai.intake` but constructed
nowhere in `src/` (DELEGATION.md section 4 item 47).

Measured 2026-10-05: `L1Router` replaced `IntakeRouter` on the live path
(`runtime.py:1104` builds `L1Router(llm_gateway=...)`), so `IntakeRouter` /
`IntakeClassifier` / `IntakeDeduplicator` are dead on the intake side -- and with
them, intake-side deduplication. They are still defined and still exported by
`aegis_ai.intake`, so a future "natural" import gets a working-looking class that
nothing wires.

This pin makes the absence explicit rather than assumed. It measures
*construction* (an `ast.Call` whose callee is a bare `Name`), not mentions -- a
docstring or a type annotation is not a construction. Three cases:
  - the scan finds a real construction (control: `L1Router` is built in src/);
  - the three intake classes have **no** construction in src/;
  - they still exist and are still exported, so deleting or renaming them comes
    back here instead of making the absence assertion vacuously true.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"

# Re-exported by `aegis_ai.intake` but never built on the live path.
_INTAKE_CLASSES = ("IntakeRouter", "IntakeClassifier", "IntakeDeduplicator")

# Built by `runtime.py` -- the control that proves the scan sees constructions.
_LIVE_CONTROL = "L1Router"


def _constructed_class_names() -> set[str]:
    """Names instantiated as `Name(...)` anywhere under src/."""
    found: set[str] = set()
    for path in sorted(SRC.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                found.add(node.func.id)
    return found


def test_the_scan_finds_the_live_router() -> None:
    constructed = _constructed_class_names()
    assert _LIVE_CONTROL in constructed, (
        f"the scan did not see {_LIVE_CONTROL} constructed in src/ -- either the live "
        f"router moved or the scan is broken; the absence assertion below would be "
        f"vacuous (found {len(constructed)} constructed names)"
    )


def test_the_intake_classes_are_constructed_nowhere_in_src() -> None:
    constructed = _constructed_class_names()
    wired = sorted(set(_INTAKE_CLASSES) & constructed)
    assert not wired, (
        f"{wired} is now constructed in src/ -- if that is deliberate, wire it fully and "
        "update DELEGATION.md section 4 item 47 (the intake side is no longer dead)"
    )


def test_the_intake_classes_still_exist_and_are_exported() -> None:
    import aegis_ai.intake as intake

    gone = [n for n in _INTAKE_CLASSES if not inspect.isclass(getattr(intake, n, None))]
    assert not gone, (
        f"{gone} is no longer a class exported by aegis_ai.intake -- if it was deleted or "
        "renamed, drop it from _INTAKE_CLASSES and update DELEGATION.md section 4 item 47"
    )
