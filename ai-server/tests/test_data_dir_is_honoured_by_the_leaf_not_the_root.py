"""`AEGIS_DATA_DIR` is honoured by the *leaf* and ignored by the *root*.

`AEGIS_DATA_DIR` relocates part of the data tree and not the rest, so an operator who sets it
gets a split brain. Both halves were measured 2026-10-09 (cycle 109):

* **The leaf honours it.** The three shipped capability executors under
  `apps/builtin/ai-server/memory/{save,search,sleep}/executor.py` resolve their data root as
  ``os.environ.get("AEGIS_DATA_DIR") or os.path.join(ROOT, "data")``. Driven: running
  ``memory.save`` with ``AEGIS_DATA_DIR`` set to a temp directory writes
  ``<temp>/memory/persons.jsonl`` and leaves the repository's own ``data/`` alone.
* **The root ignores it.** `runtime.py::_build_runtime` computes
  ``base_dir = Path(__file__).resolve().parents[2]`` and ``data_dir = str(base_dir / "data")``.
  No module under `src/` reads the exact name.

So setting the variable moves what `memory.save` / `memory.search` / `memory.sleep` read and
write, while the audit DB, settings, confirmations, user model, journals and logs stay in the
repository's ``data/``. That is worse than an inert variable: the variable *appears* to work.

**Why this needs a pin rather than the prose it had.** The claim already existed, inside the
module docstring of `tests/test_egress_grant_source_is_wired.py`: "nothing under ``src/`` reads
``AEGIS_DATA_DIR``". That sentence is true and, read alone, misleading — the reader is invited
to conclude the variable is dead, when three shipped executors depend on it. A claim about
*state* whose **scope** (`src/`) hides a live reader is exactly the class this repository pins,
so the reader set is now an assertion instead of a sentence.

Two traps this file guards:

* **The name has a sibling.** `src/aegis_ai/health/alert_manager.py` reads
  ``AEGIS_DATA_DIR_WARNING_MB`` — a *different* variable. A substring scan counts it as a
  reader of `AEGIS_DATA_DIR` and then reports a `src/` reader that does not exist. The reader
  set is built from ``ast`` string arguments, and the sibling's presence is asserted as a
  control, so a scan that cannot tell the two apart fails.
* **"No reader under `src/`" is not "no reader".** The reader set spans `src/` *and* the
  shipped `apps/` manifest tree; a scan of `src/` alone would confirm the misleading sentence.
  The non-vacuity floor below counts both roots.

**Recorded, not fixed.** Making the composition root honour the variable is a behaviour change
(data moves on upgrade) and removing the executors' reads is a behaviour change too, so this
file fixes the *record* and leaves the decision to the owner (`DELEGATION.md` section 4).
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

_SERVER = Path(__file__).resolve().parents[1]
_ROOTS = (_SERVER / "src", _SERVER / "apps")
_RUNTIME = _SERVER / "src" / "aegis_ai" / "runtime.py"
_ALERT_MANAGER = _SERVER / "src" / "aegis_ai" / "health" / "alert_manager.py"

#: The variable under test, and the differently-named sibling that a substring scan confuses
#: it with. Both are read from the environment; only the first is the subject.
_ENV = "AEGIS_DATA_DIR"
_SIBLING = "AEGIS_DATA_DIR_WARNING_MB"

#: The complete set of production readers, by path relative to ``ai-server/``. An **equality**,
#: so a fourth reader and a deleted one both fail rather than silently widening the record.
_READERS = frozenset(
    {
        "apps/builtin/ai-server/memory/save/executor.py",
        "apps/builtin/ai-server/memory/search/executor.py",
        "apps/builtin/ai-server/memory/sleep/executor.py",
    }
)

#: ``src/`` alone is ~390 modules and ``apps/`` adds the manifest tree -- measured **398**
#: (2026-10-09). A scan that reads nothing must not be able to satisfy the equality below by
#: returning an empty set; the floor is a measurement with margin, not a round number.
_MIN_FILES = 380

#: The executor driven for the behavioural half. ``type: "person"`` keeps it off the LLM path,
#: so the probe makes no outbound attempt and writes no audit row into the repository's sink.
_SAVE_EXECUTOR = _SERVER / "apps" / "builtin" / "ai-server" / "memory" / "save" / "executor.py"
_PROBE_TOKEN = "cycle-109-data-dir-probe"
_PROBE_TIMEOUT_S = 120


def _python_files() -> list[Path]:
    files: list[Path] = []
    for root in _ROOTS:
        files.extend(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)
    return sorted(files)


def _env_reads(path: Path) -> set[str]:
    """Environment keys read by ``path`` -- ``environ.get`` / ``getenv`` / ``environ[...]``.

    Built from the **string argument**, never from a text search: a mention in a docstring or a
    name that merely starts with the key must not count. Returns the literal keys only, so an
    f-string or a computed key is *not* silently attributed to this variable.
    """
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    keys: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else (func.id if isinstance(func, ast.Name) else None)
            if name in {"get", "getenv"} and node.args:
                first = node.args[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    keys.add(first.value)
        elif isinstance(node, ast.Subscript):
            value = node.value
            if isinstance(value, ast.Attribute) and value.attr == "environ":
                sl = node.slice
                if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                    keys.add(sl.value)
    return keys


def _readers_of(key: str) -> set[str]:
    """Every production file that reads ``key``, relative to ``ai-server/``."""
    found: set[str] = set()
    for path in _python_files():
        if key in _env_reads(path):
            found.add(str(path.relative_to(_SERVER)).replace("\\", "/"))
    return found


def _data_dir_assignment() -> ast.AST:
    """The ``data_dir = ...`` assignment inside ``_build_runtime`` (the composition root)."""
    tree = ast.parse(_RUNTIME.read_text(encoding="utf-8"), filename=str(_RUNTIME))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_build_runtime":
            for child in ast.walk(node):
                targets: list[ast.expr] = []
                value: ast.expr | None = None
                if isinstance(child, ast.Assign):
                    targets, value = list(child.targets), child.value
                elif isinstance(child, ast.AnnAssign):
                    targets, value = [child.target], child.value
                if value is None:
                    continue
                if any(isinstance(t, ast.Name) and t.id == "data_dir" for t in targets):
                    return value
    raise AssertionError(
        "_build_runtime no longer assigns `data_dir` -- the composition root changed shape; "
        "re-measure before trusting this pin (DELEGATION.md section 4, the AEGIS_DATA_DIR item)"
    )


# ── the scan is real ──────────────────────────────────────────────────────────────────


def test_the_scan_reads_the_shipped_tree() -> None:
    files = _python_files()
    assert len(files) >= _MIN_FILES, (
        f"only {len(files)} python files under src/ and apps/ -- the reader scan is not reading "
        "the shipped tree, so the equality below would pass vacuously"
    )
    assert _SAVE_EXECUTOR.exists(), "the driven executor is gone -- the behavioural half is dead"


def test_the_sibling_name_is_its_own_variable() -> None:
    """Control: the scan finds a *different* key in a file, so it is not blind to env reads.

    Without this, a scan that returned nothing at all would satisfy the equality below for the
    wrong reason.
    """
    sibling = _env_reads(_ALERT_MANAGER)
    assert _SIBLING in sibling, (
        f"{_ALERT_MANAGER.name} no longer reads {_SIBLING} -- the control is vacuous, so the "
        "scan cannot be shown to distinguish the two names"
    )
    assert _ENV not in sibling, (
        f"{_ALERT_MANAGER.name} reads the *exact* key {_ENV} -- the reader set below is now "
        "wrong (and the composition root's scope changed)"
    )


# ── the leaf honours it ───────────────────────────────────────────────────────────────


def test_the_exact_name_is_read_by_exactly_the_three_executors() -> None:
    readers = set(_readers_of(_ENV))
    assert readers == set(_READERS), (
        "the set of production readers of "
        f"{_ENV} changed.\n"
        f"  newly reading it: {sorted(readers - _READERS)}\n"
        f"  no longer reading: {sorted(_READERS - readers)}\n"
        "A new reader means the split brain grew; a removed one means it shrank. Either way, "
        "update this record and the DELEGATION.md section 4 item."
    )


def test_the_leaf_writes_under_the_environment_variable(tmp_path) -> None:
    """Drive it: the shipped ``memory.save`` capability resolves its root from the variable.

    ``type: "person"`` takes the non-LLM branch, so no outbound attempt is made and no audit
    row is written to the repository's sink (measured: ``data/audit.db`` is byte-identical
    before and after).
    """
    data_root = tmp_path / "relocated"
    env = dict(os.environ)
    env[_ENV] = str(data_root)
    env.pop("PYTHONPATH", None)

    proc = subprocess.run(
        [sys.executable, str(_SAVE_EXECUTOR)],
        input=json.dumps({"content": _PROBE_TOKEN, "type": "person"}),
        capture_output=True,
        text=True,
        cwd=str(_SAVE_EXECUTOR.parent),
        env=env,
        timeout=_PROBE_TIMEOUT_S,
    )
    assert proc.returncode == 0, f"the executor failed:\n{proc.stdout}\n{proc.stderr}"

    written = sorted(p for p in data_root.rglob("*") if p.is_file())
    assert written, (
        f"nothing was written under {_ENV}={data_root} -- the leaf no longer honours the "
        "variable, so this record's first half is false"
    )
    assert any(p.read_text(encoding="utf-8", errors="replace").find(_PROBE_TOKEN) >= 0 for p in written), (
        f"the probe token is not in any file under {_ENV}; the executor wrote elsewhere -- "
        f"files: {[str(p.relative_to(data_root)) for p in written]}"
    )

    repo_copy = _SERVER / "data" / "memory" / "persons.jsonl"
    if repo_copy.exists():
        assert _PROBE_TOKEN not in repo_copy.read_text(encoding="utf-8", errors="replace"), (
            f"the probe landed in the repository's own {repo_copy} -- the variable was ignored "
            "on the leaf side too, which is a different (and worse) finding"
        )


# ── the root ignores it ───────────────────────────────────────────────────────────────


def test_the_composition_root_derives_its_root_without_the_environment() -> None:
    value = _data_dir_assignment()
    rendered = ast.unparse(value)

    readers = {
        node.attr for node in ast.walk(value) if isinstance(node, ast.Attribute) and node.attr in {"environ", "getenv"}
    }
    assert not readers, (
        f"the composition root's data_dir now reads the environment ({sorted(readers)}): "
        f"`data_dir = {rendered}`. If AEGIS_DATA_DIR was wired here, the split brain is fixed "
        "-- update this pin and the DELEGATION.md section 4 item instead of deleting the test."
    )
    assert "base_dir" in rendered and "data" in rendered, (
        f'the composition root\'s data_dir is no longer `base_dir / "data"`: `{rendered}`. '
        "Re-measure the two roots before trusting this record."
    )


def test_no_module_under_src_reads_the_exact_name() -> None:
    """The half the old docstring claimed -- now asserted, and paired with the reader set."""
    src_readers = sorted(path for path in _readers_of(_ENV) if path.startswith("src/"))
    assert src_readers == [], (
        f"{src_readers} read {_ENV} under src/ -- the composition root or a sibling now "
        "consults it; the 'ignored by the root' half of this record is stale"
    )
