"""The generic ineffective-flag detector.

The retired P0-2 concern was a settings flag that exists but is never read — the
shape of the original ``web_search_allowed`` bug, and of ``check_domain()`` in the
browser server. Phase 1 fixed the known instances and added a behavioural test for
one of them. This module generalises the detector: it enumerates the settings
surface and fails when a flag has no reader.

Four layers, weakest to strongest:

1. **Static** — every flag on every settings model must be referenced somewhere in
   ``src/`` outside its own definition. Fields that are not read must appear in one
   of the two maps below *with a written reason*, so a newly added dead flag fails
   the suite instead of shipping quietly.
2. **Enforcement** — every egress lock must be read by the enforcement point
   (``aegis_ai/egress/gate.py``). A flag read only by a dashboard is not a lock.
3. **Behavioural** — flipping each lock must actually change a gate decision.
   This is the only layer that proves the flag is *effective* rather than merely
   *mentioned*.
4. **The second surface** — layers 1–3 scan the *pydantic settings models*, and that
   unit is a choice: on 2026-10-02 the survey pointed out that a whole configuration
   *surface* can sit outside it. One does. ``aegis_ai/config.py``'s ``Config`` dataclass
   is filled straight from the environment and never validated by the settings store, and
   measured that day 5 of its 13 fields were referenced nowhere and 1 only by a startup
   log line. Layer 4 discovers that dataclass and applies the same rule to it — with the
   stricter reading of "read" described below.

The models are **discovered, not listed**. A hand-maintained model list is how this
detector missed ``AutonomyProfile`` entirely for months: the settings surface grew
and the list did not. Discovery means a new model is covered the moment it is
declared, and ``test_the_scan_actually_covers_the_settings_surface`` asserts the
discovery still finds every model.

Known limitation of layer 1: the reader scan is textual on the bare field name, so
a field whose name also appears in an unrelated module reads as "read". Prefer
distinctive field names; a name like ``profile`` or ``enabled`` cannot be checked
this way. Layer 4 does not share this limitation — it parses with ``ast``, so it knows
*which* object a reference is on and whether the reference sits inside a logging call —
but it is deliberately narrower: it covers the ``Config`` surface only.

The detector is itself tested (``test_the_detector_reports_a_dead_flag``) so it
cannot rot into a no-op — the inverse of the bug it exists to catch.

**2026-09-30 (B-6)**: the debt map is **empty** now — the owner deleted the 22 fields
it recorded rather than wiring them. The skip count therefore fell from 23 to 1, and
that drop is the *record* being cleared, not debt paid quietly: the retired names are
pinned by ``tests/test_settings_debt_stays_retired.py``.
"""

from __future__ import annotations

import ast
import functools
import re
from pathlib import Path

import pytest

# Every test in this module guards the single constraint. The marker is counted by
# --require-egress-tests (see conftest.py) so this suite can never silently run empty.
pytestmark = pytest.mark.egress

_SRC = Path(__file__).resolve().parents[1] / "src"
_GATE_MODULE = _SRC / "aegis_ai" / "egress" / "gate.py"

#: Where a flag is *declared* rather than read. Excluded from the reader scan.
_DEFINITION_MODULE = _SRC / "aegis_ai" / "settings" / "models.py"

#: Fields that are genuinely, deliberately unread. Every entry needs a reason, and
#: ``test_the_unread_maps_have_no_stale_entries`` fails once a field gains a reader —
#: so an entry cannot outlive its justification.
_INTENTIONALLY_UNREAD: dict[str, str] = {
    "VoiceSettings.push_to_talk_only": (
        "The voice engines are real (local faster-whisper STT, provider-dispatched "
        "TTS), but none of them reads this: VoiceGate never consults it, so no capture "
        "path can be gated on it. It is kept because it is a *default posture* that a "
        "test pins — 'no always-listening by default' "
        "(test_voice_io.py::test_push_to_talk_is_the_default_and_wake_word_is_off) — and "
        "enforcing it is part of the voice workstream, not the constraint. It is *not* "
        "an egress risk — it cannot transmit anything. This entry used to add 'kept in "
        "the schema so the shipped settings file stays valid'; that is false and was "
        "withdrawn on 2026-09-30 (B-6) — no settings model sets `extra=`, so pydantic's "
        "default `extra='ignore'` drops an unknown key either way, and no test compares "
        "the shipped file's keys against the schema."
    ),
}

# ── Declared but unowned ──────────────────────────────────────────────────────
#
# This is an inventory of debt, **not** a set of approvals: fields that are unread
# because nobody owns the feature they configure. They are recorded here so the number
# is visible and pinned rather than hidden, and so a *new* dead flag still fails the
# suite.
#
# **Empty since 2026-09-30 (B-6), and that is a deletion rather than a payment.** The
# owner resolved the debt by deleting the 22 fields it held. Each was measured first:
# none was referenced anywhere under ``src/`` outside this definition module, so for the
# runtime the removal is behaviour-preserving. Two consequences are *not* behaviour-free
# and are recorded deliberately, because "delete an unread field" sounds like a no-op:
#
#   * the settings API now **refuses** a write that names a retired key —
#     ``SettingsStore.update_section`` rejects unknown fields rather than ignoring them,
#     so a client that used to set one of these now gets an error;
#   * the dashboard no longer **renders** a control for them, because it discovers its
#     controls from the payload rather than listing them.
#
# The retired names are pinned in ``tests/test_settings_debt_stays_retired.py``, and the
# shipped ``config/settings.json`` no longer carries their keys.

