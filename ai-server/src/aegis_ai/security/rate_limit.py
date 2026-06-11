"""Rate limiting — prevents brute-force and abuse."""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    allowed: bool = True
    remaining: int = 0
    retry_after_seconds: float = 0.0


class RateLimiter:
    """Token bucket rate limiter.

    Usage:
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        result = limiter.check("client_id")
        if result.allowed:
            # Process request
    """

    def __init__(
        self,
        max_requests: int = 60,
        window_seconds: float = 60.0,
    ) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._buckets: dict[str, list[float]] = {}

    def check(self, client_id: str) -> RateLimitResult:
        """Check if a request is allowed for the given client."""
        now = time.monotonic()
        window_start = now - self._window_seconds

        # Get or create bucket
        if client_id not in self._buckets:
            self._buckets[client_id] = []

        # Remove expired entries
        self._buckets[client_id] = [t for t in self._buckets[client_id] if t > window_start]

        bucket = self._buckets[client_id]
        remaining = self._max_requests - len(bucket)

        if remaining <= 0:
            # Rate limited
            oldest = bucket[0] if bucket else now
            retry_after = oldest + self._window_seconds - now
            return RateLimitResult(
                allowed=False,
                remaining=0,
                retry_after_seconds=max(0, retry_after),
            )

        # Allow and record
        bucket.append(now)
        return RateLimitResult(
            allowed=True,
            remaining=remaining - 1,
            retry_after_seconds=0.0,
        )

    def reset(self, client_id: str) -> None:
        """Reset rate limit for a client."""
        self._buckets.pop(client_id, None)
