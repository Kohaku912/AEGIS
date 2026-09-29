"""The settings UI has no contract with the settings schema (B-21).

`web-ui/src/pages/Settings.tsx::editableSettings` **discovers** the controls it renders
from the `GET /api/settings` payload (`AEGISSettings.model_dump()`): every boolean /
number / string field in every section, with a hand-written `preferred` list sorted
first, a `result.length >= 24` cutoff for unpreferred fields, and a `.slice(0, 32)`.

Because it discovers rather than lists, the set of controls it *offers* can never fall
out of date with the schema — there is no inventory in the UI to go stale. Measured: 80
fields are in the payload, **26 are rendered** as controls (the cutoff binds before the
slice does), and **10 of those are fields nothing in the backend reads** — so the
dashboard offers the user ten switches that change nothing. The `_UNOWNED_DEBT` entry for
`sensitive_data_storage_enabled` already says the quiet part: *"a privacy switch that
does nothing is worse than no switch."* This file is that debt seen from the user's side.

What discovery does **not** fix is the coupling. The unread fields are recorded in
`tests/test_ineffective_flags.py`; nothing tied that record to what the dashboard offers.
So the record could shrink (a field wired up, or deleted) while the UI kept offering its
control, or grow, and no test would notice. That tie is what this file adds — and it
binds in a direction worth being precise about: a *newly declared* unread field does not
by itself move the set below, because the set is an intersection with a static record. It
is `test_ineffective_flags.py` that catches the new field; this file fails once the
record is updated and the two disagree. The exception is the interesting one — a field
declared early enough **pushes another dead field out of the rendered window**, so the
visible set changes without anyone touching the record.

The reverse direction was wrong too: **5 of the 15 `preferred` keys named no settings
field at all** (`display_privacy_mode`, `notifications_enabled`, `daily_budget_usd`,
`monthly_budget_usd`, `memory_budget_tokens` — the last is a `context_builder` runtime
attribute, not a setting). The list that says "always show these first" was spending a
third of its entries on controls that cannot exist. A hand-maintained list is the defect;
here it was a hand-maintained list that was **unverifiable**, because nothing compared it
to the schema. That half is fixed now — the five were pruned (register A-10) and
`test_every_preferred_key_names_a_real_settings_field` keeps them out — but the
unverifiability, not the five keys, is what this file is about.

**The algorithm is transcribed, not imported** — a Python test cannot execute TypeScript.
Two things keep the transcription honest: the constants are **parsed out of the TS** (so a
change there moves this test), and the shape of the loop is asserted (so a rewrite that
invalidates the transcription fails rather than silently measuring the wrong thing).

The half of this file that is a **record** is the 10 dead controls: that is the pending B-6
owner call (wire the field or delete it), so all this file does is make their visibility
impossible to change silently. The `preferred` list was the other half, and it is a
**regression pin** now: *which* controls deserve prominence is still a UI judgement, but
every entry must name a real field. Pruning the five that could not was
behaviour-preserving — an unmatched key is never consulted, because the set is only ever
queried with payload keys — and is recorded as **A-10** in `PROJECT_STATUS_REVIEW.md` §0.2.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest
from pydantic import BaseModel

from aegis_ai.settings.models import AEGISSettings

_REPO = Path(__file__).resolve().parents[2]
_UI = _REPO / "web-ui" / "src" / "pages" / "Settings.tsx"
_DEBT_SOURCE = Path(__file__).resolve().parent / "test_ineffective_flags.py"

#: `preferred` keys that name no settings field. **Empty since A-10 (2026-09-29) pruned
#: the five that never could match**: `display_privacy_mode`, `notifications_enabled`,
#: `daily_budget_usd` and `monthly_budget_usd` existed nowhere but that list, and
#: `memory_budget_tokens` is a `context_builder` runtime attribute, not a settings field.
#: Equality-checked, so re-introducing one fails here — and so does emptying the list,
#: which would make `unmatched == ∅` true for the wrong reason (see the test).
_RECORDED_NONEXISTENT_PREFERRED: frozenset[str] = frozenset()

#: Controls the UI renders for fields recorded as unread. Equality-checked in both
#: directions, so wiring a field up (or adding a new dead one) fails until this moves.
_RECORDED_DEAD_CONTROLS: frozenset[str] = frozenset(
    {
        "autonomous.browser_exploration_budget_per_day",
        "autonomous.daily_briefing_enabled",
        "autonomous.max_actions_per_hour",
        "autonomous.max_autonomous_runs_per_day",
        "autonomous.normal_interruption_budget_per_hour",
        "autonomous.research_watch_enabled",
        "autonomous.self_dev_proposal_enabled",
        "autonomous.social_poll_interval_seconds",
        "servers.health_check_interval_seconds",
        "servers.reconnect_policy",
    }
)

#: The shape the transcription depends on. If the TS is rewritten, these must be revisited.
_REQUIRED_TS_SHAPE: tuple[str, ...] = (
    "const preferred = new Set([",
    "Object.entries(settings)",
    "Object.entries(rawSection",
    'typeof value === "boolean"',
    'typeof value === "number"',
    'typeof value === "string"',
    "result.length >=",
    "result.sort(",
    ".slice(0,",
)


def _ui_source() -> str:
    assert _UI.exists(), (
        f"{_UI} is missing. This test reads the settings page to check the controls it "
        "offers; without it the check is vacuous, so it fails rather than skipping."
    )
    return _UI.read_text(encoding="utf-8")


def _preferred_keys(text: str) -> list[str]:
    match = re.search(r"const preferred = new Set\(\[(.*?)\]\);", text, re.S)
    assert match, "could not find the `preferred` list in Settings.tsx"
    return re.findall(r'"([^"]+)"', match.group(1))


def _caps(text: str) -> tuple[int, int]:
    cutoff_line = next((line for line in text.splitlines() if "result.length >=" in line), None)
    sort_line = next((line for line in text.splitlines() if "result.sort(" in line), None)
    assert cutoff_line and sort_line, "could not find the cutoff / slice lines"
    cutoff = int(re.search(r"result\.length >= (\d+)", cutoff_line).group(1))
    limit = int(re.search(r"slice\(0, (\d+)\)", sort_line).group(1))
    return cutoff, limit


def _settings_fields() -> set[str]:
    """Every settings field as ``section.field``, from the model's own dump."""
    payload = AEGISSettings().model_dump()
    return {f"{section}.{key}" for section, raw in payload.items() if isinstance(raw, dict) for key in raw}