_UNOWNED_DEBT: dict[str, str] = {}

#: Field names declared on more than one settings model. Layer 1's reader scan is textual
#: on the *bare* name, so for a colliding name it cannot attribute a reader to a model: a
#: reader of ANY owner makes EVERY owner look read. The set is pinned by
#: ``test_the_bare_name_scan_is_blind_only_to_the_recorded_collisions`` so that adding a
#: field whose name already exists on another model fails here — that is the exact moment
#: the detector goes blind for that name — instead of shipping a dead flag unseen.
#:
#: Measured 2026-10-09: the only collision is ``enabled``, declared on ``AgentSettings``
#: (read at ``runtime.py:1724``), ``CapabilityPermission`` (read), and ``IntakeSettings``
#: (**read by nothing** — see ``test_the_collision_hides_a_real_dead_flag``). So the one
#: name the scan cannot check is also the one hiding a dead flag.
_KNOWN_NAME_COLLISIONS: frozenset[str] = frozenset({"enabled"})

#: The egress locks, as (settings path, purpose used to probe the gate).
_EGRESS_LOCKS: tuple[tuple[str, str], ...] = (
    ("privacy.external_egress_allowed", "llm.chat"),
    ("privacy.egress_allowed_hosts", "llm.chat"),
    ("privacy.external_llm_allowed", "llm.chat"),
    ("privacy.web_search_allowed", "web.search"),
    ("voice.external_voice_api_allowed", "voice.tts"),
    ("privacy.external_messaging_allowed", "messaging.line"),
)

#: For each lock: the configuration with that lock closed, and the same
#: configuration with only that lock opened. (label, purpose, closed, open) where
#: each side is a (privacy overrides, voice overrides, allowlist) triple.
_LOCK_BEHAVIOUR: tuple[tuple[str, str, tuple, tuple], ...] = (
    (
        "privacy.external_egress_allowed",
        "llm.chat",
        ({"external_llm_allowed": True}, {}, ["api.deepseek.com"]),
        (
            {"external_egress_allowed": True, "external_llm_allowed": True},
            {},
            ["api.deepseek.com"],
        ),
    ),
    (
        "privacy.external_llm_allowed",
        "llm.chat",
        ({"external_egress_allowed": True}, {}, ["api.deepseek.com"]),
        (
            {"external_egress_allowed": True, "external_llm_allowed": True},
            {},
            ["api.deepseek.com"],
        ),
    ),
    (
        "privacy.web_search_allowed",
        "web.search",
        ({"external_egress_allowed": True}, {}, ["html.duckduckgo.com"]),
        (
            {"external_egress_allowed": True, "web_search_allowed": True},
            {},
            ["html.duckduckgo.com"],
        ),
    ),
    (
        "voice.external_voice_api_allowed",
        "voice.tts",
        ({"external_egress_allowed": True}, {}, ["speech.platform.bing.com"]),
        (
            {"external_egress_allowed": True},
            {"external_voice_api_allowed": True},
            ["speech.platform.bing.com"],
        ),
    ),
    (
        "privacy.egress_allowed_hosts",
        "llm.chat",
        ({"external_egress_allowed": True, "external_llm_allowed": True}, {}, []),
        (
            {"external_egress_allowed": True, "external_llm_allowed": True},
            {},
            ["api.deepseek.com"],
        ),
    ),
    (
        "privacy.external_messaging_allowed",
        "messaging.line",
        ({"external_egress_allowed": True}, {}, ["api.line.me"]),
        (
            {"external_egress_allowed": True, "external_messaging_allowed": True},
            {},
            ["api.line.me"],
        ),
    ),
)


# ── The detector ──────────────────────────────────────────────────────────────


def _references(text: str, field: str) -> bool:
    """True when ``field`` appears in ``text`` as a whole identifier."""
    return re.search(rf"(?<![\w]){re.escape(field)}(?![\w])", text) is not None


def _readers(field: str, *, definition_module: Path = _DEFINITION_MODULE) -> list[str]:
    """Every module under ``src/`` that references ``field``, minus its definition.

    The definition module is excluded because the field's own declaration line
    would otherwise count as a reader — which is exactly the false negative that
    let ``web_search_allowed`` go unnoticed.
    """
    found: list[str] = []
    for path in _SRC.rglob("*.py"):
        if path == definition_module or "__pycache__" in path.parts:
            continue
        if _references(path.read_text(encoding="utf-8", errors="replace"), field):
            # as_posix() so the report is identical on Windows and POSIX.
            found.append(path.relative_to(_SRC).as_posix())
    return sorted(found)


def _settings_models() -> list[type]:
    """Every settings model, discovered rather than listed."""
    from pydantic import BaseModel

    from aegis_ai.settings import models

    return sorted(
        {
            value
            for value in vars(models).values()
            if isinstance(value, type) and issubclass(value, BaseModel) and value is not BaseModel
        },
        key=lambda model: model.__name__,
    )


def _scanned_fields() -> list[str]:
    """Every settings field as ``Model.field``.

    Keyed per model rather than by bare name so the failure message says which model
    owns the field, and so two models cannot share one unread-map entry.
    """
    return sorted(
        f"{model.__name__}.{field}"
        for model in _settings_models()
        for field in model.model_fields
    )


def _field_of(key: str) -> str:
    return key.split(".", 1)[1]


