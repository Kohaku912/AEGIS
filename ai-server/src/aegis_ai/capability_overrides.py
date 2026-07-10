"""Persistent user overrides for capability risk policy."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.capability_overrides")

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


def _normalize_risk_label(label: str, default: str = "READ_ONLY") -> str:
    key = str(label or "").strip().lower()
    return _RISK_LABEL_TO_NAME.get(key, default)


@dataclass
class CapabilityOverride:
    capability_id: str
    risk_level: str = ""
    requires_approval: bool | None = None
    approval_mode: str = ""
    enabled: bool | None = None
    updated_at: int = 0
    updated_by: str = "system"
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CapabilityOverrideStore:
    """JSON-backed capability override store.

    The manifest remains immutable source material. This store contains user
    policy choices that are overlaid by CapabilityCatalog at runtime.
    """

    def __init__(self, path: str | Path = "data/settings/capability_overrides.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._overrides: dict[str, CapabilityOverride] = {}
        self.corrupted = False
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            items = data.get("overrides", data) if isinstance(data, dict) else {}
            if not isinstance(items, dict):
                raise ValueError("override store root must be an object")
            loaded: dict[str, CapabilityOverride] = {}
            for cap_id, raw in items.items():
                if not isinstance(raw, dict):
                    continue
                override = CapabilityOverride(
                    capability_id=str(raw.get("capability_id") or cap_id),
                    risk_level=_normalize_risk_label(str(raw.get("risk_level") or ""), default="")
                    if raw.get("risk_level")
                    else "",
                    requires_approval=(
                        bool(raw["requires_approval"])
                        if raw.get("requires_approval") is not None
                        else None
                    ),
                    approval_mode=str(raw.get("approval_mode") or ""),
                    enabled=bool(raw["enabled"]) if raw.get("enabled") is not None else None,
                    updated_at=int(raw.get("updated_at") or 0),
                    updated_by=str(raw.get("updated_by") or "system"),
                    reason=str(raw.get("reason") or ""),
                )
                loaded[override.capability_id] = override
            self._overrides = loaded
            self.corrupted = False
        except Exception:
            self.corrupted = True
            self._overrides = {}
            logger.warning("Capability override store is corrupt: %s", self.path, exc_info=True)

    def reload(self) -> None:
        self._overrides = {}
        self.corrupted = False
        self._load()

    def _save(self) -> None:
        payload = {
            "version": 1,
            "updated_at": int(time.time() * 1000),
            "overrides": {cap_id: ov.to_dict() for cap_id, ov in sorted(self._overrides.items())},
        }
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def list(self) -> dict[str, dict[str, Any]]:
        return {cap_id: ov.to_dict() for cap_id, ov in sorted(self._overrides.items())}

    def get(self, capability_id: str) -> CapabilityOverride | None:
        return self._overrides.get(capability_id)

    def upsert(
        self,
        capability_id: str,
        *,
        risk_level: str | None = None,
        requires_approval: bool | None = None,
        approval_mode: str | None = None,
        enabled: bool | None = None,
        updated_by: str = "dashboard",
        reason: str = "",
    ) -> CapabilityOverride:
        existing = self._overrides.get(capability_id)
        override = CapabilityOverride(
            capability_id=capability_id,
            risk_level=existing.risk_level if existing else "",
            requires_approval=existing.requires_approval if existing else None,
            approval_mode=existing.approval_mode if existing else "",
            enabled=existing.enabled if existing else None,
            updated_at=int(time.time() * 1000),
            updated_by=updated_by,
            reason=reason,
        )
        if risk_level is not None:
            normalized = _normalize_risk_label(risk_level, default="")
            if not normalized:
                raise ValueError(f"Invalid risk level: {risk_level}")
            override.risk_level = normalized
        if requires_approval is not None:
            override.requires_approval = bool(requires_approval)
        if approval_mode is not None:
            override.approval_mode = str(approval_mode)
        if enabled is not None:
            override.enabled = bool(enabled)

        self._overrides[capability_id] = override
        self.corrupted = False
        self._save()
        return override

    def reset(self, capability_id: str) -> bool:
        existed = capability_id in self._overrides
        if existed:
            self._overrides.pop(capability_id, None)
            self._save()
        return existed
