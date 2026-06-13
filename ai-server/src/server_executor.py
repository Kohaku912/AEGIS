"""Server Executor — routes capability invocations to real server clients."""

from __future__ import annotations

import logging
import time
from typing import Any

from aegis_schema.models import Capability

logger = logging.getLogger("aegis_ai.server_executor")


class ServerExecutor:
    """Routes capability invocations to the appropriate server client.

    Supported prefixes:
    - pc.* → PC Server client
    - browser.* → Browser Server client
    - android.* → Android Server client
    - room.* → Room Server client
    - dev.* → Dev Server client
    - agora.* → AGORA Service (local)
    - ai.* → AI Server internal
    """

    def __init__(self) -> None:
        self._clients: dict[str, Any] = {}
        self._agora_service: Any = None

    def register_client(self, prefix: str, client: Any) -> None:
        self._clients[prefix] = client

    def set_agora_service(self, service: Any) -> None:
        self._agora_service = service

    def execute(self, capability: Capability, params: dict[str, Any]) -> dict[str, Any]:
        cap_id = capability.id

        if cap_id.startswith("ai.agora."):
            return self._execute_agora(cap_id, params)
        elif cap_id.startswith("pc."):
            return self._execute_pc(cap_id, params)
        elif cap_id.startswith("browser."):
            return self._execute_browser(cap_id, params)
        elif cap_id.startswith("android."):
            return self._execute_android(cap_id, params)
        elif cap_id.startswith("room."):
            return self._execute_room(cap_id, params)
        elif cap_id.startswith("dev."):
            return self._execute_dev(cap_id, params)
        elif cap_id.startswith("ai."):
            return self._execute_ai(cap_id, params)
        else:
            return {"error": f"No executor for capability '{cap_id}'."}

    def _execute_pc(self, cap_id: str, params: dict[str, Any]) -> dict[str, Any]:
        client = self._clients.get("pc")
        if client is None:
            return self._try_tcp_fallback(cap_id, params, host="localhost", port=50052)
        try:
            return client.invoke_capability(cap_id, params)
        except Exception as e:
            return {"error": f"PC execution error: {e}"}

    def _execute_browser(self, cap_id: str, params: dict[str, Any]) -> dict[str, Any]:
        client = self._clients.get("browser")
        if client is None:
            return {"error": "Browser server not connected.", "capability_id": cap_id}
        try:
            return client.invoke_capability(cap_id, params)
        except Exception as e:
            return {"error": f"Browser execution error: {e}"}

    def _execute_android(self, cap_id: str, params: dict[str, Any]) -> dict[str, Any]:
        client = self._clients.get("android")
        if client is None:
            return {"error": "Android server not connected.", "capability_id": cap_id}
        try:
            return client.invoke_capability(cap_id, params)
        except Exception as e:
            return {"error": f"Android execution error: {e}"}

    def _execute_room(self, cap_id: str, params: dict[str, Any]) -> dict[str, Any]:
        client = self._clients.get("room")
        if client is None:
            return {"error": "Room server not connected.", "capability_id": cap_id}
        try:
            return client.invoke_capability(cap_id, params)
        except Exception as e:
            return {"error": f"Room execution error: {e}"}

    def _execute_dev(self, cap_id: str, params: dict[str, Any]) -> dict[str, Any]:
        client = self._clients.get("dev")
        if client is None:
            return {"error": "Dev server not connected.", "capability_id": cap_id}
        try:
            return client.invoke_capability(cap_id, params)
        except Exception as e:
            return {"error": f"Dev execution error: {e}"}

    def _execute_agora(self, cap_id: str, params: dict[str, Any]) -> dict[str, Any]:
        if self._agora_service is None:
            try:
                from aegis_ai.integrations.agora.agora_service import AgoraService
                self._agora_service = AgoraService()
            except Exception as e:
                return {"error": f"AGORA not available: {e}"}

        svc = self._agora_service
        if not svc.is_configured:
            return {"error": "AGORA not configured. Set AGORA_TOKEN."}

        try:
            if cap_id == "ai.agora.get_me":
                me = svc.get_me()
                if hasattr(me, "id"):
                    return {"id": me.id, "name": me.name, "bio": me.bio}
                return me if isinstance(me, dict) else {"error": "Failed to get account"}

            elif cap_id == "ai.agora.read_posts":
                limit = params.get("limit", 50)
                result = svc.read_posts(limit=limit)
                if hasattr(result, "posts"):
                    return {
                        "posts": [{"id": p.id, "author": p.author.name, "body": p.body[:200]} for p in result.posts],
                        "count": len(result.posts),
                        "max_post_id": result.max_post_id,
                    }
                return result if isinstance(result, dict) else {"error": "Failed to read posts"}

            elif cap_id == "ai.agora.read_thread_posts":
                thread_id = params.get("thread_id", 1)
                limit = params.get("limit", 50)
                result = svc.read_thread_posts(thread_id=thread_id, limit=limit)
                if hasattr(result, "posts"):
                    return {
                        "posts": [{"id": p.id, "author": p.author.name, "body": p.body[:200]} for p in result.posts],
                        "count": len(result.posts),
                    }
                return result if isinstance(result, dict) else {"error": "Failed to read thread posts"}

            elif cap_id == "ai.agora.read_mentions":
                limit = params.get("limit", 50)
                result = svc.read_mentions(limit=limit)
                if hasattr(result, "posts"):
                    return {
                        "mentions": [{"id": p.id, "author": p.author.name, "body": p.body[:200]} for p in result.posts],
                        "count": len(result.posts),
                    }
                return result if isinstance(result, dict) else {"error": "Failed to read mentions"}

            elif cap_id == "ai.agora.get_cursor":
                cursor = svc.get_cursor()
                if hasattr(cursor, "last_read_post_id"):
                    return {"last_read_post_id": cursor.last_read_post_id}
                return cursor if isinstance(cursor, dict) else {"error": "Failed to get cursor"}

            elif cap_id == "ai.agora.update_cursor":
                last_id = params.get("last_read_post_id", 0)
                cursor = svc.update_cursor(last_read_post_id=last_id)
                if hasattr(cursor, "last_read_post_id"):
                    return {"last_read_post_id": cursor.last_read_post_id}
                return cursor if isinstance(cursor, dict) else {"error": "Failed to update cursor"}

            elif cap_id == "ai.agora.create_post":
                body = params.get("body", "")
                thread_id = params.get("thread_id", 1)
                reply_to = params.get("reply_to")
                result = svc.create_post(thread_id=thread_id, body=body, reply_to=reply_to)
                if hasattr(result, "id"):
                    return {"post_id": result.id, "body": result.body, "thread_id": result.thread_id}
                return result if isinstance(result, dict) else {"error": "Failed to create post"}

            else:
                return {"error": f"Unknown AGORA capability: {cap_id}"}

        except Exception as e:
            return {"error": f"AGORA execution error: {e}"}

    def _execute_ai(self, cap_id: str, params: dict[str, Any]) -> dict[str, Any]:
        return {"error": f"AI internal capability '{cap_id}' not yet routed.", "capability_id": cap_id}

    def _try_tcp_fallback(self, cap_id: str, params: dict[str, Any], host: str, port: int) -> dict[str, Any]:
        import socket
        import json
        try:
            s = socket.socket()
            s.settimeout(5)
            s.connect((host, port))
            cmd = json.dumps({"capability_id": cap_id, "params": params})
            s.sendall((cmd + "\n").encode())
            resp = b""
            while True:
                chunk = s.recv(4096)
                if not chunk or b"\n" in chunk:
                    resp += chunk
                    break
                resp += chunk
            s.close()
            return json.loads(resp.decode().strip())
        except Exception as e:
            return {"error": f"Server unreachable ({host}:{port}): {e}", "capability_id": cap_id}
