"""AEGIS Agent Server — Phase 8 (Agent Server 分離).

`aegis-openhands-agent.service` として host 上で動く別プロセス。
MCP tools/list + tools/call を受ける HTTP エンドポイントとヘルスチェックを
提供する。

エンドポイント:
- POST /mcp      : JSON-RPC 2.0 で `tools/list` / `tools/call` / `initialize` を受ける
- GET  /healthz  : ヘルスチェック
- POST /cancel/<task_id> : 該当 task_id の会話をキャンセル (best-effort)

AEGIS 本体 (ai-server) とは別プロセスで動く:
- AEGIS 本体プロセスには `openhands-sdk` をインストールしなくてよい
- OpenHands SDK は agent server 側のオプション依存 (Phase 8 DoD)
- AEGIS capability 実行は Phase 7 MCP gateway と同じ protocol で受ける
  → Phase 9 で dev-server 削除しても capability ID は変わらない

Phase 8 MVP:
- stdlib の `http.server` ベース (FastAPI / aiohttp 不要)
- OpenHands SDK 未インストールでも AEGIS capability 実行は動く
  (events は空 / 単一 "message" イベントのみ)
- OpenHands SDK があれば `adapter.py` 経由で会話駆動
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_agent_server.main")

# Hard-cap body size to avoid DoS.
_MAX_BODY_BYTES = 1 * 1024 * 1024  # 1 MB

# Cancelled task IDs (in-memory). Multiple agent server replicas がある場合は
# 共有 KV (Redis) に置き換える前提 — Phase 8 MVP では single replica 想定.
_cancelled: set[str] = set()
_cancelled_lock = threading.RLock()
_running_backends: dict[str, Any] = {}
_running_backends_lock = threading.RLock()
_ENV_LOADED = False


def _mark_cancelled(task_id: str) -> None:
    with _cancelled_lock:
        _cancelled.add(task_id)


def _consume_cancelled(task_id: str) -> bool:
    with _cancelled_lock:
        if task_id in _cancelled:
            _cancelled.discard(task_id)
            return True
        return False


def _register_running_backend(task_id: str, backend: Any) -> None:
    with _running_backends_lock:
        _running_backends[task_id] = backend


def _unregister_running_backend(task_id: str, backend: Any) -> None:
    with _running_backends_lock:
        if _running_backends.get(task_id) is backend:
            _running_backends.pop(task_id, None)


def _interrupt_running_backend(task_id: str) -> bool:
    with _running_backends_lock:
        backend = _running_backends.get(task_id)
    if backend is None:
        return False
    try:
        return bool(asyncio.run(backend.cancel(task_id)))
    except Exception:  # noqa: BLE001
        logger.warning("failed to interrupt running backend for %s", task_id, exc_info=True)
        return False


def _load_project_env() -> None:
    """Load repo `.env` once so standalone agent-server sees LLM credentials."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        _ENV_LOADED = True
        return
    candidates = (
        Path(__file__).resolve().parents[3] / ".env",
        Path(__file__).resolve().parents[2] / ".env",
    )
    for env_path in candidates:
        if env_path.exists():
            load_dotenv(env_path, override=False)
            break
    _ENV_LOADED = True


def _configured_agent_server_token() -> str:
    _load_project_env()
    return str(os.environ.get("AGENT_SERVER_TOKEN") or "").strip()


def _is_authorized_request(headers: Any) -> bool:
    required = _configured_agent_server_token()
    if not required:
        return True
    header = str(headers.get("Authorization", "") or "").strip()
    if not header.lower().startswith("bearer "):
        return False
    supplied = header[7:].strip()
    return bool(supplied) and supplied == required


# ---------------------------------------------------------------------------
# MCP dispatch
# ---------------------------------------------------------------------------


def _dispatch_mcp(payload: dict[str, Any]) -> dict[str, Any]:
    """JSON-RPC 2.0 の method を見て dispatch する.

    対応 method:
    - initialize: server info + capabilities を返す
    - tools/list: AEGIS capability 一覧 (MCP tool schema)
    - tools/call: capability 実行
    """
    request_id = payload.get("id", 1)
    method = payload.get("method", "")
    params = payload.get("params", {}) or {}

    if method == "initialize":
        return _initialize_response(request_id)
    if method == "tools/list":
        return _tools_list_response(request_id, params)
    if method == "tools/call":
        return _tools_call_response(request_id, params)
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"method not found: {method!r}"},
    }


