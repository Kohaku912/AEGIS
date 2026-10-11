"""The resident support agent is declared three times and read by nothing (item 110).

The owner's mandate is AEGIS's *resident, proactive support* (「常駐されたユーザーの先回り
サポート」).  The switch that is supposed to carry it -- ``support_agent_enabled`` -- is
declared, shipped ``true``, documented as working, and **read by no line of code**.

Three declarations, zero readers:

* ``settings/models.py::AutonomousSettings`` declares ``support_agent_enabled: bool =
  Field(default=True)`` and the shipped ``config/settings.json`` sets it ``true``;
* ``interaction/router.py::InteractionRouter`` accepts a ``support_agent`` argument and
  stores it as ``self._support`` -- and never reads that attribute, and no call site ever
  passes the argument, so it is always ``None``;
* ``settings/store.py::SettingsStore``'s class docstring *uses* the field in a usage
  example (``settings.autonomous.support_agent_enabled = False``).

The docs promise behaviour: ``docs/settings.md`` ("Enable support agent"),
``docs/beta-runbook.md`` ("提案のみ、自動実行なし"), ``docs/operations.md`` (a snippet that
sets it).  None of it is backed by code.

**Why the detector is silent.**  ``test_ineffective_flags.py`` layer 1 answers one
question: *does the bare field name appear anywhere under ``src/`` outside its own
definition module?*  It says so itself -- "the reader scan is textual on the bare field
name".  The docstring's ``settings.autonomous.support_agent_enabled = False`` is exactly
such an appearance, so layer 1 calls the field **read**, the unread maps stay empty, and
the suite is green on a switch that does nothing.  The limitation the detector's own
docstring names is a *same-named field in an unrelated module*; this is a second, sharper
failure of the same scan -- a **docstring is not a reader**.

``_readers`` is imported from the detector rather than re-implemented.  A second scanner
would be a second definition of "read", and the two could disagree without either being
wrong.

**Nothing here is fixed by this file.**  Wiring the switch is a **behaviour change** --
it would give the support agent an on/off posture, and the router would begin handing
``self._support`` to the plan path -- so it is an owner decision, recorded in
``DELEGATION.md`` §4 item 110.  These tests are the record that must be *cleared* when
that decision is taken: each one fails the moment a real reader appears.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

from test_ineffective_flags import (
    _DEFINITION_MODULE,
    _log_only_readers,
    _readers,
    _real_readers,
    _recorded_unread,
    _scanned_fields,
)

_HERE = Path(__file__).resolve()
_AI_SERVER = _HERE.parents[1]
_SRC = _AI_SERVER / "src"

_FLAG = "support_agent_enabled"
_FIELD_KEY = "AutonomousSettings.support_agent_enabled"
_MODELS = _SRC / "aegis_ai" / "settings" / "models.py"
_STORE = _SRC / "aegis_ai" / "settings" / "store.py"
_ROUTER = _SRC / "aegis_ai" / "interaction" / "router.py"
_SHIPPED = _AI_SERVER / "config" / "settings.json"
_DOCS = _AI_SERVER.parent / "docs"

#: Settings fields whose layer-1 textual reader is not code at all: the only
#: non-definition occurrence is a docstring (``support_agent_enabled``) or a
#: module-path token in an import (``intake``).  Measured 2026-10-12 (item 110):
#: exactly two of the 70 scanned fields.  The gate's ``PrivacySettings.*`` flags
#: are *not* here -- the gate reads them by passing the field name as a string
#: (``self._privacy_setting("privacy", "web_search_allowed")``), which
#: ``_string_equal_readers`` recognises.
_TEXTUAL_ONLY_SETTINGS_FIELDS = frozenset(
    {
        "AEGISSettings.intake",
        "AutonomousSettings.support_agent_enabled",
    }
)

#: A field read *only* through the gate's string-keyed resolver, used as the
#: positive control for ``_string_equal_readers``: without it, a string-equal
#: reader that stopped being detected would make the bounded set above grow
#: silently.
_STRING_KEYED_CONTROL_FIELD = "web_search_allowed"


def _parse(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _docstring_lines(tree: ast.AST) -> set[int]:
    """Line numbers covered by a module/class/function docstring."""
    lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            body = getattr(node, "body", [])
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                doc = body[0]
                lines.update(range(doc.lineno, doc.end_lineno + 1))
    return lines


def _string_equal_readers(field: str) -> list[str]:
    """Modules holding a *non-docstring* string constant equal to ``field``.

    The gate reads its privacy flags this way: the field name is passed as a
    string (``self._privacy_setting("privacy", "web_search_allowed")``), so a
    string-equal constant is a real read.  A docstring that merely *mentions* the
    field is prose, not a read -- which is the whole defect this pin records.
    """
    found: list[str] = []
    for path in sorted(_SRC.rglob("*.py")):
        if path == _DEFINITION_MODULE or "__pycache__" in path.parts:
            continue
        tree = _parse(path)
        doc_lines = _docstring_lines(tree)
        if any(
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value == field
            and node.lineno not in doc_lines
            for node in ast.walk(tree)
        ):
            found.append(path.relative_to(_SRC).as_posix())
    return found


def _attribute_contexts(path: Path, attr: str) -> tuple[list[int], list[int]]:
    """(Store lines, Load lines) for ``.<attr>`` in ``path``."""
    stores: list[int] = []
    loads: list[int] = []
    for node in ast.walk(_parse(path)):
        if isinstance(node, ast.Attribute) and node.attr == attr:
            (stores if isinstance(node.ctx, ast.Store) else loads).append(node.lineno)
    return sorted(stores), sorted(loads)


def _router_call_keywords() -> list[tuple[str, set[str]]]:
    """(module, keyword names) for every ``InteractionRouter(...)`` call in ``src/``."""
    calls: list[tuple[str, set[str]]] = []
    for path in sorted(_SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for node in ast.walk(_parse(path)):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "InteractionRouter"
            ):
                calls.append(
                    (
                        path.relative_to(_SRC).as_posix(),
                        {kw.arg for kw in node.keywords if kw.arg},
                    )
                )
    return calls


# ── The flag exists, is shipped on, and is documented ─────────────────────────


def test_the_flag_is_declared_on_the_model_and_shipped_on():
    """Not chasing ghosts: the switch must still be declared and shipped ``true``."""
    from aegis_ai.settings.models import AutonomousSettings

    assert _FLAG in AutonomousSettings.model_fields, (
        f"AutonomousSettings no longer declares {_FLAG!r} -- delete this pin with a "
        "reason rather than leaving a vacuous one."
    )
    assert AutonomousSettings.model_fields[_FLAG].default is True, (
        f"{_FLAG!r} no longer defaults True; re-measure whether it is still the "
        "'resident support on by default' switch this pin records."
    )
    shipped = json.loads(_SHIPPED.read_text(encoding="utf-8"))["autonomous"]
    assert shipped.get(_FLAG) is True, (
        f"the shipped settings file no longer sets {_FLAG!r} true: {shipped.get(_FLAG)!r}"
    )


def test_the_docs_promise_the_switch_does_something():
    """A user can set it and the docs say it acts -- the promise nobody keeps."""
    settings_doc = (_DOCS / "settings.md").read_text(encoding="utf-8")
    assert _FLAG in settings_doc, (
        "docs/settings.md no longer documents the switch; if it was removed from the "
        "docs because it does nothing, remove it from the model too."
    )
    runbook = (_DOCS / "beta-runbook.md").read_text(encoding="utf-8")
    assert _FLAG in runbook, (
        "docs/beta-runbook.md no longer carries the switch -- if its row was dropped, "
        "shrink this pin and DELEGATION.md §4 item 110 together."
    )
    operations = (_DOCS / "operations.md").read_text(encoding="utf-8")
    assert _FLAG in operations, (
        "docs/operations.md no longer shows the switch being set."
    )


# ── No code reads it, and the detector is why nobody noticed ──────────────────


def test_no_code_reads_the_flag():
    """The property: no attribute read, no getattr, no string-keyed read."""
    assert _real_readers(_FLAG, definition_module=_DEFINITION_MODULE) == [], (
        f"{_FLAG!r} now has an attribute read -- this pin has done its job; wire the "
        "switch deliberately and clear DELEGATION.md §4 item 110."
    )
    assert _log_only_readers(_FLAG, definition_module=_DEFINITION_MODULE) == [], (
        f"{_FLAG!r} is now mentioned in a logging call. A log line is still not a read; "
        "but this pin's premise (it appears nowhere in code) has changed -- re-measure."
    )
    assert _string_equal_readers(_FLAG) == [], (
        f"{_FLAG!r} is now passed as a string constant (a string-keyed read). If that "
        "is a real reader, clear the record; if it is another docstring, it should not "
        "be a Constant outside a docstring -- investigate."
    )


def test_the_only_non_definition_occurrence_is_a_docstring():
    """The sole textual hit layer 1 sees is prose inside a class docstring."""
    assert _readers(_FLAG) == ["aegis_ai/settings/store.py"], (
        f"{_FLAG!r} is now referenced by {_readers(_FLAG)}; the docstring-only premise "
        "has changed -- re-measure before trusting this pin."
    )
    store_doc = _docstring_lines(_parse(_STORE))
    lines = [
        i
        for i, line in enumerate(_STORE.read_text(encoding="utf-8").splitlines(), start=1)
        if _FLAG in line
    ]
    assert lines, "the store no longer mentions the flag; this pin is now vacuous"
    assert all(line in store_doc for line in lines), (
        f"the occurrence of {_FLAG!r} in settings/store.py is no longer inside a "
        f"docstring (lines {lines}, docstring covers {sorted(store_doc)}). If it moved "
        "into code, the flag now has a reader -- update this pin and item 110."
    )


def test_the_detector_calls_the_flag_read():
    """Layer 1 sees a reader -- which is exactly why the suite is green.

    Asserts the *detector's own* answer, so this test documents the gap rather than
    guessing at it.  An empty list here would mean layer 1 already fails and this pin
    is redundant.
    """
    assert _readers(_FLAG), (
        f"'{_FLAG}' now has no reader at all -- layer 1 of test_ineffective_flags will "
        "already be failing. Record it in _UNOWNED_DEBT and delete this pin's entry."
    )


def test_the_textual_only_settings_fields_are_bounded():
    """The population of fields layer 1 calls read on prose alone, pinned and bounded.

    Adding a field whose only mention is a docstring or a module-path token fails
    here -- which is the moment a human must decide, instead of shipping a dead flag
    unseen.  The control half proves the rule is not vacuous: a field the gate reads
    by string must be recognised as read.
    """
    assert _string_equal_readers(_STRING_KEYED_CONTROL_FIELD), (
        f"the control '{_STRING_KEYED_CONTROL_FIELD}' is no longer recognised as a "
        "string-keyed read; _string_equal_readers is broken and the bounded set below "
        "would silently grow. Fix the helper before trusting the assertion."
    )
    bounded = {
        key
        for key in _scanned_fields()
        if _readers(key.split(".", 1)[1])
        and not _real_readers(key.split(".", 1)[1], definition_module=_DEFINITION_MODULE)
        and not _log_only_readers(
            key.split(".", 1)[1], definition_module=_DEFINITION_MODULE
        )
        and not _string_equal_readers(key.split(".", 1)[1])
    }
    assert bounded == set(_TEXTUAL_ONLY_SETTINGS_FIELDS), (
        f"unrecorded: {sorted(bounded - set(_TEXTUAL_ONLY_SETTINGS_FIELDS))}. "
        f"recorded but now really read: "
        f"{sorted(set(_TEXTUAL_ONLY_SETTINGS_FIELDS) - bounded)}."
    )


def test_the_detectors_maps_do_not_excuse_the_flag():
    """The gap is the detector's silence, not an entry in its unread maps.

    ``_UNOWNED_DEBT``/``_INTENTIONALLY_UNREAD`` mean "deliberately unread with a
    reason".  This switch is meant to be *read* and is dead only because nobody wired
    it; recording it there would quiet the suite without fixing anything.
    """
    assert _FIELD_KEY not in set(_recorded_unread()), (
        f"{_FIELD_KEY} was added to the detector's unread maps. Keep the record here "
        "and in DELEGATION.md §4 item 110 instead."
    )


# ── The router half: the parameter is stored and never read ───────────────────


def test_the_router_stores_the_support_agent_and_never_reads_it():
    """``self._support = support_agent`` is a Store; ``self._support`` is never Loaded."""
    stores, loads = _attribute_contexts(_ROUTER, "_support")
    assert stores, (
        "the router no longer assigns self._support -- the parameter may have been "
        "renamed; re-derive this pin."
    )
    assert loads == [], (
        f"self._support is now read at lines {loads}. That is the live reader this pin "
        "was waiting for -- clear the record (this file and DELEGATION.md §4 item 110) "
        "and update the docs."
    )


def test_no_call_site_passes_a_support_agent():
    """Every ``InteractionRouter(...)`` is built without ``support_agent``."""
    calls = _router_call_keywords()
    assert calls, "no InteractionRouter(...) call was found; this pin is now vacuous"
    offenders = sorted(module for module, kws in calls if "support_agent" in kws)
    assert offenders == [], (
        f"a call site now passes support_agent: {offenders}. If the support agent was "
        "wired deliberately, clear this record; if it is still None everywhere, remove "
        "the keyword again."
    )
