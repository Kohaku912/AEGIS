"""Phase 3 (2026-09-27): one vocabulary for capability safety annotations.

Regression context
------------------
The irreversibility vocabulary used to be declared twice, as bare comments, with
two different value sets:

* ``CapabilityManifest`` / ``PolicyResult``: ``fully_reversible | recoverable |
  difficult | irreversible``
* ``DelegationContext`` / the ``llm_task_interpreter`` prompt: ``reversible |
  difficult | irreversible``

``DelegationPolicyStore.evaluate`` matches dimensions by **exact string
equality**, so a manifest declaring ``recoverable`` put ``recoverable`` into the
delegation context, which never equalled a rule's ``reversible`` — and a
``forbidden`` rule silently stopped firing. Nothing raised, nothing logged.

``aegis_schema.safety_vocab`` is now the single declaration, and
``normalize_reversibility`` the single mapping.
"""

from __future__ import annotations

import pytest

from aegis_schema import safety_vocab as sv


# ── Vocabulary shape ────────────────────────────────────────────────────────

def test_every_vocabulary_is_duplicate_free_and_has_an_unknown_member() -> None:
    for field, allowed in sv.VOCABULARIES.items():
        assert len(set(allowed)) == len(allowed), f"{field} has duplicate members"
        assert sv.UNKNOWN in allowed, f"{field} must allow {sv.UNKNOWN!r}"


def test_the_delegation_vocabulary_is_exactly_the_image_of_the_mapping() -> None:
    """Not a subset: ``reversible`` is delegation-only, and that is the point.

    Every delegation value must be reachable from some manifest value, and no
    manifest value may map outside the delegation vocabulary — otherwise the
    boundary silently invents a dimension value no rule can be written against.
    """
    reachable = {sv.normalize_reversibility(value) for value in sv.REVERSIBILITY}
    assert reachable == set(sv.DELEGATION_REVERSIBILITY)


def test_manifest_field_rejects_the_delegation_only_spelling() -> None:
    """The two surfaces are deliberately asymmetric."""
    assert "reversible" not in sv.REVERSIBILITY
    # A manifest must not use the delegation spelling...
    assert sv.normalize_dimension("reversibility", "reversible") == sv.UNKNOWN
    # ...but the delegation-side normaliser accepts it, because user rules and
    # the llm_task_interpreter prompt were written against that spelling.
    assert sv.normalize_reversibility("reversible") == "reversible"


# ── Normalisation ───────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    ("declared", "expected"),
    [
        (None, "unknown"),
        ("", "unknown"),
        ("   ", "unknown"),
        ("garbage", "unknown"),
        ("fully_reversible", "reversible"),
        ("recoverable", "reversible"),
        ("reversible", "reversible"),  # already-delegation spelling, kept as alias
        ("difficult", "difficult"),
        ("irreversible", "irreversible"),
        ("unknown", "unknown"),
    ],
)
def test_normalize_reversibility_maps_onto_the_delegation_vocabulary(
    declared: object, expected: str
) -> None:
    assert sv.normalize_reversibility(declared) == expected


def test_normalize_reversibility_never_returns_a_permissive_default() -> None:
    """Unrecognised input must not read as 'reversible'."""
    for junk in (None, "", "REVERSIBLE", "fully-reversible", 3, [], {}):
        assert sv.normalize_reversibility(junk) == sv.UNKNOWN


def test_absent_destructive_effects_differs_from_an_empty_list() -> None:
    """``[]`` is the claim 'destroys nothing'; an absent key is 'not stated'."""
    assert sv.normalize_destructive_effects(None) == [sv.UNKNOWN]
    assert sv.normalize_destructive_effects([]) == []
    assert sv.normalize_destructive_effects("file_delete") == ["file_delete"]
    assert sv.normalize_destructive_effects(123) == [sv.UNKNOWN]


def test_normalize_dimension_rejects_an_unknown_field() -> None:
    with pytest.raises(KeyError):
        sv.normalize_dimension("not_a_field", "x")


