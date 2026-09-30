"""The generic ineffective-flag detector.

The retired P0-2 concern was a settings flag that exists but is never read — the
shape of the original ``web_search_allowed`` bug, and of ``check_domain()`` in the
browser server. Phase 1 fixed the known instances and added a behavioural test for
one of them. This module generalises the detector: it enumerates the settings
surface and fails when a flag has no reader.

Three layers, weakest to strongest:

1. **Static** — every flag on every settings model must be referenced somewhere in
   ``src/`` outside its own definition. Fields that are not read must appear in one
   of the two maps below *with a written reason*, so a newly added dead flag fails
   the suite instead of shipping quietly.
2. **Enforcement** — every egress lock must be read by the enforcement point
   (``aegis_ai/egress/gate.py``). A flag read only by a dashboard is not a lock.
3. **Behavioural** — flipping each lock must actually change a gate decision.
   This is the only layer that proves the flag is *effective* rather than merely
   *mentioned*.

The models are **discovered, not listed**. A hand-maintained model list is how this
detector missed ``AutonomyProfile`` entirely for months: the settings surface grew
and the list did not. Discovery means a new model is covered the moment it is
declared, and ``test_the_scan_actually_covers_the_settings_surface`` asserts the
discovery still finds every model.

Known limitation of layer 1: the reader scan is textual on the bare field name, so
a field whose name also appears in an unrelated module reads as "read". Prefer
distinctive field names; a name like ``profile`` or ``enabled`` cannot be checked
this way.

The detector is itself tested (``test_the_detector_reports_a_dead_flag``) so it
cannot rot into a no-op — the inverse of the bug it exists to catch.
"""

from __future__ import annotations

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
        "path can be gated on it. Kept in the schema so the shipped settings file stays "
        "valid; wiring it is part of the voice workstream, not the constraint. It is "
        "*not* an egress risk — it cannot transmit anything."
    ),
}

# ── Declared but unowned ──────────────────────────────────────────────────────
#
# This is an inventory of debt, **not** a set of approvals. These fields are not
# "intentionally unread"; they are unread because nobody owns the feature they
# configure. They are recorded here so the number is visible and pinned rather than
# hidden, and so a *new* dead flag still fails the suite. Every entry should be
# resolved — wired, or deleted — not left. Tracked in PROJECT_STATUS_REVIEW.md §3.

_AUTONOMOUS = (
    "The autonomous loop runs on hardcoded budgets and intervals; no code path reads "
    "this field, so editing it in the settings file changes nothing. Unowned: wire it "
    "into the loop, or delete it."
)
_AGENT = (
    "The agent runner does not consult settings for this; profile selection and "
    "concurrency are fixed in code. Unowned: wire it, or delete it."
)
_INTAKE = (
    "The intake pipeline does not consult settings for this; classification and "
    "deduplication use fixed values. Unowned: wire it, or delete it."
)
_MEMORY = (
    "The memory subsystem does not consult settings for this; the behaviour is fixed "
    "in code. Unowned: wire it, or delete it."
)
_SERVER = (
    "Server connection behaviour is fixed in code and not read from settings. "
    "Unowned: wire it, or delete it."
)

_UNOWNED_DEBT: dict[str, str] = {
    "AutonomousSettings.approval_proposal_limit": _AUTONOMOUS,
    "AutonomousSettings.browser_exploration_budget_per_day": _AUTONOMOUS,
    "AutonomousSettings.daily_briefing_enabled": _AUTONOMOUS,
    "AutonomousSettings.follow_up_timeout": _AUTONOMOUS,
    "AutonomousSettings.max_actions_per_hour": _AUTONOMOUS,
    "AutonomousSettings.max_autonomous_runs_per_day": _AUTONOMOUS,
    "AutonomousSettings.normal_interruption_budget_per_hour": _AUTONOMOUS,
    "AutonomousSettings.research_watch_enabled": _AUTONOMOUS,
    "AutonomousSettings.self_dev_proposal_enabled": _AUTONOMOUS,
    "AutonomousSettings.social_poll_interval_seconds": _AUTONOMOUS,
    "AgentSettings.default_profile": _AGENT,
    "AgentSettings.max_concurrent": _AGENT,
    "IntakeSettings.classifier_profile": _INTAKE,
    "IntakeSettings.dedup_novelty_threshold": _INTAKE,
    "IntakeSettings.dedup_window_size": _INTAKE,
    "IntakeSettings.max_importance": _INTAKE,
    "MemorySettings.procedural_learning_enabled": _MEMORY,
    "MemorySettings.reflection_enabled": _MEMORY,
    "MemorySettings.semantic_memory_enabled": _MEMORY,
    "MemorySettings.sensitive_data_storage_enabled": (
        "Reads like a privacy control and is not one: nothing reads it, so turning it "
        "off changes no behaviour. Under the single constraint the *egress* gate is what "
        "actually protects user data, and that gate is separately enforced and "
        "mutation-proved. Unowned: wire it to real storage policy, or delete it — a "
        "privacy switch that does nothing is worse than no switch."
    ),
    "ServerSettings.health_check_interval_seconds": _SERVER,
    "ServerSettings.reconnect_policy": _SERVER,
}

#: The egress locks, as (settings path, purpose used to probe the gate).
_EGRESS_LOCKS: tuple[tuple[str, str], ...] = (
    ("privacy.external_egress_allowed", "llm.chat"),
    ("privacy.egress_allowed_hosts", "llm.chat"),
    ("privacy.external_llm_allowed", "llm.chat"),
    ("privacy.web_search_allowed", "web.search"),
    ("voice.external_voice_api_allowed", "voice.tts"),
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
    assert len(fields) >= 90, f"only {len(fields)} settings flags were scanned"
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

    destination = "https://api.deepseek.com/v1" if purpose == "llm.chat" else None
    if destination is None:
        destination = {
            "web.search": "https://html.duckduckgo.com/html/",
            "voice.tts": "https://speech.platform.bing.com",
        }[purpose]
    request = EgressRequest(destination, purpose=purpose, component="ineffective-flag-detector")

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
