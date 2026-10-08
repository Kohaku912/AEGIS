"""Every path in `[tool.ruff.lint.per-file-ignores]` must name a file that exists.

`ai-server/pyproject.toml` declares lint exemptions keyed by project-relative
path. Ruff does **not** warn about a key whose file is gone: the entry then
asserts an exemption that is **not in force**, and a later reader who adds an
unused variable to that file believes it is exempt.

Measured 2026-10-08 (cycle 107): **8 of 25** keys named a missing file --
`agents/research.py`, `agents/support.py`, `agents/self_dev.py`, `mind/desire.py`,
`mind/emotion.py`, `mind/goals.py` (deleted) and `autonomous_loop.py`,
`planner.py` (relocated into `autonomous/`). All eight were inert: removing them
left `ruff check src tests` at **1194 findings**, unchanged, and the CI gate
(`ruff check src tests --select F821`) green.

⚠️ **What this pin does not cover**: the reverse direction. A file that needs an
exemption and has none is invisible here -- only a full `ruff check src tests`
reports it. This pins the *absence of dead declarations*, not completeness.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

AI_SERVER = Path(__file__).resolve().parents[1]
PYPROJECT = AI_SERVER / "pyproject.toml"

# A key that must be present -- the control. If the table stops being parsed,
# every other assertion here passes on an empty population.
CONTROL = "src/aegis_ai/mind/identity.py"

# Measured 2026-10-08 (cycle 107): 17 keys after the sweep (25 before). A floor,
# not an equality: adding an exemption is fine, losing the table is not.
MIN_KEYS = 17


def _ruff_lint() -> dict:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    try:
        return data["tool"]["ruff"]["lint"]
    except KeyError as exc:  # a removed table must fail loudly, not vacuously
        raise AssertionError(f"{PYPROJECT} no longer declares [tool.ruff.lint]") from exc


def _declared() -> dict[str, list[str]]:
    lint = _ruff_lint()
    assert "per-file-ignores" in lint, (
        f"{PYPROJECT} no longer declares [tool.ruff.lint.per-file-ignores] -- if the "
        f"table was intentionally removed, delete this pin with it"
    )
    return lint["per-file-ignores"]


def test_the_table_is_not_vacuous() -> None:
    """Control: the table must parse to a non-trivial population."""
    declared = _declared()
    assert len(declared) >= MIN_KEYS, (
        f"only {len(declared)} per-file-ignores keys parsed (expected >= {MIN_KEYS}) -- "
        f"either the table is being read wrong or exemptions were dropped wholesale"
    )
    assert CONTROL in declared, f"the control key {CONTROL!r} is gone from {PYPROJECT}"


def test_every_declared_path_exists() -> None:
    """Each key must name a file that exists, relative to the config's directory."""
    stale = sorted(rel for rel in _declared() if not (AI_SERVER / rel).exists())
    assert not stale, (
        "per-file-ignores keys naming a file that does not exist -- ruff does not warn "
        "about these, so each one silently asserts an exemption that is not in force. "
        "Delete the key, or retarget it (retargeting *grants* the exemption, so make "
        "that a deliberate choice):\n  " + "\n  ".join(stale)
    )


def test_every_declared_code_can_suppress_something() -> None:
    """An ignore for a code that is never enabled, or is globally ignored, is inert.

    `select` decides which rules run at all; a per-file ignore for a code outside
    it cannot suppress anything. A code in the global `ignore` list is already
    suppressed everywhere, so a per-file entry for it is inert too.
    """
    lint = _ruff_lint()
    enabled = [code.upper() for code in lint.get("select", [])]
    enabled += [code.upper() for code in lint.get("extend-select", [])]
    globally_off = {code.upper() for code in lint.get("ignore", [])}

    def _enabled(code: str) -> bool:
        return any(code.startswith(sel) or sel.startswith(code) for sel in enabled)

    inert: list[str] = []
    for rel, codes in sorted(_declared().items()):
        for code in codes:
            code = code.upper()
            if code in globally_off:
                inert.append(f"{rel} = {code} (globally ignored already)")
            elif not _enabled(code):
                inert.append(f"{rel} = {code} (not in select={enabled})")
    assert not inert, "per-file-ignores entries that cannot suppress anything:\n  " + "\n  ".join(inert)
