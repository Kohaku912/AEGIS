"""Server Executor — routes capability invocations to real server clients.

Routing is manifest-driven via CapabilityCatalog.
Capability ID format: server_id.app_id.action
  e.g., pc-server.screenshot.get_screenshot
"""

from __future__ import annotations

import json
import logging
import socket
from typing import Any

from aegis_schema.models import Capability

logger = logging.getLogger("aegis_ai.server_executor")


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

            if self._catalog is not None:
                result = self._catalog.execute(cap_id, params)
                if result.ok:
                    return result.result if isinstance(result.result, dict) else {"result": result.result}
                return {"error": result.error.get("message", "Execution failed"), "code": result.error.get("code", "")}

            return {"error": f"No client for server '{server_id}'."}

        if cap_id.startswith("pc-server.") or cap_id.startswith("pc."):
            return self._execute_pc_tcp(cap_id, params)

        return {"error": f"No executor for capability '{cap_id}'."}

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
            s = socket.socket()
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
            s.close()
            return json.loads(resp.decode().strip())
        except Exception as e:
            return {"error": f"PC server unreachable: {e}", "capability_id": cap_id}

    @staticmethod
    def _format_tcp_command(fmt: str, params: dict[str, Any]) -> str:
        if "{" not in fmt:
            return fmt
        try:
            return fmt.format(**params)
        except KeyError:
            safe = {k: v for k, v in params.items()}
            try:
                return fmt.format(**safe)
            except Exception:
                return fmt
