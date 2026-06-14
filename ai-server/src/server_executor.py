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
        elif cap_id.startswith("ai.search."):
            return self._execute_search(cap_id, params)
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
            return self._pc_tcp_execute(cap_id, params)
        try:
            return client.invoke_capability(cap_id, params)
        except Exception as e:
            return {"error": f"PC execution error: {e}"}

    def _pc_tcp_execute(self, cap_id: str, params: dict[str, Any]) -> dict[str, Any]:
        import socket
        import json

        cap_to_cmd = {
            "pc-server.screenshot.get_screenshot": "screenshot",
            "pc-server.window.get_active_window": "active_window",
            "pc-server.window.list_windows": "windows",
            "pc-server.clipboard.get_clipboard": "clipboard",
            "pc-server.system.get_os_info": "os_info",
            "pc-server.screen.get_screen_size": "screen_size",
            "pc-server.overlay.show_overlay": f"show_overlay {params.get('text', '')}",
            "pc-server.overlay.hide_overlay": "hide_overlay",
            "pc-server.app.launch_app": f"launch_app {params.get('app', '')}",
            "pc-server.window.focus_window": f"focus_window {params.get('title', '')}",
            "pc-server.window.resize_window": f"resize_window {params.get('title', '')},{params.get('width', 0)},{params.get('height', 0)}",
            "pc-server.window.minimize_window": f"minimize_window {params.get('title', '')}",
            "pc-server.window.maximize_window": f"maximize_window {params.get('title', '')}",
            "pc-server.window.close_window": f"close_window {params.get('title', '')}",
            "pc-server.input.mouse_move": f"mouse_move {params.get('x', 0)},{params.get('y', 0)}",
            "pc-server.input.mouse_click": f"mouse_click {params.get('x', 0)},{params.get('y', 0)},{params.get('button', 'left')}",
            "pc-server.input.keyboard_type": f"keyboard_type {params.get('text', '')}",
            "pc-server.input.press_hotkey": f"press_hotkey {params.get('keys', '')}",
            "pc-server.mouse.drag": f"mouse_drag {params.get('from_x', 0)},{params.get('from_y', 0)},{params.get('to_x', 0)},{params.get('to_y', 0)}",
            "pc-server.mouse.scroll": f"mouse_scroll {params.get('amount', 0)}",
            "pc-server.file.list": f"list_files {params.get('path', '.')}|{str(params.get('recursive', False)).lower()}",
            "pc-server.file.read": f"read_file {params.get('path', '')}|{params.get('max_bytes', 10000)}",
            "pc-server.file.search": f"search_files {params.get('path', '.')}|{params.get('pattern', '')}",
            "pc-server.file.write": f"write_file {params.get('path', '')}|{params.get('content', '')}|{str(params.get('append', False)).lower()}",
            "pc-server.file.delete": f"delete_file {params.get('path', '')}",
            "pc-server.file.copy": f"copy_file {params.get('src', '')}|{params.get('dst', '')}",
            "pc-server.file.move": f"move_file {params.get('src', '')}|{params.get('dst', '')}",
            "pc-server.file.create_dir": f"create_dir {params.get('path', '')}|{str(params.get('recursive', True)).lower()}",
            "pc-server.file.delete_dir": f"delete_dir {params.get('path', '')}|{str(params.get('recursive', False)).lower()}",
            "pc-server.file.metadata": f"file_metadata {params.get('path', '')}",
            "pc-server.file.set_permissions": f"set_file_permissions {params.get('path', '')}|{str(params.get('readonly', False)).lower()}",
            "pc-server.process.list": "list_processes",
            "pc-server.process.kill": f"kill_process {params.get('pid', 0)}",
            "pc-server.network.info": "network_info",
            "pc-server.disk.info": "disk_info",
            "pc-server.app.running_apps": "running_apps",
            "pc-server.system.env_vars": "env_vars",
            "pc-server.system.cwd": "cwd",
            "pc-server.system.get_env": f"get_env {params.get('name', '')}",
            "pc-server.system.logged_in_users": "logged_in_users",
            "pc-server.approval.overlay": f"overlay_approval {params.get('action', '')}",
            "pc-server.shell.execute": f"execute_shell {params.get('command', '')}|{params.get('working_dir', '')}",
            "pc-server.shell.powershell": f"execute_powershell {params.get('command', '')}|{params.get('working_dir', '')}",
            "pc-server.service.list": "list_services",
            "pc-server.service.start": f"start_service {params.get('name', '')}",
            "pc-server.service.stop": f"stop_service {params.get('name', '')}",
            "pc-server.task.list": "list_scheduled_tasks",
            "pc-server.registry.read": f"read_registry {params.get('key', '')}|{params.get('value_name', '')}",
            "pc-server.registry.list_keys": f"list_registry_keys {params.get('key', '')}",
            "pc-server.system.installed_software": "installed_software",
            "pc-server.system.windows_features": "windows_features",
            "pc-server.system.event_log": f"event_log {params.get('log_name', 'Application')}|{params.get('count', 10)}",
            "pc-server.system.performance_counters": "performance_counters",
            "pc-server.clipboard.set": f"set_clipboard {params.get('text', '')}",
            "pc-server.clipboard.image": "clipboard_image",
            "pc-server.app.open_url": f"open_url {params.get('url', '')}",
            "pc-server.system.lock": "lock_workstation",
            "pc-server.system.empty_recycle_bin": "empty_recycle_bin",
            "pc-server.screenshot.window": f"capture_window {params.get('title', '')}",
        }

        cmd = cap_to_cmd.get(cap_id)
        if cmd is None:
            return {"error": f"Unknown PC capability: {cap_id}"}

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
                source = params.get("source", "")
                if source == "autonomous":
                    pass
                elif not params.get("master_approved", False):
                    return {"error": "Only master can instruct AEGIS to post. Other users can only chat."}
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

    def _execute_search(self, cap_id: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            from aegis_ai.integrations.duckduckgo_search import DuckDuckGoSearch
        except ImportError:
            return {"error": "DuckDuckGo search module not available."}

        search = DuckDuckGoSearch()
        query = params.get("query", "")
        max_results = params.get("max_results", 5)

        if not query:
            return {"error": "query parameter is required."}

        if cap_id == "ai.search.web":
            response = search.search(query, max_results=max_results)
        elif cap_id == "ai.search.news":
            response = search.news(query, max_results=max_results)
        else:
            return {"error": f"Unknown search capability: {cap_id}"}

        if not response.success:
            return {"error": response.error, "query": query}

        return {
            "query": response.query,
            "results": [{"title": r.title, "url": r.url, "snippet": r.snippet, "source": r.source} for r in response.results],
            "count": len(response.results),
        }

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