def _initialize_response(request_id: Any) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2025-06-18",
            "serverInfo": {"name": "aegis-openhands-agent", "version": "0.1.0"},
            "capabilities": {"tools": {"listChanged": False}},
        },
    }


def _tools_list_response(request_id: Any, params: dict[str, Any]) -> dict[str, Any]:
    """AEGIS CapabilityCatalog → MCP tool schema 一覧.

    Phase 7 `mcp_gateway.list_tools_for_agent` を直接使う。
    """
    try:
        from aegis_ai.tools.mcp_gateway import list_tools_for_agent  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return _internal_error(request_id, f"mcp_gateway import failed: {exc}")
    # No profile enforcement at the agent server boundary — the AEGIS core
    # has already filtered by profile before sending the request.
    from aegis_ai.agents.profiles.models import AgentProfile  # type: ignore

    profile = AgentProfile(
        id="agent-server",
        backend="openhands",
        llm_profile_name="tool_planning",
        allowed_capabilities=[],
        denied_capabilities=[],
    )
    tools = list_tools_for_agent(profile)
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"tools": tools, "nextCursor": None},
    }


def _tools_call_response(request_id: Any, params: dict[str, Any]) -> dict[str, Any]:
    name = str(params.get("name", "") or "")
    arguments = params.get("arguments", {}) or {}
    if not name:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32602, "message": "params.name is required"},
        }

    # cancel check
    session_id = str(arguments.get("session_id", "") or "")
    if session_id and _consume_cancelled(session_id):
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": "cancelled"}],
                "isError": True,
                "is_error": True,
                "error_code": "cancelled",
                "error": "agent run cancelled",
                "events": [{"kind": "cancelled", "ts_ms": int(time.time() * 1000)}],
            },
        }

    if name == "agent.run":
        return _agent_run_response(request_id, arguments)

    try:
        from aegis_ai.tools.mcp_gateway import call_tool_for_agent  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return _internal_error(request_id, f"mcp_gateway import failed: {exc}")

    # Phase 8 MVP: agent server には AEGIS runtime 全体がないので、call 用の
    # broker をその場で構築する。ToolBroker(registry=ToolRegistry()) で
    # self-contained な実行。catalog / policy engine / approval manager は
    # プロセス内に常駐しないが capability 登録 (ToolRegistry) は動く。
    from aegis_ai.tool_registry import ToolRegistry  # type: ignore
    from tool_broker import ToolBroker  # type: ignore

    runtime = _make_runtime_stub()
    started_ms = int(time.time() * 1000)
    # ToolBroker 経由 (Phase 7 §36 singleton hook がないため、毎回 new)
    broker = ToolBroker(registry=ToolRegistry())
    runtime.tool_broker = broker
    try:
        result = call_tool_for_agent(
            name,
            arguments,
            profile=_agent_server_profile(),
            runtime=runtime,
        )
    except Exception as exc:  # noqa: BLE001
        return _internal_error(request_id, f"call_tool_for_agent failed: {exc!r}")

    is_error = bool(result.get("isError", False))
    events = [
        {
            "kind": "action",
            "tool": name,
            "arguments": json.dumps(arguments, ensure_ascii=False, default=str),
            "ts_ms": int(time.time() * 1000),
        },
        {
            "kind": "completed" if not is_error else "failed",
            "ts_ms": int(time.time() * 1000),
            "summary": str(_first_text(result.get("content", []))),
        },
    ]
    finished_ms = int(time.time() * 1000)
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            **result,
            "events": events,
            "duration_ms": finished_ms - started_ms,
        },
    }
    if is_error:
        response["result"]["is_error"] = True
    return response


def _agent_run_response(request_id: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        result = _run_openhands_task(arguments)
    except Exception as exc:  # noqa: BLE001
        return _internal_error(request_id, f"agent.run failed: {exc!r}")

    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result,
    }
    return response


def _internal_error(request_id: Any, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32603, "message": message},
    }


def _first_text(content: list[dict[str, Any]]) -> str:
    for item in content or []:
        if item.get("type") == "text":
            return str(item.get("text", ""))
    return ""


def _make_runtime_stub() -> Any:
    """`call_tool_for_agent` が要求する `runtime` 属性を満たす stub."""
    runtime = type("_RuntimeStub", (), {})()
    runtime.tool_broker = None
    return runtime


