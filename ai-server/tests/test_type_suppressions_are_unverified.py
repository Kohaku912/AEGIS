"""`mypy` is declared, installed, and never run — so the suppressions it justifies are unverified.

Measured 2026-10-01 on this tree (mypy 2.3.1, and no configuration of any kind):

* **Declared, and therefore installed.** `mypy>=1.8` is a `dev` extra of `ai-server` and
  `browser-server` (mirrored in both `uv.lock` files), so `pip install -e ".[dev]"` / `uv sync`
  puts a type checker on the machine. `infra/docker/ai-server.Dockerfile:42` deliberately keeps it
  out of the *production* image — that comment is about the image, not a claim that it runs here.
* **Nothing runs it.** There is no `.github/`, no `Makefile` and no pre-commit config in this repo,
  and no line of any runner script invokes it. The only mention under `scripts/` is
  `audit_common.py`'s `".mypy_cache"` skip-list entry — a directory **nothing creates**, so the
  audit tool's exclusion list quietly asserts that a type checker runs.
* **No configuration.** No `[tool.mypy]` section in any of the four `pyproject.toml` files, and no
  `mypy.ini` / `.mypy.ini` / `setup.cfg`. mypy's *defaults* are the only configuration there is.
* **It does not pass.** `python -m mypy src` → **317 errors in 94 files** (407 checked). That is why
  wiring it is a scoping decision rather than a one-line gate — the `ruff` gate next door had to be
  scoped to `--select F821` for the same reason (`DELEGATION.md` §4 item 7).

The load-bearing consequence: **53 `# type: ignore` comments** across 26 files carry mypy error
codes — a *claim* that the checker was satisfied on that line — and nothing verifies it. Measured
with `--warn-unused-ignores`, **21 of them suppress nothing** (16 in `src/`, 5 in `tests/`), and the
control (`--check-untyped-defs`, which rules out "mypy simply did not look") leaves the `src/` count
at **16**. A reader who sees `# type: ignore[arg-type]` concludes that type checking is in force.

Two asymmetries worth keeping: `browser-server` declares mypy and carries **0** suppressions, while
`room-server` declares **nothing** and carries **2**. Neither is accounted for by a declaration.

**What this file pins, and what it deliberately does not.** It pins the three *static* facts a CI
run can check without executing mypy: the declaration set, the absence of a runner, and the
un-scoped (`bare`) suppressions. It does **not** re-measure the 317 errors or the 21 stale
suppressions — that needs mypy, which the CI venv does not have (measured while adding the ruff
gate: a uv-managed venv with no `pip` at all). Those two numbers are dated measurements recorded
here, not assertions; the pin's job is to make the *static* facts impossible to change silently.

**How suppressions are counted.** By `tokenize`, keeping only COMMENT tokens whose text *begins*
with the directive — so a docstring or a comment that merely *mentions* `# type: ignore` is not
counted. This file is scanned along with the rest (there is no self-exclusion), and it carries none.

**Recorded, not fixed.** Whether to wire a mypy gate or drop the declaration and its suppressions is
a scope call, so it is an owner item (`DELEGATION.md` §4). Nothing here is wired, deleted or
silenced — in particular the 10 bare suppressions are recorded as debt, not approved.
"""

from __future__ import annotations

import os
import re
import tokenize
import tomllib
from functools import lru_cache
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]

_SKIP_DIRS = frozenset({".git", ".venv", "node_modules", "__pycache__", ".workbuddy-ai"})

_TOOL = "mypy"

#: Files whose job is to *run a sequence of commands*. A `.py` file is the code under check and a
#: Dockerfile is an image recipe, so neither is a runner. That is a structural distinction by
#: extension, not a per-file exclusion list — the same move `test_dockerfiles_are_owned.py` makes
#: when it keeps the frozen `docker-compose.yml.archive` out of its scan.
_RUNNER_SUFFIXES = frozenset({".ps1", ".sh", ".yml", ".yaml"})
_RUNNER_NAMES = frozenset({"Makefile"})

#: pyproject.toml files that declare mypy. A dependency nobody runs is still a dependency that gets
#: installed, so the set is pinned by equality: a new declarer (or a dropped one) must be recorded.
_RECORDED_DECLARERS: frozenset[str] = frozenset(
    {"ai-server/pyproject.toml", "browser-server/pyproject.toml"}
)

