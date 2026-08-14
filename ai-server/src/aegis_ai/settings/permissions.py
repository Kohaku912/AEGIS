"""Permission integration — connects Settings to PolicyEngine and ToolBroker.

This module provides a SettingsPermissionGuard that wraps PolicyEngine
to check capability permissions from user settings.

Settings can disable capabilities. Purchase and policy-bypass remain DENY in PolicyEngine.
"""

from __future__ import annotations

from typing import Any

from aegis_ai.settings.store import SettingsStore
from aegis_schema.models import Capability
from policy_engine import PolicyDecision, PolicyEngine, PolicyResult


class SettingsPermissionGuard:
    """Wraps PolicyEngine with user settings from SettingsStore.

    Checks:
    1. Is the capability disabled in settings?
    2. Is the capability in the denylist?
    3. Is the capability's server disabled?
    4. Then delegates to PolicyEngine for safety check.

    This is additive — it can only RESTRICT, never EXPAND permissions.
    """

    def __init__(
        self,
        policy_engine: PolicyEngine,
        settings_store: SettingsStore,
    ) -> None:
        self._policy = policy_engine
        self._store = settings_store

    def evaluate(
        self,
        capability: Capability,
        params: dict[str, Any] | None = None,
    ) -> PolicyResult:
        """Evaluate capability with settings check + PolicyEngine safety check."""
        settings = self._store.get()

        # Check if capability is disabled
        if capability.id in settings.capabilities.disabled_capabilities:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason=f"Capability '{capability.id}' is disabled in settings",
                capability_id=capability.id,
                risk_level=capability.risk_level,
            )

        # Check denylist
        if capability.id in settings.capabilities.denylist:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason=f"Capability '{capability.id}' is in denylist",
                capability_id=capability.id,
                risk_level=capability.risk_level,
            )

        # Check server enabled
        server_prefix = capability.id.split(".")[0]
        server_enabled_map = {
            "browser": settings.servers.browser_server_enabled,
            "browser-server": settings.servers.browser_server_enabled,
            "pc": settings.servers.pc_server_enabled,
            "pc-server": settings.servers.pc_server_enabled,
            "android": settings.servers.android_server_enabled,
            "android-server": settings.servers.android_server_enabled,
            "room": settings.servers.room_server_enabled,
            "room-server": settings.servers.room_server_enabled,
            "dev": settings.servers.dev_server_enabled,
            "dev-server": settings.servers.dev_server_enabled,
            "ai": True,
            "ai-server": True,
        }
        if not server_enabled_map.get(server_prefix, True):
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason=f"Server for '{capability.id}' is disabled in settings",
                capability_id=capability.id,
                risk_level=capability.risk_level,
            )

        # Check per-capability max safety level
        if cap_perm := settings.capabilities.per_capability.get(capability.id):
            if not cap_perm.enabled:
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason=f"Capability '{capability.id}' is disabled in settings",
                    capability_id=capability.id,
                    risk_level=capability.risk_level,
                )
            if capability.risk_level.value > cap_perm.max_safety_level:
                return PolicyResult(
                    decision=PolicyDecision.DENY,
                    reason=f"Capability '{capability.id}' exceeds max safety level in settings",
                    capability_id=capability.id,
                    risk_level=capability.risk_level,
                )

        parts = str(capability.id or "").split(".")
        app_id = parts[1].lower() if len(parts) >= 3 else ""
        tags = {str(item).lower() for item in (getattr(capability, "tags", None) or [])}
        if (app_id == "clipboard" or "clipboard" in tags) and not settings.privacy.clipboard_capture_enabled:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason="Clipboard capture is disabled in privacy settings",
                capability_id=capability.id,
                risk_level=capability.risk_level,
            )
        if (app_id == "camera" or "camera" in tags) and not settings.privacy.camera_snapshot_enabled:
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason="Camera snapshot is disabled in privacy settings",
                capability_id=capability.id,
                risk_level=capability.risk_level,
            )

        # Delegate to PolicyEngine for safety check
        return self._policy.evaluate(capability, params)

    def is_capability_enabled(self, capability_id: str) -> bool:
        """Check if a capability is enabled in settings."""
        settings = self._store.get()

        if capability_id in settings.capabilities.disabled_capabilities:
            return False
        if capability_id in settings.capabilities.denylist:
            return False

        if cap_perm := settings.capabilities.per_capability.get(capability_id):
            return cap_perm.enabled

        return True