def _colliding_field_names() -> set[str]:
    """Field names declared on two or more settings models.

    These are the names layer 1's bare-name scan cannot decide: a reference to the name
    anywhere makes *every* model that declares it look read, so an unread owner is
    invisible. The rest of the surface is unaffected — for a name on a single model the
    textual scan and a model-aware one agree.
    """
    owners: dict[str, list[str]] = {}
    for model in _settings_models():
        for field in model.model_fields:
            owners.setdefault(field, []).append(model.__name__)
    return {name for name, models in owners.items() if len(models) >= 2}


def _section_is_read(section: str) -> bool:
    """True when some module reads an attribute of the ``section`` settings section.

    Detects ``X.<section>.<field>`` (and a bare ``X.<section>``) anywhere under ``src/``,
    excluding ``__pycache__``. This is deliberately *not* the layer-1 scan: it is used only
    to pin that a section is read by **no** live path, where the bare-name textual scan
    would count the section's own module name (``aegis_ai.intake``) as a reader.

    Known inexactness, stated so it is not mistaken for a general detector: the
    string-keyed resolvers the gate uses (``self._privacy_setting("privacy", ...)``) are
    not attribute accesses and so are invisible here — which is exactly why this helper
    must never replace ``_readers``. For ``intake`` the scan is exact: measured 2026-10-09,
    ``.intake`` appears as an attribute access nowhere (the only ``intake`` references are
    ``from aegis_ai.intake import ...``, an ``ImportFrom``, not an ``Attribute``).
    """
    for path in _SRC.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        if any(
            isinstance(node, ast.Attribute) and node.attr == section
            for node in ast.walk(tree)
        ):
            return True
    return False


def _recorded_unread() -> dict[str, str]:
    """Both unread maps, merged. ``_INTENTIONALLY_UNREAD`` wins on a clash."""
    return {**_UNOWNED_DEBT, **_INTENTIONALLY_UNREAD}


# ── Layer 1: static ───────────────────────────────────────────────────────────


def test_the_scan_actually_covers_the_settings_surface():
    """Guard the detector: an empty or truncated field list would pass vacuously."""
    models = _settings_models()
    fields = _scanned_fields()

    assert len(models) >= 10, f"only {len(models)} settings models were discovered"
    # 72 measured after B-6 deleted the 22 recorded-dead fields (the pre-deletion count
    # was 94). The floor guards the *discovery*, so it tracks the live surface.
    assert len(fields) >= 70, f"only {len(fields)} settings flags were scanned"
    assert "PrivacySettings.external_egress_allowed" in fields
    assert "VoiceSettings.external_voice_api_allowed" in fields


@pytest.mark.parametrize("key", _scanned_fields())
def test_every_settings_flag_has_a_reader(key: str):
    """A flag nobody reads is a promise nobody keeps."""
    recorded = _recorded_unread()
    if key in recorded:
        pytest.skip(f"recorded: {recorded[key]}")

    readers = _readers(_field_of(key))
    assert readers, (
        f"settings flag '{key}' is declared but never read anywhere in src/ "
        f"(outside its own definition). Either wire it up, delete it, or record it in "
        f"_INTENTIONALLY_UNREAD / _UNOWNED_DEBT with a reason."
    )


def test_the_unread_maps_have_no_stale_entries():
    """A recorded entry must not outlive the problem it excuses."""
    stale = [key for key in _recorded_unread() if _readers(_field_of(key))]
    assert stale == [], (
        f"{stale} are recorded as unread but now have a reader — remove them."
    )


def test_the_unread_maps_name_real_fields():
    """Catch a typo, which would silently excuse nothing."""
    known = set(_scanned_fields())
    unknown = sorted(set(_recorded_unread()) - known)
    assert unknown == [], f"the unread maps name fields that do not exist: {unknown}"


def test_every_dead_flag_is_accounted_for():
    """The headline number, asserted rather than merely reported.

    Pins the size of the debt so it cannot quietly grow: adding a dead flag fails
    ``test_every_settings_flag_has_a_reader``, and *fixing* one fails this until the
    recorded maps shrink with it.
    """
    recorded = set(_recorded_unread())
    unread = {
        key for key in _scanned_fields() if not _readers(_field_of(key))
    }
    assert unread == recorded, (
        f"unread and recorded disagree. Unrecorded: {sorted(unread - recorded)}. "
        f"Recorded but actually read: {sorted(recorded - unread)}."
    )


def test_the_retired_autonomy_profile_stays_retired():
    """``AutonomyProfile`` was deleted in P1-3, and must not come back.

    It was never read anywhere, its profile ladder described the approval mechanism
    deleted in Phase 5b, and its ``# Always forbidden (structural)`` comment claimed
    a guarantee nothing enforced. Wiring it would mean re-introducing a plan-level
    approval surface, which the owner boundary forbids.
    """
    from aegis_ai.settings import models

    assert not hasattr(models, "AutonomyProfile")
    assert "autonomy" not in models.AEGISSettings.model_fields
    assert "Always forbidden (structural)" not in _DEFINITION_MODULE.read_text(
        encoding="utf-8"
    )


