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
from urllib.parse import urlsplit

logger = logging.getLogger("aegis_ai.llm.provider_circuit")

_DEFAULT_FAILURES = int(os.environ.get("AEGIS_LLM_BALANCE_FAILURES", "1"))
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
        self._probe_in_flight = False

    def record_success(self) -> None:
        with self._lock:
            self._consecutive_failures = 0
            self._opened_at_ms = 0
            self._last_error = ""
            self._probe_in_flight = False

    def record_error(self, error: Any) -> bool:
        """Record a provider error. Returns True when the circuit newly opens."""
        if not is_balance_error(error):
            with self._lock:
                if self._probe_in_flight and self._opened_at_ms:
                    self._probe_in_flight = False
                    self._opened_at_ms = int(time.time() * 1000)
                    self._last_error = str(error)[:500]
            return False
        now_ms = int(time.time() * 1000)
        newly_opened = False
        with self._lock:
            self._consecutive_failures += 1
            self._probe_in_flight = False
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

    def allow_request(self) -> bool:
        """Allow normal calls, or exactly one recovery probe after cooldown."""
        now_ms = int(time.time() * 1000)
        with self._lock:
            if self._opened_at_ms <= 0:
                return True
            if now_ms - self._opened_at_ms < self._cooldown_ms:
                return False
            if self._probe_in_flight:
                return False
            self._probe_in_flight = True
            return True

    def status(self) -> dict[str, Any]:
        now_ms = int(time.time() * 1000)
        with self._lock:
            open_now = self._is_open_unlocked(now_ms)
            return {
                "open": open_now,
                "degraded": self._opened_at_ms > 0,
                "recovery_probe_due": self._opened_at_ms > 0 and not open_now and not self._probe_in_flight,
                "recovery_probe_in_flight": self._probe_in_flight,
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
            self._probe_in_flight = False

    def _is_open_unlocked(self, now_ms: int) -> bool:
        if self._opened_at_ms <= 0:
            return False
        return now_ms - self._opened_at_ms < self._cooldown_ms


def provider_origin(base_url: str | None) -> str:
    """Return a stable provider origin for circuit isolation."""
    value = str(base_url or "https://api.openai.com").strip().rstrip("/")
    parsed = urlsplit(value if "://" in value else f"https://{value}")
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}" or value.lower()


class ProviderCircuitRegistry:
    """Own one billing circuit per provider origin."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._circuits: dict[str, LlmProviderCircuit] = {}

    def get(self, base_url: str | None) -> LlmProviderCircuit:
        origin = provider_origin(base_url)
        with self._lock:
            circuit = self._circuits.get(origin)
            if circuit is None:
                circuit = LlmProviderCircuit()
                self._circuits[origin] = circuit
            return circuit

    def statuses(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            return {origin: circuit.status() for origin, circuit in self._circuits.items()}

    def status(self) -> dict[str, Any]:
        providers = self.statuses()
        open_items = {origin: value for origin, value in providers.items() if value.get("open")}
        degraded_items = {origin: value for origin, value in providers.items() if value.get("degraded")}
        return {
            "open": bool(open_items),
            "degraded": bool(degraded_items),
            "remaining_ms": max((int(item.get("remaining_ms", 0)) for item in open_items.values()), default=0),
            "last_error": next((str(item.get("last_error", "")) for item in degraded_items.values()), ""),
            "providers": providers,
        }

    def is_open(self) -> bool:
        return bool(self.status()["open"])

    def remaining_ms(self) -> int:
        return int(self.status()["remaining_ms"])

    def reset(self) -> None:
        with self._lock:
            for circuit in self._circuits.values():
                circuit.reset()


# Registry used by providers. The aggregate facade preserves the existing status API.
PROVIDER_CIRCUITS = ProviderCircuitRegistry()
PROVIDER_CIRCUIT = PROVIDER_CIRCUITS
