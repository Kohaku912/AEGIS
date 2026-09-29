"""The AEGIS-initiated confirmation store.

A confirmation is recorded here and rendered by the dashboard. That is the whole
contract. In particular this store:

* **cannot block anything.** ``request()`` records a question; it returns immediately and
  never waits for an answer. Nothing in the execution path consults it, so a capability
  can never be held up by a confirmation — the retired gate's defining behaviour is
  structurally absent rather than merely switched off.
* **does not decide anything.** It has no reference to the policy engine, the tool
  broker or a capability manifest, and it does no risk inference or keyword matching.
  AEGIS supplies the description; the user supplies the answer.
* **keeps a history.** Resolved requests are retained (JSONL, last write wins per id) so
  the dashboard can show what AEGIS asked and what was decided — the post-hoc view of
  its own initiative.

Timestamps are epoch **milliseconds**; see ``models.now_ms``.
"""

from __future__ import annotations

import json
import logging
import threading
import uuid
from pathlib import Path
from typing import Any, Callable

from aegis_ai.confirmation.models import (
    ConfirmationRequest,
    ConfirmationStatus,
    now_ms,
)

logger = logging.getLogger("aegis_ai.confirmation.store")

#: A confirmation that is never answered lapses, so a stale question cannot sit in the
#: queue looking like a decision the user still owes. Thirty minutes is a judgement call,
#: not a policy: AEGIS re-raises if it still matters.
DEFAULT_TTL_MS = 30 * 60 * 1000

#: Emitted when a request is created.
EVENT_CREATED = "approval.created"
#: Emitted when a request reaches any terminal state. One name covers approved /
#: rejected / expired / cancelled / executed / failed: a consumer that only wants to
#: know "something changed, re-read the queue" does not have to enumerate the statuses,
#: and the status itself is on the payload. The names keep their historical ``approval``
#: prefix because they are the event names already published on the dashboard wire.
EVENT_RESOLVED = "approval.resolved"

Listener = Callable[[str, ConfirmationRequest], None]

#: Fields the user may narrow when they answer "yes, but like this". Deliberately only
#: the *descriptive* fields: ``capability_id`` / ``tool_name`` are AEGIS's statement of
#: what it intends to do, and letting them be rewritten would turn the confirmation into
#: a way to direct a different action than the one AEGIS reasoned about.
#:
#: ``note`` is absent on purpose — it is already an explicit parameter of every decision
#: method, so accepting it here too would give one field two competing sources.
USER_EDITABLE_FIELDS = frozenset(
    {
        "summary",
        "target",
        "preview",
        "expected_effect",
        "side_effects",
    }
)


def new_confirmation_id() -> str:
    """``cfm_``-prefixed so a confirmation is never mistaken for a retired approval."""
    return f"cfm_{uuid.uuid4().hex[:12]}"


