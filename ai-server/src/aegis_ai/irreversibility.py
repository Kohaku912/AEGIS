"""Post-hoc ledger of irreversible and hard-to-undo operations.

Why this exists
---------------
Approval was retired as a constraint on 2026-09-27 — the only constraint left is
user-information egress, **re-scoped 2026-09-30** so that *unpermitted* disclosure is
forbidden while outbound connections, and disclosure the user permits, are allowed.
Removing a pre-execution gate only works if it is replaced by *post-hoc visibility*,
which is what this module provides. It answers two questions and blocks nothing:

1. **Inventory** — which capabilities can do something that cannot be taken
   back? (derived from the manifests, so it is complete by construction)
2. **Occurrences** — which of those actually ran, when, and with what outcome?
   (joined from the audit log on ``capability_id``)

The inventory is derived from the declarations rather than from a hand-written
list, so a newly added capability cannot silently escape it — the
``test_every_manifest_declares_the_safety_annotation_vocabulary`` test makes an
undeclared capability a test failure.

Severity and ``unknown``
------------------------
``unknown`` is deliberately *not* on the severity scale: it is not a point
between "recoverable" and "difficult", it is the absence of a claim. Callers
choose whether to surface it via ``include_unknown``. It defaults to ``True``
because an operation nobody described is exactly what an owner would want to see,
not what they would want hidden.

Usage::

    from aegis_ai.capability_catalog import CapabilityCatalog
    from aegis_ai import irreversibility

    ledger = irreversibility.summarize(CapabilityCatalog.instance())
    ledger["irreversible"]        # capabilities that cannot be undone
    ledger["by_destructive_effect"]["file_delete"]   # the "what was deleted" view
"""

from __future__ import annotations

from typing import Any, Iterable

from aegis_schema import safety_vocab

__all__ = [
    "DEFAULT_THRESHOLD",
    "SEVERITY",
    "annotation",
    "annotate_policy_result",
    "inventory",
    "irreversible_capability_ids",
    "occurrences",
    "summarize",
]

#: Ordered severity of the manifest reversibility vocabulary. ``unknown`` is
#: intentionally absent — see the module docstring.
SEVERITY: dict[str, int] = {
    "fully_reversible": 0,
    "recoverable": 1,
    "difficult": 2,
    "irreversible": 3,
}

#: What "worth reporting" means by default: cannot be undone, or only at a cost.
DEFAULT_THRESHOLD = "difficult"

_ANNOTATION_FIELDS = (
    "ownership_scope",
    "reversibility",
    "data_loss_risk",
    "active_work_loss_risk",
    "blast_radius",
)


def annotation(manifest: Any) -> dict[str, Any]:
    """Extract the safety annotations from a manifest, normalised.

    Works on a :class:`~aegis_ai.folder_registry.CapabilityManifest`, a
    ``PolicyResult``, or any object exposing the same attribute names. Missing
    or out-of-vocabulary values read as ``unknown``.
    """
    entry: dict[str, Any] = {
        "capability_id": str(getattr(manifest, "capability_id", "") or ""),
        "title": str(getattr(manifest, "title", "") or ""),
        "server_id": str(getattr(manifest, "server_id", "") or ""),
        "operation_category": str(getattr(manifest, "operation_category", "") or ""),
    }
    for field in _ANNOTATION_FIELDS:
        entry[field] = safety_vocab.normalize_dimension(field, getattr(manifest, field, None))
    entry["destructive_effects"] = safety_vocab.normalize_destructive_effects(
        getattr(manifest, "destructive_effects", None)
    )
    entry["side_effects"] = [
        str(item) for item in (getattr(manifest, "side_effects", None) or [])
    ]
    return entry


def annotate_policy_result(policy_result: Any, manifest: Any) -> Any:
    """Copy the manifest's annotations onto a ``PolicyResult``, in place.

    ``PolicyEngine`` only ever sees an ``aegis_schema.Capability``, so it cannot
    fill these itself. ``ToolBroker`` holds both objects and calls this, which is
    what makes a recorded audit entry describe *why* an action was risky without
    having to re-resolve the manifest later.
    """
    if policy_result is None:
        return policy_result
    if manifest is None:
        for field in _ANNOTATION_FIELDS:
            setattr(policy_result, field, safety_vocab.UNKNOWN)
        policy_result.destructive_effects = [safety_vocab.UNKNOWN]
        return policy_result
    for field in _ANNOTATION_FIELDS:
        setattr(
            policy_result,
            field,
            safety_vocab.normalize_dimension(field, getattr(manifest, field, None)),
        )
    policy_result.destructive_effects = safety_vocab.normalize_destructive_effects(
        getattr(manifest, "destructive_effects", None)
    )
    return policy_result


def _severity(value: str) -> int:
    """Severity of a declared reversibility; ``unknown`` sorts above everything.

    Only used for ordering the output. Filtering treats ``unknown`` explicitly,
    so this ranking never decides inclusion.
    """
    return SEVERITY.get(value, len(SEVERITY))


def _validate_threshold(threshold: str) -> str:
    if threshold not in SEVERITY:
        raise ValueError(f"threshold must be one of {sorted(SEVERITY)}, got {threshold!r}")
    return threshold


def _is_reportable(entry: dict[str, Any], threshold: str, include_unknown: bool) -> bool:
    declared = entry["reversibility"]
    if declared == safety_vocab.UNKNOWN:
        return include_unknown
    return SEVERITY[declared] >= SEVERITY[threshold]


