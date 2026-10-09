"""Every `path.py::symbol` citation in `DOCS` must resolve.

DELEGATION.md §4 item 70. A bare `runtime.py:NNN` is not durable: the number rots
as soon as anyone inserts a line above it (cycle 67 renumbered eleven citations
that had drifted by +9 to +168). `path.py::symbol` is the durable form, and this
pin keeps it honest -- the file must exist and must actually define the symbol.

Measured 2026-10-06 (cycle 67): **33 citations** (per-document sum) across `AGENTS.md`
and `DELEGATION.md`; the union is 28, and all resolve. Two had an *incomplete path* and were corrected
in the same cycle (`autonomous_loop.py` -> `autonomous/autonomous_loop.py`, and a
bare `test_mind_persistence_failures_are_named.py` -> `tests/...`); the symbols
themselves were already right. Re-measured 2026-10-09 (cycle 113): the union is **45**.

Measured 2026-10-09 (cycle 113, §4 item 80): the durable form did not stop the
*numbers*. Eight `runtime.py:NNN` citations in the register had drifted again
(+1 to +14), and one number named **two** targets -- `runtime.py:1110` was
`tool_broker = ToolBroker(` in `DELEGATION.md` and `DelegationPolicyStore` in a
test docstring, and both had been *right when written*, at different moments.
So the durable form gained a checked number: `path.py::symbol@NNN`. The symbol
half is checked by `test_every_citation_resolves` (the `@` is outside the
symbol's character class), the number half by the tests below.

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

# The documents this pin reads. Measured 2026-10-09 (cycle 113): **14** maintained
# `*.md` files carry at least one `path.py::symbol` citation -- `AGENTS.md` 12,
# `DELEGATION.md` 36, `PROJECT_STATUS_REVIEW.md` 17, and eleven others 1-10 each.
# These three are the ones the register's own claims live in, and the third was
# added because it carried **three** unresolvable citations that nothing read
# (two to modules deleted in cycle 105, one with an incomplete path). The other
# eleven carried **11** unresolvable citations between them (enumerated, not
# sampled, in `DELEGATION.md` §4 item 82); cycle 114 corrected all 11 -- seven
# incomplete paths whose target still exists, and four citations to targets that
# are genuinely gone (one deleted `l2_mind` symbol, the `FORBIDDEN_CAPABILITIES`
# constant in three safety docs). Widening `DOCS` to cover those eleven is a
# scope decision that stays open; this pin reads the three documents the
# register's own claims live in.
DOCS = ("AGENTS.md", "DELEGATION.md", "PROJECT_STATUS_REVIEW.md")

# '-' MUST be in the class: the repo has `ai-server/tests/...` citations.
CITATION = re.compile(r"([A-Za-z_][\w/.-]*\.py)::([A-Za-z_][A-Za-z0-9_]*)")

# Where a citation's path may be rooted. A citation writes the path relative to
# one of these; the first that exists wins.
BASES = (ROOT, ROOT / "ai-server", ROOT / "ai-server" / "src", ROOT / "ai-server" / "src" / "aegis_ai")

# A citation that must resolve -- the control. If this stops resolving, the
# resolver is broken and every other assertion is vacuous.
CONTROL = ("runtime.py", "_build_runtime")

# --- The enumerated coverage hole (cycle 114, DELEGATION.md §4 item 82) ---
#
# Documents that carry durable `path.py::symbol` citations but are NOT in `DOCS` --
# they are not where the register's own claims live. Item 82 enumerated the
# population by measurement; cycle 114 corrected every unresolvable citation in it
# (seven incomplete paths whose target still exists, four citations to targets that
# are genuinely gone). This tuple pins the *correction* over the enumerated
# population. It does NOT widen the resolution pin above: `DOCS` stays the three
# documents the register's own claims live in, and widening it remains an owner
# decision (item 82).
ENUMERATED = (
    "BUG_REPORT.md",
    "IMPROVEMENT_PROPOSAL.md",
    "AGENT_PROGRESS.md",
    "docs/android-safety.md",
    "docs/dev-safety.md",
    "docs/pc-safety.md",
    "ai-server/tests/conftest.py",
    "ai-server/tests/test_schema_validator_stays_retired.py",
)

# Measured 2026-10-09 (cycle 114): the eight documents above carry **15** durable
# citations between them. A floor, not an equality.
MIN_ENUMERATED = 10

# Symbols that were deleted and must never reappear as a live `path.py::SYMBOL`
# citation. `FORBIDDEN_CAPABILITIES` was removed on 2026-09-29 (B-12 / A-1); three
# safety docs describe that removal, and each used to cite it as
# `settings/validation.py::FORBIDDEN_CAPABILITIES` -- which made a deleted constant
# read as live. Cycle 114 de-cited them (cycle 105's rule: a citation to a deleted
# target stops being a citation).
RETIRED_SYMBOLS = ("FORBIDDEN_CAPABILITIES",)

# Measured 2026-10-06 (cycle 67): the **union** over DOCS was 28 distinct
# (path, symbol) pairs; the per-document sum was 33, so summing the two lists
# double-counts the five citations the docs share. Re-measured 2026-10-09
# (cycle 113): **45**, over the three documents in DOCS. The floor below is
# deliberately left at the older value --
# its job is to catch the pattern ceasing to match (an empty set), not to track
# the population, and an equality would fail whenever a citation is legitimately
# dropped. A floor, not an equality.
MIN_CITATIONS = 28

# --- Anchored citations: `path.py::symbol@NNN` (cycle 113, DELEGATION.md §4 item 80) ---
#
# A bare `path.py:NNN` cannot be checked: its owner is the *paragraph's subject*,
# which is prose, so nothing can decide which line the number was meant to name.
# The anchored form names the symbol the number must land inside:
#
#     runtime.py::_build_runtime@1111
#
# The pattern above already captures the (path, symbol) half -- `@` is not in
# `[A-Za-z0-9_]` -- so the *symbol* is checked by `test_every_citation_resolves`.
# This half checks the *number*: it must fall inside the named symbol's own line
# span, and must not land on a blank line or a bare closing delimiter. Those are
# the two ways a drifted number was actually observed to fail (cycle 112:
# `runtime.py:1110` had drifted onto a lone `)`, and `:1020` / `:1165` onto blank
# lines -- both still *inside* their old symbol, so a span check alone would have
# missed them).
ANCHORED = re.compile(r"([A-Za-z_][\w/.-]*\.py)::([A-Za-z_][A-Za-z0-9_]*)@(\d+)")

# A line that carries nothing: empty, or only closers / separators.
BARE_LINE = re.compile(r"^[\s)\]}>,]*$")

# Measured 2026-10-09 (cycle 113): the union over DOCS is 12 distinct
# (path, symbol, line) triples. A floor, not an equality.
MIN_ANCHORED = 12

# The control: if this pair stops appearing among the anchored citations, the
# anchored extraction has stopped matching the docs' form.
ANCHORED_CONTROL = ("runtime.py", "_build_runtime")


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


def _anchored() -> set[tuple[str, str, int]]:
    """Every `path.py::symbol@NNN` in DOCS, as (path, symbol, line)."""
    found: set[tuple[str, str, int]] = set()
    for name in DOCS:
        text = (ROOT / name).read_text(encoding="utf-8")
        for rel, symbol, line in ANCHORED.findall(text):
            found.add((rel, symbol, int(line)))
    return found


def _spans(source: str, symbol: str) -> list[tuple[int, int]]:
    """1-based inclusive line spans of every def/class/assignment named `symbol`."""
    out: list[tuple[int, int]] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == symbol:
                out.append((node.lineno, node.end_lineno or node.lineno))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == symbol for t in targets):
                out.append((node.lineno, node.end_lineno or node.lineno))
    return out


def _anchor_faults(rel: str, symbol: str, line: int, source: str) -> list[str]:
    """Empty when `symbol@line` is well anchored in `source`."""
    spans = _spans(source, symbol)
    if not spans:
        return [f"{rel}::{symbol}@{line} -- {symbol!r} is not defined in {rel}"]
    if not any(lo <= line <= hi for lo, hi in spans):
        return [f"{rel}::{symbol}@{line} -- line {line} is outside {symbol!r} (spans {spans})"]
    lines = source.split("\n")
    if not (1 <= line <= len(lines)):
        return [f"{rel}::{symbol}@{line} -- {rel} has only {len(lines)} lines"]
    if BARE_LINE.match(lines[line - 1]):
        return [f"{rel}::{symbol}@{line} -- lands on a blank/close-only line: {lines[line - 1]!r}"]
    return []


def test_the_anchored_extraction_is_not_vacuous() -> None:
    """Control: the anchored pattern must still find citations."""
    found = _anchored()
    assert len(found) >= MIN_ANCHORED, (
        f"only {len(found)} anchored citations extracted (expected >= {MIN_ANCHORED}) -- "
        f"the ANCHORED pattern no longer matches the docs' `path.py::symbol@NNN` form"
    )
    assert any((rel, sym) == ANCHORED_CONTROL for rel, sym, _ in found), (
        f"the control {ANCHORED_CONTROL} is no longer present among the anchored citations"
    )


def test_every_anchored_citation_lands_inside_its_symbol() -> None:
    """Each anchored number must fall inside its symbol and land on real text."""
    faults: list[str] = []
    for rel, symbol, line in sorted(_anchored()):
        path = _resolve(rel)
        if path is None:
            faults.append(
                f"{rel}::{symbol}@{line} -- no such file under any of {[str(b) for b in BASES]}"
            )
            continue
        faults += _anchor_faults(rel, symbol, line, path.read_text(encoding="utf-8"))
    assert not faults, (
        "anchored citations whose number does not land where it claims (re-measure the "
        "line, or move the anchor):\n  " + "\n  ".join(faults)
    )


def test_the_anchor_predicate_rejects_the_two_observed_failures() -> None:
    """Positive and negative controls for `_anchor_faults`, independent of the docs.

    Without this, a green `test_every_anchored_citation_lands_inside_its_symbol`
    could mean either "every citation is right" or "the predicate never fires".
    """
    src = "def f():\n    x = 1\n\n    return x\n"
    assert _anchor_faults("m.py", "f", 2, src) == []      # inside, on real text
    assert _anchor_faults("m.py", "f", 99, src)           # outside the span
    assert _anchor_faults("m.py", "f", 3, src)            # inside, but blank
    assert _anchor_faults("m.py", "g", 2, src)            # symbol not defined

    closer = "def f():\n    x = (\n        1\n    )\n    return x\n"
    assert _anchor_faults("m.py", "f", 4, closer)         # inside, but a lone `)`
    assert _anchor_faults("m.py", "f", 5, closer) == []   # inside, on real text


def test_the_enumerated_documents_carry_no_dead_citations() -> None:
    """Item 82's population: every durable citation in it must resolve.

    This is the positive half of cycle 114's fix. Without it, a citation corrected
    in `BUG_REPORT.md` or a safety doc could silently rot again -- those documents
    are deliberately *not* in `DOCS`, so `test_every_citation_resolves` does not
    read them.
    """
    failures: list[str] = []
    seen = 0
    for name in ENUMERATED:
        text = (ROOT / name).read_text(encoding="utf-8")
        for rel, symbol in sorted(set(CITATION.findall(text))):
            seen += 1
            path = _resolve(rel)
            if path is None:
                failures.append(f"{name}: {rel}::{symbol} -- no such file under any of {[str(b) for b in BASES]}")
            elif not _defines(path, symbol):
                failures.append(f"{name}: {rel}::{symbol} -- {path} does not define {symbol!r}")
    assert seen >= MIN_ENUMERATED, (
        f"only {seen} citations extracted from ENUMERATED (expected >= {MIN_ENUMERATED}) -- "
        f"either the pattern stopped matching or the population shrank"
    )
    assert not failures, (
        "dead citations in the enumerated documents (complete the path, or drop the "
        "citation if the target is gone):\n  " + "\n  ".join(failures)
    )


def test_the_retired_symbols_are_not_cited_as_live() -> None:
    """A deleted symbol must not reappear as `path.py::SYMBOL` in ENUMERATED.

    `test_the_enumerated_documents_carry_no_dead_citations` would already catch this
    (the symbol is gone, so `_defines` is False) -- but only while the target file
    still exists. This states the rule directly, so re-adding the citation form is
    reported as "you are citing a retired symbol", not as a generic resolution
    failure.
    """
    hits: list[str] = []
    for name in ENUMERATED:
        text = (ROOT / name).read_text(encoding="utf-8")
        for rel, symbol in CITATION.findall(text):
            if symbol in RETIRED_SYMBOLS:
                hits.append(f"{name}: {rel}::{symbol}")
    assert not hits, (
        "a retired symbol is cited as if it were live (drop the `::` citation form; "
        "the symbol no longer exists):\n  " + "\n  ".join(hits)
    )


# --- Bare line citations: `path.py:NNN` must land on real text (cycle 131, item 70) ---
#
# A bare `path.py:NNN` cannot be *resolved* to a symbol (item 70): its owner is the
# paragraph's subject, which is prose. But one property IS decidable, and it is the
# one the rot class actually violates: **the number must land on a line of the cited
# file**. A blank line, a lone closer, or a number past EOF is not a target, so a
# citation that lands there is stale no matter what the prose meant.
#
# Measured 2026-10-09 (cycle 131): `DOCS` carry **414** bare citations (occurrences,
# not a set); **290** resolve under `BASES`. Of those, **38** land on a blank /
# close-only line or past EOF -- and every one is a *record*: a line that quotes a
# number deliberately (an old->new mapping, a false-positive census, a "measurements
# before the implementation" table, a pre-deletion snapshot, or a note explicitly set
# aside). They are enumerated below with their reason; the other **376** land on real
# text.
#
# Why a census and not a rule: the same citation is a *record* on one line and a
# *live pointer* on another, and nothing textual separates them -- measured this cycle
# by trying four partitions (per-line dates, block-level dates, region kind, symbol
# co-location); each either misclassified the dated ledgers or produced false
# positives. So the pin freezes the *exception set* instead, which is this codebase's
# idiom (`_INTENTIONALLY_UNREAD`, `RETIRED_SYMBOLS`): a new blank landing must be
# added here, deliberately, with a reason.
#
# The pin caught the rot class on its first run: `runtime.py:1165` (x5),
# `runtime.py:792` (x2) and `intake/l1_router.py:160` (x2) were live pointers that a
# one-line insertion had shifted by +1 (`0061427` at `runtime.py:355`, `8c9f0cf` in
# `intake/l1_router.py`) -- after the last sweep. They were renumbered in the same
# cycle (`DELEGATION.md` §4 item 92).
BARE = re.compile(r"([A-Za-z_][\w/.-]*\.py):(\d+)")

# (path, line) -> why a blank/close landing is a *record* rather than rot.
_BARE_RECORDS: dict[tuple[str, int], str] = {
    ("memory/factory.py", 38): (
        "past EOF (the file is 36 lines): `create_semantic_memory` was deleted in "
        "cycle 103; the notes are pre-deletion snapshots, and one is the "
        "`factory.py:38` -> `memory/factory.py:38` disambiguation"
    ),
    ("memory/semantic.py", 28): (
        "past EOF (the file is 25 lines): the orphan `SemanticMemory` class was "
        "deleted in cycle 103; the notes are pre-deletion snapshots"
    ),
    ("runtime.py", 1020): (
        "item 26's census (a flagged-and-dismissed entry) and the §5 row that "
        "records the pre-cycle-103 state"
    ),
    ("runtime.py", 1065): (
        "item 25's pre-deletion snapshot -- the JSONL `audit.py` writer it names was "
        "deleted in cycle 104"
    ),
    ("runtime.py", 1110): "item 80's own record of the drifted number",
    ("runtime.py", 1219): "item 67's producer measurement (a record of the measurement)",
    ("runtime.py", 1254): "item 67's producer measurement (a record of the measurement)",
    ("runtime.py", 1375): (
        "item 29's pre-execution snapshot -- branch (2) would move this very line"
    ),
    ("web/routes/chat.py", 154): "item 67's producer measurement (a record of the measurement)",
    ("grpc_server.py", 191): "the cycle-25 census entry and item 26's record of it",
    ("grpc_server.py", 402): "item 70's old->new mapping (`:402` -> `:405`)",
    ("llm/gateway.py", 162): "the census and old->new mapping (`:162-169` -> `:168-174`)",
    ("intake/l1_router.py", 160): "the census and old->new mapping entries that quote it",
    ("backup/retention.py", 49): "the record of the `:49` -> `:60` fix",
    ("egress/startup.py", 59): (
        "set aside explicitly: the range starts on a blank line but covers the claim"
    ),
    ("capability_catalog.py", 70): (
        "inside the table introduced as 'measurements before the implementation'"
    ),
}

# A floor on the extracted population, so the pin cannot pass vacuously. Measured
# 2026-10-09 (cycle 131): 414 occurrences over `DOCS`, 290 resolvable.
MIN_BARE = 300


def _bare_citations() -> list[tuple[str, str, int]]:
    """Every `path.py:NNN` in `DOCS`, as (document, path, line)."""
    found: list[tuple[str, str, int]] = []
    for name in DOCS:
        text = (ROOT / name).read_text(encoding="utf-8")
        for rel, n in BARE.findall(text):
            found.append((name, rel, int(n)))
    return found


def _bare_faults(rel: str, line: int, source: str) -> list[str]:
    """Empty when `rel:line` lands on a real line of `source`."""
    lines = source.split("\n")
    if not (1 <= line <= len(lines)):
        return [f"{rel}:{line} -- {rel} has only {len(lines)} lines"]
    if BARE_LINE.match(lines[line - 1]):
        return [f"{rel}:{line} -- lands on a blank/close-only line: {lines[line - 1]!r}"]
    return []


def test_the_bare_citation_population_is_not_vacuous() -> None:
    """Control: the pattern must still find bare citations."""
    found = _bare_citations()
    assert len(found) >= MIN_BARE, (
        f"only {len(found)} bare `path.py:NNN` citations extracted (expected >= "
        f"{MIN_BARE}) -- the pattern no longer matches the docs' bare form"
    )


def test_the_bare_landing_predicate_rejects_the_observed_failures() -> None:
    """Positive and negative controls for `_bare_faults`, independent of the docs."""
    src = "def f():\n    x = 1\n\n    return x\n"
    assert _bare_faults("m.py", 2, src) == []  # real text
    assert _bare_faults("m.py", 3, src)  # blank
    assert _bare_faults("m.py", 99, src)  # past EOF
    assert _bare_faults("m.py", 0, src)  # not a line
    closer = "def f():\n    x = (\n        1\n    )\n"
    assert _bare_faults("m.py", 4, closer)  # a lone `)`


def test_no_bare_citation_lands_on_a_blank_line() -> None:
    """A `path.py:NNN` that lands on nothing is stale -- unless it is a record."""
    failures: list[str] = []
    for name, rel, line in sorted(_bare_citations()):
        path = _resolve(rel)
        if path is None:
            continue  # an unresolvable path is a different surface (item 82)
        faults = _bare_faults(rel, line, path.read_text(encoding="utf-8"))
        if faults and (rel, line) not in _BARE_RECORDS:
            failures.append(f"{name}: " + "; ".join(faults))
    assert not failures, (
        "bare citations that land on nothing and are not recorded exceptions "
        "(re-measure the line, or add the record with its reason):\n  "
        + "\n  ".join(failures)
    )


def test_every_recorded_bare_exception_is_still_needed() -> None:
    """A recorded exception nothing needs is a lie -- the list must not rot.

    Same rule as `_INTENTIONALLY_UNREAD`: a declared property nothing validates
    rots. If a record is renumbered to real text, its entry here must go.
    """
    stale: list[str] = []
    for (rel, line), _reason in sorted(_BARE_RECORDS.items()):
        path = _resolve(rel)
        if path is None:
            stale.append(f"{rel}:{line} -- no such file any more")
            continue
        if not _bare_faults(rel, line, path.read_text(encoding="utf-8")):
            stale.append(f"{rel}:{line} -- now lands on real text; drop the entry")
    assert not stale, (
        "recorded bare-citation exceptions that are no longer needed:\n  "
        + "\n  ".join(stale)
    )
