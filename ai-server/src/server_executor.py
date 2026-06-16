"""Server Executor — routes capability invocations to real server clients.

Routing is manifest-driven via CapabilityCatalog.
Capability ID format: server_id.app_id.action
  e.g., pc-server.screenshot.get_screenshot
"""

from __future__ import annotations

import json
import logging
import re
import socket
import string
from typing import Any

from aegis_schema.models import Capability

logger = logging.getLogger("aegis_ai.server_executor")


def _safe_raw_preview(raw: str, limit: int = 500) -> str:
    """Return a diagnostic preview without leaking obvious secrets."""
    preview = raw[:limit]
    preview = re.sub(
        r"(?i)(password|passwd|secret|token|api_key|apikey|access_key)\s*[=:]\s*[^\s,;]+",
        r"\1=[REDACTED]",
        preview,
    )
    preview = re.sub(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "[EMAIL_REDACTED]",
        preview,
    )
    preview = re.sub(
        r"(?i)(phone(?:\s+number)?|tel|mobile)\s*[:=]\s*[\d+()\-\s]{7,}",
        r"\1=[REDACTED]",
        preview,
    )
    return preview.encode("unicode_escape", errors="backslashreplace").decode("ascii")


class _TcpCommandParams(dict[str, Any]):
    """Format helper that treats missing/None values as empty strings."""

    def __missing__(self, key: str) -> str:
        return ""


class ServerExecutor:
    """Routes capability invocations to the appropriate server client.

    Uses CapabilityCatalog to resolve manifests and route by server_id.
    For capabilities without direct clients, uses ExecutorRegistry (subprocess).
    """

    def __init__(self) -> None:
        self._clients: dict[str, Any] = {}
        self._catalog: Any = None

    def register_client(self, server_id: str, client: Any) -> None:
        self._clients[server_id] = client

    def set_catalog(self, catalog: Any) -> None:
        self._catalog = catalog

    def execute(self, capability: Capability, params: dict[str, Any]) -> dict[str, Any]:
        cap_id = capability.id

        manifest = None
        if self._catalog is not None:
            manifest = self._catalog.resolve(cap_id)

        if manifest is not None:
            server_id = manifest.server_id

            if server_id in self._clients:
                try:
                    return self._clients[server_id].invoke_capability(cap_id, params)
                except Exception as e:
                    return {"error": f"{server_id} execution error: {e}"}

            if server_id == "pc-server":
                return self._execute_pc_tcp(cap_id, params, manifest)

            executor = self._get_executor(manifest)
            if executor and executor.get("type") == "http":
                return self._execute_http(executor, params)

            if self._catalog is not None:
                result = self._catalog.execute(cap_id, params)
                if result.ok:
                    return result.result if isinstance(result.result, dict) else {"result": result.result}
                return {
                    "error": result.error.get("message", "Execution failed"),
                    "code": result.error.get("code", ""),
                    "details": result.error.get("details", {}),
                }

            return {"error": f"No client for server '{server_id}'."}

        if cap_id.startswith("pc-server.") or cap_id.startswith("pc."):
            return self._execute_pc_tcp(cap_id, params)

        return {"error": f"No executor for capability '{cap_id}'."}

    def _get_executor(self, manifest: Any) -> dict[str, Any] | None:
        if self._catalog is None:
            return None
        exec_reg = self._catalog.get_executor_registry()
        if exec_reg is None:
            return None
        exec_manifest = exec_reg.get(manifest)
        if exec_manifest is None:
            return None
        return {
            "type": exec_manifest.executor_type,
            "command": exec_manifest.command,
            "endpoint": exec_manifest.endpoint,
            "working_dir": exec_manifest.working_dir,
            "timeout_ms": exec_manifest.timeout_ms,
            "file_path": exec_manifest.file_path,
        }

    def _execute_http(self, executor: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        import urllib.request
        endpoint = executor.get("endpoint", "")
        timeout_ms = executor.get("timeout_ms", 30000)

        if not endpoint:
            return {"error": "No HTTP endpoint configured"}

        try:
            data = json.dumps(params).encode("utf-8")
            req = urllib.request.Request(
                endpoint,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout_ms / 1000) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result
        except Exception as e:
            return {"error": f"HTTP execution error: {e}", "endpoint": endpoint}

    def _execute_pc_tcp(
        self, cap_id: str, params: dict[str, Any], manifest: Any = None
    ) -> dict[str, Any]:
        tcp_fmt = ""
        if manifest is not None:
            tcp_fmt = getattr(manifest, "tcp_command", "")
        if not tcp_fmt and self._catalog is not None:
            m = self._catalog.resolve(cap_id)
            if m:
                tcp_fmt = getattr(m, "tcp_command", "")

        if not tcp_fmt:
            return {"error": f"Unknown PC capability: {cap_id}"}

        cmd = self._format_tcp_command(tcp_fmt, params)

        try:
            with socket.socket() as s:
                s.settimeout(10)
                s.connect(("localhost", 50052))
                s.sendall((cmd + "\n").encode())
                resp = b""
                while True:
                    chunk = s.recv(65536)
                    if not chunk or b"\n" in chunk:
                        resp += chunk
                        break
                    resp += chunk
        except OSError as e:
            return {"error": f"PC server unreachable: {e}", "capability_id": cap_id}

        raw = resp.decode(errors="replace").strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            return {
                "error": f"Invalid JSON from PC server: {e}",
                "capability_id": cap_id,
                "raw_preview": _safe_raw_preview(raw),
            }

    @staticmethod
    def _format_tcp_command(fmt: str, params: dict[str, Any]) -> str:
        if "{" not in fmt:
            return fmt
        formatter = string.Formatter()
        normalized: dict[str, Any] = {}
        for _, field_name, _, _ in formatter.parse(fmt):
            if not field_name:
                continue
            value = params.get(field_name, "")
            if value is None:
                value = ""
            elif isinstance(value, bool):
                value = str(value).lower()
            normalized[field_name] = value
        try:
            return fmt.format_map(_TcpCommandParams(normalized))
        except Exception:
            logger.debug("Failed to format TCP command: fmt=%s params=%s", fmt, params, exc_info=True)
            return fmt
