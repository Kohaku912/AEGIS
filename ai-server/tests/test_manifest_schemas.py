"""Validate all capability manifests against Pydantic boundary models."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aegis_ai.folder_registry import FolderCapabilityRegistry
from aegis_schema import safety_vocab


def _capabilities_root() -> Path:
    here = Path(__file__).resolve()
    return here.parents[1] / "capabilities"


def test_all_builtin_manifests_load_without_registry_errors() -> None:
    root = _capabilities_root()
    registry = FolderCapabilityRegistry(str(root))
    errors = registry.errors()
    assert not errors, f"manifest load errors: {errors[:5]}"
    manifests = registry.list_all(origin="builtin")
    assert manifests, "expected builtin capability manifests"


def test_manifest_input_schema_is_object_when_present() -> None:
    root = _capabilities_root()
    for path in root.rglob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        schema = data.get("input_schema") or data.get("input") or {}
        if schema:
            assert schema.get("type") in {"object", None}, f"{path} input schema must be object"


def test_every_manifest_declares_the_safety_annotation_vocabulary() -> None:
    """Phase 3 (2026-09-27): irreversibility metadata must be explicit.

    An absent key used to read as a safe-looking default (``blast_radius=single``,
    ``data_loss_risk=none``, ``reversibility=reversible``), so an unclassified
    capability was indistinguishable from a benign one. All six keys must now be
    present and drawn from ``aegis_schema.safety_vocab``.
    """
    root = _capabilities_root()
    missing: list[str] = []
    invalid: list[str] = []
    for path in sorted(root.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rel = path.relative_to(root).as_posix()
        for field, allowed in safety_vocab.VOCABULARIES.items():
            if field not in data:
                missing.append(f"{rel}:{field}")
                continue
            declared = data[field]
            for value in declared if isinstance(declared, list) else [declared]:
                if value not in allowed:
                    invalid.append(f"{rel}:{field}={value!r}")
    assert not missing, f"manifests missing safety annotations: {missing[:10]}"
    assert not invalid, f"out-of-vocabulary safety annotations: {invalid[:10]}"


def test_irreversible_manifests_declare_what_is_lost() -> None:
    """``irreversible`` paired with ``data_loss_risk=none`` is a contradiction."""
    root = _capabilities_root()
    offenders = [
        path.relative_to(root).as_posix()
        for path in sorted(root.rglob("*.json"))
        if (data := json.loads(path.read_text(encoding="utf-8"))).get("reversibility")
        == "irreversible"
        and data.get("data_loss_risk") == "none"
    ]
    assert not offenders, f"irreversible but claims no data loss: {offenders}"


def test_drain_does_not_claim_to_be_read_only() -> None:
    """``pc-server.personal_data.drain`` empties the buffer it reads.

    ``pc-server/src/personal_data.rs`` implements it as ``guard.buffer.drain(..)``,
    so the events it returns are the only copy: the operation mutates PC-side state
    and cannot be undone. It used to be declared ``read_only`` /
    ``fully_reversible`` / no side effects, which described the opposite — the
    ledger doc listed it under "Deferred… worth verifying against the Rust
    implementation" until that verification was done (2026-09-28).
    """
    root = _capabilities_root()
    path = root / "builtin" / "pc-server" / "personal_data" / "drain.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["operation_category"] != "read_only"
    assert data["reversibility"] != "fully_reversible"
    assert data["destructive_effects"], "a consuming read must say what it consumes"
    assert data["risk"]["side_effects"], "emptying the buffer is a side effect"


def test_drain_classification_still_matches_the_rust_implementation() -> None:
    """Pin the assumption the classification above rests on.

    This is a reminder, not a proof: if ``drain()`` stops emptying the buffer, the
    manifest has to be revisited, and this test is what says so.
    """
    rust = Path(__file__).resolve().parents[2] / "pc-server" / "src" / "personal_data.rs"
    if not rust.exists():
        pytest.skip("pc-server sources are not present in this checkout")
    assert "buffer.drain(" in rust.read_text(encoding="utf-8")


def _declared_risk_labels() -> dict[str, list[str]]:
    """Every ``risk.level`` label a manifest declares, mapped to its users."""
    root = _capabilities_root()
    used: dict[str, list[str]] = {}
    for path in sorted(root.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        label = data.get("risk", {}).get("level")
        if label is None:
            continue
        used.setdefault(str(label), []).append(path.relative_to(root).as_posix())
    return used


def test_every_manifest_risk_label_is_registered() -> None:
    """A manifest label that is absent from ``_RISK_LABEL_TO_NAME`` is a silent downgrade.

    ``normalize_risk_label()`` does not raise on an unknown label — it returns the
    default ``READ_ONLY``, which ``PolicyEngine.DEFAULT_RISK_MAP`` maps to ``ALLOW``.
    ``SAFE_ACTION`` (and every tier above it) maps to ``ALLOW_WITH_AUDIT`` instead.
    So an unregistered label makes a capability *less* visible than its author
    intended, silently.

    This is not hypothetical. ``audited_action`` was missing until 2026-09-28, so 12
    capabilities that declare ``audited_action`` — ``browser-server.form.submit``,
    ``social.post``, ``account.create``, ``file.upload``, ``element.click``,
    ``form.fill``, ``social.react``, ``page.browse``, ``android-server.ui.tap`` /
    ``ui.swipe`` / ``ui.type_text`` and ``pc-server.file.write`` — resolved to
    ``READ_ONLY`` and executed **without** the audit their label promises. A page
    *navigate* (``safe``) was audited; a form submit was not.

    The check is deliberately label-vs-registry only: it needs no exclusion list, so
    it cannot develop one as a blind spot.
    """
    from aegis_ai.capability_catalog import _RISK_LABEL_TO_NAME

    used = _declared_risk_labels()
    assert used, "no manifests declared a risk level — this test would be vacuous"

    unregistered = {label: users for label, users in used.items() if label.strip().lower() not in _RISK_LABEL_TO_NAME}
    assert not unregistered, (
        "manifest risk labels missing from _RISK_LABEL_TO_NAME "
        "(they silently fall back to READ_ONLY => PolicyDecision.ALLOW): "
        + "; ".join(f"{label!r} used by {users[:3]}" for label, users in unregistered.items())
    )


def test_audited_action_is_classified_as_safe_action() -> None:
    """``audited_action`` must reach ``ALLOW_WITH_AUDIT``, not ``ALLOW``.

    Guards the specific fix from silently reverting, and pins the decision rather
    than just the label mapping — the label is only a means to that end.
    """
    from aegis_ai.capability_catalog import risk_level_from_label
    from aegis_schema.models import RiskLevel

    assert risk_level_from_label("audited_action") == RiskLevel.SAFE_ACTION

    root = _capabilities_root()
    declared = {
        path.relative_to(root).as_posix()
        for path, data in ((p, json.loads(p.read_text(encoding="utf-8"))) for p in root.rglob("*.json"))
        if data.get("risk", {}).get("level") == "audited_action"
    }
    assert len(declared) >= 10, (
        f"only {len(declared)} manifests declare 'audited_action' — if the label was "
        "retired, update this test and the dict comment rather than deleting it blindly"
    )