class ConfirmationStore:
    """In-memory confirmations, persisted append-only as JSONL.

    Loading is last-write-wins per ``approval_id``: every change appends the full record,
    so a partially written line is simply superseded by the next one and a torn tail can
    be skipped without losing the history.
    """

    def __init__(
        self,
        data_dir: str = "data",
        *,
        default_ttl_ms: int = DEFAULT_TTL_MS,
    ) -> None:
        self._dir = Path(data_dir) / "confirmation"
        self._path = self._dir / "confirmations.jsonl"
        self._lock = threading.RLock()
        self._items: dict[str, ConfirmationRequest] = {}
        self._listeners: list[Listener] = []
        self._default_ttl_ms = int(default_ttl_ms)
        self._load()

    # ── persistence ───────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not self._path.is_file():
            return
        loaded = 0
        try:
            for line in self._path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    # A torn final line from an interrupted write. The record it was
                    # updating is still present from its previous line, so skipping is
                    # safe and better than discarding the whole history.
                    logger.warning("Skipping malformed confirmation record in %s", self._path)
                    continue
                if not isinstance(payload, dict) or not payload.get("approval_id"):
                    continue
                item = ConfirmationRequest.from_dict(payload)
                self._items[item.approval_id] = item
                loaded += 1
        except OSError:
            logger.warning("Could not read %s", self._path, exc_info=True)
            return
        if loaded:
            logger.info("Loaded %s confirmation record(s) from %s", loaded, self._path)

    def _persist(self, item: ConfirmationRequest) -> None:
        try:
            self._dir.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")
        except OSError:
            # Losing the on-disk history must not lose the live request: the user can
            # still answer it in the dashboard, they just cannot read it back later.
            logger.warning("Could not persist confirmation %s", item.approval_id, exc_info=True)

    # ── listeners (the SSE stream) ────────────────────────────────────────────

    def add_listener(self, listener: Listener) -> Callable[[], None]:
        """Register ``listener(event_name, request)``; returns an unsubscribe callable."""
        with self._lock:
            self._listeners.append(listener)

        def _remove() -> None:
            with self._lock:
                if listener in self._listeners:
                    self._listeners.remove(listener)

        return _remove

    def _emit(self, event: str, item: ConfirmationRequest) -> None:
        with self._lock:
            listeners = list(self._listeners)
        for listener in listeners:
            try:
                listener(event, item)
            except Exception:
                # A broken stream must never break the store.
                logger.debug("Confirmation listener failed", exc_info=True)

    # ── writes ────────────────────────────────────────────────────────────────

    def request(self, **fields: Any) -> ConfirmationRequest:
        """Record a confirmation AEGIS has decided to raise.

        Returns immediately — this method never waits for an answer, and no caller is
        expected to block on the result. The returned object is a snapshot, like every
        other read, so mutating it cannot alter the store without persistence.
        """
        approval_id = str(fields.pop("approval_id", "") or new_confirmation_id())
        item = ConfirmationRequest(approval_id=approval_id, **fields)
        if item.expires_at is None:
            item.expires_at = item.created_at + self._default_ttl_ms
        item.status = ConfirmationStatus.PENDING.value

        with self._lock:
            self._items[item.approval_id] = item
            snapshot = ConfirmationRequest.from_dict(item.to_dict())
        self._persist(snapshot)
        logger.info(
            "AEGIS raised confirmation %s (%s) for %s",
            snapshot.approval_id,
            snapshot.summary or snapshot.capability_id or "unspecified",
            snapshot.capability_id or "no capability",
        )
        self._emit(EVENT_CREATED, snapshot)
        return snapshot

    def resolve(
        self,
        approval_id: str,
        status: ConfirmationStatus | str,
        *,
        decided_by: str = "",
        note: str = "",
    ) -> ConfirmationRequest | None:
        """Move an open confirmation to ``status``. Returns ``None`` if it was not open.

        Only PENDING requests are resolvable: re-answering an already-decided question
        would let a stale dashboard tab rewrite a decision the user has moved on from.
        """
        target = ConfirmationStatus(status) if not isinstance(status, ConfirmationStatus) else status
        with self._lock:
            item = self._items.get(approval_id)
            if item is None or not item.is_open:
                return None
            item.status = target.value
            item.resolved_at = now_ms()
            if decided_by:
                item.decided_by = decided_by
            if note:
                item.note = note
            snapshot = ConfirmationRequest.from_dict(item.to_dict())

        self._persist(snapshot)
        logger.info("Confirmation %s -> %s", approval_id, snapshot.status)
        self._emit(EVENT_RESOLVED, snapshot)
        return snapshot

    def approve(self, approval_id: str, *, decided_by: str = "", note: str = "") -> ConfirmationRequest | None:
        return self.resolve(approval_id, ConfirmationStatus.APPROVED, decided_by=decided_by, note=note)

    def reject(self, approval_id: str, *, decided_by: str = "", note: str = "") -> ConfirmationRequest | None:
        return self.resolve(approval_id, ConfirmationStatus.REJECTED, decided_by=decided_by, note=note)

    def cancel(self, approval_id: str, *, decided_by: str = "", note: str = "") -> ConfirmationRequest | None:
        """Withdraw a question AEGIS no longer needs answered."""
        return self.resolve(approval_id, ConfirmationStatus.CANCELLED, decided_by=decided_by, note=note)

    def modify_and_approve(
        self,
        approval_id: str,
        *,
        edits: dict[str, Any] | None = None,
        decided_by: str = "",
        note: str = "",
    ) -> ConfirmationRequest | None:
        """Answer "yes, but like this" — apply the user's narrowing, then approve.

        The user is allowed to narrow the *description* of what AEGIS proposed, not to
        rewrite the proposal into a different one. So only the descriptive fields in
        ``USER_EDITABLE_FIELDS`` can be overridden; ``capability_id`` and the id fields
        are AEGIS's statement of what it is about to do and are left alone.

        The pre-edit record is not lost: persistence is append-only, so the previous
        JSONL line still holds exactly what AEGIS originally proposed, while the store
        and the dashboard show the version the user agreed to.
        """
        applied = {
            key: value
            for key, value in (edits or {}).items()
            if key in USER_EDITABLE_FIELDS
        }
        with self._lock:
            item = self._items.get(approval_id)
            if item is None or not item.is_open:
                return None
            for key, value in applied.items():
                setattr(item, key, value)
            if applied:
                logger.info(
                    "Confirmation %s edited by user: %s",
                    approval_id,
                    ", ".join(sorted(applied)),
                )
        return self.resolve(approval_id, ConfirmationStatus.APPROVED, decided_by=decided_by, note=note)

    def mark_executed(self, approval_id: str, *, note: str = "") -> ConfirmationRequest | None:
        """The approved action was carried out. Drives the dashboard's Executed bucket."""
        return self._reopen_and_settle(approval_id, ConfirmationStatus.EXECUTED, note=note)

    def mark_failed(self, approval_id: str, *, note: str = "") -> ConfirmationRequest | None:
        """The approved action was attempted and failed."""
        return self._reopen_and_settle(approval_id, ConfirmationStatus.FAILED, note=note)

    def _reopen_and_settle(
        self, approval_id: str, status: ConfirmationStatus, *, note: str
    ) -> ConfirmationRequest | None:
        """Record an outcome for a decision that was already made.

        Unlike ``resolve``, this accepts a request that is no longer pending: APPROVED
        -> EXECUTED is a report about the action, not a second answer to the question.

        The guard is ``APPROVED`` specifically, not "any decided status". A rejected
        request must not be able to reach EXECUTED — "no" followed by "done" would mean
        AEGIS carried out the very thing the user declined.
        """
        with self._lock:
            item = self._items.get(approval_id)
            if item is None or item.status != ConfirmationStatus.APPROVED.value:
                return None
            item.status = status.value
            item.resolved_at = now_ms()
            if note:
                item.note = note
            snapshot = ConfirmationRequest.from_dict(item.to_dict())

        self._persist(snapshot)
        self._emit(EVENT_RESOLVED, snapshot)
        return snapshot

    def expire_stale(self, *, moment_ms: int | None = None) -> list[ConfirmationRequest]:
        """Lapse every open confirmation past its ``expires_at``."""
        moment = now_ms() if moment_ms is None else int(moment_ms)
        expired: list[ConfirmationRequest] = []
        with self._lock:
            open_items = [item for item in self._items.values() if item.is_open]
        for item in open_items:
            if not item.is_expired_at(moment):
                continue
            resolved = self.resolve(item.approval_id, ConfirmationStatus.EXPIRED)
            if resolved is not None:
                expired.append(resolved)
        return expired

    # ── reads ─────────────────────────────────────────────────────────────────

    def get(self, approval_id: str) -> ConfirmationRequest | None:
        with self._lock:
            item = self._items.get(approval_id)
            return ConfirmationRequest.from_dict(item.to_dict()) if item else None

    def pending(self) -> list[ConfirmationRequest]:
        """Open confirmations, oldest first (the order the dashboard queues them in)."""
        with self._lock:
            items = [item for item in self._items.values() if item.is_open]
        items.sort(key=lambda item: item.created_at)
        return [ConfirmationRequest.from_dict(item.to_dict()) for item in items]

    def pending_count(self) -> int:
        with self._lock:
            return sum(1 for item in self._items.values() if item.is_open)

    def all(self, *, limit: int = 200) -> list[ConfirmationRequest]:
        """Newest first, capped — the history view."""
        with self._lock:
            items = list(self._items.values())
        items.sort(key=lambda item: item.created_at, reverse=True)
        return [ConfirmationRequest.from_dict(item.to_dict()) for item in items[: max(0, int(limit))]]

    def clear(self) -> None:
        """Drop everything, in memory and on disk. Test helper; not used at runtime."""
        with self._lock:
            self._items.clear()
        try:
            self._path.unlink(missing_ok=True)
        except OSError:
            logger.debug("Could not remove %s", self._path, exc_info=True)
