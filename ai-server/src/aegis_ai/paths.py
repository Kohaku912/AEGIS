"""Path resolution helpers for AEGIS.

Phase 7 (instruction.md §36): the ``CapabilityCatalog.instance()``
singleton needs a default capabilities directory. Instead of duplicating
the path-search logic, we centralise it here.
"""
from __future__ import annotations

import os
from pathlib import Path

# Directories that look like the AEGIS capabilities root.
_CAPABILITIES_DIR_NAMES = ("capabilities", "builtin")

# Directories that, when present, identify the AEGIS project root.
_PROJECT_MARKERS = (
    "ai-server",
    "AGENTS.md",
    "instruction.md",
    "protos",
)


def find_project_root(start: Path | str | None = None) -> Path:
    """Walk up from ``start`` (or CWD) until an AEGIS project marker is found.

    Returns the project root. If no marker is found within 5 levels,
    the starting directory itself is returned (best effort).
    """
    base = Path(start or os.getcwd()).resolve()
    for _ in range(6):
        for marker in _PROJECT_MARKERS:
            if (base / marker).exists():
                return base
        parent = base.parent
        if parent == base:
            break
        base = parent
    return Path(start or os.getcwd()).resolve()


def find_capabilities_dir(start: Path | str | None = None) -> str:
    """Return the most likely path to the ``capabilities/`` folder.

    The lookup order is:

    1. ``$AEGIS_CAPABILITIES_DIR`` environment variable (escape hatch
       for tests / packaged distributions).
    2. ``<project_root>/capabilities`` — the canonical location.
    3. ``<project_root>/ai-server/capabilities`` — historical layout
       (older versions of the repo).
    4. CWD as a last resort.
    """
    env = os.environ.get("AEGIS_CAPABILITIES_DIR")
    if env:
        return str(Path(env).resolve())

    root = find_project_root(start)
    for name in _CAPABILITIES_DIR_NAMES:
        candidate = root / name
        if candidate.is_dir():
            return str(candidate.resolve())

    nested = root / "ai-server" / "capabilities"
    if nested.is_dir():
        return str(nested.resolve())

    return str((root / "capabilities").resolve())


__all__ = ["find_project_root", "find_capabilities_dir"]