def _rendered(payload: dict, *, preferred: set[str], cutoff: int, limit: int) -> list[str]:
    """Transcribe ``editableSettings``: discovery, preference sort, cutoff, slice.

    ``Object.entries`` order is the payload's insertion order, which for
    ``model_dump()`` is the model's field declaration order — that is why the visible set
    depends on where a field is declared, not on how important it is.
    """
    result: list[str] = []
    for section, raw in payload.items():
        if not isinstance(raw, dict):
            continue
        for key, value in raw.items():
            if key not in preferred and len(result) >= cutoff:
                continue
            if isinstance(value, (bool, int, float, str)):
                result.append(f"{section}.{key}")
    result.sort(key=lambda key: 0 if key.split(".", 1)[1] in preferred else 1)
    return result[:limit]


def _rendered_controls() -> list[str]:
    preferred = set(_preferred_keys(_ui_source()))
    cutoff, limit = _caps(_ui_source())
    return _rendered(AEGISSettings().model_dump(), preferred=preferred, cutoff=cutoff, limit=limit)


def _section_of_settings_class() -> dict[str, str]:
    """``AutonomousSettings`` → ``autonomous``, derived from the model's annotations.

    The debt record in ``test_ineffective_flags.py`` names fields by **class**
    (``AutonomousSettings.max_actions_per_hour``); the UI payload names them by
    **section** (``autonomous.max_actions_per_hour``). Intersecting the two without
    translating yields the empty set, which passes every ``==`` assertion written
    against it. The translation is derived here rather than hand-copied, so renaming a
    section moves this too.
    """
    mapping: dict[str, str] = {}
    for section, field_info in AEGISSettings.model_fields.items():
        annotation = field_info.annotation
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            mapping[annotation.__name__] = section
    return mapping


def _recorded_unread() -> set[str]:
    """The unread maps from ``test_ineffective_flags.py``, as ``section.field``.

    Parsed rather than imported so this file cannot be defeated by an import-order or
    collection change in the detector, and so the coupling is to the *record*.

    The maps are **annotated** assignments (``_UNOWNED_DEBT: dict[str, str] = {...}``),
    so an ``ast.Assign``-only scan does not see them: it returns the empty set and every
    assertion built on it passes vacuously. Both node kinds are handled, and the count is
    asserted by ``test_the_debt_record_is_readable`` so this cannot regress silently.
    """
    tree = ast.parse(_DEBT_SOURCE.read_text(encoding="utf-8"))
    to_section = _section_of_settings_class()
    keys: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            targets, value = [node.target], node.value
        elif isinstance(node, ast.Assign):
            targets, value = list(node.targets), node.value
        else:
            continue
        names = {t.id for t in targets if isinstance(t, ast.Name)}
        if not (names & {"_UNOWNED_DEBT", "_INTENTIONALLY_UNREAD"}):
            continue
        assert isinstance(value, ast.Dict), f"{names} is no longer a dict literal"
        for key in value.keys:
            assert isinstance(key, ast.Constant) and isinstance(key.value, str)
            cls, _, field = key.value.partition(".")
            assert cls in to_section, (
                f"{key.value!r} names a settings class {cls!r} that is not a section of "
                f"AEGISSettings ({sorted(to_section)}). The record and the model have "
                "diverged — the class was renamed, or the record is stale."
            )
            keys.add(f"{to_section[cls]}.{field}")
    return keys


