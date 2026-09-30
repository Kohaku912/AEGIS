"""The settings UI's contract with the settings schema (B-21).

`web-ui/src/pages/Settings.tsx::editableSettings` **discovers** the controls it renders
from the `GET /api/settings` payload (`AEGISSettings.model_dump()`): every boolean /
number / string field in every section, with a hand-written `preferred` list sorted
first, a `result.length >= 24` cutoff for unpreferred fields, and a `.slice(0, 32)`.

Because it discovers rather than lists, the set of controls it *offers* can never fall
out of date with the schema — there is no inventory in the UI to go stale. What
discovery does **not** fix is the *coupling*: a control the dashboard offers is a promise
that moving it does something, and nothing tied that promise to whether any backend code
reads the field. So the dashboard could offer a control for a field with no reader, and
no test would notice.

## What this file used to be, and what it is now

It was written to record that coupling's **defect**: 10 of the 26 rendered controls were
for fields nothing read — *"a privacy switch that does nothing is worse than no switch."*
That record was the pending B-6 owner call, and B-6 resolved it on 2026-09-30 by
**deleting** the 22 recorded-dead fields (see `test_ineffective_flags.py`). The record of
10 dead controls is therefore gone, and this file is **re-pointed** from the defect to the
invariant that defect was evidence for: the dashboard must render **no** control for a
field with no reader. That is a stronger claim than the old one, because it constrains
fields that do not exist yet — and the old record could not, since it was an intersection
with a static list.

The `preferred` list is the other half, and it is a **regression pin**: *which* controls
deserve prominence is still a UI judgement, but every entry must name a real field. It
has been pruned twice — five entries that could never match (register A-10, 2026-09-29),
and `self_dev_proposal_enabled` on 2026-09-30 (B-6 deleted the field it named) — and
`test_every_preferred_key_names_a_real_settings_field` keeps them out.

**The algorithm is transcribed, not imported** — a Python test cannot execute TypeScript.
Two things keep the transcription honest: the constants are **parsed out of the TS** (so a
change there moves this test), and the shape of the loop is asserted (so a rewrite that
invalidates the transcription fails rather than silently measuring the wrong thing).
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

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
#:
#: `self_dev_proposal_enabled` was pruned on 2026-09-30 (B-6) and is **not** recorded
#: here: its key was never wrong, its *field* was deleted, so an entry for it would
#: excuse a key that can no longer be legitimate.
_RECORDED_NONEXISTENT_PREFERRED: frozenset[str] = frozenset()

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
    # 9 since B-6 deleted `self_dev_proposal_enabled` (was 10); the floor guards the
    # *parse*, not the UI judgement, so it tracks the live list.
    assert len(preferred) >= 9, f"only {len(preferred)} preferred keys parsed: {preferred}"
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
    the intersection in the test below would be empty for the wrong reason.

    Equality, and the record holds exactly one entry since B-6 cleared the debt map — so
    a scan that goes blind fails here rather than quietly reporting nothing unread.
    """
    recorded = _recorded_unread()
    assert recorded == {"voice.push_to_talk_only"}, (
        f"the unread record parsed as {sorted(recorded)}. Expected exactly the one "
        "deliberate entry (`_INTENTIONALLY_UNREAD`); the debt map has been empty since "
        "B-6 (2026-09-30). The maps are annotated assignments "
        "(`_UNOWNED_DEBT: dict[str, str] = {...}`); a bare-`ast.Assign` scan misses them "
        "and silently reports nothing unread."
    )


# ── The invariant: a control the user can move must change something ──────────


def test_the_ui_offers_no_control_for_a_field_nothing_reads() -> None:
    """The user-facing half of the unread-settings debt, as an invariant.

    This test **replaced** a record (B-6, 2026-09-30). It used to assert that the
    dashboard offered exactly ten controls for fields nothing read — the debt seen from
    the user's side. The owner resolved that debt by deleting the fields, so the record
    is gone and the claim it was evidence for is what gets pinned: the dashboard offers
    **no** control for a field with no reader.

    The assertion is an *absence*, so on its own it is vacuously true the moment either
    scan breaks. Three positive guards are what make it worth keeping:
    ``test_the_scan_actually_sees_controls_and_preferences`` (the rendered set is real),
    ``test_the_debt_record_is_readable`` (the unread record parsed), and the non-empty
    check below (a record that emptied would make the intersection empty for the wrong
    reason).
    """
    rendered = set(_rendered_controls())
    unread = _recorded_unread()

    assert unread, (
        "the unread record is empty, so this test proves nothing. If the last recorded "
        "field was wired up or deleted, delete this test with a reason rather than "
        "leaving a vacuous one."
    )
    assert rendered & unread == set(), (
        "the settings page offers a control for a field nothing reads:\n"
        f"  {sorted(rendered & unread)}\n"
        "A control the user can move that changes nothing is worse than a missing one. "
        "Either wire the field up, or delete it and drop it from the record."
    )


# ── Direction 2: the preference list names fields that do not exist ───────────


def test_every_preferred_key_names_a_real_settings_field() -> None:
    """`preferred` says "show these first"; every entry must name a field that exists.

    The list was pruned to its ten live entries on 2026-09-29 (register A-10) and to nine
    on 2026-09-30 (B-6 deleted the field behind `self_dev_proposal_enabled`). Which
    controls deserve prominence is still a UI judgement, so this pins the *claim* and not
    the content: add a key freely, but it has to name a real settings field.

    The second assertion is the non-vacuity guard. `unmatched == ∅` is equally true of an
    emptied list — and an empty `preferred` would quietly disable the preference sort,
    which is the opposite of the defect this file records. The `len(preferred) >= 9`
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
    window — which is why a field with no reader can leave the visible set (or arrive in
    it) without anyone touching a record. That is also why
    `test_the_ui_offers_no_control_for_a_field_nothing_reads` can fail on a model change
    that never mentions an unread field.
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