def _agent_server_profile() -> Any:
    """agent server 内で capability 実行時に与える profile (全許可)."""
    from aegis_ai.agents.profiles.models import AgentProfile  # type: ignore

    return AgentProfile(
        id="agent-server",
        backend="openhands",
        llm_profile_name="tool_planning",
        allowed_capabilities=[],
        denied_capabilities=[],
    )


def _run_openhands_task(arguments: dict[str, Any]) -> dict[str, Any]:
    import asyncio

    from aegis_ai.agents.backends.openhands.backend import OpenHandsBackend
    from aegis_ai.agents.runtime.models import AgentTask

    task_id = str(arguments.get("session_id") or f"agent-{int(time.time() * 1000)}")
    goal = str(arguments.get("goal") or "").strip()
    if not goal:
        return {
            "content": [{"type": "text", "text": "goal is required"}],
            "isError": True,
            "is_error": True,
            "error_code": "invalid_arguments",
            "error": "goal is required",
            "events": [],
        }

    _load_project_env()
    llm_config = _resolve_llm_config(dict(arguments.get("llm") or {}))
    workspace_spec = _workspace_from_arguments(dict(arguments.get("workspace") or {}))
    metadata = dict(arguments.get("metadata") or {})
    metadata["llm"] = llm_config
    metadata["workspace"] = {
        "mode": workspace_spec.mode,
        "path": workspace_spec.path,
        "mount_ro": workspace_spec.mount_ro,
        "protected_paths": list(workspace_spec.protected_paths),
        "base_branch": workspace_spec.base_branch,
        "worktree_branch": workspace_spec.worktree_branch,
    }
    tools = _filter_openhands_tools(arguments.get("tools"))
    if tools:
        metadata["tools"] = tools

    task = AgentTask(
        task_id=task_id,
        goal=goal,
        timeout_seconds=int(arguments.get("timeout_seconds") or 600),
        metadata=metadata,
    )

    backend = OpenHandsBackend(default_workspace=workspace_spec, base_dir=os.getcwd())
    _register_running_backend(task_id, backend)
    try:
        result = asyncio.run(backend.run(task))
        response = _agent_result_to_response(result)
        return response
    finally:
        _unregister_running_backend(task_id, backend)


def _agent_result_to_response(result: Any) -> dict[str, Any]:
    from aegis_ai.task.task_manager import TaskStatus

    status = getattr(result, "status", TaskStatus.FAILED)
    is_error = status != TaskStatus.COMPLETED
    events: list[dict[str, Any]] = []
    summary = str(getattr(result, "summary", "") or "")
    if summary:
        events.append(
            {
                "kind": "message",
                "role": "assistant",
                "text": summary,
                "ts_ms": int(time.time() * 1000),
            }
        )
    for action in list(getattr(result, "actions", []) or []):
        events.append(
            {
                "kind": "action",
                "tool": str(getattr(action, "capability_id", "") or "unknown"),
                "arguments": json.dumps(getattr(action, "arguments", {}) or {}, ensure_ascii=False, default=str),
                "duration_ms": int(getattr(action, "duration_ms", 0) or 0),
                "ts_ms": int(time.time() * 1000),
            }
        )
    terminal_kind = "completed"
    if status == TaskStatus.CANCELLED:
        terminal_kind = "cancelled"
    elif is_error:
        terminal_kind = "failed"
    events.append(
        {
            "kind": terminal_kind,
            "summary": summary,
            "ts_ms": int(time.time() * 1000),
        }
    )
    payload = {
        "content": [{"type": "text", "text": summary or status.name.lower()}],
        "isError": is_error,
        "is_error": is_error,
        "summary": summary,
        "events": events,
        "duration_ms": int(getattr(getattr(result, "usage", None), "duration_ms", 0) or 0),
        "usage": {
            "input_tokens": int(getattr(getattr(result, "usage", None), "input_tokens", 0) or 0),
            "output_tokens": int(getattr(getattr(result, "usage", None), "output_tokens", 0) or 0),
            "cache_hit_tokens": int(getattr(getattr(result, "usage", None), "cache_hit_tokens", 0) or 0),
            "cost_usd": float(getattr(getattr(result, "usage", None), "cost_usd", 0.0) or 0.0),
            "model": str(getattr(getattr(result, "usage", None), "model", "") or ""),
        },
        "provider": str(getattr(getattr(result, "usage", None), "provider", "") or ""),
    }
    errors = list(getattr(result, "errors", []) or [])
    if errors:
        first = errors[0]
        payload["error_code"] = str(getattr(first, "code", "execution_error") or "execution_error")
        payload["error"] = str(getattr(first, "message", "agent run failed") or "agent run failed")
    elif status == TaskStatus.CANCELLED:
        payload["error_code"] = "cancelled"
        payload["error"] = summary or "agent run cancelled"
    return payload


