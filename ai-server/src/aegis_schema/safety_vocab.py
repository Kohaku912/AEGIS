"""Canonical vocabularies for capability safety annotations.

Why this module exists
----------------------
Before 2026-09-27 the irreversibility vocabulary was declared twice, as bare
comments in two places, with **two different value sets**:

* ``aegis_ai.folder_registry.CapabilityManifest`` / ``policy_engine.PolicyResult``
  documented ``fully_reversible | recoverable | difficult | irreversible``.
* ``aegis_ai.personal_ai.delegation.DelegationContext`` and the
  ``llm_task_interpreter`` prompt documented ``reversible | difficult | irreversible``.

The delegation policy matches dimensions by **exact string equality**
(``delegation.py``), so a manifest declaring ``recoverable`` would silently stop
matching any user rule written as ``reversible``. Declaring the vocabulary in one
place — and normalising at the boundary — removes that class of bug.

Two vocabularies, one direction
-------------------------------
* ``REVERSIBILITY`` is the **manifest** vocabulary: precise, written by whoever
  declares the capability.
* ``DELEGATION_REVERSIBILITY`` is the **delegation** vocabulary: coarser, because
  it is the dimension a user's rule is written against.
* ``normalize_reversibility()`` maps the former onto the latter, and is the only
  place that mapping is allowed to happen.

Classification conventions (Phase 3, applied to all 126 builtin manifests)
--------------------------------------------------------------------------
1. If the declared operation has a deterministic effect, classify that effect.
2. If the effect depends on caller-supplied arguments, classify the **worst case
   reachable through the declared input schema** (e.g. ``shell.execute`` →
   ``irreversible`` / ``system_wide``).
3. Use ``unknown`` when even the worst case cannot be bounded from the manifest —
   i.e. the manifest itself declares its intent ambiguous.
4. ``irreversible`` must not be paired with ``data_loss_risk="none"``: an
   irreversible operation has to say what is lost.

These fields are **annotations for post-hoc visibility**. They never gate
execution — the only constraint is that user information must not leave the
local environment, and that is enforced by ``aegis_ai.egress``.
"""

from __future__ import annotations

#: Whose state the operation touches. ``unknown`` when the manifest is silent.
OWNERSHIP_SCOPES: tuple[str, ...] = ("aegis", "user", "system", "external", "unknown")

#: How hard it is to undo. Manifest-side vocabulary.
REVERSIBILITY: tuple[str, ...] = (
    "fully_reversible",
    "recoverable",
    "difficult",
    "irreversible",
    "unknown",
)

#: Controlled vocabulary of destructive effect classes. Groupable, unlike the
#: free-form ``risk.side_effects`` prose the manifests also carry. ``unknown`` is
#: a member so that a *silent* manifest (key absent) is distinguishable from one
#: that declares ``[]`` — "nothing destructive" is a claim, not a default.
DESTRUCTIVE_EFFECTS: tuple[str, ...] = (
    "file_delete",          # removes or truncates files/directories
    "data_overwrite",       # mutates existing stored data
    "message_send",         # transmits content to another party
    "purchase",             # spends money or commits to payment
    "account_change",       # creates/modifies/removes an account or credential
    "permission_change",    # changes permissions, policies, or access rules
    "process_terminate",    # stops or kills a running process/app
    "device_state_change",  # changes physical device or environment state
    "memory_delete",        # removes stored memory/knowledge
    "schedule_change",      # creates or cancels commitments/scheduled work
    "remote_transmit",      # emits a signal that cannot be recalled (IR/radio)
    "unknown",              # manifest is silent — not the same as "none"
)

#: Probability that data is destroyed.
DATA_LOSS_RISKS: tuple[str, ...] = ("none", "low", "medium", "high", "unknown")

#: Probability that in-flight user work is destroyed.
ACTIVE_WORK_LOSS_RISKS: tuple[str, ...] = ("none", "low", "medium", "high", "unknown")

#: How far one operation reaches.
BLAST_RADII: tuple[str, ...] = ("single", "bounded", "bulk", "system_wide", "unknown")

#: The delegation dimension vocabulary — deliberately coarser than
#: :data:`REVERSIBILITY`. ``reversible`` is retained as the spelling user rules
#: were written against.
DELEGATION_REVERSIBILITY: tuple[str, ...] = (
    "reversible",
    "difficult",
    "irreversible",
    "unknown",
)

#: Sentinel for "the manifest does not say". Never a safe-looking default:
#: claiming ``none``/``single`` when the value is absent is an unfounded claim.
UNKNOWN = "unknown"

#: Manifest reversibility → delegation reversibility.
_REVERSIBILITY_TO_DELEGATION: dict[str, str] = {
    "fully_reversible": "reversible",
    "recoverable": "reversible",
    "reversible": "reversible",  # already-delegation spelling; accepted as an alias
    "difficult": "difficult",
    "irreversible": "irreversible",
    "unknown": "unknown",
}

#: Every vocabulary, keyed by manifest field name. Used by tests and the ledger.
VOCABULARIES: dict[str, tuple[str, ...]] = {
    "ownership_scope": OWNERSHIP_SCOPES,
    "reversibility": REVERSIBILITY,
    "destructive_effects": DESTRUCTIVE_EFFECTS,
    "data_loss_risk": DATA_LOSS_RISKS,
    "active_work_loss_risk": ACTIVE_WORK_LOSS_RISKS,
    "blast_radius": BLAST_RADII,
}


def normalize_reversibility(value: object) -> str:
    """Map any declared reversibility onto :data:`DELEGATION_REVERSIBILITY`.

    Unrecognised or absent values become ``unknown`` — never a permissive
    default, because the caller cannot know what it was handed.
    """
    if value is None:
        return UNKNOWN
    text = str(value).strip()
    if not text:
        return UNKNOWN
    return _REVERSIBILITY_TO_DELEGATION.get(text, UNKNOWN)


def normalize_dimension(field: str, value: object) -> str:
    """Coerce a declared annotation onto its vocabulary, else ``unknown``."""
    allowed = VOCABULARIES.get(field)
    if allowed is None:
        raise KeyError(f"unknown annotation field: {field!r}")
    text = "" if value is None else str(value).strip()
    return text if text in allowed else UNKNOWN


def normalize_destructive_effects(value: object) -> list[str]:
    """Coerce ``destructive_effects`` to a list, defaulting to ``["unknown"]``.

    An absent key means the manifest never declared anything, which is *not* the
    same as declaring ``[]`` ("this operation destroys nothing"). Collapsing the
    two would let an unclassified capability read as harmless.
    """
    if value is None:
        return [UNKNOWN]
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple)):
        return [UNKNOWN]
    return [str(item) for item in value]
