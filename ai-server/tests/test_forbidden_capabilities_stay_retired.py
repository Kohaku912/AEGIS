"""A-1: the settings deny-list stays deleted, and the intents it named are still refused.

`settings/validation.py` used to define ``FORBIDDEN_CAPABILITIES`` — 39 capability ids that
settings must never enable — and three loops comparing them against
``disabled_capabilities``, ``allowlist`` and ``per_capability`` by exact string.
``CapabilityPermissions.allowlist`` existed only to be policed by the second of those loops:
it advertised "Capability IDs explicitly allowed (bypass other checks)" and no code
performed that bypass. Both were deleted on 2026-09-29 (A-1).

The measurements behind that call:

- **0 of the 39 ids resolved** in the live 128-id catalog, so the comparison could never
  match anything. Two dialects: 8 canonical (``pc-server.file.delete``) and 31 short
  (``browser.send_email``, no app segment).
- **0 of 128 live capabilities had a forbidden action** — there was nothing to guard, which
  is why the defect was invisible.
- The gate that actually runs, ``settings/permissions.py::SettingsPermissionGuard``, keys on
  ``capability.id``, i.e. the *canonical* spelling. So the guard recognised only the spelling
  the gate never looks up, and rejected only settings entries that were no-ops anyway.
- One of the three loops had a body of ``pass``: it could not append an error at all.
- ``allowlist`` had no consumer anywhere in ``src/``.

**A deletion pin must do more than assert a constant is gone** — that alone is satisfied by
weakening the system. So this file also drives the real ``ToolBroker`` and reads the live
gate, and fails if the refusal path moves or the gate stops keying on canonical ids. That is
the substantive claim: the list named ids that could not be invoked at all, so deleting it
removed a claim, not a control.

Companion pin for the same blind spot: ``tests/test_guarded_settings_fields.py`` (B-13).
Full measurement and the retired inventory: ``PROJECT_STATUS_REVIEW.md`` §5.12.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from aegis_ai.capability_catalog import CapabilityCatalog
from aegis_ai.settings.models import AEGISSettings, CapabilityPermissions
from policy_engine import PolicyEngine

_AI_SERVER = Path(__file__).resolve().parents[1]
_SRC = _AI_SERVER / "src"
_VALIDATOR = _SRC / "aegis_ai" / "settings" / "validation.py"
_PERMISSIONS = _SRC / "aegis_ai" / "settings" / "permissions.py"
_SETTINGS_JSON = _AI_SERVER / "config" / "settings.json"

#: The retired constant and the retired field. Named here, and nowhere under ``src/``.
_RETIRED_IDENTIFIER = "FORBIDDEN_CAPABILITIES"
_RETIRED_FIELD = "allowlist"

#: Samples of the retired deny-list, spanning both of its dialects. The full 39-entry
#: inventory is in ``PROJECT_STATUS_REVIEW.md`` §5.12 and in the commit that deleted it;
#: these four are kept only so the pin can prove, against the live catalog and the real
#: broker, that the ids it named were never invocable.
_RETIRED_SAMPLE: tuple[str, ...] = (
    "browser.send_email",  # short dialect
    "browser-server.social.send_email",  # canonical dialect, same intent
    "pc-server.file.delete",  # canonical, one of the list's own 8
    "dev-server.build.disable_policy_engine",  # canonical, names a deleted server
)


def _parsed(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8", newline=""))
    except SyntaxError:  # pragma: no cover - a syntax error fails elsewhere
        return None


def _source_files() -> list[Path]:
    return [
        path
        for path in sorted(_SRC.rglob("*.py"))
        if "__pycache__" not in path.parts and "generated" not in path.parts
    ]


def _modules_naming(identifier: str) -> list[str]:
    """Modules under ``src/`` that mention ``identifier`` as a whole word, prose included.

    Whole-word and prose-inclusive on purpose: the claim is that the name is gone from the
    source tree, not merely that it is no longer bound. A docstring promising a deny-list
    would be the same defect in a cheaper costume.
    """
    pattern = re.compile(rf"(?<![\w]){re.escape(identifier)}(?![\w])")
    return [
        path.relative_to(_SRC).as_posix()
        for path in _source_files()
        if pattern.search(path.read_text(encoding="utf-8", errors="replace"))
    ]


def _attribute_reads(tree: ast.AST | None) -> set[str]:
    """Every attribute name read anywhere in ``tree``."""
    if tree is None:
        return set()
    return {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}


def _capabilities_field_accesses(tree: ast.AST | None) -> set[str]:
    """``<something>.capabilities.<field>`` accesses, as field names."""
    if tree is None:
        return set()
    found: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Attribute)
            and node.value.attr == "capabilities"
        ):
            found.add(node.attr)
    return found


def _catalog(tmp_path: Path) -> CapabilityCatalog:
    return CapabilityCatalog(
        capabilities_dir="capabilities",
        apps_dir="apps",
        data_dir=str(tmp_path),
    )


# ── Guards on the detector itself ─────────────────────────────────────────────


def test_the_identifier_scan_can_find_an_identifier() -> None:
    """A scan that can never hit would pass every "is gone" assertion below vacuously."""
    hits = _modules_naming("validate_settings_change")
    assert len(hits) >= 2, f"the identifier scan found {hits}"
    assert "aegis_ai/settings/validation.py" in hits
    assert "aegis_ai/settings/store.py" in hits


def test_the_attribute_scan_can_find_a_capabilities_field() -> None:
    hits = _capabilities_field_accesses(_parsed(_PERMISSIONS))
    assert "per_capability" in hits, f"the attribute scan found {sorted(hits)}"


# ── The artefacts stay deleted ───────────────────────────────────────────────


def test_the_deny_list_name_is_gone_from_source() -> None:
    """Nothing under ``src/`` names it — not in code, not in a docstring."""
    assert _modules_naming(_RETIRED_IDENTIFIER) == []


def test_the_validator_no_longer_polices_a_capability_field() -> None:
    """Any re-added capability policing in the validator fails here, whatever it is called."""
    assert _capabilities_field_accesses(_parsed(_VALIDATOR)) == set()


def test_no_module_reads_a_capabilities_allowlist() -> None:
    readers = [
        path.relative_to(_SRC).as_posix()
        for path in _source_files()
        if _RETIRED_FIELD in _capabilities_field_accesses(_parsed(path))
    ]
    assert readers == []


def test_the_allowlist_field_is_gone_from_the_model() -> None:
    assert _RETIRED_FIELD not in CapabilityPermissions.model_fields
    assert not hasattr(AEGISSettings().capabilities, _RETIRED_FIELD)


def test_the_shipped_settings_file_has_no_allowlist_key() -> None:
    """The shipped JSON is explicit-shaped, so a deleted field must leave the file too."""
    text = _SETTINGS_JSON.read_text(encoding="utf-8")
    assert _RETIRED_FIELD not in text
    assert set(json.loads(text)["capabilities"]) == {
        "disabled_capabilities",
        "per_capability",
        "denylist",
    }


# ── What refuses these intents instead ───────────────────────────────────────


def test_the_retired_ids_are_not_in_the_live_catalog(tmp_path: Path) -> None:
    """The list named ids that could not be invoked at all — it protected nothing."""
    live = {entry["id"] for entry in _catalog(tmp_path).list_for_llm()}
    assert len(live) >= 128, f"the live catalog shrank to {len(live)} ids"
    assert sorted(set(_RETIRED_SAMPLE) & live) == []


def test_the_broker_refuses_an_unregistered_id_before_any_policy_check(tmp_path: Path) -> None:
    """The refusal that actually protects: ``NOT_FOUND`` from the live catalog.

    Drives the real broker against the real ``capabilities/`` tree. ``policy_decision`` is
    asserted empty because the refusal must happen *before* the policy engine — if this path
    ever starts falling through to it, the deleted list would have been load bearing, and
    that is exactly what this pin is for.
    """
    from tool_broker import ExecutionSource, InvokeStatus, ToolBroker, ToolExecutionRequest
    from tool_registry import ToolRegistry

    from aegis_ai.audit import AuditLog

    data_dir = tmp_path / "data"
    broker = ToolBroker(
        registry=ToolRegistry(),
        policy_engine=PolicyEngine(data_dir=str(data_dir)),
        audit_log=AuditLog(path=str(data_dir / "audit.jsonl")),
        catalog=_catalog(tmp_path),
    )
    for cap_id in _RETIRED_SAMPLE:
        result = broker.execute(
            ToolExecutionRequest(
                capability_id=cap_id,
                arguments={},
                source=ExecutionSource.USER_EXPLICIT,
            )
        )
        assert result.status == InvokeStatus.NOT_FOUND, (cap_id, result.status, result.error)
        assert result.policy_decision == "", (cap_id, result.policy_decision)


def test_the_live_gate_still_keys_on_canonical_capability_ids() -> None:
    """The design that made the deny-list's spelling wrong is still the design.

    ``per_capability.get(capability.id)`` in ``evaluate`` and ``.get(capability_id)`` in
    ``is_capability_enabled`` — the receiver and the argument, read from source. If the gate
    ever switched to a short-form key space, this fails and the dialect argument must be
    re-measured rather than assumed.
    """
    lookups = [
        node
        for node in ast.walk(_parsed(_PERMISSIONS))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "get"
        and isinstance(node.func.value, ast.Attribute)
        and node.func.value.attr == "per_capability"
    ]
    assert len(lookups) == 2, f"expected two per_capability lookups, found {len(lookups)}"
    assert sorted({ast.unparse(node.args[0]) for node in lookups}) == [
        "capability.id",
        "capability_id",
    ]


def test_the_pattern_engine_still_denies_the_intent_families() -> None:
    """The control that does cover these intents, pinned behaviourally.

    The deleted list's own comment claimed it was the mechanism for payments and policy
    self-modification. It was not — this is, for four representative intents in canonical
    spelling. If these ever stop matching, the deletion was not as safe as recorded.
    """
    patterns = [re.compile(p) for p in PolicyEngine.EXPLICIT_DENY_PATTERNS]
    for intent in (
        "pc-server.payments.click_payment_button",
        "browser-server.social.purchase_item",
        "pc-server.egress.bypass_egress",
        "dev-server.build.disable_policy_engine",
    ):
        assert any(p.match(intent) for p in patterns), intent
