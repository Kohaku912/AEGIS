"""User permission for external egress — the re-scoped constraint's second path.

**The constraint, re-scoped 2026-09-30** (owner):

    **Unpermitted** user information must never leave the local environment. Outbound
    connections are allowed, and user information may be sent externally **with the
    user's permission**.

Before the re-scope, "permission" was standing configuration only: the master switch,
the per-purpose feature flag, and a host allowlist. That path still exists and is
unchanged. This module adds the second one the re-scope requires — a permission the user
gave about a **specific** destination, recorded through the machinery AEGIS already uses
to ask.

Why this is not the retired approval gate
-----------------------------------------
The gate retired on 2026-09-27 forced a prompt whenever a *manifest* said so, which made
the user a bottleneck on work they had already delegated. Nothing here reads a manifest,
infers a risk, or matches keywords. This module is **read-only over decisions the user
already made**: it answers "has the user permitted this destination?" and never asks.
Raising the question is the *voluntary* ask's job (``aegis_ai.confirmation``), which the
loop may choose to use — pinned by ``tests/test_forced_gate_stays_retired.py`` and by the
"the gate never requests" assertion in ``tests/test_egress_permission.py``.

Scope of a grant
----------------
A grant is ``(host, purpose)``, matched **exactly** and case-insensitively on the host.
There is deliberately **no wildcard**: a blanket "allow everything" grant is not
representable, because that is the shape that turns a permission check back into a wall
with a hole in it. A broader grant is a separate decision, not a default.

A grant expires. ``expires_at`` is honoured, so a permission given for one task does not
silently become a standing one.

Where a grant comes from
------------------------
``ConfirmationGrantSource`` adapts an object with the ``ConfirmationStore`` read surface
(``all``). The adapter **duck-types** it rather than importing ``aegis_ai.confirmation``,
so the gate keeps its small dependency surface and cannot accidentally grow a second
route to the ask machinery.

The wire field set is not invented here either: a grant is an ordinary confirmation whose
``capability_id`` is :data:`EGRESS_PERMISSION_CAPABILITY` and whose ``target`` carries the
scope. That means the shipped dashboard renders it with no new bundle, and the decision is
auditable through the same history view as every other ask.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Iterable

#: The ``capability_id`` a confirmation carries when it records egress permission.
#: A confirmation with any other ``capability_id`` is not a grant, whatever its status.
EGRESS_PERMISSION_CAPABILITY = "egress.external_permission"

#: Separator between host and purpose inside a grant's scope string.
SCOPE_SEPARATOR = "|"

#: Confirmation statuses that count as "the user permitted this".
_PERMITTING_STATUSES = frozenset({"approved", "executed"})

#: How many confirmations ``ConfirmationGrantSource`` scans by default.
#:
#: The scan is newest-first and bounded, so a grant that has fallen outside the window is
#: **not honoured**. That is a fail-closed failure: the request is denied, never allowed on
#: an unread record. The bound is recorded here so it is a visible limit rather than a
#: silent one; a store large enough to hit it should expose a narrower query.
DEFAULT_SCAN_LIMIT = 500


def now_ms() -> int:
    """Milliseconds since the epoch — the confirmation package's timestamp convention."""
    return int(time.time() * 1000)


@dataclass(frozen=True)
class EgressPermission:
    """A user's permission to send to one destination for one purpose."""

    grant_id: str
    host: str
    purpose: str
    granted_at_ms: int | None = None
    expires_at_ms: int | None = None

    def is_expired_at(self, moment_ms: int) -> bool:
        return self.expires_at_ms is not None and self.expires_at_ms <= moment_ms


def format_scope(host: str, purpose: str) -> str:
    """Render a grant scope for a confirmation's ``target`` field."""
    return f"{str(host).strip().lower()}{SCOPE_SEPARATOR}{str(purpose).strip()}"


def parse_scope(target: str) -> tuple[str, str] | None:
    """Parse a grant scope, or ``None`` when it is not a well-formed scope.

    A malformed scope yields no grant — an unparseable permission is not a permission.
    """
    if not target or SCOPE_SEPARATOR not in target:
        return None
    host, _, purpose = str(target).partition(SCOPE_SEPARATOR)
    host = host.strip().lower()
    purpose = purpose.strip()
    if not host or not purpose:
        return None
    return host, purpose


class ConfirmationGrantSource:
    """Reads egress grants out of an object with ``ConfirmationStore``'s read surface.

    Read-only by construction: the only method it calls is ``all``. It cannot ask, resolve
    or mutate, so wiring it into the gate cannot reintroduce a forced prompt.
    """

    def __init__(self, store: Any, *, limit: int = DEFAULT_SCAN_LIMIT) -> None:
        self._store = store
        self._limit = max(0, int(limit))

    def grants(self) -> list[EgressPermission]:
        """Every recorded grant, newest first. Unparseable records are skipped."""
        if self._store is None:
            return []
        reader = getattr(self._store, "all", None)
        if not callable(reader):
            return []
        try:
            items: Iterable[Any] = reader(limit=self._limit)
        except Exception:
            return []

        found: list[EgressPermission] = []
        for item in items:
            capability = str(getattr(item, "capability_id", "") or "")
            if capability != EGRESS_PERMISSION_CAPABILITY:
                continue
            status = str(getattr(item, "status", "") or "").lower()
            if status not in _PERMITTING_STATUSES:
                continue
            scope = parse_scope(str(getattr(item, "target", "") or ""))
            if scope is None:
                continue
            host, purpose = scope
            found.append(
                EgressPermission(
                    grant_id=str(getattr(item, "approval_id", "") or ""),
                    host=host,
                    purpose=purpose,
                    granted_at_ms=_as_int(getattr(item, "resolved_at", None)),
                    expires_at_ms=_as_int(getattr(item, "expires_at", None)),
                )
            )
        return found

    def grant_for(self, *, host: str, purpose: str, moment_ms: int | None = None) -> EgressPermission | None:
        """The newest unexpired grant for exactly this ``(host, purpose)``, if any."""
        moment = now_ms() if moment_ms is None else int(moment_ms)
        wanted_host = str(host or "").strip().lower()
        wanted_purpose = str(purpose or "").strip()
        if not wanted_host or not wanted_purpose:
            return None
        for grant in self.grants():
            if grant.host != wanted_host or grant.purpose != wanted_purpose:
                continue
            if grant.is_expired_at(moment):
                continue
            return grant
        return None


def _as_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
