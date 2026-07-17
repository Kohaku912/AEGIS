"""Folder-Based Capability Registry — discovers capabilities from folder structure.

Capabilities are defined by JSON files in:
- capabilities/builtin/<server_id>/<app_id>/<action>.json
- capabilities/generated/<server_id>/<app_id>/<action>.json

Capability ID is auto-generated from path:
  <server_id>.<app_id>.<action>

Short name for LLM: <app_id>.<action>
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.folder_registry")


@dataclass
class CapabilityManifest:
    capability_id: str = ""
    title: str = ""
    description: str = ""
    server_id: str = ""
    app_id: str = ""
    action: str = ""
    operation_category: str = ""
    origin: str = ""
    version: str = "1.0.0"
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    risk_level: str = "low"
    side_effects: list[str] = field(default_factory=list)
    requires_approval: bool = False
    manifest_risk_level: str = "low"
    manifest_requires_approval: bool = False
    approval_mode: str = ""
    enabled: bool = True
    override: dict[str, Any] | None = None
    tags: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    examples: list[Any] = field(default_factory=list)
    short_name: str = ""
    only_master: bool = True
    tcp_command: str = ""
    tcp_command_json: str = ""
    completion: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)
    file_path: str = ""
    loaded_at: int = 0
    # New policy attributes
    ownership_scope: str = ""  # aegis | user | system | external
    reversibility: str = ""  # fully_reversible | recoverable | difficult | irreversible
    destructive_effects: list[str] = field(default_factory=list)
    data_loss_risk: str = "none"  # none | low | medium | high
    active_work_loss_risk: str = "none"
    blast_radius: str = "single"  # single | bounded | bulk | system_wide

    def to_tool_description(self) -> str:
        parts = [self.title or self.capability_id]
        if self.description:
            parts.append(self.description)
        props = self.input_schema.get("properties", {})
        if props:
            params = ", ".join(f"{k}: {v.get('type', 'any')}" for k, v in props.items())
            parts.append(f"Params: {params}")
        parts.append(f"Risk: {self.risk_level}")
        parts.append(f"Origin: {self.origin}")
        return " | ".join(parts)


@dataclass
class ExecutorManifest:
    action: str = ""
    executor_type: str = "command"
    command: str = ""
    endpoint: str = ""
    working_dir: str = "."
    timeout_ms: int = 30000
    stdin_format: str = "json"
    stdout_format: str = "json"
    env: dict[str, str] = field(default_factory=dict)
    file_path: str = ""


@dataclass
class ExecutionResult:
    ok: bool = False
    capability_id: str = ""
    result: Any = None
    error: dict[str, Any] | None = None
    meta: dict[str, Any] = field(default_factory=dict)


def _derive_ids(file_path: str, base_dir: str) -> dict[str, str] | None:
    rel = os.path.relpath(file_path, base_dir)
    parts = Path(rel).parts
    if len(parts) < 4:
        return None
    return {
        "origin": parts[0],
        "server_id": parts[1],
        "app_id": parts[2],
        "action": Path(parts[3]).stem,
    }


def _validate(data: dict, ids: dict) -> str:
    for key in ("server_id", "app_id", "action"):
        val = data.get(key, "")
        if val and val != ids.get(key):
            return f"JSON {key}='{val}' != path '{ids[key]}'"
    if not str(data.get("operation_category", "")).strip():
        return "Missing required field 'operation_category'"
    return ""


class FolderCapabilityRegistry:
    def __init__(self, capabilities_dir: str = "capabilities") -> None:
        self._dir = Path(capabilities_dir)
        self._manifests: dict[str, CapabilityManifest] = {}
        self._short_names: dict[str, str] = {}
        self._errors: list[dict[str, str]] = []
        self._lock = threading.RLock()
        self._load()

    def _load(self) -> None:
        with self._lock:
            self._manifests.clear()
            self._short_names.clear()
            self._errors.clear()
            for origin in ("builtin", "generated"):
                origin_dir = self._dir / origin
                if not origin_dir.exists():
                    continue
                for json_path in origin_dir.rglob("*.json"):
                    self._load_one(str(json_path), origin)

    def _load_one(self, path: str, origin: str) -> None:
        ids = _derive_ids(path, str(self._dir))
        if not ids:
            self._errors.append({"path": path, "error": "Invalid path"})
            return
        ids["origin"] = origin

        try:
            data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        except Exception as e:
            self._errors.append({"path": path, "error": str(e)})
            return

        err = _validate(data, ids)
        if err:
            self._errors.append({"path": path, "error": err})
            return

        cap_id = f"{ids['server_id']}.{ids['app_id']}.{ids['action']}"
        short = f"{ids['app_id']}.{ids['action']}"

        extra = dict(data.get("extra", {}))
        if "requires_permissions" in data and "requires_permissions" not in extra:
            extra["requires_permissions"] = data.get("requires_permissions", [])

        manifest_risk = data.get("risk", {}).get("level", "low")
        manifest_requires_approval = data.get("risk", {}).get("requires_approval", False)

        self._manifests[cap_id] = CapabilityManifest(
            capability_id=cap_id,
            title=data.get("title", ids["action"].replace("_", " ").title()),
            description=data.get("description", ""),
            server_id=ids["server_id"],
            app_id=ids["app_id"],
            action=ids["action"],
            operation_category=str(data.get("operation_category", "")),
            origin=origin,
            version=data.get("version", "1.0.0"),
            input_schema=data.get("input_schema", data.get("input", {})),
            output_schema=data.get("output_schema", {}),
            risk_level=manifest_risk,
            side_effects=data.get("risk", {}).get("side_effects", []),
            requires_approval=manifest_requires_approval,
            manifest_risk_level=manifest_risk,
            manifest_requires_approval=manifest_requires_approval,
            approval_mode=str(data.get("risk", {}).get("approval_mode", "")),
            enabled=bool(data.get("enabled", True)),
            tags=data.get("tags", []),
            aliases=data.get("aliases", []),
            examples=data.get("examples", []),
            short_name=short,
            only_master=data.get("only_master", True),
            tcp_command=data.get("tcp_command", ""),
            tcp_command_json=data.get("tcp_command_json", ""),
            completion=data.get("completion", {}),
            extra=extra,
            file_path=path,
            loaded_at=int(time.time() * 1000),
            ownership_scope=str(data.get("ownership_scope", "")),
            reversibility=str(data.get("reversibility", "")),
            destructive_effects=data.get("destructive_effects", []),
            data_loss_risk=str(data.get("data_loss_risk", "none")),
            active_work_loss_risk=str(data.get("active_work_loss_risk", "none")),
            blast_radius=str(data.get("blast_radius", "single")),
        )
        if short not in self._short_names:
            self._short_names[short] = cap_id

    def reload(self) -> dict[str, Any]:
        old = len(self._manifests)
        self._load()
        return {"old": old, "new": len(self._manifests), "errors": self._errors}

    def get(self, cap_id: str) -> CapabilityManifest | None:
        with self._lock:
            if cap_id in self._manifests:
                return self._manifests[cap_id]
            full = self._short_names.get(cap_id)
            return self._manifests.get(full) if full else None

    def list_all(self, origin: str | None = None) -> list[CapabilityManifest]:
        with self._lock:
            result = list(self._manifests.values())
        if origin:
            result = [m for m in result if m.origin == origin]
        return result

    def errors(self) -> list[dict[str, str]]:
        with self._lock:
            return list(self._errors)

    def count(self) -> int:
        with self._lock:
            return len(self._manifests)


class ExecutorRegistry:
    def __init__(self, apps_dir: str = "apps") -> None:
        self._dir = Path(apps_dir)
        self._executors: dict[str, ExecutorManifest] = {}
        self._apps_dir = Path(apps_dir)
        self._lock = threading.RLock()
        self._load()

    def _load(self) -> None:
        with self._lock:
            self._executors.clear()
            for origin in ("builtin", "generated"):
                origin_dir = self._dir / origin
                if not origin_dir.exists():
                    continue
                for json_path in origin_dir.rglob("executor.json"):
                    self._load_one(str(json_path), origin)

    def _load_one(self, path: str, origin: str) -> None:
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        except Exception:
            return
        p = Path(path)
        try:
            relative = p.parent.relative_to(self._dir / origin)
        except ValueError:
            return
        parts = relative.parts
        if len(parts) < 3:
            return
        server_id = parts[0]
        app_id = parts[1]
        action = parts[2]
        key = f"{origin}.{server_id}.{app_id}.{action}"
        self._executors[key] = ExecutorManifest(
            action=action,
            executor_type=data.get("type", "command"),
            command=data.get("command", ""),
            endpoint=data.get("endpoint", ""),
            working_dir=data.get("working_dir", "."),
            timeout_ms=data.get("timeout_ms", 30000),
            stdin_format=data.get("stdin", "json"),
            stdout_format=data.get("stdout", "json"),
            env=data.get("env", {}),
            file_path=path,
        )

    def reload(self) -> dict[str, Any]:
        old = len(self._executors)
        self._load()
        return {"old": old, "new": len(self._executors)}

    def get(self, manifest: CapabilityManifest) -> ExecutorManifest | None:
        key = f"{manifest.origin}.{manifest.server_id}.{manifest.app_id}.{manifest.action}"
        with self._lock:
            return self._executors.get(key)

    def execute(self, manifest: CapabilityManifest, arguments: dict[str, Any]) -> ExecutionResult:
        cap_id = manifest.capability_id
        start = time.perf_counter()

        exec_manifest = self.get(manifest)
        if exec_manifest is None:
            return ExecutionResult(
                ok=False, capability_id=cap_id,
                error={"code": "EXECUTOR_NOT_FOUND", "message": f"No executor for {cap_id}"},
                meta=self._meta(manifest, 0),
            )

        if exec_manifest.executor_type != "command":
            return ExecutionResult(
                ok=False, capability_id=cap_id,
                error={"code": "UNSUPPORTED_TYPE", "message": f"Type '{exec_manifest.executor_type}' not supported"},
                meta=self._meta(manifest, 0),
            )

        exec_file = Path(exec_manifest.file_path)
        work_dir = str((exec_file.parent / exec_manifest.working_dir).resolve())
        apps_root = str(self._apps_dir.resolve())
        if not work_dir.startswith(apps_root):
            return ExecutionResult(
                ok=False, capability_id=cap_id,
                error={"code": "WORKING_DIR_VIOLATION", "message": "Cannot escape app folder"},
                meta=self._meta(manifest, 0),
            )

        env = os.environ.copy()
        env.update(exec_manifest.env)
        timeout = exec_manifest.timeout_ms / 1000.0
        command = self._normalize_command(exec_manifest.command, work_dir)

        try:
            stdin_data = json.dumps(arguments) if exec_manifest.stdin_format == "json" else None
            result = subprocess.run(
                command, shell=True, cwd=work_dir,
                input=stdin_data, capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=timeout, env=env,
            )
            dur = (time.perf_counter() - start) * 1000

            if result.returncode != 0:
                return ExecutionResult(
                    ok=False, capability_id=cap_id,
                    error={
                        "code": "EXECUTION_FAILED",
                        "message": f"Exit {result.returncode}",
                        "details": {
                            "exit_code": result.returncode,
                            "stderr": result.stderr,
                            "stdout": result.stdout,
                            "command": command,
                            "working_dir": work_dir,
                            "executor_file": str(exec_manifest.file_path),
                        },
                    },
                    meta=self._meta(manifest, dur),
                )

            output = result.stdout
            if exec_manifest.stdout_format == "json":
                try:
                    output = json.loads(result.stdout)
                except json.JSONDecodeError:
                    output = {"raw_output": result.stdout[:5000]}

            return ExecutionResult(ok=True, capability_id=cap_id, result=output, meta=self._meta(manifest, dur))

        except subprocess.TimeoutExpired:
            dur = (time.perf_counter() - start) * 1000
            return ExecutionResult(
                ok=False, capability_id=cap_id,
                error={
                    "code": "EXECUTION_TIMEOUT",
                    "message": f"Timed out after {timeout}s",
                    "details": {
                        "command": command,
                        "working_dir": work_dir,
                        "executor_file": str(exec_manifest.file_path),
                        "timeout_ms": exec_manifest.timeout_ms,
                    },
                },
                meta=self._meta(manifest, dur),
            )
        except Exception as e:
            dur = (time.perf_counter() - start) * 1000
            return ExecutionResult(
                ok=False, capability_id=cap_id,
                error={
                    "code": "EXECUTION_ERROR",
                    "message": str(e),
                    "details": {
                        "command": command,
                        "working_dir": work_dir,
                        "executor_file": str(exec_manifest.file_path),
                    },
                },
                meta=self._meta(manifest, dur),
            )

    @staticmethod
    def _normalize_command(command: str, work_dir: str) -> str:
        """Make checked-in executor commands portable across host and Docker."""
        if "executor.py" not in command:
            return command
        executor_path = Path(work_dir) / "executor.py"
        if not executor_path.exists():
            return command
        return f'"{sys.executable}" "{executor_path}"'

    def _meta(self, m: CapabilityManifest, dur: float) -> dict:
        return {
            "server_id": m.server_id, "app_id": m.app_id,
            "action": m.action, "origin": m.origin,
            "duration_ms": round(dur, 1), "executor_type": "command",
        }

    def count(self) -> int:
        with self._lock:
            return len(self._executors)
