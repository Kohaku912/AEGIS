"""Shared LLM provider circuit breaker for billing / balance failures.

When the cloud provider returns 402 / insufficient balance, open the circuit
so autonomous loops stop hammering the API until cooldown expires.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from typing import Any

logger = logging.getLogger("aegis_ai.llm.provider_circuit")

_DEFAULT_FAILURES = int(os.environ.get("AEGIS_LLM_BALANCE_FAILURES", "2"))
_DEFAULT_COOLDOWN_MS = int(os.environ.get("AEGIS_LLM_BALANCE_COOLDOWN_MS", str(30 * 60 * 1000)))


def is_balance_error(error: Any) -> bool:
    """Return True when an exception or error string indicates billing/balance failure."""
    status = getattr(error, "status_code", None)
    if status is None:
        response = getattr(error, "response", None)
        status = getattr(response, "status_code", None)
    if status == 402:
        return True

    body = ""
    response = getattr(error, "response", None)
    if response is not None:
        try:
            body = str(getattr(response, "text", "") or getattr(response, "content", "") or "")
        except Exception:
            body = ""
    text = f"{error} {body}".lower()
    markers = (
        "402",
        "insufficient balance",
        "insufficient_quota",
        "insufficient_funds",
        "billing hard limit",
        "exceeded your current quota",
        "payment required",
    )
    return any(marker in text for marker in markers)


class LlmProviderCircuit:
    """Process-wide circuit for provider balance / billing failures."""

    def __init__(
        self,
        failure_threshold: int = _DEFAULT_FAILURES,
        cooldown_ms: int = _DEFAULT_COOLDOWN_MS,
    ) -> None:
        self._failure_threshold = max(1, failure_threshold)
        self._cooldown_ms = max(1_000, cooldown_ms)
        self._lock = threading.Lock()
        self._consecutive_failures = 0
        self._opened_at_ms = 0
        self._last_error = ""
        self._open_count = 0

    def record_success(self) -> None:
        with self._lock:
            self._consecutive_failures = 0
            if self._opened_at_ms and self._is_open_unlocked(int(time.time() * 1000)):
                return
            self._opened_at_ms = 0
            self._last_error = ""

    def record_error(self, error: Any) -> bool:
        """Record a provider error. Returns True when the circuit newly opens."""
        if not is_balance_error(error):
            return False
        now_ms = int(time.time() * 1000)
        newly_opened = False
        with self._lock:
            self._consecutive_failures += 1
            self._last_error = str(error)[:500]
            if self._consecutive_failures >= self._failure_threshold:
                if not self._is_open_unlocked(now_ms):
                    newly_opened = True
                    self._open_count += 1
                    logger.warning(
                        "LLM provider circuit OPEN after %d balance failures: %s",
                        self._consecutive_failures,
                        self._last_error,
                    )
                self._opened_at_ms = now_ms
        return newly_opened

    def is_open(self) -> bool:
        now_ms = int(time.time() * 1000)
        with self._lock:
            return self._is_open_unlocked(now_ms)

    def remaining_ms(self) -> int:
        now_ms = int(time.time() * 1000)
        with self._lock:
            if not self._is_open_unlocked(now_ms):
                return 0
            return max(0, self._opened_at_ms + self._cooldown_ms - now_ms)

    def status(self) -> dict[str, Any]:
        now_ms = int(time.time() * 1000)
        with self._lock:
            open_now = self._is_open_unlocked(now_ms)
            return {
                "open": open_now,
                "remaining_ms": max(0, self._opened_at_ms + self._cooldown_ms - now_ms) if open_now else 0,
                "consecutive_failures": self._consecutive_failures,
                "last_error": self._last_error,
                "open_count": self._open_count,
                "failure_threshold": self._failure_threshold,
                "cooldown_ms": self._cooldown_ms,
            }

    def reset(self) -> None:
        with self._lock:
            self._consecutive_failures = 0
            self._opened_at_ms = 0
            self._last_error = ""

    def _is_open_unlocked(self, now_ms: int) -> bool:
        if self._opened_at_ms <= 0:
            return False
        if now_ms - self._opened_at_ms >= self._cooldown_ms:
            self._opened_at_ms = 0
            self._consecutive_failures = 0
            return False
        return True


# Process singleton used by provider, cost tracker, autonomous loop, health.
PROVIDER_CIRCUIT = LlmProviderCircuit()