def test_the_bare_name_scan_is_blind_only_to_the_recorded_collisions():
    """Layer 1's documented limitation, made executable and bounded.

    The docstring above admits the scan is textual on the bare field name, so a name that
    also appears on an unrelated model reads as "read". That is a claim about the code, and
    until now nothing validated it — a new colliding name would silently blind the detector
    for that name and no test would notice.

    This pins the *bound* rather than the absence: the set of colliding names must equal
    ``_KNOWN_NAME_COLLISIONS``. Adding a field whose name already exists on another model
    fails here, which is the moment a human must decide (rename one field, or extend the
    record and say which model is now unverifiable) instead of shipping a dead flag unseen.
    """
    collisions = _colliding_field_names()
    assert collisions == set(_KNOWN_NAME_COLLISIONS), (
        f"the set of field names declared on more than one settings model changed: "
        f"{sorted(collisions)} (recorded: {sorted(_KNOWN_NAME_COLLISIONS)}).\n"
        "A colliding name is invisible to the bare-name reader scan — a reader of one owner "
        "makes every owner look read — so the detector has just gone blind for any *new* "
        "name here. Rename the colliding field, or extend _KNOWN_NAME_COLLISIONS and record "
        "which model is now unverifiable and why."
    )


def test_the_collision_hides_a_real_dead_flag():
    """The concrete flag the collision hides, measured rather than asserted in prose.

    ``IntakeSettings.enabled`` is declared, defaults ``True``, and is read by **nothing**:
    ``L1Router``/``L1Executor`` are constructed without settings and no module reads an
    attribute of the ``intake`` section. It nonetheless passes ``test_every_settings_flag_has_a_reader``
    because its bare name ``enabled`` is also declared on ``AgentSettings`` (read) and
    ``CapabilityPermission`` (read) — so the scan sees readers and stops.

    It cannot be moved into the unread maps below either: ``test_settings_ui_matches_the_schema.py``
    forbids the dashboard rendering a control for a recorded-unread field, and this field
    *is* rendered (measured: the 20th of 26 controls). So the field is a switch that does
    nothing — the exact defect this file exists to catch — and the only thing standing
    between it and the suite is the name collision. Pinned here so the fact is executable;
    the owner call (wire the switch into the intake path, or delete the field and its
    control) is recorded in ``DELEGATION.md`` §4.
    """
    assert "enabled" in _KNOWN_NAME_COLLISIONS, "the premise: `enabled` is the colliding name"
    assert "IntakeSettings.enabled" in _scanned_fields(), (
        "IntakeSettings.enabled no longer exists — delete this test with a reason rather "
        "than leaving a vacuous one."
    )
    assert not _section_is_read("intake"), (
        "the `intake` settings section is now read by a live path, so IntakeSettings.enabled "
        "is no longer dead and this test's premise is gone — delete it with a reason."
    )
    assert _readers("enabled"), (
        "the bare-name scan no longer reports readers for `enabled`; the collision stopped "
        "being load-bearing and this test should be re-derived."
    )
    assert "IntakeSettings.enabled" not in _recorded_unread(), (
        "IntakeSettings.enabled is now in the unread maps. It cannot be: it is *rendered* by "
        "the dashboard, and test_settings_ui_matches_the_schema.py forbids rendering a control "
        "for a recorded-unread field. Either wire it, or delete the field and its control."
    )


# ── Layer 2: enforcement ──────────────────────────────────────────────────────


@pytest.mark.parametrize("lock_path", [lock for lock, _ in _EGRESS_LOCKS])
def test_every_egress_lock_is_read_by_the_enforcement_point(lock_path: str):
    """A lock read only by a dashboard is not a lock — the gate must read it."""
    section, field = lock_path.split(".", 1)
    gate_source = _GATE_MODULE.read_text(encoding="utf-8")

    assert _references(gate_source, field), (
        f"the egress lock '{lock_path}' is not read by {_GATE_MODULE.name}. "
        f"Until the enforcement point reads it, flipping it does nothing."
    )
    # The section matters too: reading a same-named field from the wrong section
    # would be a silent no-op.
    assert _references(gate_source, section), (
        f"{_GATE_MODULE.name} never mentions the '{section}' settings section, so it "
        f"cannot be reading '{lock_path}' from it."
    )


# ── Layer 3: behavioural ──────────────────────────────────────────────────────


def _gate(settings_store_factory, privacy: dict, voice: dict, allowed_hosts: list[str]):
    from aegis_ai.egress import EgressGate

    return EgressGate(
        settings_store=settings_store_factory(voice=voice or None, **privacy),
        allowed_hosts=allowed_hosts,
    )


@pytest.mark.parametrize(
    "label,purpose,closed,opened",
    _LOCK_BEHAVIOUR,
    ids=[entry[0] for entry in _LOCK_BEHAVIOUR],
)
def test_each_egress_lock_changes_the_decision(
    settings_store_factory, label, purpose, closed, opened
):
    """Flipping this lock — and nothing else — must change DENY into ALLOW.

    This is what makes the flag *effective* rather than merely mentioned. The two
    configurations differ in exactly one lock, so the difference in the decision is
    attributable to that lock alone.
    """
    from aegis_ai.egress import EgressDecision, EgressRequest

    # The probe destination is derived from the configuration under test rather than from a
    # second hand-written purpose→host table. The host a lock is meant to permit is exactly
    # the one in `opened`'s allowlist, so the two cannot drift apart — adding a lock to
    # `_LOCK_BEHAVIOUR` is now sufficient, and no third copy of the mapping exists to forget.
    opened_hosts = opened[2]
    assert len(opened_hosts) == 1, (
        f"[{label}] the behaviour table must name exactly one host to probe"
    )
    request = EgressRequest(
        f"https://{opened_hosts[0]}/", purpose=purpose, component="ineffective-flag-detector"
    )

    closed_decision = _gate(settings_store_factory, *closed).check(request)
    opened_decision = _gate(settings_store_factory, *opened).check(request)

    assert closed_decision is EgressDecision.DENY, (
        f"[{label}] the gate allowed egress while the lock was closed"
    )
    assert opened_decision is EgressDecision.ALLOW, (
        f"[{label}] opening this lock (and nothing else) did not change the decision — "
        f"the flag is declared but ineffective"
    )


