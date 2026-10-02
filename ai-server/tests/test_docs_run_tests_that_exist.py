"""A document that tells the reader to run a test file must name one that exists.

Measured 2026-10-02. `docs/testing.md` — the central testing guide, marked "Status: Active" —
listed **17 test filenames that exist nowhere in the repository**, and pointed at `../tests/`,
which is not a directory. `docs/android-server.md` and `docs/research-e2e.md` gave commands for
three more. None of them could be run, and nothing noticed.

The earlier sweep of this defect class (2026-09-28) fixed `docs/pc-server.md`,
`docs/room-server.md` and `docs/testing-real-devices.md`, and produced
`test_server_docs_are_accurate.py` — but that pin reads only the `## Directory Structure` fence of
each server's `AGENTS.md`, so a `pytest tests/...` command in a *different* fence of a *different*
document was never in scope. A sweep's own coverage is a claim; this one measured it.

This pin reads **fenced code blocks only**. That is structural, not stylistic: a command fence is
an instruction the reader will copy, while prose is where a document legitimately *discusses* a
file that no longer exists. `docs/pc-server.md` and `docs/room-server.md` name their retired test
files in prose, and those references must stay — they are the record that the defect happened.
Prose is therefore free; a fence is not.

`docs/dev-server.md` is the one tolerated exception: it is banner-marked "REMOVED (Phase 9) … do
not follow the setup instructions below", and the Dev Server directory is gone, so its `## Testing`
fence names a test that cannot exist. It is **recorded** below rather than excluded, and the pin
asserts the observed set **equals** the recorded one — so fixing the document fails until the
record is emptied, and a *new* dead reference fails immediately.

Scope is set by rule, not by an exclusion list: dotted directories are pruned wholesale, so local
tool state and skill documents full of placeholder paths stay out without anyone maintaining a
list of them.
"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]

#: Vendor/build trees pruned by name. Dotted directories are pruned by **rule** instead of a list
#: (see ``_markdown_files``), so a new agent tool writing `.something/` never widens the scan.
_SKIP_DIR_NAMES = frozenset({"node_modules", "__pycache__"})

#: Documents allowed to name a test file that does not exist, with the reason. Equality is
#: asserted in both directions, so this set is a claim that must stay true.
_RECORDED_DEAD: frozenset[tuple[str, str]] = frozenset(
    {
        # Banner-marked historical record: "REMOVED (Phase 9) … do not follow the setup
        # instructions below". The dev-server/ directory no longer exists.
        ("docs/dev-server.md", "test_dev_server.py"),
    }
)

_FENCE = re.compile(r"^```.*?$(.*?)^```", re.S | re.M)

#: A test path inside a fence, with either separator (these documents are written for Windows).
_TEST_PATH = re.compile(r"tests[/\\]([A-Za-z0-9_]+\.py)")


@lru_cache(maxsize=1)
def _markdown_files() -> tuple[Path, ...]:
    """Every shipped ``*.md``; dotted trees are pruned structurally.

    Measured 2026-10-02: this selects 104 markdown files and exactly one dead reference. Keeping
    dotted trees instead selects 272 and adds four false positives — placeholder examples inside
    skill documents (``tests/test_a.py``, ``tests/test_xxx.py``) and local agent-tool state
    (``.mimocode/``, ``.omo/``), none of which is shipped documentation.
    """
    out: list[Path] = []
    for root, dirs, files in os.walk(_REPO):
        dirs[:] = sorted(
            d for d in dirs if d not in _SKIP_DIR_NAMES and not d.startswith(".")
        )
        out.extend(Path(root) / name for name in files if name.endswith(".md"))
    return tuple(sorted(out))


@lru_cache(maxsize=1)
def _existing_tests() -> frozenset[str]:
    """Basenames of every test module, so a path is judged by name anywhere in the tree.

    The documents write `tests/foo.py`; the suite lives at `ai-server/tests/foo.py`. Matching on
    the basename keeps the check about *whether the file exists*, which is the only claim a
    command makes.
    """
    tests_dir = _REPO / "ai-server" / "tests"
    assert tests_dir.is_dir(), f"{tests_dir} is missing — the scan would pass vacuously"
    return frozenset(path.name for path in tests_dir.rglob("*.py"))


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(_REPO).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _references() -> list[tuple[str, str]]:
    """Every ``(document, test basename)`` named inside a fenced block."""
    found: list[tuple[str, str]] = []
    for path in _markdown_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for block in _FENCE.findall(text):
            for name in _TEST_PATH.findall(block):
                found.append((_rel(path), name))
    return found


def test_every_test_named_in_a_fence_exists() -> None:
    existing = _existing_tests()
    # Floors are deliberately below the measured values (144 test modules, 13 references), so a
    # scan that silently stops reading the tree fails here instead of passing on an empty set.
    assert len(existing) >= 100, (
        f"found only {len(existing)} test modules under ai-server/tests — the scan is not "
        "reading the tree, so the assertion below would pass vacuously"
    )
    refs = _references()
    assert len(refs) >= 8, (
        f"found only {len(refs)} test paths inside fenced blocks across "
        f"{len(_markdown_files())} markdown files — the fence or path regex has stopped matching, "
        "which is indistinguishable from a passing scan"
    )

    observed = {(doc, name) for doc, name in refs if name not in existing}
    assert observed == _RECORDED_DEAD, (
        "the set of documents naming a test file that does not exist changed.\n"
        "  newly broken (a command now points at a missing file): "
        f"{sorted(observed - _RECORDED_DEAD)}\n"
        "  no longer broken (the document was fixed, or the test was added): "
        f"{sorted(_RECORDED_DEAD - observed)}\n"
        "Either fix the command, or record it above with the reason it must stay."
    )
