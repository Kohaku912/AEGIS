"""Seven notification settings that the ineffective-flag detector calls *read*.

``tests/test_ineffective_flags.py`` layer 1 answers one question: *does the bare
field name appear anywhere under ``src/`` outside its own definition module?*  It
says so itself — "the reader scan is textual on the bare field name, so a field
whose name also appears in an unrelated module reads as 'read'."  The limitation
it names is a *same-named field in an unrelated module*.

This module records a second, sharper failure of the same scan: a reference
**inside code the runtime never executes** also counts as a reader.  All seven
``NotificationSettings`` fields are referenced — by exactly two methods,
``NotificationPreferences._load_from_settings`` and
``QuietHoursManager._load_from_settings`` — and ``runtime.py`` constructs neither
class, nor the ``NotificationRouter`` that owns them.  So layer 1 reports every
one of the seven as read, the unread maps stay empty, and the detector is green
on seven flags that no live path consults.

The class-level fact is already recorded (`docs/feature-catalog.md` §8 lists
``NotificationRouter`` and all channels as 宣言のみ, and §7 says ``send()`` does
not fan out).  What was *not* recorded is the settings-level consequence: the
user can set these seven in ``config/settings.json`` or the dashboard, they are
documented in ``docs/settings.md`` and ``docs/notification-gateway.md`` as
working, and nothing on the live path reads them.

Three layers, in the order that matters:

* **The readers work** (``test_the_reader_code_works_when_it_is_given_a_store``).
  Without this control the rest is worthless: a pin that only asserts "nothing
  reads the field" passes just as happily when the reader is *broken*.  This
  control builds each class with a store and watches the setting take effect, so
  the defect measured here is the *wiring*, not the reader.
* **The scan can tell live from dead** (``test_the_scan_can_tell_a_live_reader_...``).
  The second control: a field with a genuinely reachable reader must *not* land
  in the dead set, or the property below is vacuous.
* **The wiring does not exist** (the remaining tests).  ``runtime.py`` builds
  ``NotificationManager(event_manager=...)``; nothing under ``src/`` constructs
  the three classes outside ``router.py`` itself.

Reads are attributed to the **innermost enclosing class.method**, not the file
(see ``aegis-pin-a-dead-surface`` §"a reader inside dead code still counts").
A file-level scan would stay green if someone added a read of one of these fields
to a *live* method in one of the same two files.  Only ``Load``-context attribute
reads count, so the declaration in ``settings/models.py`` is not a read.

``_readers`` is imported from the detector rather than re-implemented.  A second
scanner would be a second definition of "read", and the two could disagree
without either being wrong.

Nothing here is fixed by this file.  Wiring the router is a **behaviour change**
— quiet hours would begin deferring, and the external channels would begin
attempting sends (behind the egress gate) — so it is an owner decision, recorded
in ``DELEGATION.md`` §4 item 35.  These tests are the record that must be
*cleared* when that decision is taken: each one fails the moment the wiring
appears.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

# The detector's own scan primitive and its recorded-unread maps. Imported, not
# copied: "read" must mean one thing in this suite.
from test_ineffective_flags import _readers, _recorded_unread

_SRC = Path(__file__).resolve().parents[1] / "src"
_RUNTIME = _SRC / "aegis_ai" / "runtime.py"

#: The two methods that own every reader of the seven fields, and the only two
#: modules allowed to reference them. Both classes are constructed nowhere but
#: ``router.py``, which is itself constructed nowhere.
_DEAD_READER_MODULES = frozenset(
    {
        "aegis_ai/notification/preferences.py",
        "aegis_ai/notification/quiet_hours.py",
    }
)

#: ``class.method`` — the innermost enclosing scope a read may sit in.
_DEAD_READ_SITES = frozenset(
    {
        "NotificationPreferences._load_from_settings",
        "QuietHoursManager._load_from_settings",
    }
)

#: field name → the module that reads it. Seven fields, two files.
_FIELD_READERS: dict[str, str] = {
    "approval_notification_enabled": "aegis_ai/notification/preferences.py",
    "support_suggestions_enabled": "aegis_ai/notification/preferences.py",
    "daily_briefing_notification": "aegis_ai/notification/preferences.py",
    "error_notification": "aegis_ai/notification/preferences.py",
    "quiet_hours_enabled": "aegis_ai/notification/quiet_hours.py",
    "quiet_hours_start": "aegis_ai/notification/quiet_hours.py",
    "quiet_hours_end": "aegis_ai/notification/quiet_hours.py",
}

#: A field read by *live* methods, used as the scan's positive control.
#: ``LLMRouter`` is constructed at ``runtime.py:939``.
_LIVE_CONTROL_FIELD = "external_llm_allowed"

#: The exact read sites the control requires. Naming them — rather than merely
#: asserting "something outside the dead set" — is what gives the control teeth:
#: an earlier draft asserted only the latter, and a mutation that rewrote *one* of
#: the two reads as ``getattr(..., "external_llm_allowed")`` survived it, because
#: the other read still satisfied the loose condition. If one of these methods is
#: renamed, update this tuple; do not relax the assertion.
_LIVE_CONTROL_SITES = frozenset(
    {
        ("aegis_ai/llm/factory.py", "create_llm_provider_from_settings"),
        ("aegis_ai/llm/router.py", "LLMRouter._select_provider"),
    }
)


def _read_sites(field: str) -> set[tuple[str, str]]:
    """``(module, innermost class.method)`` for every ``Load``-context read.

    ``Load`` context only, so a field *declaration* is not a read.  Scope, not
    file: a read added to a live method in one of the same two files must move
    the answer.
    """
    sites: set[tuple[str, str]] = set()

    def visit(node: ast.AST, scope: str, module: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                visit(child, f"{scope}.{child.name}", module)
                continue
            if (
                isinstance(child, ast.Attribute)
                and child.attr == field
                and isinstance(child.ctx, ast.Load)
            ):
                sites.add((module, scope.lstrip(".") or "<module>"))
            visit(child, scope, module)

    for path in sorted(_SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        module = path.relative_to(_SRC).as_posix()
        if module == "aegis_ai/settings/models.py":  # the declaration
            continue
        visit(ast.parse(path.read_text(encoding="utf-8")), "", module)
    return sites


def _constructed_classes(path: Path) -> set[str]:
    """Names called as constructors in ``path``.

    ``ast``, not text: a class named in a comment or a docstring is not an
    invocation, and ``router.py``'s own docstring names ``NotificationRouter``.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    called: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                called.add(func.id)
            elif isinstance(func, ast.Attribute):
                called.add(func.attr)
    return called


