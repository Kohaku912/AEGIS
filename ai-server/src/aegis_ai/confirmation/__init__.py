"""AEGIS-initiated confirmation.

A confirmation is something AEGIS *chooses* to ask the user. It replaces nothing:
the forced approval gate was retired on 2026-09-27 because it made the user a
bottleneck on work they had already delegated. What survives is the *question* —
raised by AEGIS when it judges that the user should decide — and the dashboard
that renders it.

The dividing line is worth stating precisely, because it is the whole point of
this package:

* **Retired**: a capability is *blocked* because a manifest, a risk level or a
  rule says it must be approved first. Nothing may wait on this package.
* **Kept**: AEGIS decides, on its own judgement, to ask. The question is
  recorded, surfaced in the dashboard, and answered at the user's convenience.
  The answer informs what AEGIS does next; it never unblocks a held-up call.

So ``ConfirmationStore.request()`` returns immediately and no execution path
consults the store. There is no manifest lookup, no risk inference and no keyword
matching anywhere in this package — the decision belongs to the LLM (see
"LLM-Driven Operations" in ``AGENTS.md``).

Public surface::

    from aegis_ai.confirmation import ConfirmationStore, ConfirmationStatus

    store = ConfirmationStore("data")
    item = store.request(summary="Send the revised draft to Sato-san?",
                         capability_id="mail.send", target="sato@example.com")
    store.approve(item.approval_id, decided_by="user")
"""

from __future__ import annotations

from aegis_ai.confirmation.models import (
    ConfirmationRequest,
    ConfirmationStatus,
    now_ms,
)
from aegis_ai.confirmation.store import (
    DEFAULT_TTL_MS,
    EVENT_CREATED,
    EVENT_RESOLVED,
    ConfirmationStore,
    Listener,
    new_confirmation_id,
)

__all__ = [
    "DEFAULT_TTL_MS",
    "EVENT_CREATED",
    "EVENT_RESOLVED",
    "ConfirmationRequest",
    "ConfirmationStatus",
    "ConfirmationStore",
    "Listener",
    "new_confirmation_id",
    "now_ms",
]
