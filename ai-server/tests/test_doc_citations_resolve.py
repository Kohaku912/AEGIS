"""Every `path.py::symbol` citation in the project docs must resolve.

DELEGATION.md §4 item 70. A bare `runtime.py:NNN` is not durable: the number rots
as soon as anyone inserts a line above it (cycle 67 renumbered eleven citations
that had drifted by +9 to +168). `path.py::symbol` is the durable form, and this
pin keeps it honest -- the file must exist and must actually define the symbol.

Measured 2026-10-06 (cycle 67): **33 citations** (per-document sum) across `AGENTS.md`
and `DELEGATION.md`; the union is 28, and all resolve. Two had an *incomplete path* and were corrected
in the same cycle (`autonomous_loop.py` -> `autonomous/autonomous_loop.py`, and a
bare `test_mind_persistence_failures_are_named.py` -> `tests/...`); the symbols
themselves were already right.

⚠️ **Two ways this pin could be vacuous, both pinned below.**
  - If the extraction pattern stops matching, every assertion passes on an empty
    set. `test_the_extraction_is_not_vacuous` fixes the count.
  - `\\w` excludes `-`, so a pattern written as `[\\w/]*` silently truncates a
    hyphenated path: `ai-server/tests/x.py` was captured as `server/tests/x.py`,
    and a resolver then reported seven *correct* citations as "file not found".
    `test_the_pattern_keeps_hyphenated_paths` pins the pattern itself.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ("AGENTS.md", "DELEGATION.md")

# '-' MUST be in the class: the repo has `ai-server/tests/...` citations.
CITATION = re.compile(r"([A-Za-z_][\w/.-]*\.py)::([A-Za-z_][A-Za-z0-9_]*)")

# Where a citation's path may be rooted. A citation writes the path relative to
# one of these; the first that exists wins.
BASES = (ROOT, ROOT / "ai-server", ROOT / "ai-server" / "src", ROOT / "ai-server" / "src" / "aegis_ai")

# A citation that must resolve -- the control. If this stops resolving, the
# resolver is broken and every other assertion is vacuous.
CONTROL = ("runtime.py", "_build_runtime")

# Measured 2026-10-06 (cycle 67): the **union** over DOCS is 28 distinct
# (path, symbol) pairs. ⚠️ The per-document sum is 33 -- the docs share five
# citations, so summing the two lists double-counts them. A floor, not an
# equality: adding a citation is fine, losing the pattern is not.
MIN_CITATIONS = 28


def _citations() -> set[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    for name in DOCS:
        found |= set(CITATION.findall((ROOT / name).read_text(encoding="utf-8")))
    return found


def _resolve(rel: str) -> Path | None:
    for base in BASES:
        candidate = base / rel
        if candidate.exists():
            return candidate
    return None


def _defines(path: Path, symbol: str) -> bool:
    """True if `path` defines `symbol` as a def/class or a module-level name."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == symbol:
                return True
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id == symbol:
                    return True
    return False


def test_the_extraction_is_not_vacuous() -> None:
    """Control: the pattern must still find citations, and the control must resolve."""
    found = _citations()
    assert len(found) >= MIN_CITATIONS, (
        f"only {len(found)} citations extracted (expected >= {MIN_CITATIONS}) — the "
        f"pattern in this module is no longer matching the docs' citation form"
    )
    assert CONTROL in found, f"the control citation {CONTROL} is no longer present in {DOCS}"


def test_the_pattern_keeps_hyphenated_paths() -> None:
    """Pin the instrument: `\\w` excludes '-', which silently truncates a path.

    Measured 2026-10-06 (cycle 67): a first version of this module used `[\\w/]*`
    and captured `ai-server/tests/x.py` as `server/tests/x.py`; the resolver then
    reported seven *correct* citations as unresolved.
    """
    got = CITATION.findall("see `ai-server/tests/test_thing.py::test_it` for the pin")
    assert got == [("ai-server/tests/test_thing.py", "test_it")], (
        f"the pattern captured {got} — a hyphenated path is being truncated"
    )


def test_every_citation_resolves() -> None:
    """Each cited file must exist and must define the cited symbol."""
    failures: list[str] = []
    for rel, symbol in sorted(_citations()):
        path = _resolve(rel)
        if path is None:
            failures.append(f"{rel}::{symbol} — no such file under any of {[str(b) for b in BASES]}")
            continue
        if not _defines(path, symbol):
            failures.append(f"{rel}::{symbol} — {path} does not define {symbol!r}")
    assert not failures, (
        "citations that do not resolve (fix the path or the symbol, or drop the "
        "citation):\n  " + "\n  ".join(failures)
    )
