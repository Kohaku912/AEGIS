"""Audit grouping context.

Keeps audit grouping local to the current execution context so chat turns,
autonomous cycles, and approval continuations can be displayed as one unit
without changing every audit call site.
"""

from __future__ import annotations

import re
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Iterator

_TRACEPARENT_RE = re.compile(
    r"^00-(?P<trace_id>[0-9a-f]{32})-(?P<span_id>[0-9a-f]{16})-(?P<flags>[0-9a-f]{2})$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AuditGroupContext:
    group_id: str
    group_type: str = "system"
    group_title: str = ""
    trace_id: str = ""
    span_id: str = ""
    workflow_id: str = ""
    task_id: str = ""


_current_audit_group: ContextVar[AuditGroupContext | None] = ContextVar(
    "aegis_current_audit_group",
    default=None,
)


def get_audit_group() -> AuditGroupContext | None:
    """Return the current audit group context, if any."""
    return _current_audit_group.get()


def parse_traceparent(value: str) -> tuple[str, str]:
    """Parse W3C traceparent header into (trace_id, span_id)."""
    match = _TRACEPARENT_RE.match(str(value or "").strip())
    if not match:
        return "", ""
    return match.group("trace_id"), match.group("span_id")


def new_trace_ids() -> tuple[str, str]:
    """Generate OTel-compatible trace/span ids."""
    return uuid.uuid4().hex, uuid.uuid4().hex[:16]


@contextmanager
def audit_group(
    group_id: str,
    *,
    group_type: str = "system",
    group_title: str = "",
    trace_id: str = "",
    span_id: str = "",
    workflow_id: str = "",
    task_id: str = "",
) -> Iterator[AuditGroupContext | None]:
    """Temporarily attach audit entries to one logical operation."""
    if not group_id:
        yield None
        return
    ctx = AuditGroupContext(
        group_id=str(group_id),
        group_type=str(group_type or "system"),
        group_title=str(group_title or ""),
        trace_id=str(trace_id or ""),
        span_id=str(span_id or ""),
        workflow_id=str(workflow_id or ""),
        task_id=str(task_id or ""),
    )
    token = _current_audit_group.set(ctx)
    try:
        yield ctx
    finally:
        _safe_reset_audit_group(token)


def _safe_reset_audit_group(token: object) -> None:
    """Reset a ContextVar token even if Flask/OTel copied the execution context.

    ``ContextVar.reset`` raises ValueError when the token was created in a
    different context (FlaskInstrumentor attach/detach). That must never 500
    a request.
    """
    try:
        _current_audit_group.reset(token)  # type: ignore[arg-type]
    except (ValueError, LookupError):
        try:
            _current_audit_group.set(None)
        except Exception:
            pass


def bind_audit_group(
    group_id: str,
    *,
    group_type: str = "system",
    group_title: str = "",
    trace_id: str = "",
    span_id: str = "",
    workflow_id: str = "",
    task_id: str = "",
) -> AuditGroupContext | None:
    """Set the current audit group without a matching reset token."""
    if not group_id:
        return None
    ctx = AuditGroupContext(
        group_id=str(group_id),
        group_type=str(group_type or "system"),
        group_title=str(group_title or ""),
        trace_id=str(trace_id or ""),
        span_id=str(span_id or ""),
        workflow_id=str(workflow_id or ""),
        task_id=str(task_id or ""),
    )
    _current_audit_group.set(ctx)
    return ctx


def clear_audit_group() -> None:
    """Clear the current audit group; never raises across copied contexts."""
    try:
        _current_audit_group.set(None)
    except Exception:
        pass


@contextmanager
def correlation_from_headers(
    headers: dict[str, str] | None,
    *,
    group_id: str,
    group_type: str = "http",
    group_title: str = "",
    task_id: str = "",
    workflow_id: str = "",
) -> Iterator[AuditGroupContext | None]:
    """Open an audit group using incoming trace/request headers when present."""
    headers = headers or {}
    trace_id, span_id = parse_traceparent(headers.get("traceparent", ""))
    if not trace_id:
        trace_id, span_id = new_trace_ids()
    request_id = str(headers.get("X-Request-ID") or headers.get("x-request-id") or group_id)
    with audit_group(
        request_id,
        group_type=group_type,
        group_title=group_title or request_id,
        trace_id=trace_id,
        span_id=span_id,
        workflow_id=workflow_id,
        task_id=task_id,
    ) as ctx:
        yield ctx


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
        trace_id=str(metadata.get("trace_id") or ""),
        span_id=str(metadata.get("span_id") or ""),
        workflow_id=str(metadata.get("workflow_id") or ""),
        task_id=str(metadata.get("task_id") or ""),
    )
