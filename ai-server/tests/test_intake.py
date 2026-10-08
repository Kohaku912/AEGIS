"""Intake config + import boundary.

Phase 4's v1 intake behaviour tests lived here until 2026-10-08; that path
(`IntakeRouter` / `IntakeClassifier` / `IntakeDeduplicator` and the data models in
`intake/models.py`) was deleted with DELEGATION.md §4 item 47, and its 27 tests went
with it. What remains is the part of the package that is still live:

- `IntakeSettings` (in `aegis_ai.settings`) — the config that gates the intake path. Its
  two bounded v1 fields (`requires_agent_threshold`, `fallback_requires_agent`) were
  retired in the same change: deleting the v1 path left them with no reader, and an unread
  field must be *retired* rather than recorded, because the settings page must not render
  a control for one (`test_settings_ui_matches_the_schema.py`). Their names are pinned by
  `test_settings_debt_stays_retired.py`;
- the import-boundary invariant from instruction.md §8: `intake/*` must not import
  the OpenHands SDK (nor anthropic / openai / langchain).

The boundary parametrization now names the *surviving* modules. The old list named
`aegis_ai.intake`, `.models`, `.classifier`, `.deduplicator`, `.router` — so it
covered four modules that are now gone and **never covered the live `l1_*` modules
at all**; the L1 layer was the one part of the package the invariant did not reach.
"""
from __future__ import annotations

import importlib
import inspect
import textwrap

import pytest

# ---------------------------------------------------------------------------
# IntakeSettings
# ---------------------------------------------------------------------------


def test_intake_settings_defaults() -> None:
    """`IntakeSettings` のデフォルト."""
    from aegis_ai.settings import IntakeSettings

    s = IntakeSettings()
    assert s.enabled is True


def test_aegis_settings_contains_intake() -> None:
    """`AEGISSettings.intake` が `IntakeSettings` インスタンス."""
    from aegis_ai.settings import AEGISSettings, IntakeSettings

    s = AEGISSettings()
    assert isinstance(s.intake, IntakeSettings)
    assert s.intake.enabled is True


# ---------------------------------------------------------------------------
# import 境界 — intake/* は openhands を import しない
# ---------------------------------------------------------------------------


def _module_source(module_name: str) -> str:
    return textwrap.dedent(inspect.getsource(importlib.import_module(module_name)))


@pytest.mark.parametrize(
    "module_name",
    [
        "aegis_ai.intake",
        "aegis_ai.intake.l1_models",
        "aegis_ai.intake.l1_router",
        "aegis_ai.intake.l1_executor",
    ],
)
def test_intake_module_does_not_import_openhands(module_name: str) -> None:
    """intake パッケージは openhands SDK を import しない (§6 import 境界)."""
    src = _module_source(module_name)
    # Control: a scan of an empty (or unreadable) source would pass vacuously.
    assert len(src) > 200, f"{module_name}: source looks empty ({len(src)} chars)"
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            for forbidden in ("openhands", "anthropic", "openai", "langchain"):
                assert forbidden not in stripped, (
                    f"forbidden import in {module_name}: {stripped}"
                )
