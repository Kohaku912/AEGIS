"""Session helpers for passkey auth."""

from __future__ import annotations

import secrets
from typing import Any

from aegis_ai.auth.models import AuthSession
from aegis_ai.auth.passkey_store import PasskeyStore, now_ms


class SessionStore:
    """Create and validate server-side sessions."""

    def __init__(self, store: PasskeyStore, lifetime_ms: int = 12 * 60 * 60 * 1000) -> None:
        self.store = store
        self.lifetime_ms = lifetime_ms

    def create(self, user_id: str, *, user_agent: str = "", ip_address: str = "") -> AuthSession:
        now = now_ms()
        session = AuthSession(
            session_id=secrets.token_urlsafe(32),
            user_id=user_id,
            created_at=now,
            expires_at=now + self.lifetime_ms,
            last_seen_at=now,
            last_auth_at=now,
            csrf_token=secrets.token_urlsafe(32),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.store.add_session(session)
        return session

    def get(self, session_id: str) -> AuthSession | None:
        session = self.store.get_session(session_id)
        if session is None:
            return None
        session.last_seen_at = now_ms()
        self.store.update_session(session)
        return session

    def touch_fresh(self, session: AuthSession) -> AuthSession:
        session.last_auth_at = now_ms()
        session.csrf_token = secrets.token_urlsafe(32)
        self.store.update_session(session)
        return session

    def revoke(self, session_id: str) -> None:
        self.store.revoke_session(session_id)

    @staticmethod
    def to_public_dict(session: AuthSession, user: Any, *, fresh_window_ms: int) -> dict[str, Any]:
        now = now_ms()
        return {
            "authenticated": True,
            "user": user.to_dict() if hasattr(user, "to_dict") else user,
            "expires_at": session.expires_at,
            "last_auth_at": session.last_auth_at,
            "fresh": now - session.last_auth_at <= fresh_window_ms,
            "csrf_token": session.csrf_token,
        }
