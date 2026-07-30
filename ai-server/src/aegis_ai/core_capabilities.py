"""In-process AI Server capabilities."""

from __future__ import annotations

import base64
import logging
import mimetypes
import os
import threading
from pathlib import Path
from typing import Any

from aegis_ai.integrations.agora.agora_service import AgoraService
from aegis_ai.integrations.agora.agora_types import AgoraFetchResult, AgoraPost
from aegis_ai.memory.memory_ingest import (
    build_agora_posts_text,
    save_memory_payload,
    sync_agora_posts_to_memory,
)

logger = logging.getLogger("aegis_ai.core_capabilities")


class AegisCoreCapabilityClient:
    """Executes AI-local capabilities without leaving the AI server process."""

    IMAGE_MAX_BYTES = 5 * 1024 * 1024
    READ_MAX_BYTES = 10 * 1024 * 1024
    ALLOWED_IMAGE_MIMES = {"image/png", "image/jpeg", "image/webp", "image/gif"}

    def __init__(self, *, data_dir: str, server_executor: Any, personal_managers: dict[str, Any] | None = None) -> None:
        self._data_dir = Path(data_dir).resolve()
        configured = os.getenv("AEGIS_WORKSPACE_DIR", "").strip()
        self._workspace = Path(configured).expanduser().resolve() if configured else self._data_dir / "aegis_workspace"
        self._workspace.mkdir(parents=True, exist_ok=True)
        self._server_executor = server_executor
        self._personal = personal_managers or {}
        self._agora = AgoraService()
        self._agora_memory_lock = threading.RLock()
        self._agora_memory_inflight: set[int] = set()
        social_manager = self._personal.get("social_manager")
        if social_manager is not None:
            social_manager.set_cursor_updater("agora", self._agora.update_cursor)

    @property
    def workspace_dir(self) -> Path:
        return self._workspace

    def invoke_capability(self, capability_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = params or {}
        if capability_id == "ai-server.notification.broadcast_overlay":
            return self._broadcast_overlay(params)
        if capability_id == "ai-server.workspace.write_file":
            return self._write_file(params)
        if capability_id == "ai-server.workspace.read_file":
            return self._read_file(params)
        if capability_id == "ai-server.workspace.list_files":
            return self._list_files(params)
        if capability_id.startswith("ai-server.memory."):
            return self._memory(capability_id, params)
        if capability_id.startswith("ai-server.agora."):
            return self._agora_capability(capability_id, params)
        if capability_id.startswith("ai-server.user_model."):
            return self._user_model(capability_id, params)
        if capability_id.startswith("ai-server.hook."):
            return self._hooks(capability_id, params)
        if capability_id.startswith("ai-server.commitment."):
            return self._commitments(capability_id, params)
        if capability_id.startswith("ai-server.delegation_policy."):
            return self._delegation_policy(capability_id, params)
        if capability_id.startswith("ai-server.situation."):
            return self._situation(capability_id, params)
        if capability_id.startswith("ai-server.interruption."):
            return self._interruption(capability_id, params)
        if capability_id.startswith("ai-server.repair."):
            return self._repair(capability_id, params)
        if capability_id.startswith("ai-server.presentation."):
            return self._presentation(capability_id, params)
        return {"ok": False, "error": f"Unsupported AI capability: {capability_id}", "code": "UNSUPPORTED_CAPABILITY"}

    @staticmethod
    def _dataclass_to_dict(value: Any) -> Any:
        if isinstance(value, list):
            return [AegisCoreCapabilityClient._dataclass_to_dict(item) for item in value]
        if isinstance(value, dict):
            return {k: AegisCoreCapabilityClient._dataclass_to_dict(v) for k, v in value.items()}
        if hasattr(value, "to_dict"):
            return value.to_dict()
        if hasattr(value, "__dict__"):
            return {
                key: AegisCoreCapabilityClient._dataclass_to_dict(item)
                for key, item in value.__dict__.items()
            }
        return value

    def _memory(self, capability_id: str, params: dict[str, Any]) -> dict[str, Any]:
        manager = self._personal.get("memory_manager")
        if capability_id.endswith(".sleep"):
            sleep_manager = self._personal.get("sleep_manager")
            if sleep_manager is None:
                return {"ok": False, "error": "SleepManager unavailable", "code": "BACKEND_UNAVAILABLE"}
            reason = str(params.get("reason") or "manual").strip() or "manual"
            try:
                started = bool(sleep_manager.start_sleep(reason=reason))
                status = sleep_manager.get_status() if hasattr(sleep_manager, "get_status") else {}
                if not started:
                    return {
                        "ok": True,
                        "started": False,
                        "state": status.get("state", "running"),
                        "status": status,
                        "result": "Memory sleep is already running.",
                    }
                return {
                    "ok": True,
                    "started": True,
                    "state": status.get("state", "running"),
                    "status": status,
                    "result": "Memory sleep consolidation has started.",
                }
            except Exception as exc:
                return {"ok": False, "error": str(exc), "code": "SLEEP_START_FAILED"}
        if capability_id.endswith(".save"):
            result = save_memory_payload(
                params,
                data_dir=str(self._data_dir),
                llm_provider=self._personal.get("llm_provider"),
            )
            return result.to_dict()
        if capability_id.endswith(".search"):
            query = str(params.get("query") or "").strip()
            if not query:
                return {"ok": False, "error": "query is required", "code": "INVALID_ARGUMENT"}
            limit = min(max(int(params.get("limit") or 10), 1), 50)
            if manager is not None and hasattr(manager, "search_memory"):
                hits = manager.search_memory(query, limit=limit)
            else:
                from aegis_ai.memory.advanced import AdvancedMemory

                advanced = AdvancedMemory(data_dir=str(self._data_dir / "memory"))
                hits = [
                    {"type": "fact", "content": getattr(item, "content", str(item)), "source": "advanced"}
                    for item in advanced.search_facts(query)[:limit]
                ]
            return {
                "ok": True,
                "query": query,
                "results": hits,
                "result": "No memory found." if not hits else f"Found {len(hits)} memory item(s).",
            }
        return {"ok": False, "error": "Unsupported memory capability", "code": "UNSUPPORTED_CAPABILITY"}

    def _agora_capability(self, capability_id: str, params: dict[str, Any]) -> dict[str, Any]:
        if capability_id.endswith(".read_posts"):
            requested_since_id = int(params.get("since_id") or 0)
            since_id = requested_since_id
            limit = min(max(int(params.get("limit") or 20), 1), 200)
            cursor_before = 0
            if since_id <= 0:
                cursor = self._agora.get_cursor()
                if isinstance(cursor, dict):
                    return {"ok": False, **cursor}
                cursor_before = int(getattr(cursor, "last_read_post_id", 0) or 0)
                since_id = cursor_before
            result = self._agora.read_posts(since_id=since_id, limit=limit)
            if isinstance(result, dict):
                return {"ok": False, **result}
            posts = result.posts if isinstance(result, AgoraFetchResult) else []
            if posts:
                social_manager = self._personal.get("social_manager")
                inbox_items = social_manager.ingest("agora", posts) if social_manager is not None else []
                new_external_ids = {
                    int(item.external_message_id)
                    for item in inbox_items
                    if str(item.external_message_id).isdigit()
                }
                posts_to_process = (
                    [post for post in posts if int(getattr(post, "id", 0) or 0) in new_external_ids]
                    if social_manager is not None
                    else posts
                )
                if social_manager is not None and hasattr(social_manager, "enqueue_processing"):
                    social_manager.enqueue_processing(inbox_items)
                    processed_items = []
                else:
                    processed_items = social_manager.process_new_items(inbox_items) if social_manager is not None else []
                pending_items = processed_items or inbox_items
                self._enqueue_agora_memory_sync(posts_to_process)
                posts_text = build_agora_posts_text(
                    posts,
                    header=(
                        f"AGORA: Retrieved {len(posts)} post(s); durable processing is queued."
                    ),
                )
                payload = {
                    "ok": True,
                    "message": posts_text,
                    "result": posts_text,
                    "summary": posts_text,
                    "posts": [self._dataclass_to_dict(post) for post in posts],
                    "mentions": [],
                    "saved_people": [],
                    "social_observations": 0,
                    "social_episodes": 0,
                    "advanced_conversations": 0,
                    "memory_sync_pending": bool(posts_to_process),
                }
                payload["social_inbox_items"] = [item.to_dict() for item in processed_items or inbox_items]
            else:
                payload = {
                    "ok": True,
                    "message": "AGORA: No new posts.",
                    "result": "AGORA: No new posts.",
                    "summary": "AGORA: No new posts.",
                    "posts": [],
                    "mentions": [],
                    "saved_people": [],
                    "social_observations": 0,
                    "social_episodes": 0,
                    "advanced_conversations": 0,
                }
            payload.update(
                {
                    "ok": True,
                    "has_new_posts": bool(posts),
                    "max_post_id": result.max_post_id,
                    "unread_count": len(posts),
                    "cursor_before": cursor_before,
                    "cursor_after": cursor_before,
                    "retrieved_through": result.max_post_id,
                    "processing_pending": bool(posts) and (
                        social_manager is None
                        or any(
                            item.status.value not in {"replied", "acknowledged", "skipped", "failed"}
                            for item in pending_items
                        )
                    ),
                    "read_mode": "history" if requested_since_id > 0 else "unread",
                    "fallback_recent": False,
                }
            )
            return payload
        if capability_id.endswith(".post"):
            body = str(params.get("body") or params.get("message") or "").strip()
            if not body:
                return {"ok": False, "error": "body is required", "code": "INVALID_ARGUMENT"}
            result = self._agora.create_post(
                thread_id=int(params.get("thread_id") or 1),
                body=body,
                reply_to=int(params["reply_to"]) if params.get("reply_to") not in (None, "") else None,
            )
            if isinstance(result, dict):
                return {"ok": False, **result}
            if isinstance(result, AgoraPost):
                return {"ok": True, "post": self._dataclass_to_dict(result), "result": f"Posted to AGORA as #{result.id}."}
            return {"ok": True, "result": str(result)}
        return {"ok": False, "error": "Unsupported AGORA capability", "code": "UNSUPPORTED_CAPABILITY"}

    def _enqueue_agora_memory_sync(self, posts: list[Any]) -> None:
        """Queue LLM-backed memory enrichment outside the retrieval RPC."""
        with self._agora_memory_lock:
            selected = [
                post
                for post in posts
                if int(getattr(post, "id", 0) or 0) not in self._agora_memory_inflight
            ]
            self._agora_memory_inflight.update(int(getattr(post, "id", 0) or 0) for post in selected)
        if not selected:
            return
        threading.Thread(
            target=self._sync_agora_memory,
            args=(selected,),
            daemon=True,
            name="agora-memory-sync",
        ).start()

    def _sync_agora_memory(self, posts: list[Any]) -> None:
        try:
            sync_agora_posts_to_memory(
                posts=posts,
                data_dir=str(self._data_dir),
                llm_provider=self._personal.get("llm_provider"),
            )
        except Exception:
            logger.exception("Queued AGORA memory sync failed")
        finally:
            with self._agora_memory_lock:
                self._agora_memory_inflight.difference_update(
                    int(getattr(post, "id", 0) or 0) for post in posts
                )

    def _resolve_workspace_path(self, raw_path: str, *, must_exist: bool = False) -> Path:
        if not raw_path or not str(raw_path).strip():
            raise ValueError("path is required")
        candidate = Path(str(raw_path)).expanduser()
        if not candidate.is_absolute():
            candidate = self._workspace / candidate
        resolved = candidate.resolve()
        try:
            resolved.relative_to(self._workspace)
        except ValueError as exc:
            raise ValueError("Path must stay inside the AEGIS workspace") from exc
        if must_exist and not resolved.exists():
            raise FileNotFoundError(f"File not found in AEGIS workspace: {raw_path}")
        return resolved

    def _prepare_image(self, image_path: str) -> dict[str, Any]:
        path = self._resolve_workspace_path(image_path, must_exist=True)
        if not path.is_file():
            raise ValueError("image_path must point to a file")
        size = path.stat().st_size
        if size > self.IMAGE_MAX_BYTES:
            raise ValueError("Image is larger than 5MB")
        mime = mimetypes.guess_type(str(path))[0] or ""
        if mime not in self.ALLOWED_IMAGE_MIMES:
            raise ValueError("Unsupported image type. Use png, jpeg, webp, or gif")
        data = path.read_bytes()
        return {
            "image_path": str(path),
            "image_mime": mime,
            "image_base64": base64.b64encode(data).decode("ascii"),
            "image_size_bytes": len(data),
        }

    def _broadcast_overlay(self, params: dict[str, Any]) -> dict[str, Any]:
        message = str(params.get("message") or params.get("body") or params.get("text") or "").strip()
        if not message:
            return {"ok": False, "error": "message is required", "code": "INVALID_ARGUMENT"}
        title = str(params.get("title") or "AEGIS")
        duration_ms = int(params.get("duration_ms") or 8000)
        duration_seconds = max(1, int(round(duration_ms / 1000)))
        color = str(params.get("color") or "")
        raw_targets = params.get("targets") or ["pc", "android"]
        targets = [str(item).strip().lower() for item in raw_targets] if isinstance(raw_targets, list) else [str(raw_targets).strip().lower()]
        image = None
        if params.get("image_path"):
            try:
                image = self._prepare_image(str(params["image_path"]))
            except Exception as exc:
                return {"ok": False, "error": str(exc), "code": "INVALID_IMAGE_PATH"}

        delivered: list[str] = []
        failed: dict[str, Any] = {}
        skipped: list[str] = []
        results: dict[str, Any] = {}

        for target in targets:
            if target in {"pc", "pc-server"}:
                payload = {
                    "title": title,
                    "body": message,
                    "duration_seconds": duration_seconds,
                    "style": color or "info",
                }
                if image:
                    payload.update({k: image[k] for k in ("image_base64", "image_mime")})
                result = self._server_executor.execute_capability("pc-server.overlay.show_rich", payload)
                results["pc"] = result
                if result.get("error") or result.get("shown") is False:
                    failed["pc"] = result.get("error") or result
                else:
                    delivered.append("pc")
                continue

            if target in {"android", "android-server"}:
                payload = {
                    "text": message,
                    "title": title,
                    "duration_ms": duration_ms,
                    "color": color,
                }
                if image:
                    payload.update({k: image[k] for k in ("image_base64", "image_mime")})
                result = self._server_executor.execute_capability("android-server.overlay.show", payload)
                results["android"] = result
                if result.get("error"):
                    failed["android"] = result.get("error")
                elif image and result.get("connection_mode") != "reverse_stream":
                    failed["android"] = "Image overlays require the Android reverse stream connection"
                else:
                    delivered.append("android")
                continue

            skipped.append(target)

        return {
            "ok": bool(delivered) and not failed,
            "delivered": delivered,
            "failed": failed,
            "skipped": skipped,
            "results": results,
            "image": {k: image[k] for k in ("image_path", "image_mime", "image_size_bytes")} if image else None,
        }

    def _write_file(self, params: dict[str, Any]) -> dict[str, Any]:
        try:
            path = self._resolve_workspace_path(str(params.get("relative_path") or ""))
        except Exception as exc:
            return {"ok": False, "error": str(exc), "code": "INVALID_PATH"}
        content = params.get("content")
        content_base64 = params.get("content_base64")
        append = bool(params.get("append", False))
        overwrite = bool(params.get("overwrite", True))
        if content is None and content_base64 is None:
            return {"ok": False, "error": "content or content_base64 is required", "code": "INVALID_ARGUMENT"}
        if path.exists() and not append and not overwrite:
            return {"ok": False, "error": "File already exists and overwrite=false", "code": "FILE_EXISTS"}
        try:
            data = base64.b64decode(str(content_base64), validate=True) if content_base64 is not None else str(content).encode("utf-8")
        except Exception as exc:
            return {"ok": False, "error": f"Invalid content_base64: {exc}", "code": "INVALID_BASE64"}
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = "ab" if append else "wb"
        with path.open(mode) as f:
            f.write(data)
        return {"ok": True, "path": str(path), "relative_path": str(path.relative_to(self._workspace)), "size_bytes": path.stat().st_size}

    def _read_file(self, params: dict[str, Any]) -> dict[str, Any]:
        try:
            path = self._resolve_workspace_path(str(params.get("relative_path") or ""), must_exist=True)
        except Exception as exc:
            return {"ok": False, "error": str(exc), "code": "INVALID_PATH"}
        if not path.is_file():
            return {"ok": False, "error": "Path is not a file", "code": "NOT_A_FILE"}
        max_bytes = int(params.get("max_bytes") or self.READ_MAX_BYTES)
        max_bytes = min(max(1, max_bytes), self.READ_MAX_BYTES)
        data = path.read_bytes()
        if len(data) > max_bytes:
            data = data[:max_bytes]
            truncated = True
        else:
            truncated = False
        try:
            content = data.decode("utf-8")
            return {"ok": True, "relative_path": str(path.relative_to(self._workspace)), "content": content, "truncated": truncated}
        except UnicodeDecodeError:
            return {
                "ok": True,
                "relative_path": str(path.relative_to(self._workspace)),
                "content_base64": base64.b64encode(data).decode("ascii"),
                "encoding": "base64",
                "truncated": truncated,
            }

    def _list_files(self, params: dict[str, Any]) -> dict[str, Any]:
        try:
            root = self._resolve_workspace_path(str(params.get("relative_dir") or "."))
        except Exception as exc:
            return {"ok": False, "error": str(exc), "code": "INVALID_PATH"}
        if not root.exists():
            return {"ok": True, "files": [], "relative_dir": str(root.relative_to(self._workspace))}
        if not root.is_dir():
            return {"ok": False, "error": "Path is not a directory", "code": "NOT_A_DIRECTORY"}
        recursive = bool(params.get("recursive", False))
        max_entries = min(max(int(params.get("max_entries") or 100), 1), 1000)
        iterator = root.rglob("*") if recursive else root.iterdir()
        files = []
        for item in iterator:
            if len(files) >= max_entries:
                break
            stat = item.stat()
            files.append(
                {
                    "relative_path": str(item.relative_to(self._workspace)),
                    "is_dir": item.is_dir(),
                    "size_bytes": stat.st_size if item.is_file() else 0,
                    "modified_ms": int(stat.st_mtime * 1000),
                }
            )
        return {"ok": True, "relative_dir": str(root.relative_to(self._workspace)), "files": files, "truncated": len(files) >= max_entries}

    def _user_model(self, capability_id: str, params: dict[str, Any]) -> dict[str, Any]:
        store = self._personal.get("user_model_store")
        if store is None:
            return {"ok": False, "error": "UserModelStore unavailable"}
        if capability_id.endswith(".get"):
            return {"ok": True, "model": store.get().to_dict(), "context": store.relevant_context(params.get("query", ""))}
        if capability_id.endswith(".update"):
            store.update(dict(params.get("patch") or params), reason=str(params.get("reason") or "capability update"))
            return {"ok": True, "model": store.get().to_dict()}
        return {"ok": False, "error": "Unsupported user model capability"}

    def _hooks(self, capability_id: str, params: dict[str, Any]) -> dict[str, Any]:
        manager = self._personal.get("hook_engine")
        if manager is None:
            return {"ok": False, "error": "HookEngine unavailable"}
        if capability_id.endswith(".list"):
            return {"ok": True, "hooks": manager.list_hooks()}
        if capability_id.endswith(".upsert"):
            return {"ok": True, "hook": manager.upsert_hook(params)}
        if capability_id.endswith(".delete"):
            return {"ok": manager.delete_hook(str(params.get("hook_id") or ""))}
        return {"ok": False, "error": "Unsupported hook capability"}

    def _commitments(self, capability_id: str, params: dict[str, Any]) -> dict[str, Any]:
        manager = self._personal.get("commitment_manager")
        if manager is None:
            return {"ok": False, "error": "CommitmentManager unavailable"}
        if capability_id.endswith(".list"):
            return {"ok": True, "commitments": manager.list_commitments(status=params.get("status"))}
        if capability_id.endswith(".upsert"):
            return {"ok": True, "commitment": manager.upsert_commitment(params)}
        if capability_id.endswith(".transition"):
            item = manager.transition(
                str(params.get("commitment_id") or ""),
                str(params.get("status") or "completed"),
                reason=str(params.get("reason") or ""),
                postpone_until_ms=int(params.get("postpone_until_ms") or 0),
            )
            return {"ok": item is not None, "commitment": item}
        if capability_id.endswith(".wakeup"):
            commitment_id = str(params.get("commitment_id") or "")
            item = manager.get_commitment(commitment_id) if commitment_id else None
            due = manager.due_commitments()
            return {
                "ok": True,
                "commitment": item,
                "due": due,
                "due_count": len(due),
                "wakeup": bool(item or due),
            }
        return {"ok": False, "error": "Unsupported commitment capability"}

    def _delegation_policy(self, capability_id: str, params: dict[str, Any]) -> dict[str, Any]:
        manager = self._personal.get("delegation_policy")
        if manager is None:
            return {"ok": False, "error": "DelegationPolicy unavailable"}
        if capability_id.endswith(".list"):
            return {"ok": True, **manager.get_summary()}
        if capability_id.endswith(".upsert"):
            return {"ok": True, "rule": manager.upsert_rule(params)}
        if capability_id.endswith(".delete"):
            return {"ok": manager.delete_rule(str(params.get("rule_id") or ""))}
        return {"ok": False, "error": "Unsupported delegation capability"}

    def _situation(self, capability_id: str, params: dict[str, Any]) -> dict[str, Any]:
        manager = self._personal.get("situation_model")
        if manager is None:
            return {"ok": False, "error": "SituationModel unavailable"}
        if capability_id.endswith(".get"):
            return {"ok": True, "situation": manager.get_state()}
        if capability_id.endswith(".update"):
            return {"ok": True, "situation": manager.update_from_observation(str(params.get("source") or "manual"), dict(params.get("payload") or {}))}
        return {"ok": False, "error": "Unsupported situation capability"}

    def _interruption(self, capability_id: str, params: dict[str, Any]) -> dict[str, Any]:
        manager = self._personal.get("interruption_controller")
        if manager is None:
            return {"ok": False, "error": "InterruptionController unavailable"}
        if capability_id.endswith(".status"):
            return {"ok": True, **manager.get_status()}
        if capability_id.endswith(".flush"):
            return {"ok": True, "items": manager.flush_batch()}
        if capability_id.endswith(".emergency_stop"):
            return {"ok": True, **manager.set_emergency_stop(bool(params.get("active", True)))}
        return {"ok": False, "error": "Unsupported interruption capability"}

    def _repair(self, capability_id: str, params: dict[str, Any]) -> dict[str, Any]:
        manager = self._personal.get("repair_manager")
        if manager is None:
            return {"ok": False, "error": "RepairManager unavailable"}
        if capability_id.endswith(".list"):
            return {"ok": True, "history": manager.list_history(limit=int(params.get("limit") or 50))}
        if capability_id.endswith(".status"):
            return {"ok": True, **manager.get_status()}
        if capability_id.endswith(".disable"):
            return {"ok": True, **manager.set_disabled(bool(params.get("disabled", True)))}
        return {"ok": False, "error": "Unsupported repair capability"}

    def _presentation(self, capability_id: str, params: dict[str, Any]) -> dict[str, Any]:
        manager = self._personal.get("presentation_manager")
        if manager is None:
            return {"ok": False, "error": "PresentationManager unavailable"}
        if capability_id.endswith(".present"):
            return manager.present(params)
        if capability_id.endswith(".list"):
            limit = min(max(int(params.get("limit") or 100), 1), 500)
            return {"ok": True, "presentations": manager.list_active(limit=limit)}
        if capability_id.endswith(".dismiss"):
            return manager.dismiss(str(params.get("presentation_id") or ""))
        if capability_id.endswith(".action"):
            return manager.user_action(
                str(params.get("presentation_id") or ""),
                dict(params.get("action") or {}),
            )
        return {"ok": False, "error": "Unsupported presentation capability"}
