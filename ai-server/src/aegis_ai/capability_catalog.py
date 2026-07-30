"""Capability Catalog — unified interface over folder-based capability registry.

Single source of truth for capability resolution, alias management,
and LLM-friendly capability listing.

Canonical ID format: server_id.app_id.action
  e.g., pc-server.screenshot.get_screenshot

Backward-compatible aliases:
  - Short: screenshot.get_screenshot → pc-server.screenshot.get_screenshot
  - Old prefix: pc.screenshot.get_screenshot → pc-server.screenshot.get_screenshot (via _PREFIX_MAP)
"""

from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any

from aegis_ai.capability_overrides import CapabilityOverrideStore
from aegis_ai.folder_registry import (
    CapabilityManifest,
    ExecutionResult,
    ExecutorRegistry,
    FolderCapabilityRegistry,
)

logger = logging.getLogger("aegis_ai.capability_catalog")

_RISK_LABEL_TO_NAME = {
    "low": "READ_ONLY",
    "read": "READ_ONLY",
    "read_only": "READ_ONLY",
    "safe": "SAFE_ACTION",
    "safe_action": "SAFE_ACTION",
    "medium": "APPROVAL_REQUIRED",
    "approval": "APPROVAL_REQUIRED",
    "approval_required": "APPROVAL_REQUIRED",
    "high": "HIGH_RISK",
    "high_risk": "HIGH_RISK",
    "critical": "FORBIDDEN",
    "forbidden": "FORBIDDEN",
}

_RISK_NAME_TO_JSON_LABEL = {
    "READ_ONLY": "low",
    "SAFE_ACTION": "safe",
    "APPROVAL_REQUIRED": "approval_required",
    "HIGH_RISK": "high_risk",
    "FORBIDDEN": "critical",
}

_PREFIX_MAP = {
    "ai-server": "ai",
    "pc-server": "pc",
    "browser-server": "browser",
    "android-server": "android",
    "room-server": "room",
    "dev-server": "dev",
}

_RISK_ORDER = {
    "READ_ONLY": 1,
    "SAFE_ACTION": 2,
    "APPROVAL_REQUIRED": 3,
    "HIGH_RISK": 4,
    "FORBIDDEN": 5,
}


def normalize_risk_label(label: str, default: str = "READ_ONLY") -> str:
    """Normalize manifest/dashboard risk labels to RiskLevel enum names."""
    key = str(label or "").strip().lower()
    return _RISK_LABEL_TO_NAME.get(key, default)


def risk_json_label(risk_name: str) -> str:
    """Convert a RiskLevel enum name to the manifest JSON label."""
    normalized = normalize_risk_label(risk_name, default=str(risk_name or "").strip().upper())
    return _RISK_NAME_TO_JSON_LABEL.get(normalized, "low")


def risk_level_from_label(label: str):
    """Convert a manifest/dashboard risk label to aegis_schema.models.RiskLevel."""
    from aegis_schema.models import RiskLevel

    return RiskLevel[normalize_risk_label(label)]


