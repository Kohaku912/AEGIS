"""Audit correlation context must not raise across copied execution contexts."""

from __future__ import annotations

import contextvars

from aegis_ai.audit.context import (
    audit_group,
    bind_audit_group,
    clear_audit_group,
    get_audit_group,
)


def test_audit_group_reset_across_copied_context() -> None:
    copied = contextvars.copy_context()
    cm = audit_group("g1", group_type="http", group_title="/display/overview")
    copied.run(cm.__enter__)
    # Flask/OTel teardown often runs in a different Context than before_request.
    cm.__exit__(None, None, None)
    assert get_audit_group() is None or get_audit_group().group_id in {"g1", None}


def test_bind_and_clear_audit_group() -> None:
    bind_audit_group("req-1", group_type="http", group_title="/auth/me")
    ctx = get_audit_group()
    assert ctx is not None
    assert ctx.group_id == "req-1"
    clear_audit_group()
    assert get_audit_group() is None