# ── The detector's own regression test ────────────────────────────────────────


def test_the_detector_reports_a_dead_flag(tmp_path: Path):
    """The detector must fail on a dead flag, or it is itself an ineffective check.

    Builds a throwaway tree containing one read flag and one unread flag, and
    asserts the scanner reports exactly the unread one.
    """
    package = tmp_path / "src" / "sample"
    package.mkdir(parents=True)

    definition = package / "models.py"
    definition.write_text(
        "read_flag: bool = False\nunread_flag: bool = False\n", encoding="utf-8"
    )
    (package / "consumer.py").write_text(
        "if settings.read_flag:\n    pass\n", encoding="utf-8"
    )

    original = globals()["_SRC"]
    try:
        globals()["_SRC"] = tmp_path / "src"
        assert _readers("read_flag", definition_module=definition) == ["sample/consumer.py"]
        assert _readers("unread_flag", definition_module=definition) == []
    finally:
        globals()["_SRC"] = original


# ── Layer 4: the second configuration surface ─────────────────────────────────
#
# Layers 1–3 scan the pydantic settings models. That unit is a choice, and it has a blind
# spot: a whole configuration *surface* can sit outside it. ``aegis_ai/config.py``'s
# ``Config`` dataclass does — filled straight from the environment, never validated by the
# settings store, and invisible to layers 1–3. Measured 2026-10-02: of its 13 fields, 5
# were referenced nowhere outside their own declaration, 1 only by a startup log line, and
# 1 duplicated a settings-model field that the runtime actually reads.
#
# A *mention* is not a reader. ``logger.info("Trigger Engine: %s", "enabled" if
# config.trigger_enabled else "disabled")`` cannot change any decision, so layer 4 counts
# only references that are not inside a logging call. It parses with ``ast`` rather than
# text, which also means a docstring example is not a call site — the reason
# ``TriggerEngine``'s ``Usage:`` example (the line is ``engine = TriggerEngine()``) stayed
# invisible to a call-site scan.
#
# ⚠️ **2026-10-06: the log-only entry left this census.** ``config.trigger_enabled`` was the
# "1 only by a startup log line" counted above. Branch ① of ``DELEGATION.md`` §4 item 24 made
# it the *construction condition* of the event-driven core in ``runtime.py::_build_runtime``,
# so ``_real_readers`` now finds a reader and the equality assertion below would fail while
# the entry stayed. The census is therefore **5**, all "referenced nowhere outside their own
# declaration", and **no** entry is log-only any more. The ``main.py:27`` log line quoted
# above is unchanged and still cannot change a decision — it is now an illustration of the
# rule rather than an instance of it.

_CONFIG_MODULE = _SRC / "aegis_ai" / "config.py"

#: The logging methods whose arguments are a mention rather than a use.
_LOG_METHODS = frozenset(
    {"debug", "info", "warning", "warn", "error", "critical", "exception", "log"}
)

#: ``Config`` fields with no reader that can change anything. Every entry carries its
#: reason, and the equality assertion below fails the moment one gains a real reader.
_INEFFECTIVE_CONFIG_FIELDS: dict[str, str] = {
    "policy_default_deny": (
        "Read nowhere. The live default-deny posture belongs to the policy engine, not to "
        "this environment variable, so setting it changes nothing."
    ),
    "approval_timeout_ms": "Read nowhere — the approval timeout comes from the settings store.",
    "approval_validity_ms": "Read nowhere — approval validity comes from the settings store.",
    "llm_model": "Read nowhere — the model is chosen by the LLM gateway's own configuration.",
    "loop_cooldown_seconds": (
        "Read nowhere — the autonomous loop's cadence comes from the settings store."
    ),
}

#: ``Config`` fields sharing a name with a settings-model field: **two declarations of one
#: fact**, which nothing asserts agree. Recorded rather than merged, because which
#: declaration wins is an owner decision.
_DUPLICATED_CONFIG_FIELDS: dict[str, str] = {
    "autonomous_loop_enabled": (
        "Also on ``AutonomousSettings`` (``settings/models.py:52``). ``runtime.py:122`` gates "
        "on ``settings.autonomous.autonomous_loop_enabled`` (default **True**) while "
        "``main.py:28`` logs this copy (default **False**), so a default start prints "
        "'Autonomous Loop: disabled' while the loop is in fact started. The startup log "
        "reports a different declaration than the runtime obeys."
    ),
}

#: Roots the layer-4 census treats as "read off a ``Config`` object". The dataclass is
#: obtained either through the module singleton (``config = get_config()``) or directly
#: (``Config()``); both spellings are accepted. A read through a *renamed* local
#: (``cfg = get_config(); cfg.audit_path``) is invisible to this scan — the same class of
#: limitation as layer 1's bare-name scan, recorded rather than hidden.
_CONFIG_READER_ROOTS: frozenset[str] = frozenset(
    {"config", "self.config", "self._config", "_config", "get_config()", "Config()"}
)

