"""AEGIS-initiated confirmation: the request model.

**What a confirmation is.** Something AEGIS *chooses* to ask the user about. AEGIS acts
inside its delegated scope without asking; when it judges that the user should decide —
an irreversible step, an ambiguous goal, a genuinely new kind of action — it raises a
confirmation and the dashboard surfaces it. The same judgement decides *whether to speak
at all*, so a confirmation is the interactive half of the interruption design (P1-13 /
P1-14): "when should I interrupt?" and "what do I need from you?" are one decision.

**What a confirmation is not.** It is not the retired approval gate. That mechanism
forced a confirmation whenever a capability's manifest said so — ``requires_approval``, a
high risk level, or a rule about ``EXTERNAL_SEND`` / ``DEVICE_ACTION`` / ``PAYMENT`` —
which made the user a bottleneck on work they had already delegated. It was removed on
2026-09-27 (see ``IMPROVEMENT_PROPOSAL.md`` §9). Nothing in this package may reintroduce
it: there is no manifest lookup, no risk inference and no keyword matching here. The
decision is the LLM's — see the "LLM-Driven Operations" rules in ``AGENTS.md``.

**Why the JSON keys still say ``approval_``.** The field set is not invented here. It is
the contract the shipped ``web-ui`` bundle already renders
(``web-ui/src/types.ts::ApprovalItem``), so the wire format keeps its historical names;
renaming them would mean shipping a new bundle for no behavioural gain.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


def now_ms() -> int:
    """Milliseconds since the epoch.

    The UI compares ``expires_at - Date.now()``, so timestamps on the wire are
    milliseconds, not seconds — the same convention as ``StatusManager.last_check_ms``.
    """
    return int(time.time() * 1000)


class ConfirmationStatus(str, Enum):
    """Wire statuses, matching the buckets the dashboard already knows.

    ``web-ui/src/displayModel.ts::approvalBuckets`` uppercases whatever it receives and
    sorts it into Pending / Expiring / High risk / Resolved / Rejected / Expired /
    Cancelled / Executed / Failed, so these values are lowercase here and normalised
    there.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    EXECUTED = "executed"
    FAILED = "failed"
    SUPERSEDED = "superseded"


@dataclass
class ConfirmationRequest:
    """One question AEGIS is asking the user.

    Every field the dashboard renders is here. ``capability_id`` / ``risk`` /
    ``side_effects`` are **descriptions AEGIS supplies about its own intended action** —
    they are shown to the user and are never consulted to decide anything, which is the
    line between this and the retired gate.
    """

    approval_id: str
    summary: str = ""
    reason: str = ""
    capability_id: str = ""
    tool_name: str = ""
    risk: str = ""
    target: str = ""
    preview: str = ""
    side_effects: Any = None
    previous_action: str = ""
    similar_action_summary: str = ""
    expected_effect: str = ""
    fresh_auth_required: bool = False
    task_id: str = ""
    #: Which desire this question belongs to, when the asker knows.
    #:
    #: **LLM-supplied, and therefore untrusted.** It exists so the growth loop can
    #: attribute a rejection to a desire — without it a resolved confirmation cannot be
    #: linked to anything, and the "approval lesson" the penalty readers look for can
    #: never be written. The value is carried verbatim here; the *reader*
    #: (``AutonomousLoop``) validates it against the live desire set before using it, so
    #: an unknown or empty value yields **no lesson** rather than a wrong one.
    desire: str = ""
    step_id: str = ""
    request_id: str = ""
    status: str = ConfirmationStatus.PENDING.value
    created_at: int = field(default_factory=now_ms)
    expires_at: int | None = None
    resolved_at: int | None = None
    decided_by: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConfirmationRequest:
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{key: value for key, value in dict(data).items() if key in known})

    @property
    def is_open(self) -> bool:
        return self.status == ConfirmationStatus.PENDING.value

    def is_expired_at(self, moment_ms: int) -> bool:
        return self.expires_at is not None and self.expires_at <= moment_ms
