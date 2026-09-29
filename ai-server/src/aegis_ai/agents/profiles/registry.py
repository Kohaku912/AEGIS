"""Agent profile registry — loads `AgentProfile` from YAML.

Configuration is read from `config/agent_profiles.yaml` by default. The
location can be overridden via:

1. Constructor argument ``path=...``
2. Environment variable ``AEGIS_AGENT_PROFILES_PATH``

When the YAML is missing, the registry starts empty and all
`AgentProfileRegistry.get(...)` calls return None — so callers should
always handle a missing profile by falling back to a default.

DoD 接続 (instruction.md §36 Phase 5):
- 6 標準 profile をロードできる
- 存在しない profile への参照を許容 (None を返す) → 呼び出し側で
  fallback 戦略 (一般に "general" + audit warning) を取る.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

from aegis_ai.agents.profiles.models import (
    AgentProfile,
    AgentRiskCeiling,
    WorkspaceKind,
)

logger = logging.getLogger("aegis_ai.agents.profiles.registry")

DEFAULT_PROFILES_PATH = "config/agent_profiles.yaml"
ENV_PROFILES_PATH = "AEGIS_AGENT_PROFILES_PATH"


@dataclass
class AgentProfileRegistry:
    """In-memory registry of `AgentProfile` objects keyed by ``id``.

    The registry is intentionally *read-only* after construction in
    production paths. Tests may use ``register(...)`` / ``clear()`` to
    inject custom profiles.
    """

    profiles: dict[str, AgentProfile] = field(default_factory=dict)
    source_path: str = ""
    load_warnings: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Construction / loading
    # ------------------------------------------------------------------

    @classmethod
    def from_yaml(
        cls,
        path: str | os.PathLike[str] | None = None,
        *,
        env_var: str = ENV_PROFILES_PATH,
    ) -> AgentProfileRegistry:
        """Load profiles from YAML.

        Resolution order:
        1. ``path`` argument (explicit)
        2. ``env_var`` environment variable
        3. ``DEFAULT_PROFILES_PATH`` (relative to CWD)
        4. If the file does not exist, return an empty registry.
        """
        resolved = cls._resolve_path(path, env_var)
        registry = cls(source_path=str(resolved) if resolved else "")
        if not resolved or not Path(resolved).is_file():
            if resolved:
                logger.info(
                    "Agent profile YAML not found at %s; starting with empty registry",
                    resolved,
                )
            return registry
        registry._load_from_file(Path(resolved))
        return registry

    @staticmethod
    def _resolve_path(
        path: str | os.PathLike[str] | None,
        env_var: str,
    ) -> str | None:
        if path is not None:
            return str(path)
        env_value = os.environ.get(env_var)
        if env_value:
            return env_value
        return DEFAULT_PROFILES_PATH

    def _load_from_file(self, path: Path) -> None:
        try:
            with path.open("r", encoding="utf-8") as fh:
                raw = yaml.safe_load(fh) or {}
        except (OSError, yaml.YAMLError) as exc:
            msg = f"failed to read agent profiles YAML at {path}: {exc}"
            logger.warning(msg)
            self.load_warnings.append(msg)
            return

        profiles_raw = raw.get("profiles")
        if not isinstance(profiles_raw, dict):
            msg = f"agent profiles YAML at {path} has no top-level 'profiles' map"
            logger.warning(msg)
            self.load_warnings.append(msg)
            return

        for profile_id, payload in profiles_raw.items():
            if not isinstance(payload, dict):
                self.load_warnings.append(
                    f"profile {profile_id!r} is not a mapping; skipped"
                )
                continue
            try:
                profile = self._build_profile(str(profile_id), payload)
            except (KeyError, ValueError, TypeError) as exc:
                self.load_warnings.append(
                    f"profile {profile_id!r} failed to load: {exc}"
                )
                continue
            self.profiles[profile.id] = profile

    @staticmethod
    def _build_profile(profile_id: str, payload: dict[str, Any]) -> AgentProfile:
        """Build an `AgentProfile` from a YAML mapping.

        Required keys: ``backend``, ``llm_profile_name``. All others are
        optional with sensible defaults.
        """
        backend = str(payload.get("backend", "")).strip()
        if not backend:
            raise ValueError("missing required 'backend'")
        llm_profile = str(payload.get("llm_profile_name", "")).strip()
        if not llm_profile:
            raise ValueError("missing required 'llm_profile_name'")
        tools = _coerce_str_list(payload.get("tools", []))
        risk_ceiling = AgentRiskCeiling.parse(
            payload.get("risk_ceiling", AgentRiskCeiling.APPROVAL_REQUIRED.value)
        )
        workspace_kind = WorkspaceKind.parse(
            payload.get("workspace_kind", WorkspaceKind.ISOLATED.value)
        )
        allowed = _coerce_str_list(payload.get("allowed_capabilities", []))
        denied = _coerce_str_list(payload.get("denied_capabilities", []))
        requires_approval = _coerce_str_list(
            payload.get("requires_approval_for", [])
        )
        cost_budget = payload.get("cost_budget_usd")
        if cost_budget is not None:
            cost_budget = float(cost_budget)
        metadata_raw = payload.get("metadata", {})
        if not isinstance(metadata_raw, dict):
            metadata_raw = {}
        return AgentProfile(
            id=profile_id,
            backend=backend,
            llm_profile_name=llm_profile,
            tools=tools,
            max_runtime_sec=int(payload.get("max_runtime_sec", 1800)),
            max_iterations=int(payload.get("max_iterations", 100)),
            risk_ceiling=risk_ceiling,
            workspace_kind=workspace_kind,
            allowed_capabilities=allowed,
            denied_capabilities=denied,
            requires_approval_for=requires_approval,
            cost_budget_usd=cost_budget,
            description=str(payload.get("description", "")),
            metadata=dict(metadata_raw),
        )

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get(self, profile_id: str) -> AgentProfile | None:
        """Return the profile for ``profile_id`` or None if absent."""
        if not profile_id:
            return None
        return self.profiles.get(profile_id)

    def has(self, profile_id: str) -> bool:
        return profile_id in self.profiles

    def list_ids(self) -> list[str]:
        return sorted(self.profiles.keys())

    def all(self) -> list[AgentProfile]:
        return [self.profiles[k] for k in self.list_ids()]

    def __len__(self) -> int:
        return len(self.profiles)

    def __contains__(self, profile_id: object) -> bool:
        return isinstance(profile_id, str) and profile_id in self.profiles

    # ------------------------------------------------------------------
    # Mutation (tests only)
    # ------------------------------------------------------------------

    def register(self, profile: AgentProfile) -> None:
        """Insert or overwrite a profile. Intended for tests / dynamic
        configuration; production code should rely on `from_yaml()`.
        """
        self.profiles[profile.id] = profile

    def clear(self) -> None:
        self.profiles.clear()
        self.load_warnings.clear()


def _coerce_str_list(value: Any) -> list[str]:
    """Coerce YAML/JSON scalars to a list of strings."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Iterable):
        out: list[str] = []
        for item in value:
            if item is None:
                continue
            out.append(str(item))
        return out
    return []


__all__ = [
    "AgentProfileRegistry",
    "DEFAULT_PROFILES_PATH",
    "ENV_PROFILES_PATH",
]
