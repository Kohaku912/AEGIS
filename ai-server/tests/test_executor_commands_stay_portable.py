"""A checked-in executor command must not name a machine-specific interpreter.

``ExecutorRegistry._normalize_command`` replaces the interpreter of any command that
mentions ``executor.py`` with ``sys.executable``, because the same manifest has to run
both on the host and inside the container. So for the shipped executors the *value* of
``executor.json``'s ``command`` is **decorative** — the code ignores it.

Decorative is not the same as harmless, and it is not the same as unpinned. Measured
2026-10-01: ``apps/builtin/pc-server/screenshot/get_screenshot/executor.json`` was the
only one of seven command-type executors whose ``command`` named a host-absolute path —

    C:\\\\Users\\\\kohak\\\\...\\\\ai-server\\\\.venv\\\\Scripts\\\\python.exe executor.py

— and that path does not exist on the machine that shipped it (the venv lives at the
repository root, not under ``ai-server/``). Nothing broke, because the normalizer threw
the value away. Two things were wrong anyway:

1. It is a **latent** live break, not a hypothetical one. The normalizer only substitutes
   while ``executor.py`` sits next to the manifest; its fallback is ``return command``.
   ``test_without_executor_py_the_checked_in_command_would_be_used`` pins that fallback,
   so the risk is measured rather than assumed.
2. No test read ``executor.json`` at all, so the spelling could drift back at any time.

These tests are deliberately spelling-level, and they carry no exclusion list — an
exclusion list is itself the defect (see ``test_manifest_schemas.py``, which makes the
same choice for risk labels). They assert the recorded set of first tokens **by
equality**, so a new spelling fails whether it is more specific or less.
"""

from __future__ import annotations

import json
from pathlib import Path

from aegis_ai.folder_registry import ExecutorRegistry

_APPS = Path(__file__).resolve().parents[1] / "apps"

# The one interpreter spelling a checked-in command is allowed to name. It is not
# load-bearing (the normalizer discards it); it is recorded so that a second spelling
# cannot appear unnoticed. Update this set only together with the manifest that needs it.
_RECORDED_FIRST_TOKENS: frozenset[str] = frozenset({"python"})


def _command_executors() -> list[tuple[str, Path, str]]:
    """Every shipped ``executor.json`` of type ``command``, with its declared command.

    Discovery-based on purpose: a hand-written list of the seven executors would go stale
    the first time one is added, and the test would keep passing while covering less.
    """
    found: list[tuple[str, Path, str]] = []
    for path in sorted(_APPS.rglob("executor.json")):
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if data.get("type", "command") != "command":
            continue
        command = data.get("command", "")
        if command:
            found.append((path.relative_to(_APPS).as_posix(), path, command))
    return found


def test_the_checked_in_interpreter_is_never_load_bearing() -> None:
    """The value is inert only while ``executor.py`` sits next to the manifest.

    Asserted through the real function rather than by restating its condition, so this
    fails the moment a command manifest stops being normalized — which is exactly when
    its spelling stops being decorative and starts being executed.
    """
    executors = _command_executors()
    assert len(executors) >= 7, (
        f"found only {len(executors)} command executors — the scan is not reading the "
        "shipped tree, so everything below would pass vacuously"
    )

    load_bearing = [
        f"{rel}: {command!r} (normalized to itself)"
        for rel, path, command in executors
        if ExecutorRegistry._normalize_command(command, str(path.parent.resolve())) == command
    ]
    assert not load_bearing, (
        "these checked-in commands are executed verbatim, so their interpreter must be "
        "portable: " + "; ".join(load_bearing)
    )


def test_checked_in_interpreters_use_the_recorded_spelling() -> None:
    """Equality, not a floor: a floor cannot see a new spelling appear.

    The failure this is here to catch is a host-absolute path coming back — the measured
    instance named the author's home directory and a venv that did not exist. It also
    fails in the other direction, if the recorded spelling disappears entirely.
    """
    executors = _command_executors()
    assert len(executors) >= 7, "the scan found no command executors, so this is vacuous"

    observed = {command.split()[0] for _, _, command in executors}
    assert observed == _RECORDED_FIRST_TOKENS, (
        f"checked-in interpreters are {sorted(observed)}, expected "
        f"{sorted(_RECORDED_FIRST_TOKENS)}. A machine-specific path (e.g. "
        r"'C:\Users\...\python.exe') is inert only until executor.py moves; use the "
        "portable spelling the other executors use."
    )


def test_without_executor_py_the_checked_in_command_would_be_used(tmp_path: Path) -> None:
    """Pin the fallback, because it is what makes the spelling worth constraining.

    ``tmp_path`` has no ``executor.py``, so the normalizer returns the command unchanged.
    This is the second half of the story above: the same manifest in a directory where the
    script is missing would try to launch the interpreter it names.
    """
    command = r"C:\Users\example\aegis\ai-server\.venv\Scripts\python.exe executor.py"
    assert ExecutorRegistry._normalize_command(command, str(tmp_path)) == command
