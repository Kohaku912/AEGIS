"""In-process AI Server capabilities."""

from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path
from typing import Any


class AegisCoreCapabilityClient:
    """Executes AI-local capabilities without leaving the AI server process."""

    IMAGE_MAX_BYTES = 5 * 1024 * 1024
    READ_MAX_BYTES = 10 * 1024 * 1024
    ALLOWED_IMAGE_MIMES = {"image/png", "image/jpeg", "image/webp", "image/gif"}

    def __init__(self, *, data_dir: str, server_executor: Any) -> None:
        self._data_dir = Path(data_dir).resolve()
        configured = os.getenv("AEGIS_WORKSPACE_DIR", "").strip()
        self._workspace = Path(configured).expanduser().resolve() if configured else self._data_dir / "aegis_workspace"
        self._workspace.mkdir(parents=True, exist_ok=True)
        self._server_executor = server_executor

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
        return {"ok": False, "error": f"Unsupported AI capability: {capability_id}", "code": "UNSUPPORTED_CAPABILITY"}

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