#: ``Config`` fields with **no reader off a Config object**, hidden from the name-based
#: scan because their name is reused as a parameter or keyword argument elsewhere. This is
#: the layer-4 analogue of layer 1's bare-name blindness: ``_real_readers`` is textual on
#: the bare field name, so a field whose name appears on an unrelated object reads as
#: "read" even though no site touches ``config.<field>``. The census test below asserts the
#: *full* blind spot equals ``_INEFFECTIVE_CONFIG_FIELDS | _DUPLICATED_CONFIG_FIELDS |
#: _NAMESAKE_MASKED_CONFIG_FIELDS`` — one record per field, no second copy of the list.
_NAMESAKE_MASKED_CONFIG_FIELDS: dict[str, str] = {
    "audit_path": (
        "``AEGIS_AUDIT_PATH`` is settable, but nothing reads ``config.audit_path``. Every "
        "``audit_path`` reference in ``src/`` belongs to ``SettingsStore``'s own parameter "
        "and attribute (``settings/store.py:40,43``) or is a keyword argument, so the "
        "name-based scan reports ``settings/store.py`` as a reader and the field escapes "
        "_INEFFECTIVE_CONFIG_FIELDS."
    ),
    "llm_provider": (
        "``AEGIS_LLM_PROVIDER`` is settable, but ``.llm_provider`` appears **0** times in "
        "``src/`` — every ``llm_provider`` mention is a parameter or keyword argument to a "
        "constructor. The name-based scan reports 13 reader modules and the field escapes "
        "_INEFFECTIVE_CONFIG_FIELDS."
    ),
}

#: Settings-model fields whose only references are inside logging calls. Measured empty on
#: 2026-10-02 — layer 1's textual scan cannot tell the difference, so this records the
#: claim explicitly instead of leaving it untested.
_LOG_ONLY_SETTINGS_FIELDS: dict[str, str] = {}


def _config_fields() -> list[str]:
    """Every ``Config`` field, discovered from the dataclass rather than listed."""
    from dataclasses import fields as dataclass_fields

    from aegis_ai.config import Config

    return sorted(f.name for f in dataclass_fields(Config))


def _chains(path: Path) -> set[str]:
    """Every ``Name``-rooted dotted attribute chain in ``path``, as ``a.b.c``.

    Used to say *which object* a field is read from. A bare-name scan cannot: that is
    exactly the blindness the ``autonomous_loop_enabled`` duplication below exploits, where
    one name is declared on two objects and each has a different reader. Only chains rooted
    in a bare ``Name`` are returned, so a chained call or a subscript is simply absent
    rather than mis-prefixed.
    """
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        parts: list[str] = []
        cur: ast.expr = node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
            found.add(".".join(reversed(parts)))
    return found


