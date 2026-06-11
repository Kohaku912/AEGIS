"""Authentication — server and user authentication for AEGIS.

Provides:
- Local token authentication for server-to-server communication
- Optional password auth for Web UI
- Token generation and validation
- Failed auth tracking for audit
"""

from __future__ import annotations

import hashlib
import logging
import secrets
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("aegis_ai.security.auth")


@dataclass
class AuthResult:
    """Result of an authentication attempt."""
    authenticated: bool = False
    server_id: str = ""
    reason: str = ""
    timestamp_ms: int = 0


class LocalTokenAuth:
    """Token-based authentication for local network server communication.

    Usage:
        auth = LocalTokenAuth(token="my-secret-token")
        result = auth.validate_server("pc-server", token)
        if result.authenticated:
            # Server is authorized
    """

    def __init__(
        self,
        token: str = "",
        allowed_servers: set[str] | None = None,
        audit_log: Any = None,
    ) -> None:
        self._token = token
        self._allowed_servers = allowed_servers or set()
        self._audit = audit_log
        self._failed_attempts: dict[str, int] = {}  # server_id → count

    def validate_server(self, server_id: str, token: str) -> AuthResult:
        """Validate a server's authentication token.

        Returns AuthResult with authentication status.
        """
        now_ms = int(time.time() * 1000)

        # Check token
        if not self._token or token != self._token:
            self._failed_attempts[server_id] = self._failed_attempts.get(server_id, 0) + 1
            if self._audit:
                self._audit.log_decision(
                    "auth_failed", f"server.{server_id}", "DENY",
                    reason="Invalid token",
                    detail={"server_id": server_id},
                )
            return AuthResult(
                authenticated=False,
                server_id=server_id,
                reason="Invalid token",
                timestamp_ms=now_ms,
            )

        # Check allowlist (if configured)
        if self._allowed_servers and server_id not in self._allowed_servers:
            if self._audit:
                self._audit.log_decision(
                    "auth_failed", f"server.{server_id}", "DENY",
                    reason="Server not in allowlist",
                )
            return AuthResult(
                authenticated=False,
                server_id=server_id,
                reason="Server not in allowlist",
                timestamp_ms=now_ms,
            )

        # Success
        return AuthResult(
            authenticated=True,
            server_id=server_id,
            reason="Token valid",
            timestamp_ms=now_ms,
        )

    def get_failed_attempts(self, server_id: str) -> int:
        """Get failed auth attempt count for a server."""
        return self._failed_attempts.get(server_id, 0)

    def get_all_failed_attempts(self) -> dict[str, int]:
        """Get all failed auth attempts."""
        return dict(self._failed_attempts)


def generate_token() -> str:
    """Generate a secure random token for server authentication."""
    return secrets.token_hex(32)


def hash_token(token: str) -> str:
    """Hash a token for safe storage."""
    return hashlib.sha256(token.encode()).hexdigest()
