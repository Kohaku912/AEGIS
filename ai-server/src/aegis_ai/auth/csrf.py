"""CSRF validation for server-side passkey sessions."""

from __future__ import annotations

import hmac


CSRF_HEADER = "X-CSRF-Token"


def csrf_valid(expected: str, supplied: str) -> bool:
    return bool(expected and supplied) and hmac.compare_digest(expected, supplied)