def _declares_unknown(entry: dict[str, Any]) -> bool:
    if safety_vocab.UNKNOWN in entry["destructive_effects"]:
        return True
    return any(entry[field] == safety_vocab.UNKNOWN for field in _ANNOTATION_FIELDS)


def _manifests(registry: Any) -> Iterable[Any]:
    if registry is None:
        return ()
    lister = getattr(registry, "list_all", None)
    if not callable(lister):
        return ()
    return lister()


def inventory(
    registry: Any,
    *,
    threshold: str = DEFAULT_THRESHOLD,
    include_unknown: bool = True,
) -> list[dict[str, Any]]:
    """Capabilities at or above ``threshold`` reversibility severity.

    Sorted worst-first, then by id, so the head of the list is the thing most
    worth looking at.
    """
    _validate_threshold(threshold)
    entries = [
        entry
        for entry in (annotation(manifest) for manifest in _manifests(registry))
        if _is_reportable(entry, threshold, include_unknown)
    ]
    entries.sort(key=lambda e: (-_severity(e["reversibility"]), e["capability_id"]))
    return entries


def irreversible_capability_ids(
    registry: Any,
    *,
    threshold: str = DEFAULT_THRESHOLD,
    include_unknown: bool = True,
) -> set[str]:
    """Ids only — the cheap form, for joining against audit entries."""
    return {
        entry["capability_id"]
        for entry in inventory(registry, threshold=threshold, include_unknown=include_unknown)
    }


def summarize(
    registry: Any,
    *,
    threshold: str = DEFAULT_THRESHOLD,
    include_unknown: bool = True,
) -> dict[str, Any]:
    """Full ledger: tallies over every capability, plus the reportable subset.

    ``by_destructive_effect`` is the view the goal-change plan asks for —
    "delete / send / purchase" as groupable buckets rather than free-form prose.
    """
    _validate_threshold(threshold)
    all_entries = [annotation(manifest) for manifest in _manifests(registry)]
    reportable = [
        entry
        for entry in all_entries
        if _is_reportable(entry, threshold, include_unknown)
    ]
    reportable.sort(key=lambda e: (-_severity(e["reversibility"]), e["capability_id"]))

    def _tally(field: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in all_entries:
            counts[entry[field]] = counts.get(entry[field], 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    effect_counts: dict[str, int] = {}
    for entry in all_entries:
        for effect in entry["destructive_effects"]:
            effect_counts[effect] = effect_counts.get(effect, 0) + 1

    return {
        "total_capabilities": len(all_entries),
        "threshold": threshold,
        "include_unknown": include_unknown,
        "by_reversibility": _tally("reversibility"),
        "by_ownership_scope": _tally("ownership_scope"),
        "by_blast_radius": _tally("blast_radius"),
        "by_data_loss_risk": _tally("data_loss_risk"),
        "by_destructive_effect": dict(
            sorted(effect_counts.items(), key=lambda kv: (-kv[1], kv[0]))
        ),
        "irreversible": [
            entry["capability_id"]
            for entry in all_entries
            if entry["reversibility"] == "irreversible"
        ],
        "declares_unknown": sorted(
            entry["capability_id"] for entry in all_entries if _declares_unknown(entry)
        ),
        "reportable": reportable,
    }


def occurrences(
    audit_manager: Any,
    registry: Any,
    *,
    threshold: str = DEFAULT_THRESHOLD,
    include_unknown: bool = True,
    limit: int = 200,
    page: int = 1,
) -> dict[str, Any]:
    """Audit entries whose capability is at or above ``threshold``.

    The audit log already records ``capability_id``, so this is a join rather
    than a new write path: nothing needs to be instrumented for an irreversible
    action to be traceable.
    """
    if audit_manager is None:
        return {"entries": [], "total": 0, "scanned": 0, "threshold": threshold}

    _validate_threshold(threshold)
    watched = irreversible_capability_ids(
        registry, threshold=threshold, include_unknown=include_unknown
    )
    by_id = {entry["capability_id"]: entry for entry in map(annotation, _manifests(registry))}

    page_data = audit_manager.list_recent(limit=limit, page=page)
    raw = page_data.get("entries", []) if isinstance(page_data, dict) else []

    matched: list[dict[str, Any]] = []
    for record in raw:
        cap_id = str(record.get("capability_id") or "")
        if cap_id not in watched:
            continue
        annotations = by_id.get(cap_id, {})
        matched.append(
            {
                "entry_id": record.get("entry_id", ""),
                "timestamp_ms": record.get("timestamp_ms", 0),
                "action": record.get("action", ""),
                "decision": record.get("decision", ""),
                "reason": record.get("reason", ""),
                "risk_level": record.get("risk_level", ""),
                "request_id": record.get("request_id", ""),
                "task_id": record.get("task_id", ""),
                "capability_id": cap_id,
                "reversibility": annotations.get("reversibility", safety_vocab.UNKNOWN),
                "destructive_effects": annotations.get(
                    "destructive_effects", [safety_vocab.UNKNOWN]
                ),
                "blast_radius": annotations.get("blast_radius", safety_vocab.UNKNOWN),
                "detail_summary": record.get("detail_summary", ""),
            }
        )

    return {
        "entries": matched,
        "total": len(matched),
        "scanned": len(raw),
        "threshold": threshold,
        "watched_capabilities": len(watched),
    }