def test_normalize_dimension_falls_back_to_unknown() -> None:
    assert sv.normalize_dimension("blast_radius", None) == sv.UNKNOWN
    assert sv.normalize_dimension("blast_radius", "single") == "single"
    assert sv.normalize_dimension("blast_radius", "huge") == sv.UNKNOWN


# ── Unset metadata reads as unknown, not as a safe-looking default ──────────

def test_capability_manifest_defaults_are_unknown() -> None:
    from aegis_ai.folder_registry import CapabilityManifest

    manifest = CapabilityManifest()
    assert manifest.ownership_scope == sv.UNKNOWN
    assert manifest.reversibility == sv.UNKNOWN
    assert manifest.data_loss_risk == sv.UNKNOWN
    assert manifest.active_work_loss_risk == sv.UNKNOWN
    assert manifest.blast_radius == sv.UNKNOWN


def test_policy_result_defaults_are_unknown() -> None:
    from policy_engine import PolicyDecision, PolicyResult

    result = PolicyResult(decision=PolicyDecision.ALLOW)
    assert result.ownership_scope == sv.UNKNOWN
    assert result.reversibility == sv.UNKNOWN
    assert result.data_loss_risk == sv.UNKNOWN
    assert result.active_work_loss_risk == sv.UNKNOWN
    assert result.blast_radius == sv.UNKNOWN


def test_delegation_context_defaults_are_unknown() -> None:
    """Every dimension with no conservative end of its range defaults to ``unknown``.

    ``audience`` is the exception, asserted here rather than excluded silently: its
    default is ``private``, which is the *conservative* end of its range, so it is
    not the unfounded claim of harmlessness this test is about.
    """
    from aegis_ai.personal_ai.delegation import DelegationContext

    context = DelegationContext()
    assert context.scope == sv.UNKNOWN
    assert context.reversibility == sv.UNKNOWN
    assert context.content_sensitivity == sv.UNKNOWN
    assert context.audience == "private"


def test_undeclared_content_sensitivity_is_unknown_not_normal(tmp_path) -> None:
    """``content_sensitivity`` is not a ``CapabilityManifest`` field.

    Nothing in a manifest can declare it, so an operation that arrives without one
    must not be described as ``normal`` — that was an unfounded claim that the
    content is not sensitive.
    """
    from aegis_ai.personal_ai.delegation import DelegationPolicyStore

    store = DelegationPolicyStore(data_dir=str(tmp_path))
    decision = store.evaluate(
        "ai-server.memory.search",
        operation_context={"operation_category": "memory"},
    )
    assert decision.dimensions["content_sensitivity"] == sv.UNKNOWN


def test_undeclared_content_sensitivity_no_longer_matches_a_normal_rule(tmp_path) -> None:
    """Same trade-off as ``test_undeclared_reversibility_...``: honest, and looser.

    ``evaluate`` falls through to ``auto_allowed`` when no rule matches, so a rule
    scoped to ``content_sensitivity="normal"`` no longer fires for an operation
    whose sensitivity is undeclared. Pinned so the behaviour cannot drift silently.
    """
    from aegis_ai.personal_ai.delegation import DelegationPolicyStore

    store = DelegationPolicyStore(data_dir=str(tmp_path))
    store.upsert_rule(
        {
            "rule_id": "del_test",
            "capability_pattern": "ai-server.memory.search",
            "decision": "forbidden",
            "content_sensitivity": "normal",
        }
    )
    decision = store.evaluate(
        "ai-server.memory.search",
        operation_context={"operation_category": "memory"},
    )
    assert decision.dimensions["content_sensitivity"] == sv.UNKNOWN
    assert decision.decision == "auto_allowed"