class CapabilityCatalog:
    """Unified capability catalog — single source of truth."""

    def __init__(
        self,
        capabilities_dir: str,
        apps_dir: str = "",
        override_store: CapabilityOverrideStore | None = None,
        data_dir: str | None = None,
    ) -> None:
        self._cap_reg = FolderCapabilityRegistry(capabilities_dir)
        self._exec_reg = ExecutorRegistry(apps_dir) if apps_dir else None
        override_path = Path(data_dir or "data") / "settings" / "capability_overrides.json"
        self._override_store = override_store or CapabilityOverrideStore(override_path)
        self._aliases: dict[str, str] = {}
        self._lock = threading.RLock()
        self._apply_overrides()
        self._load_aliases()

    def _apply_overrides(self) -> None:
        """Apply persisted user overrides to manifests after disk load."""
        with self._lock:
            for manifest in self._cap_reg.list_all():
                manifest.risk_level = manifest.manifest_risk_level
                manifest.requires_approval = manifest.manifest_requires_approval
                manifest.override = None

                override = self._override_store.get(manifest.capability_id)
                if override is not None:
                    if override.risk_level:
                        manifest.risk_level = override.risk_level
                    if override.requires_approval is not None:
                        manifest.requires_approval = bool(override.requires_approval)
                    if override.approval_mode:
                        manifest.approval_mode = override.approval_mode
                    if override.enabled is not None:
                        manifest.enabled = bool(override.enabled)
                    manifest.override = override.to_dict()

                if self._override_store.corrupted:
                    manifest.risk_level = self._stricter_risk(manifest.risk_level, "APPROVAL_REQUIRED")
                    manifest.requires_approval = True
                    manifest.override = {
                        "corrupted_store": True,
                        "safe_fallback": "approval_required",
                        "updated_at": int(time.time() * 1000),
                    }

    @staticmethod
    def _stricter_risk(left: str, right: str) -> str:
        left_name = normalize_risk_label(left)
        right_name = normalize_risk_label(right)
        return left_name if _RISK_ORDER.get(left_name, 0) >= _RISK_ORDER.get(right_name, 0) else right_name

    def _load_aliases(self) -> None:
        """Build old-ID → canonical-ID mappings for backward compatibility."""
        with self._lock:
            for manifest in self._cap_reg.list_all():
                short = f"{manifest.app_id}.{manifest.action}"
                self._aliases[short] = manifest.capability_id

                short_prefix = _PREFIX_MAP.get(manifest.server_id)
                if short_prefix:
                    old_id = f"{short_prefix}.{manifest.app_id}.{manifest.action}"
                    self._aliases[old_id] = manifest.capability_id

    def reload(self) -> dict[str, Any]:
        """Reload capabilities from disk and rebuild aliases."""
        with self._lock:
            self._override_store.reload()
            result = self._cap_reg.reload()
            self._apply_overrides()
            self._aliases.clear()
            self._load_aliases()
            if self._exec_reg:
                self._exec_reg.reload()
            return result

    def resolve(self, cap_id: str) -> CapabilityManifest | None:
        """Resolve any ID format (canonical, short, or old-prefix) to manifest."""
        with self._lock:
            direct = self._cap_reg.get(cap_id)
            if direct:
                return direct
            aliased = self._aliases.get(cap_id)
            if aliased:
                return self._cap_reg.get(aliased)
            return None

    def list_all(self, origin: str | None = None) -> list[CapabilityManifest]:
        """List all capabilities."""
        with self._lock:
            return self._cap_reg.list_all(origin=origin)

    def list_for_llm(self) -> list[dict[str, Any]]:
        """Get capability list formatted for LLM consumption."""
        with self._lock:
            manifests = [m for m in self._cap_reg.list_all() if m.enabled]
        return [
            {
                "id": m.capability_id,
                "short_name": m.short_name,
                "title": m.title,
                "description": m.description,
                "operation_category": m.operation_category,
                "tags": list(m.tags),
                "aliases": list(m.aliases),
                "examples": list(m.examples),
                "params": list(m.input_schema.get("properties", {}).keys()),
                "required_params": m.input_schema.get("required", []),
                "input_schema": m.input_schema,
                "risk": m.risk_level,
                "only_master": m.only_master,
            }
            for m in manifests
        ]

    def list_for_tools(self, cap_ids: set[str] | None = None) -> list[dict[str, Any]]:
        """Convert capabilities to OpenAI tool format for tool calling.

        Args:
            cap_ids: If provided, only include these capability IDs.

        Returns:
            List of OpenAI tool definitions.
        """
        tools = []
        with self._lock:
            manifests = [m for m in self._cap_reg.list_all() if m.enabled]
        for m in manifests:
            if cap_ids and m.capability_id not in cap_ids:
                continue
            props = m.input_schema.get("properties", {})
            required = m.input_schema.get("required", [])
            parameters = {"type": "object", "properties": {}, "required": required}
            for pname, pschema in props.items():
                parameters["properties"][pname] = pschema
            tool_name = m.capability_id.replace(".", "__")
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": f"{m.title}: {m.description[:80]}",
                    "parameters": parameters,
                },
            })
        return tools

    def list_lightweight(self, cap_ids: list[str] | set[str] | None = None) -> list[dict[str, Any]]:
        """Return schema-free summaries for LLM lightweight catalogs."""
        ids = set(cap_ids) if cap_ids is not None else None
        with self._lock:
            manifests = [m for m in self._cap_reg.list_all() if m.enabled]
        summaries = []
        for m in manifests:
            if ids is not None and m.capability_id not in ids:
                continue
            summaries.append({
                "id": m.capability_id,
                "title": m.title,
                "operation_category": m.operation_category,
                "tags": list(m.tags),
                "risk": m.risk_level,
                "short_desc": m.description[:220],
            })
        return summaries

    def describe(self, cap_id: str) -> dict[str, Any] | None:
        """Return detailed manifest data for capability metadata lookup."""
        manifest = self.resolve(cap_id)
        if manifest is None:
            return None
        return {
            "id": manifest.capability_id,
            "short_name": manifest.short_name,
            "title": manifest.title,
            "description": manifest.description,
            "operation_category": manifest.operation_category,
            "tags": list(manifest.tags),
            "aliases": list(manifest.aliases),
            "examples": list(manifest.examples),
            "risk": manifest.risk_level,
            "enabled": manifest.enabled,
            "requires_approval": manifest.requires_approval,
            "manifest": {
                "risk_level": manifest.manifest_risk_level,
                "requires_approval": bool(manifest.manifest_requires_approval),
            },
            "override": dict(manifest.override or {}),
            "input_schema": manifest.input_schema or {"type": "object", "properties": {}},
            "notes": manifest.extra.get("notes", ""),
        }

    def tool_name_to_cap_id(self, tool_name: str) -> str:
        """Convert tool function name back to capability ID (double underscore to dot)."""
        return tool_name.replace("__", ".")

    def to_tool_registry_capabilities(self) -> list:
        """Convert all manifests to Capability objects for ToolRegistry registration."""
        from aegis_schema.models import Capability, RiskLevel, ServerType
        server_type_map = {
            "pc-server": ServerType.PC,
            "browser-server": ServerType.BROWSER,
            "android-server": ServerType.ANDROID,
            "room-server": ServerType.ROOM,
            "dev-server": ServerType.DEV,
            "ai-server": ServerType.AI,
        }
        caps = []
        with self._lock:
            manifests = self._cap_reg.list_all()
        for m in manifests:
            if not getattr(m, "enabled", True):
                continue
            risk_level = risk_level_from_label(m.risk_level)
            if risk_level == RiskLevel.FORBIDDEN:
                continue
            try:
                caps.append(Capability(
                    id=m.capability_id,
                    name=m.title,
                    description=(m.description[:80] if m.description else m.title or m.capability_id),
                    server_type=server_type_map.get(m.server_id, ServerType.AI),
                    risk_level=risk_level,
                    requires_approval=m.requires_approval,
                    side_effects=m.side_effects,
                    tags=m.tags,
                ))
            except ValueError:
                logger.debug("Skipping non-registerable capability: %s", m.capability_id, exc_info=True)
        return caps

    def execute(self, cap_id: str, arguments: dict[str, Any]) -> ExecutionResult:
        """Execute a capability by any ID format."""
        manifest = self.resolve(cap_id)
        if not manifest:
            return ExecutionResult(
                ok=False,
                error={"code": "NOT_FOUND", "message": f"Capability '{cap_id}' not found"},
            )
        if not self._exec_reg:
            return ExecutionResult(
                ok=False,
                error={"code": "NO_EXECUTOR", "message": "No executor registry configured"},
            )
        return self._exec_reg.execute(manifest, arguments)

    def get_executor_registry(self) -> ExecutorRegistry | None:
        """Return the underlying executor registry."""
        return self._exec_reg

    def get_folder_registry(self) -> FolderCapabilityRegistry:
        """Return the underlying folder capability registry."""
        return self._cap_reg

    def get_override_store(self) -> CapabilityOverrideStore:
        """Return the persistent override store."""
        return self._override_store

    def update_manifest_policy(
        self,
        cap_id: str,
        *,
        risk_level: str | None = None,
        requires_approval: bool | None = None,
        approval_mode: str | None = None,
        enabled: bool | None = None,
    ) -> dict[str, Any]:
        """Write risk/enabled policy into the capability JSON manifest on disk.

        This permanently updates the source-of-truth JSON file and clears any
        soft override for the same capability so effective policy matches the
        manifest after reload.
        """
        with self._lock:
            manifest = self.resolve(cap_id)
            if manifest is None:
                raise KeyError(f"Capability '{cap_id}' not found")
            path = Path(manifest.file_path)
            if not path.is_file():
                raise FileNotFoundError(f"Capability manifest file missing: {path}")

            data = json.loads(path.read_text(encoding="utf-8-sig"))
            if not isinstance(data, dict):
                raise ValueError(f"Capability manifest root must be an object: {path}")

            risk = data.get("risk")
            if not isinstance(risk, dict):
                risk = {}
            else:
                risk = dict(risk)

            if risk_level is not None:
                normalized = normalize_risk_label(str(risk_level), default="")
                if not normalized:
                    raise ValueError(f"Invalid risk level: {risk_level}")
                risk["level"] = risk_json_label(normalized)
            if requires_approval is not None:
                risk["requires_approval"] = bool(requires_approval)
            if approval_mode is not None:
                mode = str(approval_mode).strip()
                if mode:
                    risk["approval_mode"] = mode
                else:
                    risk.pop("approval_mode", None)
            data["risk"] = risk

            if enabled is not None:
                data["enabled"] = bool(enabled)

            payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_text(payload, encoding="utf-8")
            tmp.replace(path)

            # Source JSON is authoritative after a dashboard edit.
            self._override_store.reset(manifest.capability_id)
            return data

    def risk_details(self, cap_id: str) -> dict[str, Any] | None:
        """Return manifest, override, and effective risk policy for a capability."""
        manifest = self.resolve(cap_id)
        if manifest is None:
            return None
        return {
            "capability_id": manifest.capability_id,
            "manifest": {
                "risk_level": risk_json_label(manifest.manifest_risk_level),
                "requires_approval": bool(manifest.manifest_requires_approval),
                "approval_mode": str(getattr(manifest, "approval_mode", "") or ""),
                "enabled": bool(getattr(manifest, "enabled", True)),
            },
            "override": dict(manifest.override or {}),
            "effective": {
                "risk_level": risk_json_label(manifest.risk_level),
                "requires_approval": bool(manifest.requires_approval),
                "approval_mode": manifest.approval_mode,
                "enabled": bool(manifest.enabled),
            },
            "override_active": bool(manifest.override),
            "override_store_corrupted": bool(self._override_store.corrupted),
            "file_path": manifest.file_path,
        }

    def count(self) -> int:
        with self._lock:
            return self._cap_reg.count()

    def errors(self) -> list[dict[str, str]]:
        with self._lock:
            return self._cap_reg.errors()
