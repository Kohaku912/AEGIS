"""Audit grouping context.

Keeps audit grouping local to the current execution context so chat turns,
autonomous cycles, and approval continuations can be displayed as one unit
without changing every audit call site.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class AuditGroupContext:
    group_id: str
    group_type: str = "system"
    group_title: str = ""


_current_audit_group: ContextVar[AuditGroupContext | None] = ContextVar(
    "aegis_current_audit_group",
    default=None,
)


def get_audit_group() -> AuditGroupContext | None:
    """Return the current audit group context, if any."""
    return _current_audit_group.get()


@contextmanager
def audit_group(
    group_id: str,
    *,
    group_type: str = "system",
    group_title: str = "",
) -> Iterator[AuditGroupContext | None]:
    """Temporarily attach audit entries to one logical operation."""
    if not group_id:
        yield None
        return
    ctx = AuditGroupContext(
        group_id=str(group_id),
        group_type=str(group_type or "system"),
        group_title=str(group_title or ""),
    )
    token = _current_audit_group.set(ctx)
    try:
        yield ctx
    finally:
        _current_audit_group.reset(token)


def audit_group_from_metadata(metadata: dict | None) -> AuditGroupContext | None:
    """Build a context object from persisted metadata."""
    if not isinstance(metadata, dict):
        return None
    group_id = str(metadata.get("audit_group_id") or "")
    if not group_id:
        return None
    return AuditGroupContext(
        group_id=group_id,
        group_type=str(metadata.get("audit_group_type") or "system"),
        group_title=str(metadata.get("audit_group_title") or ""),
    )
