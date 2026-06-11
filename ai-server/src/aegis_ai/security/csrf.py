"""CSRF protection — cross-site request forgery prevention."""

from __future__ import annotations

import secrets
import time


class CSRFProtection:
    """CSRF token management for Flask web routes.

    Usage:
        csrf = CSRFProtection()
        token = csrf.generate_token(session_id)
        csrf.validate_token(session_id, token)
    """

    def __init__(self, token_lifetime_seconds: int = 3600) -> None:
        self._tokens: dict[str, tuple[str, float]] = {}
        self._lifetime = token_lifetime_seconds

    def generate_token(self, session_id: str) -> str:
        """Generate a new CSRF token for a session."""
        token = secrets.token_hex(32)
        self._tokens[session_id] = (token, time.time())
        return token

    def validate_token(self, session_id: str, token: str) -> bool:
        """Validate a CSRF token."""
        entry = self._tokens.get(session_id)
        if not entry:
            return False

        stored_token, created_at = entry
        if time.time() - created_at > self._lifetime:
            self._tokens.pop(session_id, None)
            return False

        return secrets.compare_digest(stored_token, token)

    def invalidate_token(self, session_id: str) -> None:
        """Invalidate a CSRF token (after use)."""
        self._tokens.pop(session_id, None)

    def cleanup_expired(self) -> int:
        """Remove expired tokens. Returns count removed."""
        now = time.time()
        expired = [k for k, (_, created) in self._tokens.items() if now - created > self._lifetime]
        for k in expired:
            del self._tokens[k]
        return len(expired)