@functools.lru_cache(maxsize=4)
def _config_chain_roots(src: Path) -> dict[str, frozenset[str]]:
    """``field`` -> roots of non-logging chains ending in ``.<field>``, across ``src``.

    A "root" is the object a field is read from: ``config`` for ``config.audit_path``,
    ``self._config`` for ``self._config.grpc_port``. A base that is a call to a bare
    ``Name`` is spelled ``name()`` so ``get_config().X`` and ``Config().X`` are visible; a
    base that is neither (a subscript, a nested call) is skipped rather than mis-prefixed.
    Lines inside a logging call are dropped — a mention in a log line is not a reader.
    """
    index: dict[str, set[str]] = {}
    for path in sorted(src.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        log_lines: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _is_logging_call(node):
                log_lines.update(sub.lineno for sub in ast.walk(node) if hasattr(sub, "lineno"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Attribute) or node.lineno in log_lines:
                continue
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            elif isinstance(cur, ast.Call) and isinstance(cur.func, ast.Name):
                parts.append(f"{cur.func.id}()")
            else:
                continue
            root, _, field = ".".join(reversed(parts)).rpartition(".")
            if field:
                index.setdefault(field, set()).add(root)
    return {field: frozenset(roots) for field, roots in index.items()}


def _config_reader_roots(field: str) -> set[str]:
    """Roots of non-logging chains ending in ``.<field>`` across ``src/``."""
    return set(_config_chain_roots(_SRC).get(field, ()))


def _config_fields_without_a_config_reader() -> set[str]:
    """``Config`` fields nothing reads *off a Config object*.

    Narrower than ``_real_readers``, which is name-based: a field whose name is reused as a
    parameter or keyword argument elsewhere reads as "read" there even though no site
    touches ``config.<field>``. That gap is the layer-4 analogue of layer 1's bare-name
    blindness, and ``_NAMESAKE_MASKED_CONFIG_FIELDS`` records its live instances.
    """
    return {
        field
        for field in _config_fields()
        if not (_config_reader_roots(field) & _CONFIG_READER_ROOTS)
    }


def _settings_field_names() -> set[str]:
    return {name for model in _settings_models() for name in model.model_fields}


def _is_logging_call(node: ast.Call) -> bool:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id == "print"
    return isinstance(func, ast.Attribute) and func.attr in _LOG_METHODS


@functools.lru_cache(maxsize=4)
def _reference_index(
    src: Path,
) -> tuple[dict[str, frozenset[str]], dict[str, frozenset[str]]]:
    """(real references, log-only references) per identifier, as ``module:line``.

    Keyed on ``src`` so the detector's own regression test, which swaps the tree, gets a
    fresh index rather than the real one.
    """
    real: dict[str, set[str]] = {}
    logged: dict[str, set[str]] = {}
    for path in sorted(src.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(src).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        log_lines: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _is_logging_call(node):
                log_lines.update(sub.lineno for sub in ast.walk(node) if hasattr(sub, "lineno"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                name = node.attr
            elif isinstance(node, ast.Name):
                name = node.id
            else:
                continue
            bucket = logged if node.lineno in log_lines else real
            bucket.setdefault(name, set()).add(f"{rel}:{node.lineno}")
    return (
        {name: frozenset(where) for name, where in real.items()},
        {name: frozenset(where) for name, where in logged.items()},
    )


def _real_readers(field: str, *, definition_module: Path) -> list[str]:
    """Modules with a reference to ``field`` that is *not* inside a logging call."""
    real, _ = _reference_index(_SRC)
    exclude = definition_module.relative_to(_SRC).as_posix()
    return sorted({where.rsplit(":", 1)[0] for where in real.get(field, ())} - {exclude})


def _log_only_readers(field: str, *, definition_module: Path) -> list[str]:
    """Modules that mention ``field`` *only* inside logging calls."""
    real, logged = _reference_index(_SRC)
    exclude = definition_module.relative_to(_SRC).as_posix()
    if {where.rsplit(":", 1)[0] for where in real.get(field, ())} - {exclude}:
        return []
    return sorted({where.rsplit(":", 1)[0] for where in logged.get(field, ())} - {exclude})


def test_the_config_scan_actually_covers_the_config_surface():
    """Guard the layer: an empty discovery would pass every assertion below vacuously."""
    fields = _config_fields()
    assert len(fields) >= 10, f"only {len(fields)} Config fields were discovered"
    assert "trigger_enabled" in fields, "the discovery missed a known field"


def test_every_config_field_has_a_real_reader_or_is_recorded():
    """A value the environment can set but nothing acts on is a lie in the log."""
    for field in _config_fields():
        if field in _INEFFECTIVE_CONFIG_FIELDS:
            continue
        readers = _real_readers(field, definition_module=_CONFIG_MODULE)
        assert readers, (
            f"Config.{field} has no reader outside its own declaration (log-only mentions: "
            f"{_log_only_readers(field, definition_module=_CONFIG_MODULE)}). Wire it, delete "
            f"it, or record it in _INEFFECTIVE_CONFIG_FIELDS with a reason."
        )


def test_the_ineffective_config_fields_are_accounted_for():
    """The headline number for the second surface, asserted rather than reported."""
    ineffective = {
        field
        for field in _config_fields()
        if not _real_readers(field, definition_module=_CONFIG_MODULE)
    }
    assert ineffective == set(_INEFFECTIVE_CONFIG_FIELDS), (
        f"unrecorded: {sorted(ineffective - set(_INEFFECTIVE_CONFIG_FIELDS))}. "
        f"recorded but now read: {sorted(set(_INEFFECTIVE_CONFIG_FIELDS) - ineffective)}."
    )


def test_the_ineffective_config_record_is_accurate():
    """Every entry must name a real field, and a log-only one must say so."""
    unknown = sorted(set(_INEFFECTIVE_CONFIG_FIELDS) - set(_config_fields()))
    assert unknown == [], f"_INEFFECTIVE_CONFIG_FIELDS names fields that do not exist: {unknown}"
    for field, reason in _INEFFECTIVE_CONFIG_FIELDS.items():
        if _log_only_readers(field, definition_module=_CONFIG_MODULE):
            assert "log" in reason.lower(), (
                f"Config.{field} is mentioned only inside a logging call — its reason must "
                f"say so, or a reader will take it for merely unwired."
            )


def test_the_duplicated_config_fields_are_recorded():
    """Two declarations of one fact must be recorded, never silently tolerated."""
    duplicated = set(_config_fields()) & _settings_field_names()
    assert duplicated == set(_DUPLICATED_CONFIG_FIELDS), (
        f"unrecorded: {sorted(duplicated - set(_DUPLICATED_CONFIG_FIELDS))}. "
        f"recorded but no longer duplicated: "
        f"{sorted(set(_DUPLICATED_CONFIG_FIELDS) - duplicated)}."
    )


def test_the_duplicated_config_field_disagrees_with_its_settings_twin(monkeypatch):
    """The reason recorded in ``_DUPLICATED_CONFIG_FIELDS``, measured rather than asserted.

    That entry claims the two ``autonomous_loop_enabled`` declarations **disagree**, so the
    startup log reports a different value than the runtime obeys. Until now the claim lived
    only in a string: either default could move and the reason would keep reading as true.
    This measures it, with the environment variable unset so the *declared* defaults are what
    is compared (``Config`` reads ``AEGIS_AUTONOMOUS_LOOP_ENABLED`` at construction).
    """
    monkeypatch.delenv("AEGIS_AUTONOMOUS_LOOP_ENABLED", raising=False)

    from aegis_ai.config import Config
    from aegis_ai.settings.models import AutonomousSettings

    config_default = Config().autonomous_loop_enabled
    settings_default = AutonomousSettings().autonomous_loop_enabled

    assert config_default is False, (
        f"Config.autonomous_loop_enabled now defaults to {config_default!r} with "
        "AEGIS_AUTONOMOUS_LOOP_ENABLED unset — the recorded reason says False."
    )
    assert settings_default is True, (
        f"AutonomousSettings.autonomous_loop_enabled now defaults to {settings_default!r} — "
        "the recorded reason says True."
    )
    assert config_default != settings_default, (
        "the two `autonomous_loop_enabled` declarations now agree, so the startup log no "
        "longer lies and _DUPLICATED_CONFIG_FIELDS' reason is stale — re-derive it, and "
        "decide whether the duplication still needs recording at all."
    )


def test_the_two_autonomous_loop_declarations_are_read_by_different_sites():
    """The other half: the log and the gate consult *different* declarations.

    Measured with a chain scan (not a bare name), so the claim is about which object is
    read: ``main.py`` logs ``config.autonomous_loop_enabled`` (the dataclass copy, default
    **False**) and ``runtime.py`` gates on ``settings.autonomous.autonomous_loop_enabled``
    (the settings copy, default **True**). Same field name, two objects — which is why the
    name-based layer-4 scan cannot see that the ``Config`` copy has **no reader of its own**:
    ``_real_readers("autonomous_loop_enabled")`` finds the *settings* twin at
    ``runtime.py:122`` and reports a reader. The last two assertions pin that blindness, so
    that fixing the scan (making it object-aware) fails here and forces a revisit rather than
    silently leaving ``Config.autonomous_loop_enabled`` unclassified.
    """
    main_chains = _chains(_SRC / "aegis_ai" / "main.py")
    runtime_chains = _chains(_SRC / "aegis_ai" / "runtime.py")

    assert "config.autonomous_loop_enabled" in main_chains, (
        "main.py no longer logs the Config copy — re-derive the reader split below."
    )
    assert "settings.autonomous.autonomous_loop_enabled" in runtime_chains, (
        "runtime.py no longer gates on the settings copy — re-derive the reader split below."
    )

    assert _log_only_readers("autonomous_loop_enabled", definition_module=_CONFIG_MODULE) == [], (
        "the Config copy is now reported as log-only. If the scan became object-aware, that "
        "is an improvement — re-derive this test and move the field into "
        "_INEFFECTIVE_CONFIG_FIELDS if it is genuinely unread."
    )
    assert _real_readers("autonomous_loop_enabled", definition_module=_CONFIG_MODULE), (
        "the name-based scan no longer reports a real reader for the Config copy, so the "
        "blindness this test documents is gone — delete the last two assertions."
    )


def test_the_config_reader_blind_spot_equals_the_recorded_fields():
    """The full set of fields with no ``config``-rooted reader, asserted not reported.

    Every member is already accounted for by exactly one record — the five ineffective
    fields, the one duplicated field, and the two namesake-masked fields. A *new* field with
    no reader, or a *newly wired* one, moves this set and fails here, forcing the record to
    be updated rather than leaving the blindness untested.
    """
    measured = _config_fields_without_a_config_reader()
    recorded = (
        set(_INEFFECTIVE_CONFIG_FIELDS)
        | set(_DUPLICATED_CONFIG_FIELDS)
        | set(_NAMESAKE_MASKED_CONFIG_FIELDS)
    )
    assert measured == recorded, (
        f"unrecorded: {sorted(measured - recorded)}. "
        f"recorded but now read off a Config object: {sorted(recorded - measured)}."
    )


def test_the_namesake_masked_config_fields_are_hidden_from_the_name_scan():
    """The two fields the name-based scan cannot see: measured, and pinned as hidden.

    ``audit_path`` and ``llm_provider`` are read off no ``Config`` object, yet
    ``_real_readers`` reports a reader for each because their name is reused elsewhere. The
    census membership is asserted per field; the last assertion measures the *masking*
    (that the name-based scan is blind), so that fixing the scan — or wiring the field —
    fails here and forces a revisit instead of silently leaving them unclassified.
    """
    assert set(_NAMESAKE_MASKED_CONFIG_FIELDS) == {"audit_path", "llm_provider"}, (
        "the recorded namesake-masked fields changed — re-derive the census."
    )
    for field, reason in _NAMESAKE_MASKED_CONFIG_FIELDS.items():
        assert field in _config_fields(), f"{field} is not a Config field — reason: {reason}"
        assert field in _config_fields_without_a_config_reader(), (
            f"Config.{field} now has a config-rooted reader — wire/delete/record it and "
            "remove it from _NAMESAKE_MASKED_CONFIG_FIELDS."
        )
        assert field not in _INEFFECTIVE_CONFIG_FIELDS, (
            f"Config.{field} is already recorded as ineffective — one record per field."
        )
        assert field not in _DUPLICATED_CONFIG_FIELDS, (
            f"Config.{field} is already recorded as duplicated — one record per field."
        )
        assert _real_readers(field, definition_module=_CONFIG_MODULE), (
            f"the name-based scan no longer reports a reader for Config.{field}, so it is no "
            "longer masked — move it to _INEFFECTIVE_CONFIG_FIELDS."
        )


def test_no_settings_flag_is_read_only_by_a_log_line():
    """The same rule as layer 4, applied to layer 1's surface.

    Layer 1's textual scan counts any mention, so a settings flag whose only reference is a
    log line would read as "read". This records the measured answer (empty) so the claim is
    tested rather than assumed.
    """
    log_only = {
        key
        for key in _scanned_fields()
        if _log_only_readers(_field_of(key), definition_module=_DEFINITION_MODULE)
        and not _real_readers(_field_of(key), definition_module=_DEFINITION_MODULE)
    }
    assert log_only == set(_LOG_ONLY_SETTINGS_FIELDS), (
        f"unrecorded: {sorted(log_only - set(_LOG_ONLY_SETTINGS_FIELDS))}. "
        f"recorded but now really read: {sorted(set(_LOG_ONLY_SETTINGS_FIELDS) - log_only)}."
    )
