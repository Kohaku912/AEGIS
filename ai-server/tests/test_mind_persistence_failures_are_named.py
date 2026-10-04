"""The `mind/` persistence family names its read failures.

Eight modules in `aegis_ai/mind/` persist to JSONL, and each had an identical
`_load` whose `except (json.JSONDecodeError, OSError): pass` made a corrupt file
indistinguishable from "no data yet". Cycle 13 (2026-10-04) named them. This pin
fixes that naming — and, just as important, fixes the *boundary* of the claim,
because a pin that only asserted "a warning appears" would overstate the family.

Measured 2026-10-04, one file at a time, with the real classes:

* a corrupt file            -> one WARNING naming the path and the exception,
                               and the object still constructs with defaults;
* a missing file            -> silent (a legitimate absence — the control);
* a valid object line       -> silent (the control);
* a valid JSON line that is **not** an object (`123`) -> RAISES `AttributeError`
                               out of `__init__`, uncaught, with no warning.

That last row is a measured divergence, not an oversight to be silently
"fixed": the family's silent path keys on the exception *type*, not on whether
the file is usable — `123` is exactly as unusable as `{"a": 1`, yet one crashes
the constructor and the other is defaulted. Two of the live construction sites
are unguarded (`runtime.py` — `Identity`, `AffectSystem`), a third swallows the
same call at DEBUG (`llm/memory_context.py`). Recorded as `DELEGATION.md` §4
item 38; widening the caught set changes behaviour, so this pin fixes the
current behaviour instead.

The liveness split is fixed here too, so the family's scope is not overstated.
Of the eight, only `Identity` is constructed outside `mind/`; `Mood`,
`Personality` and `LayeredEmotion` are live only through `AffectSystem`, and
`Desire`, `Emotion`, `GoalManager`, `SocialIntelligence` are constructed nowhere
(`Emotion`/`GoalManager` are imported only by `reflection_loop.py`, which is
itself never constructed). Recorded as `DELEGATION.md` §4 item 39.
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

import pytest

from aegis_ai.mind.desire import Desire
from aegis_ai.mind.emotion import Emotion
from aegis_ai.mind.goals import GoalManager
from aegis_ai.mind.identity import Identity
from aegis_ai.mind.layered_emotion import LayeredEmotion
from aegis_ai.mind.mood import Mood
from aegis_ai.mind.personality import Personality
from aegis_ai.mind.social_intelligence import SocialIntelligence

_AI_SERVER = Path(__file__).resolve().parents[1]
_SRC = _AI_SERVER / "src"
_MIND = _SRC / "aegis_ai" / "mind"

# (logger name, store class, class name) — the eight members of the family.
_FAMILY = [
    ("aegis_ai.mind.desire", Desire, "Desire"),
    ("aegis_ai.mind.emotion", Emotion, "Emotion"),
    ("aegis_ai.mind.goals", GoalManager, "GoalManager"),
    ("aegis_ai.mind.identity", Identity, "Identity"),
    ("aegis_ai.mind.layered_emotion", LayeredEmotion, "LayeredEmotion"),
    ("aegis_ai.mind.mood", Mood, "Mood"),
    ("aegis_ai.mind.personality", Personality, "Personality"),
    ("aegis_ai.mind.social_intelligence", SocialIntelligence, "SocialIntelligence"),
]
_FAMILY_IDS = [entry[2] for entry in _FAMILY]
_FAMILY_NAMES = {entry[2] for entry in _FAMILY}

# Measured 2026-10-04: the only family class built outside `mind/`.
_CONSTRUCTED_OUTSIDE_MIND = {"Identity"}


def _records(caplog: pytest.LogCaptureFixture, logger_name: str) -> list[logging.LogRecord]:
    return [record for record in caplog.records if record.name == logger_name]


def _warnings(
    caplog: pytest.LogCaptureFixture, logger_name: str
) -> list[logging.LogRecord]:
    return [
        record
        for record in _records(caplog, logger_name)
        if record.levelno >= logging.WARNING
    ]


def _state_file(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "state.jsonl"
    path.write_text(text, encoding="utf-8")
    return path


def _called_names(path: Path) -> set[str]:
    """Names/attributes that are *called* in `path`.

    Parsed, not grepped: a name inside a string literal or a docstring is not a
    call, which is the whole point of the liveness check below.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            names.add(func.id)
        elif isinstance(func, ast.Attribute):
            names.add(func.attr)
    return names


