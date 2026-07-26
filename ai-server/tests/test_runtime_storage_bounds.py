"""Regression tests for bounded runtime persistence."""

from __future__ import annotations

from tool_broker import _compact_audit_value


def test_compact_audit_value_omits_large_payload_and_masks_secrets() -> None:
    payload = {
        "image_base64": "A" * 1_000_000,
        "nested": {"api_token": "secret-value", "status": "ok"},
    }

    compact = _compact_audit_value(payload)

    assert compact["image_base64"]["omitted"] is True
    assert compact["image_base64"]["length"] == 1_000_000
    assert compact["nested"]["api_token"] == "***MASKED***"
    assert compact["nested"]["status"] == "ok"