def test_registry_normalizes_unset_annotations_to_unknown(tmp_path) -> None:
    """A manifest that omits the keys must not load as benign."""
    from aegis_ai.folder_registry import FolderCapabilityRegistry

    app = tmp_path / "builtin" / "ai-server" / "demo"
    app.mkdir(parents=True)
    (app / "ping.json").write_text(
        '{"title": "Ping", "server_id": "ai-server", "app_id": "demo", '
        '"action": "ping", "operation_category": "read_only", '
        '"risk": {"level": "low", "side_effects": []}}',
        encoding="utf-8",
    )
    registry = FolderCapabilityRegistry(str(tmp_path))
    manifest = registry.get("ai-server.demo.ping")
    assert manifest is not None
    assert manifest.ownership_scope == sv.UNKNOWN
    assert manifest.reversibility == sv.UNKNOWN
    assert manifest.blast_radius == sv.UNKNOWN
    assert manifest.destructive_effects == [sv.UNKNOWN]


# ── The end-to-end regression this module exists to prevent ─────────────────

def test_manifest_spelling_still_matches_a_rule_written_as_reversible(tmp_path) -> None:
    from aegis_ai.personal_ai.delegation import DelegationPolicyStore

    store = DelegationPolicyStore(data_dir=str(tmp_path))
    store.upsert_rule(
        {
            "rule_id": "del_test",
            "capability_pattern": "ai-server.agora.post",
            "decision": "forbidden",
            "reversibility": "reversible",
        }
    )
    decision = store.evaluate(
        "ai-server.agora.post",
        operation_context={
            "operation_category": "social_communication",
            "reversibility": "recoverable",  # manifest-side spelling
        },
    )
    assert decision.decision == "forbidden", "a recoverable op stopped matching a 'reversible' rule"
    assert decision.dimensions["reversibility"] == "reversible"


def test_rule_written_with_the_manifest_spelling_also_matches(tmp_path) -> None:
    from aegis_ai.personal_ai.delegation import DelegationPolicyStore

    store = DelegationPolicyStore(data_dir=str(tmp_path))
    store.upsert_rule(
        {
            "rule_id": "del_test",
            "capability_pattern": "ai-server.agora.post",
            "decision": "forbidden",
            "reversibility": "recoverable",  # rule written in the manifest spelling
        }
    )
    decision = store.evaluate(
        "ai-server.agora.post",
        operation_context={
            "operation_category": "social_communication",
            "reversibility": "fully_reversible",
        },
    )
    assert decision.decision == "forbidden"


def test_undeclared_reversibility_no_longer_matches_a_reversible_rule(tmp_path) -> None:
    """Fails *closed* in the honest sense: no declaration, no assumption.

    ``evaluate`` falls through to ``auto_allowed`` when no rule matches, so a
    dimension-scoped rule does not fire for an operation whose dimension is
    unknown. That is deliberate — see docs/irreversibility-ledger.md — and is
    pinned here so the behaviour cannot drift silently.
    """
    from aegis_ai.personal_ai.delegation import DelegationPolicyStore

    store = DelegationPolicyStore(data_dir=str(tmp_path))
    store.upsert_rule(
        {
            "rule_id": "del_test",
            "capability_pattern": "ai-server.agora.post",
            "decision": "forbidden",
            "reversibility": "reversible",
        }
    )
    decision = store.evaluate(
        "ai-server.agora.post",
        operation_context={"operation_category": "social_communication"},
    )
    assert decision.dimensions["reversibility"] == sv.UNKNOWN
    assert decision.decision == "auto_allowed"


def test_payment_deny_survives_every_reversibility_spelling(tmp_path) -> None:
    """The one hard stop in this layer must be spelling-independent."""
    from aegis_ai.personal_ai.delegation import DelegationPolicyStore

    store = DelegationPolicyStore(data_dir=str(tmp_path))
    for spelling in ("reversible", "recoverable", "difficult", "irreversible", None):
        context = {"operation_category": "payment"}
        if spelling is not None:
            context["reversibility"] = spelling
        decision = store.evaluate("pc-server.shell.execute", operation_context=context)
        assert decision.decision == "forbidden", f"payment allowed with reversibility={spelling!r}"
