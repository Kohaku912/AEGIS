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
# ``TriggerEngine``'s "Usage: engine = TriggerEngine()" block stayed invisible.

_CONFIG_MODULE = _SRC / "aegis_ai" / "config.py"

#: The logging methods whose arguments are a mention rather than a use.
_LOG_METHODS = frozenset(
    {"debug", "info", "warning", "warn", "error", "critical", "exception", "log"}
)

#: ``Config`` fields with no reader that can change anything. Every entry carries its
#: reason, and the equality assertion below fails the moment one gains a real reader.
_INEFFECTIVE_CONFIG_FIELDS: dict[str, str] = {
    "trigger_enabled": (
        "Read only by the startup log line (``main.py:27``), which therefore prints "
        "'Trigger Engine: enabled' in a process that never constructs a TriggerEngine — "
        "the survey's G-2. The flag reaches no execution path. Wiring it means building the "
        "event-driven core (an owner decision), so it is recorded rather than deleted or "
        "wired."
    ),
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

#: Settings-model fields whose only references are inside logging calls. Measured empty on
#: 2026-10-02 — layer 1's textual scan cannot tell the difference, so this records the
#: claim explicitly instead of leaving it untested.
_LOG_ONLY_SETTINGS_FIELDS: dict[str, str] = {}


def _config_fields() -> list[str]:
    """Every ``Config`` field, discovered from the dataclass rather than listed."""
    from dataclasses import fields as dataclass_fields

    from aegis_ai.config import Config

    return sorted(f.name for f in dataclass_fields(Config))


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