def _resolve_llm_config(llm: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(llm, dict):
        llm = {}
    profile_id = str(llm.get("profile") or "tool_planning").strip() or "tool_planning"
    if {"model", "api_key_env"} <= set(llm.keys()):
        return dict(llm)

    from aegis_ai.llm.settings_resolver import LLMSettingsResolver

    llm_path = Path(__file__).resolve().parents[2] / "config" / "llm.yaml"
    resolver = LLMSettingsResolver(str(llm_path))
    settings = resolver.resolve(profile_id=profile_id)
    return {
        "profile": profile_id,
        "provider": settings.provider,
        "model": settings.model,
        "api_key_env": settings.api_key_env,
        "base_url": settings.base_url,
        "max_tokens": settings.max_tokens,
        "temperature": settings.temperature,
        "timeout_seconds": settings.timeout_seconds,
    }


def _workspace_from_arguments(workspace: dict[str, Any]) -> Any:
    from aegis_ai.agents.backends.openhands.config import WorkspaceSpec

    if not isinstance(workspace, dict):
        workspace = {}
    return WorkspaceSpec(
        mode=str(workspace.get("mode") or "isolated"),
        path=workspace.get("path"),
        mount_ro=bool(workspace.get("mount_ro", False)),
        protected_paths=list(workspace.get("protected_paths") or []),
        base_branch=str(workspace.get("base_branch") or ""),
        worktree_branch=str(workspace.get("worktree_branch") or ""),
    )


def _filter_openhands_tools(value: Any) -> list[str]:
    allowed = {"terminal", "file_editor", "task_tracker"}
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item) in allowed]


# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------


class _Handler(BaseHTTPRequestHandler):
    server_version = "AegisAgentServer/0.1.0"

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        logger.info("%s - %s", self.address_string(), format % args)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            self._json_response(200, {"ok": True, "ts_ms": int(time.time() * 1000)})
            return
        self._json_response(404, {"error": "not found", "path": self.path})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/mcp" or self.path.startswith("/cancel/"):
            if not _is_authorized_request(self.headers):
                self._json_response(401, {"error": "unauthorized"})
                return
        if self.path.startswith("/cancel/"):
            task_id = self.path[len("/cancel/"):]
            _mark_cancelled(task_id)
            interrupted = _interrupt_running_backend(task_id)
            self._json_response(200, {"ok": True, "task_id": task_id, "interrupted": interrupted})
            return
        if self.path == "/mcp":
            body = self._read_body()
            try:
                payload = json.loads(body or b"{}")
            except json.JSONDecodeError as exc:
                self._json_response(400, {"error": f"invalid JSON: {exc}"})
                return
            response = _dispatch_mcp(payload)
            status = 200 if "error" not in response else 400
            if "error" in response and response["error"].get("code") == -32601:
                status = 404
            self._json_response(status, response)
            return
        self._json_response(404, {"error": "not found", "path": self.path})

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return b""
        if length > _MAX_BODY_BYTES:
            self._json_response(413, {"error": "payload too large"})
            return b""
        return self.rfile.read(length)

    def _json_response(self, status: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(host: str = "127.0.0.1", port: int = 7100) -> None:
    """`aegis-openhands-agent.service` の entrypoint."""
    _load_project_env()
    logging.basicConfig(
        level=os.environ.get("AGENT_SERVER_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    httpd = ThreadingHTTPServer((host, port), _Handler)
    logger.info("aegis-openhands-agent listening on http://%s:%d", host, port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("shutting down")
    finally:
        httpd.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aegis-openhands-agent")
    parser.add_argument("--host", default=os.environ.get("AGENT_SERVER_HOST", "127.0.0.1"))
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("AGENT_SERVER_PORT", "7100")),
    )
    args = parser.parse_args(argv)
    serve(args.host, args.port)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
