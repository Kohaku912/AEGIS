"""Durable `path.py::symbol` citations inside the test files must resolve (item 91).

`test_doc_citations_resolve.py` reads the three register documents (`DOCS`) and eight
enumerated others (`ENUMERATED`), but **nothing read the test files' own citations**.
Measured 2026-10-11 (item 91, first measured cycle 130; re-measured cycle 152):
`ai-server/tests/**/*.py` carry **44** distinct `path.py::symbol` citations across
**28** files. This pin covers them with a resolver of its own -- `DOCS`' meaning is
left unchanged (widening *it* stays item 82's decision).

Why a resolver of its own: the test files cite **differently** from the documents, so
`DOCS`' fixed `BASES` cannot read them (item 91, measured cycle 130):

  * **sibling-relative** -- ``test_passkey_auth.py::test_...`` names a file in the
    *citing* file's own directory, which no fixed base contains;
  * **bare basename** -- ``gateway.py::_audit_call`` names
    ``aegis_ai/llm/gateway.py``, so every subpackage directory must be tried;
  * **not a citation at all** -- ``test_server_roster.py``'s ``_RECORDED_DRIFT`` keys
    are ``"<path>::<retired ids>"`` *inventory strings* (``"…permissions.py::dev+dev-server"``),
    which the pattern reads as ``permissions.py::dev``. Those are enumerated below.

The pin's own file is excluded: its fixtures are *deliberately* unresolvable, and the
same is true of ``test_doc_citations_resolve.py``'s fixtures (``test_thing.py``,
``path.py::symbol``).

⚠️ **Two ways this pin could be vacuous, both pinned below.**
  * If the extraction pattern stops matching, every assertion passes on an empty set.
    ``test_the_population_is_not_vacuous`` fixes the count.
  * If the resolver silently stops finding siblings or subpackages, the citations it
    cannot find would be reported as failures -- but a resolver that finds *too much*
    would hide a real miss. ``test_the_resolver_reads_a_sibling_and_a_bare_basename``
    drives both special bases directly.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TESTS = ROOT / "ai-server" / "tests"

# The pin's own file, and the doc-citation pin whose fixtures deliberately do not resolve.
EXCLUDED_FILES = {"test_doc_citations_resolve.py", Path(__file__).name}

# '-' MUST be in the class: the repo has `ai-server/tests/...` citations.
CITATION = re.compile(r"([A-Za-z_][\w/.-]*\.py)::([A-Za-z_][A-Za-z0-9_]*)")

AEGIS = ROOT / "ai-server" / "src" / "aegis_ai"

# Where a citation's path may be rooted: the fixed bases (as in `DOCS`' pin) plus
# every subpackage directory, which is what a bare-basename citation needs.
FIXED_BASES = (ROOT, ROOT / "ai-server", ROOT / "ai-server" / "src", AEGIS)
SUBPACKAGE_BASES = tuple(sorted(d for d in AEGIS.rglob("*") if d.is_dir()))

# (file, path, symbol) -> why the pattern's match is not a citation.
_NON_CITATIONS: dict[tuple[str, str, str], str] = {
    ("test_server_roster.py", "aegis_ai/settings/permissions.py", "dev"): (
        "a `_RECORDED_DRIFT` key `\"…permissions.py::dev+dev-server\"` — an inventory "
        "string, not a citation; the pattern stops at `+`"
    ),
    ("test_server_roster.py", "aegis_ai/web/ui_overview.py", "dev"): (
        "a `_RECORDED_DRIFT` key `\"…ui_overview.py::dev-server\"` — an inventory "
        "string, not a citation; the pattern stops at `-`"
    ),
}

# A floor on the population, so the pin cannot pass vacuously. Measured 2026-10-11
# (cycle 152): 36 checked citations (44 distinct pairs, minus the 6 in the excluded
# pin file and the 2 non-citations). A floor, not an equality.
MIN_CITATIONS = 30


def _test_files() -> list[Path]:
    return [p for p in sorted(TESTS.rglob("*.py")) if p.name not in EXCLUDED_FILES]


def _citations() -> set[tuple[str, str, str]]:
    """Every (file, path, symbol) citation in the test files."""
    found: set[tuple[str, str, str]] = set()
    for path in _test_files():
        for rel, symbol in CITATION.findall(path.read_text(encoding="utf-8")):
            found.add((path.name, rel, symbol))
    return found


def _resolve(rel: str, citing_dir: Path) -> list[Path]:
    """Every existing file the citation `rel` could name, from the citing file's dir.

    Tries the citing file's own directory (sibling-relative citations), the fixed
    bases, and every subpackage directory (bare-basename citations). Returns the
    distinct resolved paths: 1 = resolved, 0 = no file, >1 = ambiguous.
    """
    candidates = [citing_dir / rel]
    for base in (*FIXED_BASES, *SUBPACKAGE_BASES):
        candidates.append(base / rel)
    return sorted({c.resolve() for c in candidates if c.exists()})


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


def test_the_population_is_not_vacuous() -> None:
    """Control: the pattern must still find citations in the test files."""
    found = _citations()
    assert len(found) >= MIN_CITATIONS, (
        f"only {len(found)} citations extracted from the test files (expected >= "
        f"{MIN_CITATIONS}) — the pattern no longer matches, or the population shrank"
    )


def test_the_resolver_reads_a_sibling_and_a_bare_basename() -> None:
    """Drive both special bases, so a resolver that stopped finding them is caught.

    Without this, a resolver regression would *report failures* (noisy but safe) --
    but a resolver widened to search the whole repo would hide a real miss. This
    states what each base is for.
    """
    sibling = _resolve("test_voice_io.py", TESTS)
    assert [p.name for p in sibling] == ["test_voice_io.py"], (
        f"a sibling-relative citation did not resolve to exactly its sibling: {sibling}"
    )
    bare = _resolve("gateway.py", TESTS)
    assert [p.as_posix() for p in bare] == [
        (AEGIS / "llm" / "gateway.py").as_posix()
    ], f"a bare-basename citation did not resolve to its subpackage file: {bare}"


def test_the_resolver_rejects_a_citation_that_names_no_file() -> None:
    """The negative control: a name nothing has must resolve to nothing."""
    assert _resolve("no_such_module_xyz.py", TESTS) == []


def test_the_definition_check_rejects_a_missing_symbol() -> None:
    """Control: `_defines` must be able to answer no, or the symbol half is vacuous.

    Every live citation resolves, so a `_defines` that always returned `True` would
    pass the population test above unnoticed. This drives both answers directly.
    """
    runtime = AEGIS / "runtime.py"
    assert _defines(runtime, "_build_runtime") is True
    assert _defines(runtime, "no_such_symbol_xyz") is False


def test_every_test_file_citation_resolves() -> None:
    """Each cited file must exist uniquely and must define the cited symbol."""
    failures: list[str] = []
    for name, rel, symbol in sorted(_citations()):
        if (name, rel, symbol) in _NON_CITATIONS:
            continue
        matches = _resolve(rel, TESTS)
        if not matches:
            failures.append(f"{name}: {rel}::{symbol} — no such file under any base")
            continue
        if len(matches) > 1:
            failures.append(
                f"{name}: {rel}::{symbol} — ambiguous: {[str(m) for m in matches]}"
            )
            continue
        if not _defines(matches[0], symbol):
            failures.append(f"{name}: {rel}::{symbol} — {matches[0]} does not define {symbol!r}")
    assert not failures, (
        "test-file citations that do not resolve (fix the path or the symbol, or drop "
        "the citation):\n  " + "\n  ".join(failures)
    )


def test_the_non_citations_are_still_needed() -> None:
    """A recorded exception nothing needs is a lie -- the list must not rot.

    Same rule as `_INTENTIONALLY_UNREAD` and `_BARE_RECORDS`: if a `_RECORDED_DRIFT`
    key is rewritten so the pattern no longer matches it, its entry here must go.
    """
    live = {(n, r, s) for n, r, s in _citations()}
    stale = [key for key in _NON_CITATIONS if key not in live]
    assert not stale, (
        "recorded non-citations that are no longer extracted (drop the entry):\n  "
        + "\n  ".join(f"{n}: {r}::{s}" for n, r, s in stale)
    )
