"""Validation rules for settings changes.

Ensures settings changes cannot weaken safety guarantees.

## Why this module no longer polices capability ids (A-1, deleted 2026-09-29)

It used to define a deny-list of 39 capability ids that settings must never enable, plus
three loops comparing it against ``disabled_capabilities``, ``allowlist`` and
``per_capability`` by exact string. The constant and all three loops were deleted.
Measured before that call:

- **0 of the 39 ids resolved** in the live 128-id catalog, so the comparison could never
  match anything. The entries came in two dialects: 8 canonical (``pc-server.file.delete``)
  and 31 short (``browser.send_email``, no app segment).
- **0 of 128 live capabilities had a forbidden action**, so there was nothing to guard —
  which is exactly why the defect was invisible.
- The gate that actually runs, ``settings/permissions.py::SettingsPermissionGuard``, keys
  on ``capability.id`` — the *canonical* spelling. So the guard recognised only the
  spelling the gate never looks up, and rejected only settings entries that were no-ops
  anyway.
- One of the three loops had a body of ``pass``: it could not append an error at all.

The intents the list named are held by mechanisms that do read the live id space:
``policy_engine.EXPLICIT_DENY_PATTERNS`` (the payment, egress-bypass and
policy-self-modification intents), the egress gate at the network layer for the egress
intents, ``DEFAULT_RISK_MAP`` (FORBIDDEN -> DENY) for anything that declares itself
forbidden, and the browser prompts for CAPTCHA/TOS. A deny-list that could only match ids
nobody can write was a *claim* of a control, not a control, so it was deleted rather than
repaired.

The retired constant's name is deliberately absent from this file — and from every other
module under ``src/`` — so the invariant is a plain text search rather than an AST
argument. ``tests/test_forbidden_capabilities_stay_retired.py`` holds the full measurement,
asserts the name appears nowhere under ``src/``, and pins the controls that replaced it.

What remains below is unrelated to capability ids and does have a live effect.
"""

from __future__ import annotations

from aegis_ai.settings.models import AEGISSettings


def validate_settings_change(
    current: AEGISSettings,
    proposed: AEGISSettings,
) -> list[str]:
    """Validate a proposed settings change.

    Returns a list of validation errors. Empty list means valid.
    """
    errors: list[str] = []

    # Check privacy settings
    if proposed.privacy.camera_snapshot_enabled and not current.privacy.camera_snapshot_enabled:
        errors.append("Enabling camera snapshot requires explicit user confirmation")

    # Check autonomous limits.
    #
    # Redundant since A-9 (2026-09-29). `SettingsStore.update_section` now builds its
    # proposal by *construction*, and this field declares `le=100`, so an out-of-range
    # value is rejected before this function is reached — measured, the check is
    # unreachable through every store path (`update`, `update_section`, `import_json`).
    # Kept deliberately: this function is public (`settings/__init__.py` re-exports it) and
    # its contract is independent of the store, and removing the only bound it re-checks
    # would retire the single live instance `tests/test_guarded_settings_fields.py` exists
    # to record. **Do not extend it to re-check more bounds** — that would put a second
    # copy of the schema in the write path, which is the duplication
    # `tests/test_settings_edit_path_enforces_schema_bounds.py` exists to prevent.
    if proposed.autonomous.max_autonomous_runs_per_hour > 100:
        errors.append("Max autonomous runs per hour cannot exceed 100")

    return errors