def _call_keywords(path: Path, class_name: str) -> list[set[str]]:
    """Keyword names of every ``class_name(...)`` call in ``path``."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    keywords: list[set[str]] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == class_name
        ):
            keywords.append({kw.arg for kw in node.keywords if kw.arg})
    return keywords


class _Store:
    """A settings store whose ``.get()`` returns a real ``AEGISSettings``.

    The *store* is a double; the settings object is the production model, so the
    reader is exercised against the real field names and real pydantic defaults.
    """

    def __init__(self, **notifications: object) -> None:
        from aegis_ai.settings.models import AEGISSettings, NotificationSettings

        self._settings = AEGISSettings(
            notifications=NotificationSettings(**notifications)
        )

    def get(self):
        return self._settings


# ── The fields exist, and a user can set them ─────────────────────────────────


def test_the_seven_fields_are_on_the_settings_model():
    """Not chasing ghosts: the model must still declare exactly these seven."""
    from aegis_ai.settings.models import NotificationSettings

    declared = set(NotificationSettings.model_fields)
    assert declared == set(_FIELD_READERS), (
        "the notification settings surface changed. If a field was added, decide "
        "whether it is read on a live path and extend this pin; if one was "
        "removed, shrink it. Either way the count below is a claim about the code."
    )


def test_the_fields_are_shipped_and_documented_as_working():
    """A user can set them and the docs say they do something.

    This is the "promise nobody keeps" shape the detector exists to catch: the
    field is in the shipped settings file, it is described in the settings
    reference, and no live path reads it.
    """
    import json

    shipped = json.loads(
        (_SRC.parent / "config" / "settings.json").read_text(encoding="utf-8")
    )["notifications"]
    missing = sorted(set(_FIELD_READERS) - set(shipped))
    assert missing == [], f"the shipped settings file no longer carries {missing}"

    settings_doc = (_SRC.parent.parent / "docs" / "settings.md").read_text(
        encoding="utf-8"
    )
    for field in _FIELD_READERS:
        assert field in settings_doc, (
            f"docs/settings.md no longer documents {field}; if it was removed "
            f"from the docs because it does nothing, remove it from the model too"
        )


# ── The controls ──────────────────────────────────────────────────────────────


def test_the_reader_code_works_when_it_is_given_a_store():
    """Control 1: the reader code is correct.

    Both classes *do* honour the settings when handed a store. So the defect
    measured below cannot be "the reader is broken" — it is that no live path
    ever hands them one. Delete either half of this and the pin would pass on a
    broken reader.
    """
    from aegis_ai.notification.models import NotificationType
    from aegis_ai.notification.preferences import NotificationPreferences
    from aegis_ai.notification.quiet_hours import QuietHoursManager

    off = NotificationPreferences(
        settings_store=_Store(approval_notification_enabled=False)
    )
    on = NotificationPreferences(settings_store=_Store())
    assert off.is_type_enabled(NotificationType.APPROVAL_REQUIRED) is False
    assert on.is_type_enabled(NotificationType.APPROVAL_REQUIRED) is True

    # A whole-day window so the assertion does not depend on the wall clock.
    quiet = QuietHoursManager(
        settings_store=_Store(
            quiet_hours_enabled=True, quiet_hours_start="00:00", quiet_hours_end="23:59"
        )
    )
    assert quiet.is_quiet() is True


def test_the_scan_can_tell_a_live_reader_from_a_dead_one():
    """Control 2: the read-site scan is not vacuous, and it attributes scope.

    Two halves. Non-vacuity: a field read by a reachable method must produce
    read sites at all. Attribution: those sites must be the *specific* live
    methods — not merely "somewhere other than the dead set", which a broken
    scope attribution (everything landing in ``<module>``) would also satisfy.
    """
    live = _read_sites(_LIVE_CONTROL_FIELD)
    assert live, (
        f"the scan found no direct read of '{_LIVE_CONTROL_FIELD}'. Either the "
        f"field is gone, or it is now read only through getattr() — pick another "
        f"live control; do not weaken this test."
    )
    missing = sorted(_LIVE_CONTROL_SITES - live)
    assert missing == [], (
        f"the scan did not attribute '{_LIVE_CONTROL_FIELD}' to {missing}; it found "
        f"{sorted(live)}. If those methods were renamed, update _LIVE_CONTROL_SITES; "
        f"if the read moved to getattr(), pick another live control."
    )
    assert {scope for _, scope in live} - _DEAD_READ_SITES, (
        f"'{_LIVE_CONTROL_FIELD}' reads only appear inside the dead scopes "
        f"{_DEAD_READ_SITES}, so this control proves nothing about attribution"
    )


def test_the_router_ignores_the_setting_because_it_passes_no_store():
    """The live construction — no store — cannot see the user's window.

    ``QuietHoursManager()`` is exactly what ``NotificationRouter.__init__``
    builds. With no store, ``_enabled`` keeps its ``False`` default, so
    ``is_quiet()`` is ``False`` no matter what the user configured. This is the
    same object as control 1, differing only in the argument.
    """
    from aegis_ai.notification.quiet_hours import QuietHoursManager

    as_production_builds_it = QuietHoursManager()
    assert as_production_builds_it.is_quiet() is False


# ── The wiring that does not exist ────────────────────────────────────────────


@pytest.mark.parametrize("field,reader", sorted(_FIELD_READERS.items()))
def test_the_detector_calls_the_field_read(field: str, reader: str):
    """Layer 1 sees a reader — which is why the detector is green.

    Asserts the *detector's own* answer, so this test documents the gap rather
    than guessing at it. An empty list here would mean layer 1 already fails and
    this pin is redundant.
    """
    readers = _readers(field)
    assert readers, (
        f"'{field}' now has no reader at all — layer 1 of test_ineffective_flags "
        f"will already be failing. Record it in _UNOWNED_DEBT and delete this pin's "
        f"entry."
    )
    assert readers == [reader], (
        f"'{field}' is now read by {readers}, not only {reader}. If a *live* path "
        f"reads it, this pin has done its job: remove the entry from _FIELD_READERS "
        f"and from DELEGATION.md §4 item 35."
    )


@pytest.mark.parametrize("field", sorted(_FIELD_READERS))
def test_every_reader_of_the_field_is_dead_code(field: str):
    """The property: *every* read of these fields sits in a dead method.

    Scoped to ``class.method``, not the file. A read added to a live method in
    one of the same two modules fails this — which a file-level check would miss.
    """
    sites = _read_sites(field)
    assert sites, f"'{field}' now has no Load-context read at all"
    offenders = sorted(
        (module, scope)
        for module, scope in sites
        if module not in _DEAD_READER_MODULES or scope not in _DEAD_READ_SITES
    )
    assert offenders == [], (
        f"'{field}' is now read outside the two unwired loaders: {offenders}. If "
        f"that is the live reader this pin was waiting for, clear the record "
        f"(_FIELD_READERS, DELEGATION.md §4 item 35) and update the docs; if a "
        f"reference merely moved inside dead code, widen _DEAD_READ_SITES."
    )


def test_the_detectors_maps_do_not_excuse_these_fields():
    """The gap is the detector's silence, not an entry in its maps.

    If one of these fields is added to ``_UNOWNED_DEBT``/``_INTENTIONALLY_UNREAD``
    the detector would start *excusing* it — but the map's contract is "deliberately
    unread", and these are intended to be read. Adding one is a decision to make
    here, not a way to quiet the suite.
    """
    recorded = set(_recorded_unread())
    overlap = sorted(set(_FIELD_READERS) & recorded)
    assert overlap == [], (
        f"{overlap} were added to the detector's unread maps. Those maps mean "
        f"'deliberately unread with a reason'; these fields are meant to be read and "
        f"are dead only because nothing constructs their readers. Keep the record in "
        f"this file and DELEGATION.md §4 item 35 instead."
    )


def test_nothing_under_src_constructs_the_dead_family():
    """``router.py`` builds the two readers; nothing builds ``router.py``.

    Measured with ``ast`` over every module, so a name in a comment or docstring
    does not count. ``router.py`` itself is the one legitimate site (lines 67-68),
    and it is unreachable — ``runtime.py`` constructs only ``NotificationManager``.
    """
    builders: dict[str, list[str]] = {}
    for path in sorted(_SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        called = _constructed_classes(path)
        for name in ("NotificationRouter", "NotificationPreferences", "QuietHoursManager"):
            if name in called:
                builders.setdefault(name, []).append(path.relative_to(_SRC).as_posix())

    assert builders == {
        "NotificationPreferences": ["aegis_ai/notification/router.py"],
        "QuietHoursManager": ["aegis_ai/notification/router.py"],
    }, (
        f"the construction sites changed: {builders}. Expected exactly router.py to "
        f"build the two readers and *nothing* to build NotificationRouter — "
        f"runtime.py builds only NotificationManager(event_manager=...)."
    )


def test_runtime_builds_the_manager_without_a_router():
    """The last link: even the manager gets no router, so ``send()`` cannot fan out."""
    keywords = _call_keywords(_RUNTIME, "NotificationManager")
    assert keywords, "runtime.py no longer constructs NotificationManager at all"
    assert all("notification_router" not in kw for kw in keywords), (
        f"runtime.py now passes notification_router to NotificationManager: {keywords}. "
        f"If the router was wired deliberately, clear this record — and expect "
        f"quiet hours and the external channels to start acting on settings."
    )


def test_the_live_manager_would_report_sent_without_delivering():
    """A latent lie, recorded rather than fixed.

    With no router, ``send()`` takes the ``else`` branch and stamps the
    notification ``SENT`` although no channel received it. It is *latent* —
    production only calls ``create_notification``/``dismiss``, never ``send()``
    (``presentation/manager.py`` creates and stores the id). Pinned so that
    either resolution forces a visit here: wiring a router makes the stamp true,
    removing ``send()`` removes the lie.
    """
    from aegis_ai.notification.notification_manager import NotificationManager

    manager = NotificationManager()  # exactly how runtime.py builds it
    created = manager.create_notification(title="t", body="b")
    sent = manager.send(created["notification_id"])

    assert sent is not None
    assert sent["status"] == "sent", (
        "send() with no router no longer reports SENT. If it now reports FAILED, "
        "update this record — that is the honest outcome."
    )
    assert manager._router is None, (
        "the manager gained a router; the SENT above is now backed by a real send. "
        "Re-measure whether the notification settings are still unread."
    )
