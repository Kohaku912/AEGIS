"""Workspace abstraction — Phase 8 (Agent Server 分離).

§19 で定義された workspace 戦略を `Workspace` ABC として表現し、
`LocalWorkspace` (in-process) と `RemoteAPIWorkspace` (HTTP remote) で
切り替え可能にする。

OpenHands SDK 呼び出しは引き続き `adapter.py` 内に閉じ込め、
`Workspace` クラスは SDK オブジェクトを返すための薄い bridge として
機能する。RemoteAPIWorkspace は HTTP 経由で agent server から SDK を
呼び出すため、AEGIS 本体プロセスに `openhands-sdk` をインストール
しなくてよい (Phase 8 DoD).

このモジュールは `from openhands.*` をしない (import 境界の不変条件).
"""

from __future__ import annotations

import logging
import os
import threading
from abc import ABC, abstractmethod
from typing import Any, Callable

from aegis_ai.agents.backends.openhands.config import WorkspaceSpec

logger = logging.getLogger("aegis_ai.agents.backends.openhands.workspace")


class Workspace(ABC):
    """Workspace の共通 interface.

    AEGIS core 側からは `Workspace` だけを意識する。`LocalWorkspace` /
    `RemoteAPIWorkspace` のどちらが返ってきても同じ API で呼べる。
    """

    name: str = "abstract"

    @abstractmethod
    def build(self, base_dir: str) -> Any:
        """OpenHands SDK の workspace オブジェクトを返す.

        Phase 8 では戻り値型は Any (SDK 依存を内部に閉じ込める).
        """

    @abstractmethod
    def is_remote(self) -> bool:
        """remote (別プロセス) で実行される workspace なら True."""

    def healthcheck(self, *, timeout_seconds: float | None = None) -> dict[str, Any]:
        """接続性の sanity check. remote のとき agent server の /healthz を叩く."""
        return {"status": "unknown", "workspace": self.name}

    def shutdown(self) -> None:
        """workspace を閉じる. ephemeral container を破棄するなど."""


class LocalWorkspace(Workspace):
    """同一プロセス内で OpenHands SDK を直接呼ぶ workspace.

    AEGIS 本体に `openhands-sdk` が入っている前提 (Phase 1-7 と同じ).
    開発 / CI / 隔離のいらない環境用。
    """

    name = "local"

    def build(self, base_dir: str) -> Any:
        from aegis_ai.agents.backends.openhands.adapter import build_workspace

        return build_workspace(self._spec, base_dir)

    def is_remote(self) -> bool:
        return False

    def __init__(self, spec: WorkspaceSpec | None = None) -> None:
        self._spec = spec or WorkspaceSpec()

    @property
    def spec(self) -> WorkspaceSpec:
        return self._spec


class RemoteAPIWorkspace(Workspace):
    """HTTP 経由で agent server (`aegis-openhands-agent.service`) に接続する workspace.

    Phase 8: AEGIS 本体プロセスには `openhands-sdk` をインストールしない。
    SDK 呼び出しは agent server 側で実行され、HTTP REST + SSE で結果 /
    progress を受け取る。

    Args:
        server_url: 例 `http://localhost:7100`. env `AGENT_SERVER_URL` で上書き可.
        timeout_seconds: HTTP request timeout (default 30).
        auth_token: 任意の bearer token. agent server 側が検証する.
    """

    name = "remote"

    def __init__(
        self,
        server_url: str | None = None,
        *,
        timeout_seconds: float = 30.0,
        auth_token: str | None = None,
        spec: WorkspaceSpec | None = None,
        http_post: Callable[..., Any] | None = None,
    ) -> None:
        url = server_url or os.environ.get("AGENT_SERVER_URL") or ""
        self._server_url = url.rstrip("/")
        self._timeout = float(timeout_seconds)
        self._auth_token = auth_token or os.environ.get("AGENT_SERVER_TOKEN") or ""
        self._spec = spec or WorkspaceSpec()
        # Injected HTTP poster for tests. Default uses urllib.
        self._http_post = http_post or _default_http_post
        self._lock = threading.RLock()
        self._last_health: dict[str, Any] = {}

    @property
    def server_url(self) -> str:
        return self._server_url

    @property
    def spec(self) -> WorkspaceSpec:
        return self._spec

    def is_remote(self) -> bool:
        return True

    def build(self, base_dir: str) -> Any:
        """remote workspace は SDK object を返さない.

        adapter 側に「remote mode では SDK 呼び出しを skip して
        `_run_remote()` に delegate する」分岐を入れる前提。
        ここでは sentinel を返して caller が気付けるようにする。
        """
        return _RemoteWorkspaceHandle(self, base_dir)

    def healthcheck(self, *, timeout_seconds: float | None = None) -> dict[str, Any]:
        """agent server の `/healthz` を叩く."""
        if not self._server_url:
            return {"status": "unconfigured", "workspace": self.name}
        timeout = self._timeout if timeout_seconds is None else float(timeout_seconds)
        try:
            resp = self._http_post(
                f"{self._server_url}/healthz",
                payload=None,
                timeout=timeout,
                headers=self._auth_headers(),
            )
        except Exception as exc:  # noqa: BLE001
            self._last_health = {"status": "unreachable", "error": str(exc), "workspace": self.name}
            return self._last_health
        self._last_health = {
            "status": "ok" if resp.get("ok") else "degraded",
            "response": resp,
            "workspace": self.name,
        }
        return self._last_health

    def post_json(
        self,
        path: str,
        payload: dict[str, Any],
        *,
        timeout_seconds: float | None = None,
    ) -> dict[str, Any]:
        """agent server に JSON POST. tools/call や /run で使用."""
        if not self._server_url:
            raise RuntimeError("RemoteAPIWorkspace: AGENT_SERVER_URL is not configured")
        url = f"{self._server_url}{path}"
        timeout = self._timeout if timeout_seconds is None else float(timeout_seconds)
        return self._http_post(
            url,
            payload=payload,
            timeout=timeout,
            headers=self._auth_headers(),
        )

    def _auth_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._auth_token:
            headers["Authorization"] = f"Bearer {self._auth_token}"
        return headers


