"""The settings debt stays deleted: 24 unread fields must not come back.

B-6 was the register row for the settings surface's **unread fields** — fields that are
declared, rendered by the dashboard, and read by nothing. On 2026-09-30 the owner resolved
the row by **deleting** them rather than wiring them, so this file records the removal.

Two more joined the set on 2026-10-08: deleting the v1 intake path (§4 item 47) left
`IntakeSettings.requires_agent_threshold` and `IntakeSettings.fallback_requires_agent` with
no reader, and an unread field cannot be merely *recorded* — the settings page must not
render a control for one (`test_settings_ui_matches_the_schema.py`) — so they were retired.

Why a deletion needs a pin at all: the detector (``test_ineffective_flags.py``) catches a
*newly added* dead field, and it would catch one of these names if it came back **without**
a reader. It cannot catch the interesting case — a retired name coming back **with** a
reader, or coming back as prose. A docstring promising a setting is exactly how the
original debt survived. So the claim here is the stronger one: these names are gone from
``src/``, from the models, and from the shipped config, and they do not come back.

The set is the *whole* deleted set, discovered from nothing — it is a hand-written record,
which is normally the defect this repo warns about. It is acceptable here only because it
is **frozen**: the fields no longer exist, so there is nothing left to discover them from.
Every live-set assertion in this file derives its expectation from the models instead.

Four directions, and a positive control that keeps the first from passing vacuously:

* the names appear nowhere under ``src/`` — code **and prose**;
* they are absent from the models' own declarations (an independent detector, so blinding
  either one is visible);
* the shipped ``config/settings.json`` carries none of their keys;
* and — the **general** form, added 2026-10-01 — no key in the shipped config is undeclared
  by a settings model. The first three cover only the 24 *named* fields, which is exactly why
  the dead ``autonomy`` block (the ``AutonomyProfile`` residue P1-3 left behind, eleven keys
  nothing read) survived them;
* ``test_the_scan_can_see_a_live_field`` proves the scan works by finding a field that is
  still there — the one unread field B-6 deliberately **kept**. An absence assertion is
  vacuously true once its scan breaks, so this control is the only thing covering it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_SERVER = Path(__file__).resolve().parents[1]
_SRC = _SERVER / "src"
_SHIPPED_CONFIG = _SERVER / "config" / "settings.json"

#: The 24 recorded fields (22 from B-6, 2 retired 2026-10-08), as ``Model.field``.
#: Recorded by class name because that is how the detector's map named them, and so the
#: model check below can compare directly.
_RETIRED_FIELDS: frozenset[str] = frozenset(
    {
        # 10 x AutonomousSettings — the autonomous loop runs on hardcoded budgets.
        "AutonomousSettings.approval_proposal_limit",
        "AutonomousSettings.browser_exploration_budget_per_day",
        "AutonomousSettings.daily_briefing_enabled",
        "AutonomousSettings.follow_up_timeout",
        "AutonomousSettings.max_actions_per_hour",
        "AutonomousSettings.max_autonomous_runs_per_day",
        "AutonomousSettings.normal_interruption_budget_per_hour",
        "AutonomousSettings.research_watch_enabled",
        "AutonomousSettings.self_dev_proposal_enabled",
        "AutonomousSettings.social_poll_interval_seconds",
        # 2 x AgentSettings — profile selection and concurrency are fixed in code.
        "AgentSettings.default_profile",
        "AgentSettings.max_concurrent",
        # 4 x IntakeSettings — the classic intake path is constructed nowhere.
        "IntakeSettings.classifier_profile",
        "IntakeSettings.dedup_novelty_threshold",
        "IntakeSettings.dedup_window_size",
        "IntakeSettings.max_importance",
        # 2 more x IntakeSettings — retired 2026-10-08, when §4 item 47 deleted the v1
        # intake path and left these two with no reader at all. Unlike the four above
        # they were still declared until then; the settings pins forced the retirement
        # (an unread field cannot be merely recorded, because the settings page must not
        # render a control for one).
        "IntakeSettings.fallback_requires_agent",
        "IntakeSettings.requires_agent_threshold",
        # 4 x MemorySettings — the memory subsystem does not consult settings for these.
        "MemorySettings.procedural_learning_enabled",
        "MemorySettings.reflection_enabled",
        "MemorySettings.semantic_memory_enabled",
        "MemorySettings.sensitive_data_storage_enabled",
        # 2 x ServerSettings — connection behaviour is fixed in code.
        "ServerSettings.health_check_interval_seconds",
        "ServerSettings.reconnect_policy",
    }
)

#: The field B-6 deliberately **kept**, and the reason the pin can prove its scan works.
#: It is unread too, but it is a pinned default posture ("no always-listening by default")
#: rather than debt — see ``_INTENTIONALLY_UNREAD`` in ``test_ineffective_flags.py``.
_SURVIVING_UNREAD_FIELD = "push_to_talk_only"


def _py_files() -> list[Path]:
    return [path for path in _SRC.rglob("*.py") if "__pycache__" not in path.parts]


def _mentions(name: str) -> list[str]:
    """Every ``src/`` module that names ``name`` as a whole identifier.

    Whole-identifier rather than substring, so a live field whose name *contains* a
    retired one cannot be reported — and prose is deliberately included: a docstring
    describing a setting that no longer exists is the original bug class.
    """
    pattern = re.compile(rf"(?<![\w]){re.escape(name)}(?![\w])")
    return sorted(
        path.relative_to(_SRC).as_posix()
        for path in _py_files()
        if pattern.search(path.read_text(encoding="utf-8", errors="replace"))
    )


def _declared_fields() -> set[str]:
    """Every field the settings models declare, as ``Model.field``.

    Derived from the models rather than listed, so this side of the comparison cannot go
    stale the way a hand-written record does.
    """
    from pydantic import BaseModel

    from aegis_ai.settings import models

    found: set[str] = set()
    for value in vars(models).values():
        if isinstance(value, type) and issubclass(value, BaseModel) and value is not BaseModel:
            found.update(f"{value.__name__}.{name}" for name in value.model_fields)
    return found


def _shipped_keys() -> set[str]:
    """Leaf key names in the shipped ``config/settings.json``."""
    payload = json.loads(_SHIPPED_CONFIG.read_text(encoding="utf-8"))

    def walk(node: object) -> set[str]:
        if not isinstance(node, dict):
            return set()
        names: set[str] = set()
        for key, value in node.items():
            names.add(key)
            names |= walk(value)
        return names

    return walk(payload)


# ── The deletion ──────────────────────────────────────────────────────────────


def test_no_retired_field_name_survives_under_src() -> None:
    """None of the 24 names appears anywhere under ``src/`` — code or prose.

    Equality against the empty set, in the shape the other ``*_stays_retired`` pins use.
    The expected side is empty, so ``test_the_scan_can_see_a_live_field`` below is what
    stops this from passing because the scan went blind.
    """
    survivors = {
        name: where
        for name in sorted(field.split(".", 1)[1] for field in _RETIRED_FIELDS)
        if (where := _mentions(name))
    }
    assert survivors == {}, (
        "a settings field deleted by B-6 is named under src/ again:\n"
        + "\n".join(f"  {name}: {where}" for name, where in survivors.items())
        + "\nDeleting a field does not make it come back with a reader, and prose counts: "
        "a docstring promising a setting nobody reads is how the original debt survived. "
        "If the field is genuinely wanted again, that is a new owner decision — record it "
        "and update this pin."
    )


def test_the_scan_can_see_a_live_field() -> None:
    """Positive control: the scan finds a field that is still there.

    Every assertion in ``test_no_retired_field_name_survives_under_src`` is of the form
    "nothing does X", which is **vacuously true** once the scan breaks — an empty file
    list, a wrong root, or a regex that matches nothing all pass it. This is the one
    assertion that fails instead. It uses the field B-6 deliberately kept, so it also
    proves the deletion did not overshoot the decision it came from.
    """
    assert _mentions(_SURVIVING_UNREAD_FIELD), (
        f"{_SURVIVING_UNREAD_FIELD} is no longer named anywhere under src/ — either the "
        "deletion overshot the B-6 decision (it kept this field on purpose), or the scan "
        "is blind and the absence assertions above prove nothing."
    )
    # A second, unrelated live field, so a single accidentally-deleted file cannot cover
    # for a broken scan.
    assert _mentions("episodic_retention_days"), "the scan cannot see a live memory field"


def test_the_retired_fields_are_absent_from_the_models() -> None:
    """The models no longer declare them — an independent detector for the same claim.

    The scan above reads text; this reads the model objects. Two detectors for one claim,
    so blinding either one is visible.
    """
    declared = _declared_fields()
    assert declared, "no settings model declared any field — the discovery is broken"
    overlap = sorted(declared & _RETIRED_FIELDS)
    assert overlap == [], (
        f"the settings models declare fields B-6 deleted: {overlap}. If they are back on "
        "purpose, update _RETIRED_FIELDS and say so in the commit message."
    )


def test_the_shipped_config_carries_no_retired_key() -> None:
    """The shipped ``config/settings.json`` no longer offers their keys.

    A stale key in the shipped file reads as "you can configure this", and nothing fails
    when you set it — the same shape as the field itself. The file is a *sample* rather
    than a full dump (it omits whole sections), so this is one-directional: every key it
    carries must be live, not every live key must appear.
    """
    shipped = _shipped_keys()
    assert shipped, "the shipped settings file parsed to no keys at all"
    retired = {field.split(".", 1)[1] for field in _RETIRED_FIELDS}
    assert sorted(shipped & retired) == [], (
        f"the shipped settings file still carries retired keys: {sorted(shipped & retired)}"
    )


# ── The general invariant the test above only sampled ─────────────────────────


def _walk_shipped_against_models() -> tuple[list[str], list[str]]:
    """Walk the shipped config against the models: ``(dead_paths, visited_paths)``.

    ``dead_paths`` are keys no settings model declares. Recurse only into fields whose
    annotation *is* a settings model — a ``dict[...]`` field
    (``capabilities.per_capability`` is ``dict[str, CapabilityPermission]``) holds
    user-chosen keys, not schema, so its contents are not judged.
    """
    from pydantic import BaseModel

    from aegis_ai.settings.models import AEGISSettings

    payload = json.loads(_SHIPPED_CONFIG.read_text(encoding="utf-8"))
    dead: list[str] = []
    visited: list[str] = []

    def walk(node: dict, model: type[BaseModel], prefix: str) -> None:
        for key, value in node.items():
            visited.append(prefix + key)
            if key not in model.model_fields:
                dead.append(prefix + key)
                continue
            annotation = model.model_fields[key].annotation
            if (
                isinstance(value, dict)
                and isinstance(annotation, type)
                and issubclass(annotation, BaseModel)
            ):
                walk(value, annotation, prefix + key + ".")

    walk(payload, AEGISSettings, "")
    return dead, visited


def test_every_shipped_key_is_a_live_settings_field() -> None:
    """The shipped config offers **no** key that no model declares.

    This is the general form of the B-6 defect, and the assertion the docstring at the top
    of this file has claimed all along ("every key it carries must be live"). Until
    2026-10-01 only the 24 *named* retired keys were checked, so a dead block that was never
    one of those names survived: ``autonomy``, the residue of the ``AutonomyProfile`` that
    P1-3 deleted. Eleven keys nothing reads — and several spelled out approval
    requirements (``external_send_requires_approval``, ``payment_requires_approval``,
    ``publish_requires_approval``), so the shipped file **read as though those gates were
    configured**. Pydantic ignores extras, so setting one neither works nor fails; the only
    symptom is a reader believing a control exists. Deleted 2026-10-01.

    One-directional, like the test above: the file is a *sample* (it omits whole sections
    such as ``agents`` and ``intake``), so a live key may be absent — but every key it does
    carry must exist.
    """
    dead, visited = _walk_shipped_against_models()
    payload = json.loads(_SHIPPED_CONFIG.read_text(encoding="utf-8"))
    # Non-vacuity. A walk that visited nothing would report no dead keys, so prove it
    # covered every top-level section *and* descended into at least one sub-model. These
    # are deliberately not a count — a count would rot when the config changes size.
    top_level_seen = {path.split(".", 1)[0] for path in visited}
    assert top_level_seen == set(payload), (
        f"the walk missed top-level sections: {sorted(set(payload) - top_level_seen)} — "
        "the dead-key result below cannot be trusted"
    )
    assert "voice.push_to_talk_only" in visited, (
        "the walk did not descend into a sub-model, so it never judged any leaf key"
    )
    assert dead == [], (
        f"the shipped settings file carries keys no settings model declares: {dead}. "
        "Pydantic ignores extras, so setting one neither works nor fails — and a key named "
        "like a control (e.g. ``*_requires_approval``) reads as though a gate were "
        "configured. Either declare the field and give it a reader, or delete the key."
    )
