"""Webhook integration — HTTP webhook sender with retry and security."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger("aegis_ai.integrations.webhook")

_SENSITIVE_KEYS = {"key", "token", "password", "secret", "cookie", "auth"}


def _mask_headers(headers: dict[str, str]) -> dict[str, str]:
    masked = {}
    for k, v in headers.items():
        if any(s in k.lower() for s in _SENSITIVE_KEYS):
            masked[k] = "***MASKED***"
        else:
            masked[k] = v
    return masked


@dataclass
class WebhookRequest:
    webhook_id: str = ""
    url: str = ""
    method: str = "POST"
    headers: dict[str, str] = field(default_factory=dict)
    payload: dict[str, Any] = field(default_factory=dict)
    secret: str = ""
    timeout_seconds: float = 30.0
    retry_count: int = 0
    max_retries: int = 3
    created_at: int = 0


@dataclass
class WebhookResponse:
    webhook_id: str = ""
    success: bool = False
    status_code: int = 0
    response_body: str = ""
    error: str = ""
    duration_ms: float = 0.0
    attempts: int = 0
    created_at: int = 0


class WebhookSender:
    """Sends HTTP webhooks with retry, signing, and audit logging."""

    def __init__(self, audit_log: Any = None) -> None:
        self._audit = audit_log

    def send(self, request: WebhookRequest) -> WebhookResponse:
        if not request.webhook_id:
            request.webhook_id = f"wh_{uuid.uuid4().hex[:10]}"
        if not request.created_at:
            request.created_at = int(time.time() * 1000)

        if not request.url:
            return WebhookResponse(
                webhook_id=request.webhook_id,
                success=False,
                error="No URL provided.",
                created_at=int(time.time() * 1000),
            )

        if request.secret:
            body = json.dumps(request.payload, ensure_ascii=False)
            sig = hmac.new(
                request.secret.encode(), body.encode(), hashlib.sha256
            ).hexdigest()
            request.headers["X-Signature-256"] = f"sha256={sig}"

        response = self._execute_with_retry(request)
        self._record_audit(request, response)
        return response

    def _execute_with_retry(self, request: WebhookRequest) -> WebhookResponse:
        attempts = 0
        last_error = ""
        start = time.perf_counter()

        while attempts <= request.max_retries:
            attempts += 1
            try:
                with httpx.Client(timeout=request.timeout_seconds) as client:
                    resp = client.request(
                        method=request.method,
                        url=request.url,
                        headers=request.headers,
                        json=request.payload,
                    )
                    duration = (time.perf_counter() - start) * 1000
                    success = 200 <= resp.status_code < 300
                    return WebhookResponse(
                        webhook_id=request.webhook_id,
                        success=success,
                        status_code=resp.status_code,
                        response_body=resp.text[:1000],
                        error="" if success else f"HTTP {resp.status_code}",
                        duration_ms=duration,
                        attempts=attempts,
                        created_at=int(time.time() * 1000),
                    )
            except httpx.TimeoutException:
                last_error = f"Timeout after {request.timeout_seconds}s"
            except httpx.RequestError as exc:
                last_error = f"Request error: {exc}"
            except Exception as exc:
                last_error = f"Unexpected error: {exc}"

            if attempts <= request.max_retries:
                time.sleep(min(2 ** attempts, 10))

        duration = (time.perf_counter() - start) * 1000
        return WebhookResponse(
            webhook_id=request.webhook_id,
            success=False,
            error=last_error,
            duration_ms=duration,
            attempts=attempts,
            created_at=int(time.time() * 1000),
        )

    def _record_audit(self, request: WebhookRequest, response: WebhookResponse) -> None:
        if self._audit is None:
            return
        try:
            from aegis_ai.audit import AuditEntry
            entry = AuditEntry(
                action="webhook_sent",
                actor="webhook_sender",
                capability_id="webhook.send",
                decision="success" if response.success else "failed",
                reason=response.error or f"HTTP {response.status_code}",
                detail={
                    "webhook_id": request.webhook_id,
                    "url": request.url[:200],
                    "method": request.method,
                    "headers": _mask_headers(request.headers),
                    "status_code": response.status_code,
                    "attempts": response.attempts,
                    "duration_ms": response.duration_ms,
                },
            )
            self._audit.append(entry)
        except Exception as exc:
            logger.warning("Failed to record webhook audit: %s", exc)