# ── Guards on the transcription ───────────────────────────────────────────────


def test_the_transcription_still_matches_the_ui_source() -> None:
    """A rewrite of `editableSettings` must fail here, not silently measure nothing."""
    text = _ui_source()
    missing = [shape for shape in _REQUIRED_TS_SHAPE if shape not in text]
    assert missing == [], (
        f"Settings.tsx no longer contains {missing}. The Python transcription in this "
        "file replicates that algorithm; re-derive it before trusting any assertion here."
    )


def test_the_scan_actually_sees_controls_and_preferences() -> None:
    """Non-vacuity: the parse found a real preference list and a real rendered set."""
    preferred = _preferred_keys(_ui_source())
    assert len(preferred) >= 10, f"only {len(preferred)} preferred keys parsed: {preferred}"
    rendered = _rendered_controls()
    assert len(rendered) >= 10, f"only {len(rendered)} controls rendered: {rendered}"
    assert "privacy.clipboard_capture_enabled" in rendered, (
        "a known live control is missing — the payload or the transcription is wrong"
    )
    cutoff, limit = _caps(_ui_source())
    assert 0 < cutoff <= limit, f"cutoff {cutoff} / limit {limit} look wrong"


def test_the_debt_record_is_readable() -> None:
    """The coupling below is to `test_ineffective_flags.py`'s maps, so they must parse.

    This is the non-vacuity guard for the *whole* file: the maps are annotated
    assignments, so a scan that only understands `ast.Assign` returns the empty set and
    `test_the_ui_offers_a_control_for_every_unread_field_it_can_fit` would then assert
    that the empty set equals the record — which is not the same claim at all.
    """
    recorded = _recorded_unread()
    assert len(recorded) >= 20, (
        f"only {len(recorded)} unread entries parsed: {sorted(recorded)}. The maps are "
        "annotated assignments (`_UNOWNED_DEBT: dict[str, str] = {...}`); a bare-"
        "`ast.Assign` scan misses them and silently reports nothing unread."
    )
    assert "autonomous.max_actions_per_hour" in recorded, (
        "the record parsed but not in the expected shape — the class→section "
        f"translation produced {sorted(recorded)[:5]}…"
    )


# ── Direction 1: the UI renders controls for fields nothing reads ─────────────


def test_the_ui_offers_a_control_for_every_unread_field_it_can_fit() -> None:
    """The user-facing half of the unread-settings debt.

    Equality both ways, so the record here and the record in
    `test_ineffective_flags.py` have to move together:

    * the record grows (a field is found unowned) and the field is rendered → fails;
    * the record shrinks (a field is wired up or deleted) and the field *was* rendered
      → fails, because the UI is still offering the control;
    * a field is declared early enough to push a dead field out of the rendered window
      → fails, with nobody having touched either record.

    What it deliberately does not assert is that a new unread field *arrives* here: the
    intersection is with a static record, so a new field is caught by
    `test_ineffective_flags.py` first. This file's job is that the two cannot disagree.
    """
    rendered = set(_rendered_controls())
    dead = rendered & _recorded_unread()

    assert dead == set(_RECORDED_DEAD_CONTROLS), (
        "the set of dead controls the settings page offers changed.\n"
        f"  newly offered : {sorted(dead - _RECORDED_DEAD_CONTROLS)}\n"
        f"  no longer offered : {sorted(_RECORDED_DEAD_CONTROLS - dead)}\n"
        "A control the user can move that changes nothing is worse than a missing one. "
        "If a field was wired up, drop it from _UNOWNED_DEBT *and* from this set."
    )
    assert dead, (
        "no dead control is rendered — either the debt was cleared (then delete this "
        "test and its record) or the transcription stopped working"
    )


# ── Direction 2: the preference list names fields that do not exist ───────────


