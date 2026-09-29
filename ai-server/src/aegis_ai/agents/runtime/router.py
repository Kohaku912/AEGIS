"""AgentRouter — Phase 5 (instruction.md §22, §36).

`AgentRouter.select()` resolves an `AgentTask.profile` to an `AgentProfile`
+ backend name. Free-text goal heuristics are intentionally avoided so
upstream LLM interpretation remains the source of truth for user intent.
When the requested profile is missing, it falls back to ``"general"`` and
emits an audit warning.

Design notes:
- profile routing uses explicit profile ids, upstream `required_coding`,
  and capability hints only.
- `select()` is synchronous and does not perform an LLM call.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Iterable

from aegis_ai.agents.profiles.models import (
    AgentProfile,
    RoutingDecision,
)
from aegis_ai.agents.profiles.registry import AgentProfileRegistry

logger = logging.getLogger("aegis_ai.agents.runtime.router")


@dataclass
class AgentRouter:
    """Selects an `AgentProfile` for a given task.

    Selection precedence:
    1. Explicit ``requested_id`` (from `AgentTask.profile`)
    2. Capability or upstream classification hints
    3. Default profile (`fallback_id`)

    All paths funnel through `_resolve()` which guarantees a
    `RoutingDecision` is returned (never raises for "unknown profile").

    Attributes:
        registry: `AgentProfileRegistry` with loaded profiles.
        fallback_id: Profile id to use when the requested id is missing
            or heuristic yields nothing useful. Default: ``"general"``.
        audit_sink: Optional callable ``(str) -> None`` that receives
            human-readable warning lines whenever a fallback happens.
            Production code passes `runtime.audit_log` (or a wrapper).
        backend_resolver: Optional callable ``(name: str) -> str | None``
            returning the registered backend for a profile. Used to mark
            the decision's ``backend`` field. Defaults to using
            ``profile.backend`` directly.
    """

    registry: AgentProfileRegistry = field(default_factory=AgentProfileRegistry)
    fallback_id: str = "general"
    audit_sink: Any = None
    backend_resolver: Any = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def select(
        self,
        requested_id: str = "",
        *,
        user_goal: str = "",
        capabilities: Iterable[str] | None = None,
        required_coding: bool | None = None,
    ) -> RoutingDecision:
        """Resolve the appropriate `AgentProfile`.

        Args:
            requested_id: Explicit profile id (from `AgentTask.profile`).
                Empty string triggers heuristic selection.
            user_goal: Free-text goal retained for audit/debug context only.
            capabilities: Optional capability id list (hint for routing).
            required_coding: If non-None, force the ``coding`` profile
                when True. Used when the upstream interpreter has
                already classified the goal.

        Returns:
            `RoutingDecision` with the selected `AgentProfile`. Never None.
        """
        requested = (requested_id or "").strip()
        cap_list = list(capabilities) if capabilities else []

        # 1. Explicit + non-empty
        if requested:
            return self._resolve(requested, requested, reason="explicit_request")

        # 2. required_coding flag (from upstream interpreter)
        if required_coding is True:
            return self._resolve("coding", "<heuristic:coding>", reason="required_coding_flag")

        # 3. Capability-driven routing: if any capability in
        #    `cap_list` has the "git", "github", "filesystem.write"
        #    namespace, treat it as coding.
        if any(self._capability_is_coding(cid) for cid in cap_list):
            return self._resolve("coding", "<heuristic:capability>", reason="coding_capability_present")

        # 4. Default fallback
        return self._resolve(
            self.fallback_id,
            "<default>",
            reason="default_fallback",
        )

    @staticmethod
    def _capability_is_coding(capability_id: str) -> bool:
        """Heuristic: capability が coding 系統かどうか."""
        cid = capability_id.lower()
        return any(
            token in cid
            for token in ("git", "github", "filesystem.write", "code.", "dev.")
        )

    def _resolve(
        self,
        target_id: str,
        requested_id: str,
        *,
        reason: str,
    ) -> RoutingDecision:
        """Resolve a target id; fall back to ``fallback_id`` with audit."""
        profile = self.registry.get(target_id)
        if profile is None:
            warning = (
                f"agent profile {target_id!r} not found; "
                f"falling back to {self.fallback_id!r} (reason={reason})"
            )
            logger.warning(warning)
            self._emit_audit(warning)
            profile = self.registry.get(self.fallback_id)
            if profile is None:
                # Last-ditch: register a minimal synthetic profile so
                # downstream code never crashes on None.
                profile = AgentProfile(
                    id=self.fallback_id,
                    backend="local",
                    llm_profile_name="local_chat",
                )
                logger.warning(
                    "fallback profile %r not in registry; using synthetic default",
                    self.fallback_id,
                )
            return RoutingDecision(
                profile=profile,
                requested_id=requested_id,
                fell_back=True,
                reason=warning,
                backend=self._resolve_backend(profile),
            )
        return RoutingDecision(
            profile=profile,
            requested_id=requested_id,
            fell_back=False,
            reason=reason,
            backend=self._resolve_backend(profile),
        )

    def _resolve_backend(self, profile: AgentProfile) -> str:
        """Use the optional resolver, else just echo the profile's backend."""
        if self.backend_resolver is None:
            return profile.backend
        try:
            resolved = self.backend_resolver(profile.backend)
        except Exception:  # noqa: BLE001 — resolver is user-supplied
            logger.debug("backend_resolver raised; using profile.backend", exc_info=True)
            return profile.backend
        return resolved or profile.backend

    def _emit_audit(self, message: str) -> None:
        if self.audit_sink is None:
            return
        try:
            self.audit_sink(message)
        except Exception:  # noqa: BLE001 — audit must never break routing
            logger.debug("audit_sink raised; continuing", exc_info=True)


__all__ = [
    "AgentRouter",
]
