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

import logging
import threading
from typing import Any

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
    "APPROVAL_REQUIRED": "medium",
    "HIGH_RISK": "high",
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

    def __init__(self, capabilities_dir: str, apps_dir: str = "") -> None:
        self._cap_reg = FolderCapabilityRegistry(capabilities_dir)
        self._exec_reg = ExecutorRegistry(apps_dir) if apps_dir else None
        self._aliases: dict[str, str] = {}
        self._lock = threading.RLock()
        self._load_aliases()

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
            result = self._cap_reg.reload()
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
            manifests = self._cap_reg.list_all()
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
            manifests = self._cap_reg.list_all()
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
                    "description": f"{m.title}: {m.description}",
                    "parameters": parameters,
                },
            })
        return tools

    def list_lightweight(self, cap_ids: list[str] | set[str] | None = None) -> list[dict[str, Any]]:
        """Return schema-free summaries for LLM lightweight catalogs."""
        ids = set(cap_ids) if cap_ids is not None else None
        with self._lock:
            manifests = self._cap_reg.list_all()
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
            risk_level = risk_level_from_label(m.risk_level)
            if risk_level == RiskLevel.FORBIDDEN:
                continue
            try:
                caps.append(Capability(
                    id=m.capability_id,
                    name=m.title,
                    description=m.description or m.title or m.capability_id,
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

    def count(self) -> int:
        with self._lock:
            return self._cap_reg.count()

    def errors(self) -> list[dict[str, str]]:
        with self._lock:
            return self._cap_reg.errors()
