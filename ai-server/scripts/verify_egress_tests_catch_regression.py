#!/usr/bin/env python
"""Prove the egress regression suite fails when the constraint is deliberately broken.

The plan's completion criterion for Phase 4 is not "an egress test exists" but "an
egress test exists **and fails when deliberately broken**". A suite that has never
been observed failing is an assumption, not a control.

This script runs the egress suite twice:

1. **Unmutated** — must pass. Establishes the baseline.
2. **Mutated** — the gate is forced to allow everything (``-p
   mutation_egress_allow_all``). Must **fail**. If it passes, the suite does not
   actually protect the constraint.

Exit code is 0 only when both hold. Nothing on disk is modified: the mutation is a
process-local monkeypatch, so this is safe to run repeatedly.

Usage (from ``ai-server/``)::

    ../.venv/Scripts/python.exe scripts/verify_egress_tests_catch_regression.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
AI_SERVER = HERE.parent
PLUGIN_DIR = HERE
PLUGIN_NAME = "mutation_egress_allow_all"


def _harden_stdout() -> None:
    """Never let console encoding abort the check.

    This script is invoked from a PowerShell harness, where ``sys.stdout`` is a
    pipe whose encoding follows the console code page (cp932 on this machine).
    Any non-ASCII byte - in our own banner text, or in echoed pytest output that
    contains a test name or an assertion repr - raises ``UnicodeEncodeError`` and
    kills the run *before* the check it was meant to perform. A crash here reads
    as "the egress suite does not catch a disabled gate", which is the opposite
    of the truth, so the encoding failure mode is worse than a cosmetic problem.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, OSError):  # pragma: no cover - exotic streams
            pass

#: The whole egress surface. A mutation must be caught by at least one of these, and
#: the unmutated run must pass all of them.
#:
#: **This roster is a second copy of a fact the marker already carries** — every file
#: below sets ``pytestmark = pytest.mark.egress``. A hand-maintained list that must be
#: kept in sync with a marker drifts silently, and it did: ``test_egress_permission.py``
#: was added by the 2026-09-30 re-scope and was *not* listed here, so the mutation check
#: would not have exercised the new permission path.
#: ``tests/test_egress_closure.py::test_the_mutation_roster_covers_every_marked_file``
#: now asserts the two agree, so the next egress file cannot be forgotten.
EGRESS_TESTS = (
    "tests/test_egress_gate.py",
    "tests/test_egress_permission.py",
    "tests/test_egress_closure.py",
    "tests/test_egress_reliability.py",
    "tests/test_ineffective_flags.py",
    "tests/test_local_llm_path.py",
    "tests/test_voice_io.py",
)


def _run(extra_args: list[str]) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    # Make the plugin importable by `-p`.
    env["PYTHONPATH"] = os.pathsep.join(
        [str(PLUGIN_DIR), env.get("PYTHONPATH", "")] if env.get("PYTHONPATH") else [str(PLUGIN_DIR)]
    )
    # Keep the WorkBuddy safe-delete shim out of pytest teardown.
    env.setdefault("CODEBUDDY_SAFE_DELETE_ENABLED", "0")

    return subprocess.run(
        [sys.executable, "-m", "pytest", *EGRESS_TESTS, *extra_args, "-q", "-p", "no:cacheprovider"],
        cwd=AI_SERVER,
        env=env,
        capture_output=True,
        text=True,
    )


def _summary(completed: subprocess.CompletedProcess) -> str:
    for line in reversed(completed.stdout.strip().splitlines()):
        if "passed" in line or "failed" in line or "error" in line:
            return line.strip()
    return "<no pytest summary line>"


def main() -> int:
    _harden_stdout()
    print("=" * 72)
    print("Egress regression check: does the suite notice a broken constraint?")
    print("=" * 72)

    print("\n[1/2] Unmutated run - the suite must pass ...")
    baseline = _run([])
    print(f"      exit={baseline.returncode}  {_summary(baseline)}")
    if baseline.returncode != 0:
        print("\nFAIL: the egress suite does not pass in its normal state.")
        print(baseline.stdout[-4000:])
        return 1

    print("\n[2/2] Mutated run (gate forced to allow everything) - must fail ...")
    mutated = _run(["-p", PLUGIN_NAME])
    print(f"      exit={mutated.returncode}  {_summary(mutated)}")
    if mutated.returncode == 0:
        print(
            "\nFAIL: the egress suite still passed with the gate disabled.\n"
            "      The tests do not actually protect the single constraint — they\n"
            "      assert on something other than the decision."
        )
        return 1
    if "mutation plugin" in mutated.stdout and "inert" in mutated.stdout:
        print("\nFAIL: the mutation plugin did not take effect, so this run proves nothing.")
        return 1

    print("\n" + "=" * 72)
    print("OK: the egress suite passes normally and fails when the gate is broken.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