class _RemoteWorkspaceHandle:
    """`RemoteAPIWorkspace.build()` が返す sentinel.

    OpenHands SDK の workspace オブジェクトの代わりに、remote call の
    ために必要な server URL だけを保持する。`OpenHandsBackend` 側は
    `isinstance(ws, _RemoteWorkspaceHandle)` で remote 判定する。
    """

    def __init__(self, workspace: RemoteAPIWorkspace, base_dir: str) -> None:
        self.workspace = workspace
        self.base_dir = base_dir


# ---------------------------------------------------------------------------
# Default HTTP poster (urllib — stdlib only, no extra dependency)
# ---------------------------------------------------------------------------


def _default_http_post(
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: float = 30.0,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    import json
    import urllib.error
    import urllib.request

    # Single egress chokepoint for the OpenHands remote backend. The agent server
    # receives task context derived from the user, so it goes through the gate.
    # Fails closed: an unconsultable gate refuses the request.
    try:
        from aegis_ai.egress import EgressRequest, get_egress_gate

        allowed = get_egress_gate().allow(
            EgressRequest(
                destination=url,
                purpose="agent.remote",
                component="openhands.workspace",
                data_summary="task context and payload",
            )
        )
    except Exception:
        logger.debug("Egress gate unavailable for OpenHands remote call — failing closed", exc_info=True)
        allowed = False
    if not allowed:
        raise RemoteAPIError(
            f"Egress denied for OpenHands remote call to {url}. "
            "The user's information must not leave the local environment.",
            status_code=0,
        )

    data: bytes | None = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
    method = "POST" if payload is not None else "GET"
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RemoteAPIError(
            f"agent server HTTP {exc.code}: {body[:500]}",
            status_code=exc.code,
        ) from exc
    except urllib.error.URLError as exc:
        raise RemoteAPIError(
            f"agent server unreachable: {exc.reason}",
            status_code=0,
        ) from exc
    except OSError as exc:
        raise RemoteAPIError(
            f"agent server connection error: {exc}",
            status_code=0,
        ) from exc
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise RemoteAPIError(
            f"agent server returned non-JSON: {body[:200]}",
            status_code=0,
        ) from exc


class RemoteAPIError(RuntimeError):
    """agent server への HTTP call が失敗したことを示す例外."""

    def __init__(self, message: str, *, status_code: int = 0) -> None:
        super().__init__(message)
        self.status_code = int(status_code)


def build_workspace_from_spec(
    spec: WorkspaceSpec,
    *,
    server_url: str | None = None,
    http_post: Callable[..., Any] | None = None,
) -> Workspace:
    """`WorkspaceSpec.mode` と env から Workspace を構築するヘルパ.

    `AGENT_BACKEND=remote` (or `AGENT_SERVER_URL` が設定されている) ときは
    `RemoteAPIWorkspace` を返し、それ以外は `LocalWorkspace` を返す。

    単体テスト / CI では `http_post` を mock に差し替え可能。
    """
    backend_mode = (os.environ.get("AGENT_BACKEND") or "").strip().lower()
    if backend_mode == "remote" or server_url or os.environ.get("AGENT_SERVER_URL"):
        return RemoteAPIWorkspace(
            server_url=server_url,
            spec=spec,
            http_post=http_post,
        )
    return LocalWorkspace(spec=spec)


__all__ = [
    "Workspace",
    "LocalWorkspace",
    "RemoteAPIWorkspace",
    "RemoteAPIError",
    "build_workspace_from_spec",
]
