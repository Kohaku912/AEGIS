"""The settings edit path enforces every bound the schema declares (B-20, fixed by A-9).

`AEGISSettings` and its sub-models declare numeric bounds on **27** fields — `ge` / `le`,
e.g. `memory.episodic_retention_days` is `ge=1, le=365` and
`autonomous.max_tasks_per_cycle` is `le=20`.

## The defect (measured 2026-09-29, B-20)

Those bounds are enforced at **construction**, and `SettingsStore.update_section` — the
only write path for a live process — used to build the proposed settings with an
**unvalidated `setattr`**::

    for key, value in values.items():
        if hasattr(section_obj, key):
            setattr(section_obj, key, value)      # <-- no validation
    return self.update(current, changed_by, reason)

`update` then ran `validate_settings_change`, which re-implemented exactly **one** of the
27 bounds by hand — `max_autonomous_runs_per_hour > 100`, which merely duplicates that
field's own `le=100` and was reachable *only* because assignment was unvalidated. So **26
of the 27 declared bounds could be exceeded through the settings API, and the value
persisted to disk.**

That was not cosmetic. The bypassable set included the **retention caps**, and those reach
real purge arithmetic — `backup/retention.py` turns `settings.memory.episodic_retention_days`
into `max_age_ms` and prunes against it, so an edit the schema rejects (`le=365`) could
retain episodes for a century.

## The fix (A-9)

`update_section` now builds the proposal by **construction** — it merges the requested keys
into the current dump and runs `AEGISSettings.model_validate`. Re-checking all 27 bounds
inside the validator was rejected: that would put a second copy of the schema in the write
path, which is the duplication this repo keeps finding. Constructing means each bound is
defined exactly once, where it already was.

Measured after the fix: **0 of 27 bounds bypassable, 27 of 27 blocked.**

## What this file is now

A **regression pin on the fix**, not a record of the defect. The sets below are
equality-checked in both directions, so:

* a new bounded field arrives **bypassed** if the write path stops validating, and fails
  here until it is looked at;
* `blocked` must still equal the full recorded set, so a write path that starts refusing
  *everything* fails too — see `test_the_edit_path_still_accepts_legal_edits`, which is the
  non-vacuity guard for that direction (`blocked == all 27` is equally satisfied by a store
  that rejects every edit).

`validate_settings_change` still re-checks its one bound. That copy is now **unreachable
through the store** — construction rejects `> 100` first — and it is deliberately kept: the
function is public (`settings/__init__.py` re-exports it) and its contract is independent
of the store, and removing it would retire the only live instance
`tests/test_guarded_settings_fields.py` exists to record. This file pins the redundancy so
that judgement stays visible.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pydantic

from aegis_ai.settings.models import AEGISSettings
from aegis_ai.settings.store import SettingsStore

_SRC = Path(__file__).resolve().parents[1] / "src"
_VALIDATOR = _SRC / "aegis_ai" / "settings" / "validation.py"

#: The metadata keys a `Field(...)` constraint lands on.
_CONSTRAINT_KEYS = ("ge", "le", "gt", "lt", "min_length", "max_length", "multiple_of")

#: Bounds the write path accepts anyway. **Empty since A-9** — every declared bound is now
#: enforced where it is declared. Equality-checked, so a bypass reappearing fails here.
_RECORDED_BYPASSED: frozenset[str] = frozenset()

#: Every bounded settings field the edit path refuses to exceed. Listed rather than derived
#: from `PROBES`, because an equality between two things computed from one source cannot
#: fail — the point is that a *new* bounded field has to be added here deliberately.
_RECORDED_ENFORCED: frozenset[str] = frozenset(
    {
        "servers.health_check_interval_seconds",
        "autonomous.max_autonomous_runs_per_hour",
        "autonomous.max_autonomous_runs_per_day",
        "autonomous.cooldown_seconds",
        "autonomous.evaluation_interval_seconds",
        "autonomous.min_action_interval_seconds",
        "autonomous.max_actions_per_hour",
        "autonomous.max_tasks_per_cycle",
        "autonomous.min_llm_interval_seconds",
        "autonomous.social_poll_interval_seconds",
        "autonomous.browser_exploration_budget_per_day",
        "autonomous.normal_interruption_budget_per_hour",
        "autonomous.approval_proposal_limit",
        "autonomous.follow_up_timeout",
        "agents.max_concurrent",
        "agents.timeout_seconds",
        "intake.requires_agent_threshold",
        "intake.dedup_window_size",
        "intake.dedup_novelty_threshold",
        "intake.max_importance",
        "memory.episodic_retention_days",
        "privacy.screenshot_retention_hours",
        "privacy.notification_text_retention_hours",
        "privacy.personal_data_event_retention_days",
        "privacy.personal_data_screenshot_retention_hours",
        "privacy.personal_data_media_retention_hours",
        "voice.voice_data_retention_hours",
    }
)

#: The bounds `validate_settings_change` re-checks by hand. Recorded so that *extending* the
#: validator (a plausible but rejected repair) turns this file red instead of making it stale.
_RECORDED_RECHECKED: frozenset[str] = frozenset({"autonomous.max_autonomous_runs_per_hour"})


def _constraints(field_info: object) -> dict[str, object]:
    out: dict[str, object] = {}
    for meta in getattr(field_info, "metadata", ()):
        for key in _CONSTRAINT_KEYS:
            value = getattr(meta, key, None)
            if value is not None:
                out[key] = value
    return out


def _constrained_fields() -> dict[str, tuple[dict[str, object], object]]:
    """Every bounded settings field, as ``section.field -> (constraints, annotation)``.

    Discovered from the models themselves, so a new bounded field is covered the moment
    it is declared.
    """
    found: dict[str, tuple[dict[str, object], object]] = {}
    for section, field in AEGISSettings.model_fields.items():
        sub = field.annotation
        for name, sub_field in getattr(sub, "model_fields", {}).items():
            cons = _constraints(sub_field)
            if cons:
                found[f"{section}.{name}"] = (cons, sub_field.annotation)
    return found


def _violating_value(cons: dict[str, object], annotation: object) -> object | None:
    """A value these constraints reject, derived from the constraints themselves."""
    is_float = annotation is float or "float" in str(annotation)
    if "le" in cons:
        return float(cons["le"]) + 1.0 if is_float else int(cons["le"]) + 1
    if "ge" in cons:
        return float(cons["ge"]) - 1.0 if is_float else int(cons["ge"]) - 1
    if "lt" in cons:
        return float(cons["lt"])  # type: ignore[arg-type]
    if "gt" in cons:
        return float(cons["gt"])  # type: ignore[arg-type]
    return None


def _legal_value(cons: dict[str, object], current: object) -> object:
    """A value these constraints *accept*, derived from the constraints themselves.

    Prefers the boundary itself (`le` / `ge` are inclusive), because an off-by-one in the
    construction path would reject exactly those.
    """
    if "le" in cons:
        return cons["le"]
    if "ge" in cons:
        return cons["ge"]
    return current


def _sub_model(section: str) -> type:
    return type(getattr(AEGISSettings(), section))


def _probes() -> dict[str, tuple[str, str, object]]:
    """``section.field -> (section, field, value the schema rejects)``."""
    out: dict[str, tuple[str, str, object]] = {}
    for key, (cons, annotation) in _constrained_fields().items():
        value = _violating_value(cons, annotation)
        if value is None:
            continue
        section, name = key.split(".", 1)
        out[key] = (section, name, value)
    return out


PROBES = _probes()


def _new_store(tmp_path: Path) -> SettingsStore:
    return SettingsStore(
        path=str(tmp_path / "settings.json"), audit_path=str(tmp_path / "audit.jsonl")
    )


def _validator_reads() -> set[str]:
    """Settings field names ``validate_settings_change`` reads, from its own AST.

    Attribute access rather than a name search, so the validator *declaring* nothing and
    the model *defining* the fields do not count as reading them.
    """
    tree = ast.parse(_VALIDATOR.read_text(encoding="utf-8"))
    sections = set(AEGISSettings.model_fields)
    found: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Attribute)
            and node.value.attr in sections
        ):
            found.add(node.attr)
    return found


def _observe(tmp_path: Path) -> dict[str, str]:
    """Drive the real store once per probe; classify the outcome.

    ``"bypassed"`` means the edit path accepted a value the schema rejects **and** the
    value is what the store now holds — checked, so a silently coerced value cannot be
    mistaken for a bypass.
    """
    store = _new_store(tmp_path)
    outcome: dict[str, str] = {}
    for key, (section, name, value) in PROBES.items():
        errors = store.update_section(section, {name: value}, changed_by="pin")
        persisted = getattr(getattr(store.get(), section), name)
        outcome[key] = "bypassed" if (not errors and persisted == value) else "blocked"
    return outcome


# ── Guards on the detector itself ─────────────────────────────────────────────


def test_the_probe_values_are_actually_rejected_by_the_schema() -> None:
    """A probe the schema *accepts* would prove nothing about the edit path."""
    assert len(PROBES) >= 20, f"only {len(PROBES)} constrained fields were discovered"
    not_rejected: list[str] = []
    for key, (section, name, value) in PROBES.items():
        try:
            _sub_model(section)(**{name: value})
        except pydantic.ValidationError:
            continue
        not_rejected.append(key)
    assert not_rejected == [], (
        f"these probe values are NOT rejected at construction, so the bypass claim is "
        f"meaningless for them: {sorted(not_rejected)}"
    )


def test_the_scan_finds_the_validator_reads() -> None:
    """The validator must be seen reading something, or 're-checked' is empty by accident."""
    reads = _validator_reads()
    assert "max_autonomous_runs_per_hour" in reads
    assert "camera_snapshot_enabled" in reads


def test_the_recorded_sets_cover_every_discovered_field() -> None:
    """The two records must partition the discovered fields, or one is silently short."""
    assert set(PROBES) == set(_RECORDED_ENFORCED) | set(_RECORDED_BYPASSED), (
        "the recorded sets do not cover the discovered bounded fields.\n"
        f"  unrecorded : {sorted(set(PROBES) - _RECORDED_ENFORCED - _RECORDED_BYPASSED)}\n"
        f"  stale      : {sorted((_RECORDED_ENFORCED | _RECORDED_BYPASSED) - set(PROBES))}"
    )


# ── The invariant ─────────────────────────────────────────────────────────────


def test_the_edit_path_accepts_every_bound_the_validator_does_not_recheck(
    tmp_path: Path,
) -> None:
    """The headline: the schema's bounds are the write path's bounds.

    Equality both ways. A bounded field the write path stops validating arrives
    **bypassed** and fails here; and if the write path is loosened, `blocked` shrinks and
    fails too — a change in which settings edits are accepted must not land silently.
    """
    observed = _observe(tmp_path)
    bypassed = {k for k, v in observed.items() if v == "bypassed"}
    blocked = {k for k, v in observed.items() if v == "blocked"}

    assert bypassed == set(_RECORDED_BYPASSED), (
        "the set of schema bounds the edit path ignores changed.\n"
        f"  newly bypassable : {sorted(bypassed - _RECORDED_BYPASSED)}\n"
        f"  no longer bypassable : {sorted(_RECORDED_BYPASSED - bypassed)}\n"
        "A field arriving here means the write path stopped constructing a validated "
        "model — that is B-20 coming back."
    )
    assert blocked == set(_RECORDED_ENFORCED), (
        f"the edit path now enforces {sorted(blocked)}; the record says "
        f"{sorted(_RECORDED_ENFORCED)}. Update both sets together."
    )


def test_the_edit_path_still_accepts_legal_edits(tmp_path: Path) -> None:
    """Non-vacuity for the 'blocked' direction, including the inclusive boundaries.

    `blocked == all 27` is also satisfied by a store that refuses *every* edit, so this
    has to show a legal value landing for each constrained field. The boundary is used
    deliberately: an off-by-one in the construction path would reject `le` / `ge` exactly.
    """
    store = _new_store(tmp_path)
    rejected: dict[str, list[str]] = {}
    for key, (cons, _annotation) in _constrained_fields().items():
        section, name = key.split(".", 1)
        current = getattr(getattr(store.get(), section), name)
        legal = _legal_value(cons, current)
        errors = store.update_section(section, {name: legal}, changed_by="pin")
        if errors:
            rejected[key] = errors
        elif getattr(getattr(store.get(), section), name) != legal:
            rejected[key] = [f"accepted but stored {current!r} instead of {legal!r}"]
    assert rejected == {}, (
        f"the edit path refused (or mis-stored) values the schema accepts: {rejected}. "
        "The 'blocked' set above is meaningless if every edit is refused."
    )


def test_the_validator_rechecks_a_single_bound() -> None:
    """Why the write path cannot rely on the validator: it re-checks one hand-copied bound.

    Kept after A-9 even though construction now rejects `> 100` first — the copy is
    redundant, and this records that it is still exactly one bound rather than a second
    copy of the schema.
    """
    reads = _validator_reads()
    constrained_names = {key.split(".", 1)[1] for key in PROBES}
    rechecked = reads & constrained_names
    assert rechecked == {name.split(".", 1)[1] for name in _RECORDED_RECHECKED}, (
        f"the validator re-checks {sorted(rechecked)} of the {len(PROBES)} bounded fields. "
        "The record says exactly one. Extending the validator to re-check more bounds is "
        "a *second copy* of the schema in the write path — the write path constructs a "
        "validated model instead (see this file's docstring)."
    )


# ── Why it matters: the bound reaches a real decision ─────────────────────────


class _RecordingEpisodic:
    """Minimal stand-in for the episodic backend; records the cutoff it is pruned with."""

    def __init__(self) -> None:
        self.max_age_ms: int | None = None

    def prune_expired(self, max_age_ms: int | None = None) -> int:
        self.max_age_ms = max_age_ms
        return 0

    def list_recent(self, limit: int) -> list:  # noqa: ARG002
        return []


def test_an_out_of_range_retention_cap_is_refused_and_the_cutoff_stays_legal(
    tmp_path: Path,
) -> None:
    """The bypass reached a real decision, so the fix has to reach it too.

    `backup/retention.py` reads `settings.memory.episodic_retention_days` and multiplies
    it by `86400 * 1000`. Before A-9 an out-of-range value was stored and became the prune
    cutoff; now the edit is refused, so the cutoff is the value the schema allows. The two
    halves are still joined by the settings object rather than by a scan, which is what
    makes this behavioural.
    """
    from aegis_ai.backup.retention import RetentionManager

    store = _new_store(tmp_path)
    declared_cap = 365
    over = declared_cap * 100

    errors = store.update_section(
        "memory", {"episodic_retention_days": over}, changed_by="pin"
    )
    assert errors, (
        "the edit path accepted an out-of-range retention cap — the write path stopped "
        "constructing a validated model. If that is deliberate, update "
        "_RECORDED_BYPASSED and say so in the commit message."
    )
    assert str(declared_cap) in " ".join(errors), (
        f"the refusal does not name the bound it enforced: {errors}"
    )

    backend = _RecordingEpisodic()
    RetentionManager(episodic_memory=backend, settings_store=store).cleanup_expired()

    stored = store.get().memory.episodic_retention_days
    assert backend.max_age_ms == stored * 86400 * 1000, (
        "the retention manager did not use the stored value — if it now clamps instead, "
        "the bound no longer reaches the decision through the store and this test should "
        "assert the clamp."
    )
    assert backend.max_age_ms <= declared_cap * 86400 * 1000, (
        "the prune cutoff exceeds the schema's cap, so the bypass is back"
    )


def test_the_retention_manager_does_not_read_every_retention_it_claims() -> None:
    """`RetentionManager`'s docstring names four retentions; `self._audit` is read never.

    Recorded rather than repaired: the audit/notification retention work is its own
    decision, but the docstring's four-item claim is measurable today.
    """
    source = (_SRC / "aegis_ai" / "backup" / "retention.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    constructor = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "__init__"
    )
    stored = {
        target.attr
        for node in ast.walk(constructor)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
    }
    assert {"_audit", "_episodic", "_settings", "_store"} <= stored, (
        "the constructor no longer stores the backends this test reasons about"
    )

    # `cleanup_expired` is the only method that deletes anything; `_audit` must not be
    # read there, because if it were, audit retention would be implemented.
    cleanup = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "cleanup_expired"
    )
    read_in_cleanup = {
        node.attr
        for node in ast.walk(cleanup)
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
    }
    assert "_audit" not in read_in_cleanup, (
        "`cleanup_expired` now consults `self._audit` — audit retention has been "
        "implemented, so the docstring's claim is no longer false. Update this test."
    )
    uses_notification = any(
        (
            isinstance(node, ast.Attribute)
            and node.attr == "notification_text_retention_hours"
        )
        or (
            isinstance(node, ast.Name)
            and node.id == "notification_text_retention_hours"
        )
        for node in ast.walk(cleanup)
    )
    assert not uses_notification, (
        "`cleanup_expired` now uses the notification retention cap — it was previously "
        "only *reported* by `get_retention_status()`. Update this test."
    )