def test_every_preferred_key_names_a_real_settings_field() -> None:
    """`preferred` says "show these first"; every entry must name a field that exists.

    The list was pruned to its ten live entries on 2026-09-29 (register A-10). Which
    controls deserve prominence is still a UI judgement, so this pins the *claim* and not
    the content: add a key freely, but it has to name a real settings field.

    The second assertion is the non-vacuity guard. `unmatched == ∅` is equally true of an
    emptied list — and an empty `preferred` would quietly disable the preference sort,
    which is the opposite of the defect this file records. The `len(preferred) >= 10`
    floor in `test_the_scan_actually_sees_controls_and_preferences` covers the rest of
    that direction.
    """
    preferred = set(_preferred_keys(_ui_source()))
    fields = {key.split(".", 1)[1] for key in _settings_fields()}
    unmatched = preferred - fields

    assert unmatched == set(_RECORDED_NONEXISTENT_PREFERRED), (
        "the `preferred` list's unmatched keys changed.\n"
        f"  newly unmatched : {sorted(unmatched - _RECORDED_NONEXISTENT_PREFERRED)}\n"
        f"  now matching : {sorted(_RECORDED_NONEXISTENT_PREFERRED - unmatched)}\n"
        "A key that names no field is spending a preference slot on a control that cannot "
        "exist: `Set.has` returns false for it and nothing happens. Point it at a real "
        "field, or delete it."
    )
    assert preferred, (
        "the `preferred` list is empty — that is a deletion, not a repair, and it makes "
        "the assertion above vacuous"
    )


# ── The fragility the discovery introduces ───────────────────────────────────


def test_a_new_field_is_rendered_only_if_it_is_declared_early_enough() -> None:
    """Why the visible set is an accident of declaration order, not of importance.

    Demonstrated on the payload rather than by editing the model: the same synthetic
    field is visible when it sits in an early section and invisible when it sits in a
    late one, because the cutoff counts *rendered* entries, not declared ones.

    Measured, the window is "the first `cutoff` rendered entries in declaration order,
    plus any preferred field anywhere". So declaring fields early evicts the tail of that
    window — and a *dead* field can leave the visible set without anyone touching either
    record. That is why `test_the_ui_offers_a_control_for_every_unread_field_it_can_fit`
    can fail on a model change that never mentions an unowned field.
    """
    text = _ui_source()
    preferred = set(_preferred_keys(text))
    cutoff, limit = _caps(text)
    payload = AEGISSettings().model_dump()

    sections = [name for name, raw in payload.items() if isinstance(raw, dict)]
    assert len(sections) >= 2, f"the payload has {len(sections)} sections; need two"
    early, late = sections[0], sections[-1]
    # `version` is a scalar top-level entry (`"1.0.0"`), not a section: the TS skips it
    # with `typeof rawSection !== "object"`, so "first section" must be the first
    # *object-valued* entry, not the first key.

    probe = "zz_probe_field"
    assert probe not in preferred

    def with_probe(section: str, *, at_end: bool) -> dict:
        rest = {k: v for k, v in payload.items() if k != section}
        patched = {**payload[section], probe: 1}
        return {**rest, section: patched} if at_end else {section: patched, **rest}

    # Render with the slice unbounded. With the real `limit` the *slice* could be what
    # hides the late probe — the assertion would hold for the wrong reason, and raising
    # the cutoff would not move it. Unbounded, only the cutoff can explain the result.
    # The real-cap render is kept below so a change to the limit alone still moves this.
    unbounded = 10**6
    visible = _rendered(with_probe(early, at_end=False), preferred=preferred, cutoff=cutoff, limit=unbounded)
    hidden = _rendered(with_probe(late, at_end=True), preferred=preferred, cutoff=cutoff, limit=unbounded)

    assert f"{early}.{probe}" in visible, (
        "a field added to the FIRST section is no longer rendered — the cutoff stopped "
        "binding, and this test's premise is gone"
    )
    assert f"{late}.{probe}" not in hidden, (
        "a field added to the LAST section is now rendered even with the slice unbounded "
        "— the cutoff stopped binding, so the visible set is no longer order-dependent "
        "and this test should be deleted with a reason rather than kept."
    )
    # The same claim under the shipped caps, so a limit change alone is visible here.
    assert f"{late}.{probe}" not in _rendered(
        with_probe(late, at_end=True), preferred=preferred, cutoff=cutoff, limit=limit
    )


@pytest.mark.parametrize("key", sorted(_RECORDED_DEAD_CONTROLS))
def test_a_recorded_dead_control_is_still_a_real_field(key: str) -> None:
    """Catch a typo in the record, which would excuse nothing."""
    assert key in _settings_fields(), f"{key} is not a settings field any more"