#: Un-scoped suppressions (`# type: ignore` with no `[code]`) — file -> count. A bare ignore
#: suppresses *every* error on its line, so it is the form that hides the most, and this is an
#: inventory of debt rather than a set of approvals. All ten sit on import lines.
_RECORDED_BARE: dict[str, int] = {
    "ai-server/src/aegis_agent_server/main.py": 6,
    "ai-server/src/aegis_ai/tools/mcp_gateway.py": 4,
}

#: Non-vacuity floors. A scan that has gone blind returns an empty set, and every assertion below
#: is satisfied by an empty set — so the surface each scan walks must be asserted non-empty.
_MIN_SUPPRESSIONS = 40
_MIN_PYPROJECTS = 4
_MIN_RUNNERS = 20

_CONFIG_FILENAMES = frozenset({"mypy.ini", ".mypy.ini", "setup.cfg"})

#: A suppression comment must **begin** with the directive. That is what makes this a *rule*
#: rather than an exclusion list: `#: Un-scoped suppressions (\`# type: ignore\` ...)` — the prose
#: comment in this very file — merely *contains* the phrase, and a rule that accepted a mention
#: would count this pin as carrying suppressions. Measured over all 640 `.py` files: the loose
#: "contains" form finds 54 and the anchored form finds 53, the single difference being that
#: comment. Every real suppression is a trailing comment or a directive line, so both anchor.
_SUPPRESSION_RE = re.compile(r"^#\s*type:\s*ignore\b")
_CODED_SUPPRESSION_RE = re.compile(r"^#\s*type:\s*ignore\s*\[")


@lru_cache(maxsize=1)
def _shipped_files() -> tuple[Path, ...]:
    """Every file under the repo except the skipped trees (walked once; ~25 k files)."""
    out: list[Path] = []
    for root, dirs, files in os.walk(_REPO):
        dirs[:] = sorted(d for d in dirs if d not in _SKIP_DIRS)
        out.extend(Path(root) / name for name in files)
    return tuple(out)


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(_REPO).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _mentions_tool(text: str, tool: str) -> bool:
    """The tool name as a **standalone word**, not as part of a longer identifier.

    A *token* rule rather than an exclusion list: `mypy_cache` and `mypy.ini` are longer
    identifiers and do not count, and the rule is stated once here instead of being applied to
    individual sites. `test_nothing_in_the_build_tooling_invokes_the_type_checker` proves the rule
    can still see a real invocation by finding `-m ruff` with it.
    """
    return re.search(rf"(?<![A-Za-z0-9_.]){re.escape(tool)}(?![A-Za-z0-9_.])", text) is not None


def _runner_files() -> list[Path]:
    return sorted(
        path
        for path in _shipped_files()
        if path.suffix in _RUNNER_SUFFIXES or path.name in _RUNNER_NAMES
    )


def _pyproject_files() -> list[Path]:
    return sorted(path for path in _shipped_files() if path.name == "pyproject.toml")


def _python_files() -> list[Path]:
    return sorted(path for path in _shipped_files() if path.suffix == ".py")


def _declares_mypy(data: dict) -> bool:
    """True if any dependency list of this `pyproject.toml` names mypy."""
    project = data.get("project") or {}
    groups = list((project.get("dependencies") or []))
    for deps in (project.get("optional-dependencies") or {}).values():
        groups.extend(deps or [])
    for deps in (data.get("dependency-groups") or {}).values():
        groups.extend(deps or [])
    return any(isinstance(dep, str) and dep.split(">=")[0].split("==")[0].strip() == _TOOL for dep in groups)


def _suppressions(path: Path) -> list[str]:
    """Every COMMENT token in the file that suppresses typing errors.

    `tokenize`, not a regex over the raw text. This file's own docstring *discusses*
    `# type: ignore`, and a string literal is not a comment — a regex scan would count this pin as
    carrying suppressions, i.e. the instrument counting itself. The scan covers this file too, and
    it carries none.
    """
    found: list[str] = []
    with path.open("rb") as handle:
        for token in tokenize.tokenize(handle.readline):
            if token.type == tokenize.COMMENT and _SUPPRESSION_RE.search(token.string):
                found.append(token.string)
    return found