@pytest.mark.parametrize("logger_name,store,class_name", _FAMILY, ids=_FAMILY_IDS)
def test_a_corrupt_file_is_named(caplog, tmp_path, logger_name, store, class_name):
    """A corrupt file names the path and the exception, and still constructs."""
    path = _state_file(tmp_path, '{"a": 1\n')

    with caplog.at_level(logging.WARNING, logger=logger_name):
        store(path=str(path))  # must not raise

    warnings = _warnings(caplog, logger_name)
    assert len(warnings) == 1, (
        f"{class_name}._load swallowed a corrupt file without naming it"
    )
    message = warnings[0].getMessage()
    assert str(path) in message
    assert "JSONDecodeError" in message


@pytest.mark.parametrize("logger_name,store,class_name", _FAMILY, ids=_FAMILY_IDS)
def test_a_missing_file_stays_silent(caplog, tmp_path, logger_name, store, class_name):
    """Control: no file yet is a legitimate absence, not a failure."""
    path = tmp_path / "state.jsonl"  # never created

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        store(path=str(path))

    assert _records(caplog, logger_name) == []


@pytest.mark.parametrize("logger_name,store,class_name", _FAMILY, ids=_FAMILY_IDS)
def test_a_valid_file_stays_silent(caplog, tmp_path, logger_name, store, class_name):
    """Control: a readable file must not warn."""
    path = _state_file(tmp_path, "{}\n")

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        store(path=str(path))

    assert _records(caplog, logger_name) == []


@pytest.mark.parametrize("logger_name,store,class_name", _FAMILY, ids=_FAMILY_IDS)
def test_a_valid_json_line_that_is_not_an_object_raises(
    caplog, tmp_path, logger_name, store, class_name
):
    """The boundary of the family's silence: keyed on exception type, not on use.

    `123` is as unusable as `{"a": 1`, but `json.loads` accepts it, so the next
    line (`last.get(...)`) raises `AttributeError` — which the family does not
    catch. Fixed as current behaviour; see `DELEGATION.md` §4 item 38.
    """
    path = _state_file(tmp_path, "123\n")

    with caplog.at_level(logging.DEBUG, logger=logger_name):
        with pytest.raises(AttributeError):
            store(path=str(path))

    assert _records(caplog, logger_name) == []


def test_every_load_in_mind_names_its_failure():
    """Structural half of the claim: no `_load` in `mind/` is a bare `pass`."""
    silent: list[str] = []
    loads = 0
    for module in sorted(_MIND.glob("*.py")):
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) or node.name != "_load":
                continue
            loads += 1
            for handler in [n for n in ast.walk(node) if isinstance(n, ast.ExceptHandler)]:
                # A handler whose whole body is `pass` swallows the failure.
                # Do NOT filter out `ast.Expr` first — a bare `logger.warning(…)`
                # statement *is* an `ast.Expr`, so dropping those would flag the
                # named handlers as silent (it did, on the first run).
                if not handler.body or all(
                    isinstance(stmt, ast.Pass) for stmt in handler.body
                ):
                    silent.append(f"{module.name}:{handler.lineno}")

    assert silent == [], f"a `_load` still swallows its failure: {silent}"
    # Control: the scan actually found the family (a broken walk would give 0).
    assert loads == len(_FAMILY)


def test_only_identity_is_constructed_outside_mind():
    """The family's scope: measured by *calling*, not by importing.

    A pin on the split rather than on a hand-written list, so wiring one of the
    six unwired members shows up here instead of silently changing what "live"
    means. `AffectSystem` is asserted present as the positive control — it is
    what keeps `Mood`, `Personality` and `LayeredEmotion` reachable.
    """
    outside: set[str] = set()
    for module in _SRC.rglob("*.py"):
        if _MIND in module.parents:
            continue
        outside |= _called_names(module)

    assert "AffectSystem" in outside, "positive control: the scan found nothing"
    assert {name for name in _FAMILY_NAMES if name in outside} == (
        _CONSTRUCTED_OUTSIDE_MIND
    )
