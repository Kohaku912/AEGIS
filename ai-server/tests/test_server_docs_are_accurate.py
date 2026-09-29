"""Each server's AGENTS.md describes a directory tree that actually exists.

`AGENTS.md` is what a coding agent reads *before* touching a server, so a tree that
names files which do not exist is a defect, not cosmetics — it is the same
"documentation claims something untrue" class as prose that says a removed approval
gate still gates.

On 2026-09-28 all four server docs had drifted, each differently:

* ``room-server`` — an **entirely fictional** layout: ``mqtt_provider.py``,
  ``capabilities/{environment,motion,devices,robot_arm}.py``, ``safety.py`` and
  ``requirements.txt`` (the project uses ``pyproject.toml`` + ``uv.lock``). The file
  even contradicted itself two lines later: "No MQTT provider is present".
* ``android-server`` — omitted the whole Compose ``ui/`` layer (12 files: the V2 app,
  the design system, and seven feature screens).
* ``pc-server`` — omitted ``uia.rs``, ``personal_data.rs``, ``system_ops.rs`` and
  ``discord_rpc.rs``.
* ``browser-server`` — omitted ``egress.py``, the module that enforces the **single
  constraint**, plus its whole ``tests/`` directory.

This pins the tree block only: every entry named inside a ``## Directory Structure``
fence must resolve under that server — as a file *or* a directory. It deliberately
does **not** check the reverse — a tree may summarise a directory (``ui/feature/``
rather than 27 files) — so adding source files never breaks it, while inventing one
does.

Entries are matched by basename anywhere under the server (``rglob``), because the
trees abbreviate nesting depth. That makes the test one-directional and forgiving
about *where* a file lives; it is strict about *whether* it exists at all.

Note on scope: an earlier revision matched only ``name.ext`` entries, which silently
skipped every **directory** in the trees (``tests/``, ``installer/``, ``ui/``). A
fictional directory would therefore have passed. ``_TREE_ENTRY`` now captures bare
names too, and ``test_the_scan_captures_directory_entries`` guards that it stays that
way — a scan that quietly matches nothing is indistinguishable from a passing one.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]

#: Servers whose AGENTS.md carries a documented directory tree.
_SERVERS: tuple[str, ...] = ("room-server", "browser-server", "pc-server", "android-server")

_TREE_BLOCK = re.compile(r"## Directory Structure\s*```(.*?)```", re.S)

#: A tree entry: `├── name` / `└── name`, with or without an extension. Deliberately
#: broad — trailing `# comments` are cut off by the character class, and continuation
#: lines (which start with `│`, not `├`/`└`) are skipped.
_TREE_ENTRY = re.compile(r"[├└]──\s*([A-Za-z0-9_./-]+)")

#: Extensions that mark an entry as a file. Ordered longest-first so `build.gradle.kts`
#: is not truncated to `build.gradle.kt`.
_KNOWN_EXT = re.compile(
    r"\.(?:pyi|kts|dts|proto|properties|gradle|yaml|yml|toml|lock|json|md|txt|sh|ps1"
    r"|xml|mod|py|rs|kt)$"
)

#: Files with no extension. Anything else without an extension is treated as a
#: directory, which only affects the wording of a failure message.
_EXTENSIONLESS_FILES: frozenset[str] = frozenset({"Dockerfile", "Makefile", "LICENSE"})


def _tree_block(server: str) -> str:
    doc = _REPO / server / "AGENTS.md"
    assert doc.exists(), f"{server}/AGENTS.md is missing"
    block = _TREE_BLOCK.search(doc.read_text(encoding="utf-8"))
    assert block is not None, f"{server}/AGENTS.md has no '## Directory Structure' fence"
    return block.group(1)


def _entries(server: str) -> list[str]:
    return sorted(set(_TREE_ENTRY.findall(_tree_block(server))))


def _is_file_entry(name: str) -> bool:
    return bool(_KNOWN_EXT.search(name)) or name.rstrip("/") in _EXTENSIONLESS_FILES


def _exists(server_dir: Path, name: str) -> bool:
    """Accept either a repo-relative path or a bare basename, file or directory."""
    if (server_dir / name).exists():
        return True
    return any(server_dir.rglob(Path(name).name))


@pytest.mark.parametrize("server", _SERVERS)
def test_every_file_in_the_documented_tree_exists(server: str):
    entries = _entries(server)
    assert len(entries) >= 5, (
        f"{server}/AGENTS.md documents only {len(entries)} entries — the tree was "
        "probably emptied or reformatted, which would make this test vacuous"
    )

    missing = [name for name in entries if not _exists(_REPO / server, name)]
    assert missing == [], (
        f"{server}/AGENTS.md documents entries that do not exist: {missing}. Update the tree to match the code."
    )


@pytest.mark.parametrize("server", _SERVERS)
def test_the_scan_captures_directory_entries(server: str):
    """Guard the guard: the tree must contribute directory entries, not just files.

    If ``_TREE_ENTRY`` regresses to an ``*.ext``-only pattern this fails, rather than
    silently dropping ``tests/``, ``installer/`` and ``ui/`` from the check above.
    """
    dirs = [name for name in _entries(server) if not _is_file_entry(name)]
    assert dirs, (
        f"{server}/AGENTS.md: no directory entry captured — the entry regex is too "
        "narrow, so directories are going unchecked"
    )