def test_the_type_checker_is_declared_only_where_it_is_recorded() -> None:
    pyprojects = _pyproject_files()
    assert len(pyprojects) >= _MIN_PYPROJECTS, (
        f"found only {len(pyprojects)} pyproject.toml files — the scan is not reading the shipped "
        "tree, so the comparison below would pass vacuously"
    )

    declaring: set[str] = set()
    configured: set[str] = set()
    for path in pyprojects:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        if _declares_mypy(data):
            declaring.add(_rel(path))
        if _TOOL in (data.get("tool") or {}):
            configured.add(_rel(path))

    assert declaring == _RECORDED_DECLARERS, (
        "the set of pyproject.toml files declaring mypy changed.\n"
        f"  newly declaring: {sorted(declaring - _RECORDED_DECLARERS)}\n"
        f"  no longer declaring: {sorted(_RECORDED_DECLARERS - declaring)}\n"
        "A dependency that gets installed is a claim about the toolchain: record it here."
    )
    assert not configured, (
        "a [tool.mypy] section appeared — the 317-error measurement recorded in this file's "
        f"docstring was taken with *no* configuration, so it is now stale: {sorted(configured)}"
    )

    configs = sorted(
        _rel(path) for path in _shipped_files() if path.name in _CONFIG_FILENAMES
    )
    assert not configs, (
        "a mypy configuration file appeared; the dated measurement in this docstring assumed there "
        f"was none: {configs}"
    )


def test_nothing_in_the_build_tooling_invokes_the_type_checker() -> None:
    runners = _runner_files()
    assert len(runners) >= _MIN_RUNNERS, (
        f"found only {len(runners)} runner scripts — the scan is not reading the shipped tree, so "
        "the absence assertion below would pass vacuously"
    )

    texts = {path: path.read_text(encoding="utf-8", errors="replace") for path in runners}

    # Positive control, and it must go through **the same helper** the assertion below uses. A
    # control that re-implements the rule proves the file loop works and nothing about the rule:
    # measured, blinding `_mentions_tool` to `return False` left this whole pin green while the
    # control was a separate `re.search`.
    wired = sorted(_rel(path) for path, text in texts.items() if _mentions_tool(text, "ruff"))
    assert wired, (
        "the token rule cannot see `ruff`, yet `scripts/test-ai-server.ps1` invokes it as "
        "`& $Python -m ruff check src tests --select F821`. The rule is blind, so the absence "
        "assertion below proves nothing."
    )
    # ...and the invocation *form* a mypy gate would take does exist in the tree, so "nothing
    # invokes mypy" is a claim about this repo rather than about a missing feature.
    assert any(re.search(r"-m\s+ruff\b", text) for text in texts.values()), (
        "no runner script uses the `-m <tool>` form, so the absence assertion is not comparable"
    )

    invoking = sorted(_rel(path) for path, text in texts.items() if _mentions_tool(text, _TOOL))
    assert not invoking, (
        "a runner script now mentions mypy. If that is a real gate, this record is superseded: "
        "delete this pin, re-measure the error count under the new configuration, and update the "
        f"suppression record with it. Files: {invoking}"
    )


def test_bare_suppressions_match_the_recorded_set() -> None:
    counts: dict[str, int] = {}
    total = 0
    for path in _python_files():
        for comment in _suppressions(path):
            total += 1
            if not _CODED_SUPPRESSION_RE.search(comment):
                key = _rel(path)
                counts[key] = counts.get(key, 0) + 1

    assert total >= _MIN_SUPPRESSIONS, (
        f"found only {total} `type: ignore` comments in the tree — the scan is not reading the "
        "shipped code, so the comparison below would pass vacuously"
    )

    assert counts == _RECORDED_BARE, (
        "the set of un-scoped (`# type: ignore`, no `[code]`) suppressions changed.\n"
        f"  newly bare: {sorted(set(counts) - set(_RECORDED_BARE))}\n"
        f"  no longer bare: {sorted(set(_RECORDED_BARE) - set(counts))}\n"
        f"  count changed: {[(k, _RECORDED_BARE[k], counts[k]) for k in counts if k in _RECORDED_BARE and counts[k] != _RECORDED_BARE[k]]}\n"
        "A bare ignore suppresses every error on its line. Give it a code, or record it above."
    )
