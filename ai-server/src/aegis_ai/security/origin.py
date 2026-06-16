"""Origin checking — validates request origins for web security."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("aegis_ai.security.origin")


class OriginChecker:
    """Validates HTTP request origins to prevent unauthorized access.

    Default: localhost only (no external access).
    """

    def __init__(
        self,
        allowed_origins: set[str] | None = None,
        allow_localhost: bool = True,
        audit_log: Any = None,
    ) -> None:
        self._allowed_origins = allowed_origins or set()
        self._allow_localhost = allow_localhost
        self._audit = audit_log

    def is_allowed(self, origin: str | None, remote_addr: str = "") -> bool:
        """Check if a request origin is allowed.

        Args:
            origin: The Origin header value.
            remote_addr: The remote IP address.

        Returns:
            True if the origin is allowed.
        """
        # Allow localhost
        if self._allow_localhost:
            if remote_addr in ("0.0.0.0", "::1", "localhost"):
                return True
            if origin and any(loc in origin for loc in ("localhost", "0.0.0.0")):
                return True

        # Check explicit allowed origins
        if origin and origin in self._allowed_origins:
            return True

        # Deny and audit
        if self._audit:
            self._audit.log_decision(
                "origin_rejected", "web", "DENY",
                reason=f"Origin '{origin}' from '{remote_addr}' not allowed",
            )
            logger.warning("Rejected origin: %s from %s", origin, remote_addr)

        return False
