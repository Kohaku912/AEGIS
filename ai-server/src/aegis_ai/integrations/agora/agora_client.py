"""AGORA client — HTTP client for AGORA chat API."""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import httpx

from aegis_ai.integrations.agora.agora_types import (
    AgoraAccount,
    AgoraCursor,
    AgoraFetchResult,
    AgoraPost,
)

logger = logging.getLogger("aegis_ai.integrations.agora")

_DEFAULT_BASE_URL = "https://agora.kakunin.me"
_DEFAULT_TIMEOUT = 30.0


class AgoraClient:
    """HTTP client for AGORA chat API. Token is read from AGORA_TOKEN env var."""

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = (base_url or os.environ.get("AGORA_BASE_URL", _DEFAULT_BASE_URL)).rstrip("/")
        self._token = token or os.environ.get("AGORA_TOKEN", "")
        self._timeout = timeout

    @property
    def is_configured(self) -> bool:
        return bool(self._token)

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any] | list[Any]:
        if not self._token:
            return {"error": "authentication_required", "message": "AGORA_TOKEN is not set."}
        url = f"{self._base_url}{path}"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.request(method, url, headers=self._headers(), **kwargs)
                if resp.status_code == 401:
                    return {"error": "authentication_required", "message": "AGORA token is invalid or expired."}
                if resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    return {
                        "error": "rate_limited",
                        "message": "AGORA rate limit exceeded.",
                        "retry_after": retry_after,
                    }
                if resp.status_code >= 500:
                    return {"error": "server_error", "message": f"AGORA server error: HTTP {resp.status_code}."}
                if resp.status_code >= 400:
                    return {
                        "error": "client_error",
                        "message": f"AGORA client error: HTTP {resp.status_code}.",
                        "body": resp.text[:500],
                    }
                return resp.json()
        except httpx.TimeoutException:
            return {"error": "timeout", "message": f"AGORA request timed out after {self._timeout}s."}
        except httpx.RequestError as exc:
            return {"error": "network_error", "message": f"AGORA network error: {type(exc).__name__}."}
        except Exception as exc:
            return {"error": "unexpected_error", "message": f"AGORA unexpected error: {type(exc).__name__}."}

    def get_me(self) -> AgoraAccount | dict[str, Any]:
        data = self._request("GET", "/api/v1/me")
        if isinstance(data, dict) and "error" in data:
            return data
        return AgoraAccount(
            id=data.get("id", 0),
            name=data.get("name", ""),
            bio=data.get("bio", ""),
            created_at=data.get("created_at", ""),
        )

    def list_posts(self, since_id: int = 0, limit: int = 50) -> AgoraFetchResult | dict[str, Any]:
        data = self._request("GET", "/api/v1/posts", params={"since_id": since_id, "limit": limit})
        if isinstance(data, dict) and "error" in data:
            return data
        posts = [AgoraPost.from_dict(p) for p in data]
        max_id = max((p.id for p in posts), default=0)
        return AgoraFetchResult(
            posts=posts,
            max_post_id=max_id,
            has_new_posts=len(posts) > 0,
            fetched_at=int(time.time() * 1000),
        )

    def list_thread_posts(
        self, thread_id: int = 1, since_id: int = 0, limit: int = 50,
    ) -> AgoraFetchResult | dict[str, Any]:
        path = f"/api/v1/threads/{thread_id}/posts"
        data = self._request("GET", path, params={"since_id": since_id, "limit": limit})
        if isinstance(data, dict) and "error" in data:
            return data
        posts = [AgoraPost.from_dict(p) for p in data]
        max_id = max((p.id for p in posts), default=0)
        return AgoraFetchResult(
            posts=posts,
            max_post_id=max_id,
            has_new_posts=len(posts) > 0,
            fetched_at=int(time.time() * 1000),
        )

    def create_post(
        self, thread_id: int = 1, body: str = "", reply_to: int | None = None,
    ) -> AgoraPost | dict[str, Any]:
        payload: dict[str, Any] = {"body": body}
        if reply_to is not None:
            payload["reply_to"] = reply_to
        data = self._request("POST", f"/api/v1/threads/{thread_id}/posts", json=payload)
        if isinstance(data, dict) and "error" in data:
            return data
        return AgoraPost.from_dict(data)

    def get_cursor(self) -> AgoraCursor | dict[str, Any]:
        data = self._request("GET", "/api/v1/me/cursor")
        if isinstance(data, dict) and "error" in data:
            return data
        return AgoraCursor(last_read_post_id=data.get("last_read_post_id", 0))

    def update_cursor(self, last_read_post_id: int) -> AgoraCursor | dict[str, Any]:
        data = self._request("PUT", "/api/v1/me/cursor", json={"last_read_post_id": last_read_post_id})
        if isinstance(data, dict) and "error" in data:
            return data
        return AgoraCursor(last_read_post_id=data.get("last_read_post_id", 0))

    def get_mentions(self, since_id: int = 0, limit: int = 50) -> AgoraFetchResult | dict[str, Any]:
        data = self._request("GET", "/api/v1/me/mentions", params={"since_id": since_id, "limit": limit})
        if isinstance(data, dict) and "error" in data:
            return data
        posts = [AgoraPost.from_dict(p) for p in data]
        max_id = max((p.id for p in posts), default=0)
        return AgoraFetchResult(
            posts=posts,
            max_post_id=max_id,
            has_new_posts=len(posts) > 0,
            fetched_at=int(time.time() * 1000),
        )
