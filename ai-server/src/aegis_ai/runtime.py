"""Process-wide AEGIS runtime singleton.

All user-facing entry points share one AegisRuntime instance so they use the
same LLM router, tool broker, policy engine, event bus, registry, and audit log.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aegis_ai.capability_catalog import CapabilityCatalog
from aegis_ai.capability_index import CapabilityIndex, CapabilityRetriever
from aegis_ai.config import Config, get_config
from aegis_ai.context_builder import ContextBuilder
from aegis_ai.folder_registry import FolderCapabilityRegistry
from aegis_ai.interaction.router import InteractionRouter
from aegis_ai.interaction.session import SessionManager
from aegis_ai.llm.gateway import LLMGateway
from aegis_ai.llm.router import LLMRouter
from aegis_ai.production_readiness import is_production_mode
from aegis_ai.web.saved_view_manager import SavedViewManager

logger = logging.getLogger("aegis_ai.runtime")


@dataclass
class AegisRuntime:
    """Shared process runtime for all AEGIS entry points."""

    config: Config
    data_dir: str
    settings_store: Any
    audit_log: Any
    event_bus: Any
    tool_registry: Any
    folder_registry: FolderCapabilityRegistry
    capability_catalog: CapabilityCatalog
    capability_index: CapabilityIndex
    capability_retriever: CapabilityRetriever
    policy_engine: Any
    server_executor: Any
    tool_broker: Any
    llm_router: LLMRouter
    llm_gateway: LLMGateway
    prompt_registry: Any
    settings_resolver: Any
    context_builder: ContextBuilder
    interaction_router: InteractionRouter
    session_manager: SessionManager
    autonomous_loop: Any = None
    event_manager: Any = None
    audit_manager: Any = None
    status_manager: Any = None
    task_manager: Any = None
    execution_engine: Any = None
    verification_service: Any = None
    notification_manager: Any = None
    memory_manager: Any = None
    sleep_manager: Any = None
    android_manager: Any = None
    user_state_manager: Any = None
    user_model_store: Any = None
    user_understanding_service: Any = None
    hook_engine: Any = None
    commitment_manager: Any = None
    situation_model: Any = None
    delegation_policy: Any = None
    social_proxy: Any = None
    social_manager: Any = None
    initiative_engine: Any = None
    continuation_manager: Any = None
    exploration_agenda: Any = None
    preference_store: Any = None
    identity: Any = None
    daily_planning_manager: Any = None
    behavioral_evaluation: Any = None
    interruption_controller: Any = None
    repair_manager: Any = None
    presentation_manager: Any = None
    agent_state: Any = None
    goal_service: Any = None
    saved_view_manager: Any = None
    operation_store: Any = None
    # Phase 5a: AEGIS-initiated confirmations. Holds the questions AEGIS chose to ask
    # the user and the answers it received. Nothing in the execution path *waits* on it,
    # so it can never block a capability — see `aegis_ai.confirmation`. Since 2026-10-01
    # the autonomous loop also *reads* it, to turn a rejection into an approval lesson;
    # it never asks or answers, which is what keeps the forced gate retired.
    confirmation_store: Any = None
    personal_data_core: Any = None
    l1_router: Any = None
    l1_executor: Any = None
    l2_mind: Any = None
    l3_reasoner: Any = None
    # Phase 1 (instruction.md §36): injected by _build_runtime when
    # `settings.agents.enabled=True`. None means the agent runtime is disabled:
    # an `ai-server.agent.*` step fails with "agent backend is not registered"
    # rather than running. The capability itself stays visible to the LLM —
    # hiding it was a manifest-declared feature flag that nothing supplied, and
    # it was removed (PROJECT_STATUS_REVIEW.md row A-12).
    agent_backend: Any = None
    # Phase 5 (instruction.md §36): loaded from `config/agent_profiles.yaml`.
    # Always present; empty registry when YAML is missing.
    agent_profiles: Any = None
    # Phase 5 (instruction.md §36): Profile selection (heuristic + explicit).
    agent_router: Any = None
    _lock: threading.RLock | None = None

    def start_autonomous_if_enabled(self) -> None:
        """Create and start the autonomous loop once if settings allow it."""
        lock = self._lock or threading.RLock()
        with lock:
            settings = self.settings_store.get()
            if not settings.autonomous.autonomous_loop_enabled:
                logger.info("Autonomous loop disabled by settings")
                return
            if self.autonomous_loop is None:
                self.autonomous_loop = _create_autonomous_loop(self)
            self.autonomous_loop.start()

    def set_agent_backend(self, backend: Any) -> None:
        """Phase 2: Swap the active AgentBackend at runtime.

        Local → OpenHands (or any registered backend) への切り替えに使う。
        同じ `AgentBackend` Protocol を満たすなら何でもいい。
        `None` を渡すと Phase 1 と同じく backend なし (agents.enabled=false
        相当) に戻る。
        """
        lock = self._lock or threading.RLock()
        with lock:
            previous = getattr(self, "agent_backend", None)
            self.agent_backend = backend
            logger.info(
                "agent_backend swapped: %s -> %s",
                getattr(previous, "name", type(previous).__name__ if previous else "None"),
                getattr(backend, "name", type(backend).__name__ if backend else "None"),
            )

    def get_agent_backend(self) -> Any:
        """現在アクティブな backend を返す (Phase 5 の AgentRouter からも利用)."""
        return getattr(self, "agent_backend", None)

    def stop(self) -> None:
        """Stop owned background runtime components."""
        l1_subscription = getattr(self, "_l1_event_subscription", "")
        if l1_subscription and self.event_manager is not None:
            try:
                self.event_manager.unsubscribe(l1_subscription)
            except Exception:
                logger.debug("Failed to unsubscribe L1 event handler", exc_info=True)
        subscription = getattr(self, "_initiative_event_subscription", "")
        if subscription and self.event_manager is not None:
            try:
                self.event_manager.unsubscribe(subscription)
            except Exception:
                logger.debug("Failed to unsubscribe initiative event handler", exc_info=True)
        l2_executor = getattr(self, "_background_l2_executor", None)
        if l2_executor is not None:
            # ``_submit_background_l2`` creates this lazily, so it exists only
            # once an event has been routed to the L2 pipeline.
            try:
                l2_executor.shutdown(wait=False)
            except Exception:
                logger.debug("Failed to stop background L2 executor", exc_info=True)
        l1_executor = getattr(self, "_background_l1_executor", None)
        if l1_executor is not None:
            # Same lazy creation as the L2 pool (``_submit_background_l1``), and
            # the same reason to stop it: its worker threads are not daemons, so
            # a leaked pool keeps the interpreter alive at exit.
            try:
                l1_executor.shutdown(wait=False)
            except Exception:
                logger.debug("Failed to stop background L1 executor", exc_info=True)
        loop = self.autonomous_loop
        if loop is not None:
            try:
                loop.stop()
            except Exception:
                logger.debug("Failed to stop autonomous loop", exc_info=True)
        status_manager = getattr(self, "status_manager", None)
        if status_manager is not None and hasattr(status_manager, "stop_background_checks"):
            # ``_build_runtime`` starts this thread, so ``stop`` has to stop it.
            # It is not an idle poller: it re-resolves pc-server/room-server with
            # ``allow_lan_scan=True``, so it probes the LAN and writes the result into
            # the endpoint resolver's process-global cache. While this was missing,
            # the daemon outlived the runtime for the rest of the process and
            # corrupted unrelated tests that assert on that cache.
            try:
                status_manager.stop_background_checks()
            except Exception:
                logger.debug("Failed to stop status manager background checks", exc_info=True)
        hook_engine = self.hook_engine
        if hook_engine is not None:
            try:
                hook_engine.stop()
            except Exception:
                logger.debug("Failed to stop hook engine", exc_info=True)
        user_state_manager = self.user_state_manager
        if user_state_manager is not None and hasattr(user_state_manager, "stop"):
            try:
                user_state_manager.stop()
            except Exception:
                logger.debug("Failed to stop user state manager", exc_info=True)
        personal_data_core = getattr(self, "personal_data_core", None)
        if personal_data_core is not None and hasattr(personal_data_core, "stop"):
            try:
                personal_data_core.stop()
            except Exception:
                logger.debug("Failed to stop personal data core", exc_info=True)
        if self.sleep_manager is not None and hasattr(self.sleep_manager, "close"):
            try:
                self.sleep_manager.close()
            except Exception:
                logger.debug("Failed to stop sleep manager", exc_info=True)
        if self.audit_log is not None and hasattr(self.audit_log, "close"):
            try:
                self.audit_log.close()
            except Exception:
                logger.debug("Failed to close audit log", exc_info=True)

    @property
    def _legacy_audit_log(self) -> Any:
        import warnings
        warnings.warn("Direct audit_log access is deprecated. Use audit_manager instead.", DeprecationWarning, stacklevel=2)
        return self.audit_log

    @property
    def _legacy_event_bus(self) -> Any:
        import warnings
        warnings.warn("Direct event_bus access is deprecated. Use event_manager instead.", DeprecationWarning, stacklevel=2)
        return self.event_bus


_RUNTIME: AegisRuntime | None = None
_RUNTIME_LOCK = threading.RLock()


def get_runtime(config: Config | None = None) -> AegisRuntime:
    """Return the process-wide AEGIS runtime singleton."""
    global _RUNTIME
    with _RUNTIME_LOCK:
        if _RUNTIME is None:
            _RUNTIME = _build_runtime(config or get_config())
        return _RUNTIME


def peek_runtime() -> AegisRuntime | None:
    """Return the live runtime without constructing one."""
    return _RUNTIME


def reset_runtime_for_tests() -> None:
    """Reset the runtime singleton for tests."""
    global _RUNTIME
    with _RUNTIME_LOCK:
        if _RUNTIME is not None:
            _RUNTIME.stop()
        _RUNTIME = None


def _load_runtime_env(base_dir: Path) -> None:
    """Load repo-local environment variables before providers initialize."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    for env_path in (base_dir.parent / ".env", base_dir / ".env"):
        if env_path.exists():
            load_dotenv(env_path, override=False)


def _llm_profile_allows_missing_api_key(settings: Any) -> bool:
    base_url = str(getattr(settings, "base_url", "") or "")
    return "localhost:11434" in base_url or "127.0.0.1:11434" in base_url


def _audit_llm_profile_health(audit_log: Any, settings_resolver: Any) -> list[dict[str, Any]]:
    """Record misconfigured LLM profiles so silent outages are visible at startup."""
    issues: list[dict[str, Any]] = []
    for profile_id in getattr(settings_resolver, "list_profile_ids", lambda: [])():
        try:
            settings = settings_resolver.resolve(profile_id=profile_id)
        except Exception as exc:
            issues.append(
                {
                    "profile_id": profile_id,
                    "error": str(exc),
                    "issue": "profile_resolution_failed",
                }
            )
            continue
        api_key_env = str(getattr(settings, "api_key_env", "") or "")
        if not api_key_env or _llm_profile_allows_missing_api_key(settings):
            continue
        if os.getenv(api_key_env, ""):
            continue
        issues.append(
            {
                "profile_id": profile_id,
                "provider": str(getattr(settings, "provider", "") or ""),
                "model": str(getattr(settings, "model", "") or ""),
                "api_key_env": api_key_env,
                "base_url": str(getattr(settings, "base_url", "") or ""),
                "issue": "missing_api_key",
            }
        )

    for issue in issues:
        logger.error(
            "LLM profile health issue: profile=%s issue=%s env=%s provider=%s model=%s",
            issue.get("profile_id", ""),
            issue.get("issue", ""),
            issue.get("api_key_env", ""),
            issue.get("provider", ""),
            issue.get("model", ""),
        )
        try:
            if audit_log is not None and hasattr(audit_log, "log_decision"):
                audit_log.log_decision(
                    "llm_profile_health",
                    "llm.profile_health",
                    "FAILED",
                    reason=f"profile={issue.get('profile_id', '')}",
                    actor="runtime",
                    detail=issue,
                )
        except Exception:
            logger.debug("Failed to audit LLM profile health issue", exc_info=True)
    return issues


def _require_l1_api_key_in_production(settings_resolver: Any) -> None:
    """Stop a production start that cannot authenticate L1 (DELEGATION.md item 46).

    ``_audit_llm_profile_health`` already records ``issue=missing_api_key`` at ERROR for
    every profile whose key is absent, so the degradation is not *silent*. It is not fatal
    either: with an empty key ``llm/gateway.py`` constructs ``TypeSafeProvider`` anyway,
    every call fails, and ``intake/l1_router._l1_unavailable_observation`` returns
    ``required_intelligence=HIGH`` so **every** event escalates. The process runs and looks
    alive while L1 classifies nothing.

    This is not new machinery -- it is the production-mode fail-fast that already exists a
    few lines above (``AEGIS_RUNTIME_MODE=production cannot start with MockLLMProvider``)
    and in ``docker_entrypoint.main`` (auth mode / session secret), extended to the one
    misconfiguration it did not cover.

    Scope is the profile L1 actually uses, discovered from
    ``llm.layer_profiles.layer_to_profile(LAYER_L1)`` rather than hardcoded, and **only**
    that profile: the other cloud profiles in ``config/llm.yaml`` are legitimately
    unconfigured, because the shipped allowlist names ``api.typesafe.ai`` and nothing else,
    so the gate denies them and they degrade to Mock by design.

    The gate is a *mode*, not a new flag, and that is what keeps CI safe -- measured
    2026-10-06: ``AEGIS_RUNTIME_MODE``'s only occurrence outside this package is
    ``.env.production.example``, and ``runtime_mode()`` defaults to ``development``.
    """
    if not is_production_mode():
        return
    from aegis_ai.llm.layer_profiles import LAYER_L1, layer_to_profile

    profile_id = layer_to_profile(LAYER_L1)
    try:
        settings = settings_resolver.resolve(profile_id=profile_id)
    except Exception as exc:
        raise RuntimeError(
            f"AEGIS_RUNTIME_MODE=production but the L1 profile {profile_id!r} does not "
            f"resolve: {exc!r}"
        ) from exc
    api_key_env = str(getattr(settings, "api_key_env", "") or "")
    if not api_key_env or _llm_profile_allows_missing_api_key(settings):
        return
    if os.getenv(api_key_env, ""):
        return
    raise RuntimeError(
        f"AEGIS_RUNTIME_MODE=production but {api_key_env} is unset, so the L1 profile "
        f"{profile_id!r} (provider={str(getattr(settings, 'provider', '') or '')!r}) cannot "
        "authenticate: every event would escalate and L1 would classify nothing. Set the "
        "key, or run with AEGIS_RUNTIME_MODE=development to keep the degraded (but loud) "
        "behaviour."
    )


def _parse_event_payload_for_l1(event: Any) -> dict[str, Any]:
    payload_json = str(getattr(event, "payload_json", "") or "{}")
    try:
        payload = json.loads(payload_json)
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {"value": payload}
    payload.setdefault("type", str(getattr(event, "event_type", "") or ""))
    payload.setdefault("event_id", str(getattr(event, "event_id", "") or ""))
    payload.setdefault("source", str(getattr(event, "source_server_id", "") or ""))
    source_type = getattr(event, "source_server_type", "")
    payload.setdefault("source_type", getattr(source_type, "name", str(source_type or "")).lower())
    return payload


def _l1_observation_payload(event: Any, observation: Any) -> dict[str, Any]:
    return {
        "event_id": str(getattr(observation, "event_id", "") or getattr(event, "event_id", "")),
        "original_event_type": str(getattr(event, "event_type", "") or ""),
        "meaning": str(getattr(observation, "meaning", "") or ""),
        "value": float(getattr(observation, "value", 0.0) or 0.0),
        "priority": float(getattr(observation, "priority", 0.0) or 0.0),
        "required_intelligence": str(getattr(getattr(observation, "required_intelligence", ""), "value", getattr(observation, "required_intelligence", "low"))),
        "confidence": float(getattr(observation, "confidence", 0.0) or 0.0),
        "raw": dict(getattr(observation, "raw", {}) or {}),
        "occurred_at_ms": int(getattr(event, "timestamp_ms", 0) or 0),
        "layer": "L1",
    }


def _l1_decision_payload(event: Any, decision: Any) -> dict[str, Any]:
    action = getattr(decision, "action", None)
    return {
        "event_id": str(getattr(decision, "event_id", "") or getattr(event, "event_id", "")),
        "original_event_type": str(getattr(event, "event_type", "") or ""),
        "action_type": str(getattr(getattr(action, "type", ""), "value", getattr(action, "type", "noop"))),
        "capability_id": str(getattr(action, "capability_id", "") or ""),
        "args": dict(getattr(action, "args", {}) or {}),
        "action_reason": str(getattr(action, "reason", "") or ""),
        "reasoning": str(getattr(decision, "reasoning", "") or ""),
        "occurred_at_ms": int(getattr(event, "timestamp_ms", 0) or 0),
        "layer": "L1",
    }


def _append_recent_l1_summary(runtime: Any, event: Any, observation: Any, decision: Any) -> None:
    recent = getattr(runtime, "_recent_l1_summaries", None)
    if recent is None:
        recent = deque(maxlen=50)
        runtime._recent_l1_summaries = recent
    recent.append(
        {
            "event_id": str(getattr(observation, "event_id", "") or getattr(event, "event_id", "")),
            "event_type": str(getattr(event, "event_type", "") or ""),
            "meaning": str(getattr(observation, "meaning", "") or ""),
            "value": float(getattr(observation, "value", 0.0) or 0.0),
            "priority": float(getattr(observation, "priority", 0.0) or 0.0),
            "required_intelligence": str(getattr(getattr(observation, "required_intelligence", ""), "value", getattr(observation, "required_intelligence", "low"))),
            "confidence": float(getattr(observation, "confidence", 0.0) or 0.0),
            "action_type": str(getattr(getattr(getattr(decision, "action", None), "type", ""), "value", getattr(getattr(decision, "action", None), "type", "noop"))),
            "summary_bucket": str(getattr(observation, "raw", {}).get("summary_bucket", "background") or "background"),
            "observed_action": str(getattr(observation, "raw", {}).get("observed_action", "") or ""),
            "possible_intent": str(getattr(observation, "raw", {}).get("possible_intent", "") or ""),
            "occurred_at_ms": int(getattr(event, "timestamp_ms", 0) or 0),
        }
    )


def _get_recent_l1_summaries(runtime: Any, *, limit: int = 10) -> list[dict[str, Any]]:
    recent = getattr(runtime, "_recent_l1_summaries", None)
    if recent is None:
        return []
    return list(recent)[-max(1, int(limit)) :]


def _truncate_text(value: Any, *, limit: int = 160) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def _compact_recent_l1_for_l1(runtime: Any, *, limit: int = 3) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for entry in _get_recent_l1_summaries(runtime, limit=limit):
        if not isinstance(entry, dict):
            continue
        items.append(
            {
                "event_type": str(entry.get("event_type") or ""),
                "summary_bucket": str(entry.get("summary_bucket") or "background"),
                "meaning": _truncate_text(entry.get("meaning") or entry.get("observed_action"), limit=120),
                "action_type": str(entry.get("action_type") or ""),
                "priority": float(entry.get("priority") or 0.0),
            }
        )
    return items


def _compact_user_state_for_l1(runtime: Any) -> dict[str, Any]:
    manager = getattr(runtime, "user_state_manager", None)
    if manager is None or not hasattr(manager, "get_current_user_state"):
        return {}
    try:
        state = dict(manager.get_current_user_state() or {})
    except Exception:
        logger.debug("Failed to load current user state for L1 capsule", exc_info=True)
        return {}
    attention = dict(state.get("attention") or {})
    activity = dict(state.get("activity") or {})
    return {
        "attention_device": str(attention.get("device") or ""),
        "attention_app": str(attention.get("app") or ""),
        "current_activity": str(activity.get("label") or ""),
        "activity_confidence": float(activity.get("confidence") or 0.0),
    }


def _compact_user_understanding_for_l1(runtime: Any, *, triggering_query: str = "") -> dict[str, Any]:
    service = getattr(runtime, "user_understanding_service", None)
    if service is None:
        return {}
    snapshot: dict[str, Any] = {}
    if hasattr(service, "get_latest_snapshot"):
        try:
            snapshot = dict(service.get_latest_snapshot() or {})
        except Exception:
            logger.debug("Failed to read cached user understanding for L1 capsule", exc_info=True)
    if not snapshot and hasattr(service, "build_snapshot"):
        try:
            built = service.build_snapshot(triggering_query)
            if hasattr(built, "to_dict"):
                snapshot = dict(built.to_dict())
            elif isinstance(built, dict):
                snapshot = dict(built)
        except Exception:
            logger.debug("Failed to build user understanding for L1 capsule", exc_info=True)
            snapshot = {}
    identity = dict(snapshot.get("identity_profile") or {})
    constraints = dict(snapshot.get("constraints") or {})
    likely_next = list(snapshot.get("likely_next_actions") or [])
    deficits = list(snapshot.get("predicted_deficits") or [])
    return {
        "summary": _truncate_text(snapshot.get("summary"), limit=180),
        "attention_device": str(identity.get("attention_device") or ""),
        "current_activity": str(identity.get("current_activity") or ""),
        "focus_mode": bool(constraints.get("focus_mode", False)),
        "likely_next_actions": [
            _truncate_text(item.get("title") or item.get("summary"), limit=100)
            for item in likely_next[:2]
            if isinstance(item, dict)
        ],
        "predicted_deficits": [
            _truncate_text(item.get("title") or item.get("summary"), limit=100)
            for item in deficits[:2]
            if isinstance(item, dict)
        ],
    }


def _compact_obligations_for_l1(runtime: Any, *, limit: int = 3) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for entry in _pending_l2_obligations(runtime, limit=limit):
        if not isinstance(entry, dict):
            continue
        items.append(
            {
                "kind": str(entry.get("kind") or entry.get("type") or ""),
                "summary": _truncate_text(
                    entry.get("summary") or entry.get("title") or entry.get("content"),
                    limit=120,
                ),
                "due_at_ms": int(entry.get("due_at_ms") or entry.get("deadline_ms") or 0),
            }
        )
    return items


def _compact_task_state_for_l1(runtime: Any, *, limit: int = 3) -> dict[str, Any]:
    tasks = _list_open_task_state(runtime, limit=max(3, limit * 3))
    items: list[dict[str, Any]] = []
    for entry in tasks[:limit]:
        if not isinstance(entry, dict):
            continue
        items.append(
            {
                "task_id": str(entry.get("task_id") or entry.get("id") or ""),
                "status": str(entry.get("status") or ""),
                "summary": _truncate_text(
                    entry.get("title") or entry.get("summary") or entry.get("description"),
                    limit=120,
                ),
            }
        )
    return {"active_task_count": len(tasks), "top_tasks": items}


def _compact_recent_facts_for_l1(runtime: Any, *, limit: int = 3) -> list[dict[str, Any]]:
    core = getattr(runtime, "personal_data_core", None)
    if core is None or not hasattr(core, "recent_facts"):
        return []
    try:
        facts = list(core.recent_facts(limit=max(1, int(limit))) or [])
    except Exception:
        logger.debug("Failed to read recent facts for L1 capsule", exc_info=True)
        return []
    items: list[dict[str, Any]] = []
    for entry in facts[:limit]:
        if not isinstance(entry, dict):
            continue
        items.append(
            {
                "statement": _truncate_text(entry.get("statement"), limit=120),
                "confidence": float(entry.get("confidence") or 0.0),
            }
        )
    return items


def _compact_world_state_for_l1(runtime: Any) -> dict[str, Any]:
    world: dict[str, Any] = {}
    situation_model = getattr(runtime, "situation_model", None)
    if situation_model is not None and hasattr(situation_model, "get_state"):
        try:
            situation = dict(situation_model.get_state() or {})
            world["situation_state"] = str(situation.get("state") or "")
            world["interruptibility"] = str(situation.get("interruptibility") or "")
        except Exception:
            logger.debug("Failed to read situation state for L1 capsule", exc_info=True)
    status_manager = getattr(runtime, "status_manager", None)
    if status_manager is not None and hasattr(status_manager, "get_snapshot"):
        try:
            snapshot = dict(status_manager.get_snapshot() or {})
            degraded = [
                server_id
                for server_id, info in snapshot.items()
                if str((info or {}).get("status") or "").lower()
                not in {"online", "healthy", "ok", "disabled", "unconfigured"}
            ]
            world["degraded_server_count"] = len(degraded)
            world["degraded_servers"] = degraded[:3]
        except Exception:
            logger.debug("Failed to read status snapshot for L1 capsule", exc_info=True)
    return world


def _build_l1_context_capsule(runtime: Any, event_payload: dict[str, Any]) -> dict[str, Any]:
    trigger_hint = _truncate_text(
        event_payload.get("message")
        or event_payload.get("summary")
        or event_payload.get("title")
        or event_payload.get("activity")
        or event_payload.get("type"),
        limit=120,
    )
    return {
        "user_state": _compact_user_state_for_l1(runtime),
        "user_understanding": _compact_user_understanding_for_l1(
            runtime,
            triggering_query=trigger_hint,
        ),
        "world_state": _compact_world_state_for_l1(runtime),
        "task_state": _compact_task_state_for_l1(runtime),
        "pending_obligations": _compact_obligations_for_l1(runtime),
        "recent_l1": _compact_recent_l1_for_l1(runtime),
        "recent_facts": _compact_recent_facts_for_l1(runtime),
    }


def _list_open_task_state(runtime: Any, *, limit: int = 20) -> list[dict[str, Any]]:
    task_manager = getattr(runtime, "task_manager", None)
    if task_manager is None or not hasattr(task_manager, "list_tasks"):
        return []
    try:
        tasks = task_manager.list_tasks(limit=max(1, int(limit)))
    except Exception:
        logger.debug("Failed to list task state for L2 context", exc_info=True)
        return []
    open_statuses = {"created", "running", "paused", "pending"}
    return [
        dict(task)
        for task in tasks
        if str(task.get("status") or "").lower() in open_statuses
    ][: max(1, int(limit))]


def _pending_l2_obligations(runtime: Any, *, limit: int = 12) -> list[dict[str, Any]]:
    commitment_manager = getattr(runtime, "commitment_manager", None)
    if commitment_manager is None or not hasattr(commitment_manager, "list_commitments"):
        return []
    try:
        items = commitment_manager.list_commitments(status="open")
    except Exception:
        logger.debug("Failed to list commitments for L2 context", exc_info=True)
        return []
    if not isinstance(items, list):
        return []
    return [dict(item) for item in items[: max(1, int(limit))] if isinstance(item, dict)]


def _recent_l2_failures(runtime: Any, *, limit: int = 8) -> list[str]:
    task_manager = getattr(runtime, "task_manager", None)
    if task_manager is None or not hasattr(task_manager, "list_open_incidents"):
        return []
    try:
        incidents = task_manager.list_open_incidents(limit=max(1, int(limit)))
    except Exception:
        logger.debug("Failed to list open incidents for L2 context", exc_info=True)
        return []
    failures: list[str] = []
    for incident in incidents[: max(1, int(limit))]:
        if not isinstance(incident, dict):
            continue
        failures.append(
            str(
                incident.get("error")
                or incident.get("result_summary")
                or incident.get("title")
                or incident.get("task_id")
                or "task incident"
            )
        )
    return failures


def _l2_world_state(runtime: Any) -> dict[str, Any]:
    world: dict[str, Any] = {}
    task_state = _list_open_task_state(runtime, limit=50)
    world["active_task_count"] = len(task_state)
    world["open_incident_count"] = len(_recent_l2_failures(runtime, limit=50))
    world["recent_l1_count"] = len(_get_recent_l1_summaries(runtime, limit=12))
    situation_model = getattr(runtime, "situation_model", None)
    if situation_model is not None and hasattr(situation_model, "get_state"):
        try:
            situation = situation_model.get_state()
            if isinstance(situation, dict):
                world["situation_state"] = str(situation.get("state") or "")
                world["interruptibility"] = str(situation.get("interruptibility") or "")
                world["situation_confidence"] = float(situation.get("confidence") or 0.0)
        except Exception:
            logger.debug("Failed to load situation state for L2 context", exc_info=True)
    status_manager = getattr(runtime, "status_manager", None)
    if status_manager is not None and hasattr(status_manager, "get_snapshot"):
        try:
            snapshot = status_manager.get_snapshot()
            if isinstance(snapshot, dict):
                degraded = [
                    server_id
                    for server_id, info in snapshot.items()
                    if str((info or {}).get("status") or "").lower()
                    not in {"online", "healthy", "ok", "disabled", "unconfigured"}
                ]
                world["degraded_servers"] = degraded[:8]
                world["degraded_server_count"] = len(degraded)
        except Exception:
            logger.debug("Failed to load status snapshot for L2 context", exc_info=True)
    user_understanding = getattr(runtime, "user_understanding_service", None)
    if user_understanding is not None and hasattr(user_understanding, "to_context_string"):
        try:
            world["user_understanding"] = str(user_understanding.to_context_string(""))[:600]
        except Exception:
            logger.debug("Failed to summarize user understanding for L2 context", exc_info=True)
    return world


def _run_l2_pipeline(runtime: Any, *, trigger: str, detail: dict[str, Any]) -> dict[str, Any]:
    mind = getattr(runtime, "l2_mind", None)
    if mind is None:
        return {"handled": False, "reason": "L2 mind unavailable", "action_type": "noop"}
    try:
        context = mind.build_context()
        context.world_state.update(
            {
                "trigger": trigger,
                "trigger_source": str(detail.get("source") or ""),
                "trigger_event_type": str(detail.get("type") or trigger),
            }
        )
        l1_info = detail.get("l1")
        if isinstance(l1_info, dict):
            context.l1_summaries = [dict(l1_info), *list(context.l1_summaries)][:12]
        result = mind.run_once(context)
        if getattr(runtime, "event_manager", None) is not None:
            runtime.event_manager.publish_event(
                "l2.execution",
                source="l2_mind",
                payload={
                    "trigger": trigger,
                    "handled": bool(result.get("handled")),
                    "action_type": str(result.get("action_type") or "noop"),
                    "task_id": str(result.get("task_id") or ""),
                    "reason": str(result.get("reason") or ""),
                },
            )
        return result
    except Exception as exc:
        logger.exception("L2 pipeline failed for trigger=%s", trigger)
        return {"handled": False, "reason": f"L2 pipeline failed: {exc!r}", "action_type": "noop"}


def _submit_background_l2(runtime: Any, *, trigger: str, detail: dict[str, Any]) -> None:
    """Run the L2 pipeline off the caller's thread (E-2).

    ``EventBus`` notifies subscribers **inline on the publisher's thread**
    (``event_bus.EventBus._notify_subscribers``), and one publisher is the gRPC
    ``PushEvent`` handler, which runs on one of the ``config.max_workers``
    request threads. The L2 pipeline can reach a multi-second outbound call
    (``agents/backends/openhands/workspace._default_http_post(timeout=30.0)``),
    so running it inline occupies a request thread for the whole call.

    On the background path the L2 result is discarded — only its side effects
    matter — so it is safe to run on a dedicated single worker. That also stops
    concurrent L2 runs from multiplying with the event rate.

    Pinned by ``tests/test_background_l2_runs_off_the_request_thread.py``.
    """
    import concurrent.futures

    executor = getattr(runtime, "_background_l2_executor", None)
    if executor is None:
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="aegis-background-l2"
        )
        runtime._background_l2_executor = executor  # type: ignore[attr-defined]
    try:
        executor.submit(_run_l2_pipeline, runtime, trigger=trigger, detail=detail)
    except RuntimeError:
        # Executor already shut down (runtime stopping) — stay correct inline.
        logger.debug("Background L2 executor unavailable; running inline", exc_info=True)
        _run_l2_pipeline(runtime, trigger=trigger, detail=detail)


def _run_l1_pipeline_for_event(runtime: Any, event: Any) -> Any | None:
    router = getattr(runtime, "l1_router", None)
    event_manager = getattr(runtime, "event_manager", None)
    if router is None or event_manager is None:
        return None
    event_payload = _parse_event_payload_for_l1(event)
    l1_capsule = _build_l1_context_capsule(runtime, event_payload)
    observation = router.observe(
        event_payload,
        event_id=str(getattr(event, "event_id", "") or ""),
        context_capsule=l1_capsule,
    )
    event_manager.publish_event("l1.observation", source="l1_router", payload=_l1_observation_payload(event, observation))
    decision = router.decide(observation)
    event_manager.publish_event("l1.decision", source="l1_router", payload=_l1_decision_payload(event, decision))
    _append_recent_l1_summary(runtime, event, observation, decision)
    action = getattr(decision, "action", None)
    action_type = str(getattr(getattr(action, "type", ""), "value", getattr(action, "type", "")))
    if action_type == "escalate":
        escalation = router.escalate(observation, reason=str(getattr(action, "reason", "") or ""))
        event_manager.publish_event("l1.escalation", source="l1_router", payload=escalation.to_payload())
    elif action_type == "capability" and getattr(runtime, "l1_executor", None) is not None:
        capability_id = str(getattr(action, "capability_id", "") or "")
        args = dict(getattr(action, "args", {}) or {})
        event_manager.publish_event(
            "l1.capability.invoked",
            source="l1_executor",
            payload={
                "event_id": str(getattr(event, "event_id", "") or ""),
                "capability_id": capability_id,
                "args": args,
                "occurred_at_ms": int(getattr(event, "timestamp_ms", 0) or 0),
                "layer": "L1",
            },
        )
        result = runtime.l1_executor.execute(
            capability_id,
            args,
            event_id=str(getattr(event, "event_id", "") or ""),
        )
        event_manager.publish_event("l1.capability.completed", source="l1_executor", payload=result.to_payload())
    return decision


def _run_l1_immediate_pipeline(runtime: Any, event: Any) -> None:
    """The immediate route's work after the routing check (item 48).

    This is everything ``_evaluate_immediate_event`` used to do once an event
    matched: the L1 pipeline itself, the ``detail["l1"]`` projection, the
    capability short-circuit, the L2 hand-off, and the ``initiative_engine`` /
    ``AutonomousLoop`` notifications.

    It stays in one function on purpose. The decision has to be **waited for** --
    the old code read ``l1_decision.action`` before it could build ``detail`` --
    so detaching only the ``observe()`` call would have left the continuation on
    the publisher's thread (no gain) or, worse, run it with ``l1_decision is
    None`` and silently dropped ``detail["l1"]`` and the capability branch.

    The ``try`` is here for the same reason ``_run_l2_pipeline`` has one: on a
    worker thread nothing above this frame can report the failure, so the
    loudness has to live inside the callable. On the publisher's thread the bus
    would have routed it to ``EventBus._dead_letter_handler`` instead.
    """
    event_type = str(getattr(event, "event_type", "") or "")
    try:
        rt = runtime
        initiative_engine = getattr(rt, "initiative_engine", None)
        l1_decision = _run_l1_pipeline_for_event(rt, event) if rt is not None else None
        l1_action = getattr(getattr(l1_decision, "action", None), "type", "")
        l1_action_value = str(getattr(l1_action, "value", l1_action))
        if l1_action_value == "ignore":
            return
        detail = _parse_event_payload_for_l1(event)
        if l1_decision is not None:
            observation = getattr(l1_decision, "observation", None)
            detail["l1"] = {
                "meaning": str(getattr(observation, "meaning", "") or ""),
                "value": float(getattr(observation, "value", 0.0) or 0.0),
                "priority": float(getattr(observation, "priority", 0.0) or 0.0),
                "required_intelligence": str(
                    getattr(
                        getattr(observation, "required_intelligence", ""),
                        "value",
                        getattr(observation, "required_intelligence", "low"),
                    )
                ),
                "confidence": float(getattr(observation, "confidence", 0.0) or 0.0),
                "action_type": l1_action_value or "noop",
                "summary_bucket": str(getattr(observation, "raw", {}).get("summary_bucket", "background") or "background"),
                "observed_action": str(getattr(observation, "raw", {}).get("observed_action", "") or ""),
                "possible_intent": str(getattr(observation, "raw", {}).get("possible_intent", "") or ""),
            }
        if l1_action_value == "capability":
            initiative_engine.record_trigger(event_type, detail)
            return
        if rt is not None and getattr(rt, "l2_mind", None) is not None:
            l2_result = _run_l2_pipeline(rt, trigger=event_type, detail=detail)
            detail["l2"] = dict(l2_result)
            if l2_result.get("handled") and str(l2_result.get("action_type") or "") not in {"noop", "observe"}:
                initiative_engine.record_trigger(event_type, detail)
                return
        initiative_engine.record_trigger(event_type, detail)
        loop = getattr(rt, "autonomous_loop", None)
        if loop is not None and hasattr(loop, "evaluate_event"):
            loop.evaluate_event(event_type, detail)
    except Exception:
        logger.exception("L1 immediate pipeline failed for event_type=%s", event_type)


def _submit_background_l1(runtime: Any, *, event: Any) -> None:
    """Run the immediate L1 route off the publisher's thread (item 48).

    The mirror of ``_submit_background_l2``. ``EventBus`` notifies subscribers
    **inline on the publisher's thread** (``event_bus.EventBus._notify_subscribers``),
    and one publisher is the gRPC ``PushEvent`` handler, which runs on one of the
    ``config.max_workers`` request threads. ``_run_l1_pipeline_for_event`` awaits
    ``router.observe(...)`` -- an LLM round-trip -- so running it inline occupies a
    request thread for the whole call. L2 was moved off that thread by E-2 and L1
    was left behind; that asymmetry is what item 48 recorded.

    A single worker, like L2, so the event rate cannot multiply concurrent L1
    runs, and FIFO order keeps consecutive immediate events in arrival order.

    Pinned by ``tests/test_l1_runs_off_the_publisher_thread.py``.
    """
    import concurrent.futures

    executor = getattr(runtime, "_background_l1_executor", None)
    if executor is None:
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="aegis-background-l1"
        )
        runtime._background_l1_executor = executor  # type: ignore[attr-defined]
    try:
        executor.submit(_run_l1_immediate_pipeline, runtime, event)
    except RuntimeError:
        # Executor already shut down (runtime stopping) -- stay correct inline.
        logger.debug("Background L1 executor unavailable; running inline", exc_info=True)
        _run_l1_immediate_pipeline(runtime, event)


# Events L1 handles on the immediate route. Since item 48 that route is handed to
# a single background worker (`_submit_background_l1`) rather than running inline
# on the publisher's thread. The background route
# (`_should_route_to_l1_background`) takes everything else that is not excluded
# below -- and that one is still inline, which item 48 did not change.
#
# ⚠️ Three of these are **declared but never produced** (measured 2026-10-05,
# recorded as DELEGATION.md section 4 item 45). The concepts they name are all
# already carried by `self_call`, so nothing is lost today:
#   - `hook.matched`    -- the hook engine publishes `self_call` on a match
#                          (`personal_ai/hooks.py::_emit_self_call`).
#   - `commitment.due`  -- a due commitment gets a per-commitment hook
#                          (`personal_ai/commitments.py::_ensure_due_hook`), so
#                          it too arrives as `self_call`.
#   - `browser.discovery` -- no producer anywhere in the repo, and browser-server
#                          has no such concept.
# They are kept (not deleted) so the intent is visible and a future producer
# routes immediately; `tests/test_l1_immediate_triggers_have_producers.py` pins
# that these three still have no literal publisher, and that every other member
# still does.
_L1_IMMEDIATE_EVENT_TYPES = {
    "social.inbox.received",
    "task.completed",
    "task.failed",
    "status.changed",
    "commitment.due",
    "browser.discovery",
    "android.permission.changed",
    "android.notification.posted",
    "android.notification_received",
    "android.user_activity.changed",
    "android.foreground_app.changed",
    "android.current_app_changed",
    "pc.user_activity.snapshot",
    "browser.user_activity.changed",
    "hook.matched",
    "self_call",
}

_L1_EXCLUDED_EVENT_PREFIXES = (
    "l1.",
    "l2.",
    "l3.",
    "presentation.",
)

_L1_EXCLUDED_EVENT_TYPES = {
    "",
}


def _should_route_to_l1_immediate(event_type: str) -> bool:
    return str(event_type or "") in _L1_IMMEDIATE_EVENT_TYPES


def _should_route_to_l1_background(event_type: str) -> bool:
    event_type = str(event_type or "")
    if event_type in _L1_EXCLUDED_EVENT_TYPES:
        return False
    if event_type.startswith(_L1_EXCLUDED_EVENT_PREFIXES):
        return False
    if _should_route_to_l1_immediate(event_type):
        return False
    return True


def _build_runtime(config: Config) -> AegisRuntime:
    from event_bus import EventBus
    from policy_engine import PolicyEngine
    from server_executor import ServerExecutor
    from tool_broker import ToolBroker
    from tool_registry import ToolRegistry

    from aegis_ai.audit import AuditLog
    from aegis_ai.llm.factory import create_llm_provider_from_settings
    from aegis_ai.llm.providers.mock import MockLLMProvider
    from aegis_ai.llm.prompt_registry import PromptRegistry
    from aegis_ai.llm.settings_resolver import LLMSettingsResolver
    from aegis_ai.settings.store import SettingsStore

    # Phase 1: optional OpenTelemetry bootstrap.
    # Keep this best-effort so tracing never blocks core runtime.
    try:
        from aegis_ai.observability.otel_tracing import init_tracing

        init_tracing()
    except Exception:
        logger.debug("OTel init failed (best-effort)", exc_info=True)

    base_dir = Path(__file__).resolve().parents[2]
    _load_runtime_env(base_dir)
    data_dir = str(base_dir / "data")
    settings_store = SettingsStore(
        path=str(base_dir / "config" / "settings.json"),
        audit_path=str(Path(data_dir) / "settings_audit.jsonl"),
    )
    audit_log = AuditLog(path=os.path.join(data_dir, "audit.jsonl"))
    event_bus = EventBus(dedup_window_ms=config.dedup_window_ms)

    # ── Egress gate (the single constraint) ─────────────────────────────────
    # Configure the single deny-by-default gate for all outbound transmission
    # BEFORE anything that could reach the network is constructed. AEGIS must not
    # transmit the user's data outside the local environment.
    from aegis_ai.egress import configure_egress_gate, verify_egress_configuration

    egress_gate = configure_egress_gate(settings_store=settings_store)
    verify_egress_configuration(
        egress_gate,
        llm_config_path=base_dir / "config" / "llm.yaml",
    )

    policy_engine = PolicyEngine(data_dir=data_dir)

    capability_catalog = CapabilityCatalog(
        capabilities_dir=str(base_dir / "capabilities"),
        apps_dir=str(base_dir / "apps"),
        data_dir=data_dir,
    )
    capability_index = CapabilityIndex(
        capability_catalog,
        chroma_path=str(Path(data_dir) / "chroma" / "capabilities"),
    )
    capability_retriever = CapabilityRetriever(capability_catalog, capability_index)
    folder_registry = capability_catalog.get_folder_registry()

    tool_registry = ToolRegistry()
    for capability in capability_catalog.to_tool_registry_capabilities():
        try:
            tool_registry.register_capability(capability)
        except ValueError:
            logger.debug("Skipping non-registerable capability: %s", capability.id, exc_info=True)

    server_executor = ServerExecutor()
    server_executor.set_catalog(capability_catalog)
    from aegis_ai.verification import VerificationService

    verification_service = VerificationService(
        audit_log=audit_log,
        browser_client=server_executor,
        pc_client=server_executor,
    )
    tool_broker = ToolBroker(
        registry=tool_registry,
        policy_engine=policy_engine,
        audit_log=audit_log,
        server_executor=server_executor,
        folder_registry=folder_registry,
        catalog=capability_catalog,
        verification_service=verification_service,
    )

    llm_router = LLMRouter(settings_store=settings_store, audit_log=audit_log)
    provider = create_llm_provider_from_settings(settings_store, audit_log=audit_log)
    if isinstance(provider, MockLLMProvider):
        if is_production_mode():
            raise RuntimeError(
                "AEGIS_RUNTIME_MODE=production cannot start with MockLLMProvider. "
                "Configure a real local or cloud LLM provider before production startup."
            )
        llm_router.register_provider("mock", provider)
        llm_router.set_default_provider("mock")
    else:
        llm_router.register_provider("default", provider)
        # Register the local provider under the name the router's local-fallback
        # lookup expects, so that `external_llm_allowed=False` routes to the real
        # local model rather than silently degrading to Mock.
        _provider_base_url = str(
            getattr(provider, "_base_url", None) or getattr(provider, "base_url", "") or ""
        )
        if "localhost" in _provider_base_url or "127.0.0.1" in _provider_base_url:
            llm_router.register_provider("ollama", provider)
        if not is_production_mode():
            llm_router.register_provider("mock", MockLLMProvider())
        llm_router.set_default_provider("default")

    prompt_registry = PromptRegistry(str(base_dir / "config" / "prompts.yaml"))
    settings_resolver = LLMSettingsResolver(str(base_dir / "config" / "llm.yaml"))
    _audit_llm_profile_health(audit_log, settings_resolver)
    # Item 46: in production the audit above is not enough -- an unauthenticated L1 still
    # starts and then escalates every event. The audit stays (it covers every profile and is
    # what makes the degradation visible outside production); this adds the fatal half for the
    # one profile L1 actually needs.
    _require_l1_api_key_in_production(settings_resolver)
    llm_gateway = LLMGateway(
        router=llm_router,
        settings_resolver=settings_resolver,
        prompt_registry=prompt_registry,
        audit_log=audit_log,
    )

    from aegis_ai.user_model import UserModelStore
    from aegis_ai.mind.identity import Identity

    user_model_store = UserModelStore(data_dir=os.path.join(data_dir, "user_model"))
    identity = Identity(path=os.path.join(data_dir, "mind_identity.jsonl"))

    context_builder = ContextBuilder(
        event_bus=event_bus,
        tool_broker=tool_broker,
        multimodal_llm=llm_gateway,
        capability_retriever=capability_retriever,
        settings_resolver=settings_resolver,
        user_model_store=user_model_store,
        identity=identity,
    )
    session_manager = SessionManager()
    interaction_router = InteractionRouter(
        llm_provider=llm_gateway,
        context_builder=context_builder,
        capability_catalog=capability_catalog,
        capability_retriever=capability_retriever,
        tool_broker=tool_broker,
        audit_log=audit_log,
        settings_store=settings_store,
    )

    from aegis_ai.event.event_manager import EventManager
    from aegis_ai.audit.audit_manager import AuditManager
    from aegis_ai.status.status_manager import StatusManager
    from aegis_ai.task.task_manager import TaskManager
    from aegis_ai.task.execution_engine import TaskExecutionEngine
    from aegis_ai.notification.notification_manager import NotificationManager
    from aegis_ai.memory.memory_manager import MemoryManager
    from aegis_ai.memory.sleep import SleepManager
    from aegis_ai.memory.advanced import AdvancedMemory
    from aegis_ai.memory.episodic_memory import EpisodicMemory
    from aegis_ai.memory.semantic_memory import SemanticMemory
    from aegis_ai.memory.skill_memory import SkillMemory
    from aegis_ai.memory.lesson_memory import LessonMemory
    from aegis_ai.memory.workflow_memory import WorkflowMemory
    from aegis_ai.memory.experiential import ExperientialMemory
    from aegis_ai.memory.person_memory import PersonMemory
    from aegis_ai.memory.memory_store import MemoryStore

    memory_dir = os.path.join(data_dir, "memory")
    advanced_memory = AdvancedMemory(data_dir=memory_dir, llm_provider=llm_gateway)
    episodic_memory = EpisodicMemory(path=os.path.join(memory_dir, "episodic.jsonl"))
    semantic_memory = SemanticMemory(path=os.path.join(memory_dir, "semantic.jsonl"))
    skill_memory = SkillMemory(path=os.path.join(memory_dir, "skills.jsonl"))
    lesson_memory = LessonMemory(path=os.path.join(memory_dir, "lessons.jsonl"))
    workflow_memory = WorkflowMemory(path=os.path.join(memory_dir, "workflows.jsonl"))
    experiential_memory = ExperientialMemory(data_dir=memory_dir, llm_provider=llm_gateway)
    person_memory = PersonMemory(path=os.path.join(memory_dir, "persons.jsonl"))
    memory_store = MemoryStore(data_dir=os.path.join(data_dir, "memory_store"))
    context_builder._memory_store = memory_store

    from aegis_ai.journal.journal_store import JournalStore
    from aegis_ai.journal.projector import JournalProjector
    from aegis_ai.observability.capability_health import CapabilityHealthView

    journal_store = JournalStore(data_dir=data_dir)
    journal_projector = JournalProjector(event_manager=None, operation_store=None)
    event_manager = EventManager(
        event_bus=event_bus,
        data_dir=data_dir,
        journal_store=journal_store,
        journal_projector=journal_projector,
    )
    journal_projector._event_manager = event_manager
    capability_health = CapabilityHealthView(tool_registry=tool_registry)
    tool_broker._capability_health = capability_health
    audit_manager = AuditManager(audit_log=audit_log, data_dir=data_dir, event_manager=event_manager)
    # Route egress decisions to the audit log for post-hoc verification of the
    # single constraint (Phase 3 visibility).
    try:
        egress_gate.set_audit(audit_manager)
    except Exception:
        logger.warning("Failed to attach audit to the egress gate", exc_info=True)
    status_manager = StatusManager(event_manager=event_manager)
    task_manager = TaskManager(event_manager=event_manager, audit_manager=audit_manager, data_dir=data_dir)
    notification_manager = NotificationManager(event_manager=event_manager)

    from aegis_ai.personal_ai import (
        CommitmentManager,
        DelegationPolicyStore,
        HookEngine,
        InterruptionController,
        SituationModel,
        SocialProxy,
    )

    personal_dir = os.path.join(data_dir, "personal_ai")
    runtime_ref: dict[str, Any] = {}
    from aegis_ai.user_state import UserStateManager

    user_state_manager = UserStateManager(
        data_dir=os.path.join(data_dir, "user_state"),
        event_manager=event_manager,
        settings_store=settings_store,
    )
    from aegis_ai.personal_data import PersonalDataCore
    from aegis_ai.autonomous import L2AutonomousMind
    from aegis_ai.intake import L1Executor, L1Router
    from aegis_ai.llm import L3Reasoner

    personal_data_core = PersonalDataCore(
        data_dir,
        event_manager=event_manager,
        settings_store=settings_store,
        audit_manager=audit_manager,
        server_executor=server_executor,
    )
    event_manager._personal_data_core = personal_data_core
    l1_router = L1Router(llm_gateway=llm_gateway)
    l1_executor = L1Executor(
        capability_catalog=capability_catalog,
        tool_broker=tool_broker,
    )
    situation_model = SituationModel(data_dir=personal_dir, event_manager=event_manager, user_state_manager=user_state_manager)
    delegation_policy = DelegationPolicyStore(
        data_dir=personal_dir,
        audit_manager=audit_manager,
        user_model_store=user_model_store,
    )
    tool_broker.set_delegation_policy(delegation_policy)
    hook_engine = HookEngine(
        data_dir=personal_dir,
        tool_broker=tool_broker,
        capability_catalog=capability_catalog,
        event_manager=event_manager,
        audit_manager=audit_manager,
        autonomous_loop_getter=lambda: getattr(runtime_ref.get("runtime"), "autonomous_loop", None),
        user_state_manager=user_state_manager,
    )
    commitment_manager = CommitmentManager(data_dir=personal_dir, audit_manager=audit_manager, hook_engine=hook_engine)
    interruption_controller = InterruptionController(
        data_dir=personal_dir,
        situation_model=situation_model,
        user_model_store=user_model_store,
        commitment_manager=commitment_manager,
        audit_manager=audit_manager,
    )
    notification_manager.set_interruption_controller(interruption_controller)
    social_proxy = SocialProxy(data_dir=personal_dir, event_manager=event_manager, audit_manager=audit_manager)
    from aegis_ai.social.manager import SocialManager

    social_manager = SocialManager(
        data_dir=os.path.join(data_dir, "social"),
        llm=llm_gateway,
        tool_broker=tool_broker,
        event_manager=event_manager,
        audit_manager=audit_manager,
    )

    def _social_relationship_context(item: Any) -> dict[str, Any]:
        person = person_memory.resolve(str(getattr(item, "author", "") or ""))
        if person is None:
            return {}
        return {
            "person_id": person.person_id,
            "name": person.name,
            "role": person.role,
            "relationship": person.relationship,
            "trust_level": person.trust_level,
            "interaction_count": person.interaction_count,
            "preferences": dict(person.preferences),
            "topics": list(person.topics),
            "last_context": person.last_context,
        }

    social_manager.set_relationship_provider(_social_relationship_context)
    # Prefer live AGORA identity; fall back to deferred refresh via read_posts / get_me.
    try:
        from aegis_ai.integrations.agora.agora_service import AgoraService

        _agora_boot = AgoraService(data_dir=os.path.join(data_dir, "social"))
        me = _agora_boot.get_me()
        if not (isinstance(me, dict) and me.get("error")):
            author_id = int(getattr(me, "id", 0) or 0)
            author_name = str(getattr(me, "name", "") or "").strip()
            social_manager.set_self_authors(
                author_ids={author_id} if author_id else set(),
                author_names={author_name} if author_name else set(),
            )
            logger.info(
                "Boot-wired SocialManager self authors id=%s name=%s",
                author_id or None,
                author_name or None,
            )
    except Exception:
        logger.info("AGORA self-author boot wiring deferred until first read_posts", exc_info=True)
    from aegis_ai.autonomous.continuation_manager import ContinuationManager
    from aegis_ai.autonomous.exploration_agenda import ExplorationAgenda
    from aegis_ai.autonomous.initiative_engine import InitiativeEngine
    from aegis_ai.personal_ai.preference_learning import ConditionalPreferenceStore
    from aegis_ai.personal_ai.daily_planning import DailyPlanningManager
    from aegis_ai.evaluation.behavioral import BehavioralEvaluation

    initiative_engine = InitiativeEngine(os.path.join(data_dir, "autonomous"))
    continuation_manager = ContinuationManager(os.path.join(data_dir, "autonomous"))
    exploration_agenda = ExplorationAgenda(os.path.join(data_dir, "autonomous"))
    preference_store = ConditionalPreferenceStore(personal_dir)
    daily_planning_manager = DailyPlanningManager(
        personal_dir,
        llm=llm_gateway,
        commitment_manager=commitment_manager,
        continuation_manager=continuation_manager,
    )
    behavioral_evaluation = BehavioralEvaluation(
        initiative_engine=initiative_engine,
        continuation_manager=continuation_manager,
        social_manager=social_manager,
        task_manager=task_manager,
    )
    from aegis_ai.operations import OperationStore

    operation_store = OperationStore(data_dir=data_dir)
    # Phase 5a: the confirmation store is process-wide because three readers share it —
    # the `/api/approvals/*` endpoints, the resource/overview projections, and the
    # LLM-callable capability AEGIS uses to raise a question on its own initiative.
    from aegis_ai.confirmation import ConfirmationStore

    confirmation_store = ConfirmationStore(data_dir)
    tool_broker.set_continuation_manager(continuation_manager)

    context_builder._situation_model = situation_model
    context_builder._user_state_manager = user_state_manager
    context_builder._delegation_policy = delegation_policy
    context_builder._commitment_manager = commitment_manager
    from aegis_ai.integrations.android.manager import AndroidServerManager

    android_manager = AndroidServerManager(
        data_dir=data_dir,
        event_manager=event_manager,
        status_manager=status_manager,
    )
    server_executor.register_client("android-server", android_manager)

    from aegis_ai.integrations.room import RoomServerGrpcClient

    server_executor.register_client("room-server", RoomServerGrpcClient())

    from aegis_ai.core_capabilities import AegisCoreCapabilityClient

    server_executor.register_client(
        "ai-server",
        AegisCoreCapabilityClient(
            data_dir=data_dir,
            server_executor=server_executor,
            personal_managers={
                "user_model_store": user_model_store,
                "hook_engine": hook_engine,
                "commitment_manager": commitment_manager,
                "delegation_policy": delegation_policy,
                "situation_model": situation_model,
                "user_state_manager": user_state_manager,
                "interruption_controller": interruption_controller,
                "social_proxy": social_proxy,
                "social_manager": social_manager,
                "llm_provider": llm_gateway,
                # Phase 5a: lets AEGIS raise a confirmation on its own initiative
                # (``ai-server.confirmation.request``) and read the answer back.
                "confirmation_store": confirmation_store,
            },
        ),
    )

    verification_service._android = android_manager
    from aegis_ai.temporal.client import init_temporal_runtime

    temporal_runtime = init_temporal_runtime(
        tool_broker=tool_broker,
        llm_gateway=llm_gateway,
        journal_store=journal_store,
    )
    execution_engine = TaskExecutionEngine(
        task_manager=task_manager,
        tool_broker=tool_broker,
        llm_gateway=llm_gateway,
        prompt_registry=prompt_registry,
        settings_resolver=settings_resolver,
        verification_service=verification_service,
        event_manager=event_manager,
        audit_manager=audit_manager,
        temporal_runtime=temporal_runtime,
    )

    interaction_router._task_manager = task_manager
    interaction_router._execution_engine = execution_engine


    memory_manager = MemoryManager(
        advanced_memory=advanced_memory,
        episodic_memory=episodic_memory,
        semantic_memory=semantic_memory,
        skill_memory=skill_memory,
        lesson_memory=lesson_memory,
        workflow_memory=workflow_memory,
        experiential_memory=experiential_memory,
        person_memory=person_memory,
        memory_store=memory_store,
        llm_gateway=llm_gateway,
        event_manager=event_manager,
    )
    personal_data_core._memory = memory_manager
    from aegis_ai.personal_ai import RepairManager
    from aegis_ai.user_understanding import UserUnderstandingService

    repair_manager = RepairManager(
        data_dir=personal_dir,
        tool_broker=tool_broker,
        audit_manager=audit_manager,
        memory_manager=memory_manager,
    )
    user_understanding_service = UserUnderstandingService(
        data_dir=os.path.join(data_dir, "user_understanding"),
        user_model_store=user_model_store,
        user_state_manager=user_state_manager,
        commitment_manager=commitment_manager,
        delegation_policy=delegation_policy,
        person_memory=person_memory,
        personal_data_core=personal_data_core,
        task_manager=task_manager,
        repair_manager=repair_manager,
    )
    from aegis_ai.agency import AgentState, GoalLifecycleService

    agent_state = AgentState(
        identity=identity,
        situation_model=situation_model,
        commitment_manager=commitment_manager,
        social_manager=social_manager,
        task_manager=task_manager,
        repair_manager=repair_manager,
        delegation_policy=delegation_policy,
        daily_planning_manager=daily_planning_manager,
        person_memory=person_memory,
        memory_manager=memory_manager,
        preference_store=preference_store,
        user_understanding_service=user_understanding_service,
    )
    behavioral_evaluation.set_memory_manager(memory_manager)
    context_builder._agent_state = agent_state
    context_builder._user_understanding_service = user_understanding_service
    social_manager.set_agent_state(agent_state)
    daily_planning_manager.set_agent_state(agent_state)
    repair_manager.set_agent_state(agent_state)
    goal_service = GoalLifecycleService(
        task_manager=task_manager,
        llm_gateway=llm_gateway,
    )
    execution_engine._goal_service = goal_service
    core_client = server_executor._clients.get("ai-server")
    if core_client is not None and hasattr(core_client, "_personal"):
        core_client._personal["memory_manager"] = memory_manager
        core_client._personal["repair_manager"] = repair_manager
        core_client._personal["personal_data_core"] = personal_data_core
    tool_broker.set_repair_manager(repair_manager)
    execution_engine._repair_manager = repair_manager
    from aegis_ai.backup.retention import RetentionManager

    sleep_manager = SleepManager(
        memory_manager=memory_manager,
        event_manager=event_manager,
        audit_manager=audit_manager,
        llm_gateway=llm_gateway,
    )
    sleep_manager._personal_data_core = personal_data_core
    sleep_manager._retention = RetentionManager(
        episodic_memory=episodic_memory,
        audit_log=audit_log,
        settings_store=settings_store,
        memory_store=memory_store,
    )
    if core_client is not None and hasattr(core_client, "_personal"):
        core_client._personal["sleep_manager"] = sleep_manager

    from aegis_ai.presentation.manager import PresentationManager
    from aegis_ai.presentation.device_router import DeviceRouter, OverlayBroadcastAdapter, DashboardAdapter, XRPendingAdapter
    from aegis_ai.presentation.object_store import PresentationObjectStore

    pres_object_store = PresentationObjectStore(data_dir=data_dir)
    pres_overlay_adapter = OverlayBroadcastAdapter(core_capability_client=core_client)
    pres_dashboard_adapter = DashboardAdapter()
    pres_xr_adapter = XRPendingAdapter()
    pres_device_router = DeviceRouter(
        overlay_adapter=pres_overlay_adapter,
        dashboard_adapter=pres_dashboard_adapter,
        xr_adapter=pres_xr_adapter,
    )
    presentation_manager = PresentationManager(
        object_store=pres_object_store,
        device_router=pres_device_router,
        event_manager=event_manager,
        audit_manager=audit_manager,
        notification_manager=notification_manager,
        interruption_controller=interruption_controller,
        conditional_preference_store=preference_store,
        data_dir=data_dir,
    )
    repair_manager.set_presentation_manager(presentation_manager)
    if core_client is not None and hasattr(core_client, "_personal"):
        core_client._personal["presentation_manager"] = presentation_manager

    def _publish_cognition_event(event_type: str, payload: dict[str, Any]) -> None:
        source = "l3_reasoner" if str(event_type).startswith("l3.") else "l2_mind"
        event_manager.publish_event(event_type, source=source, payload=payload)

    l3_reasoner = L3Reasoner(
        llm_gateway=llm_gateway,
        capability_catalog=capability_catalog,
        event_publisher=_publish_cognition_event,
    )
    l2_mind = L2AutonomousMind(
        llm_gateway=llm_gateway,
        memory_system=advanced_memory,
        desire_system=None,
        task_state_provider=lambda: _list_open_task_state(runtime_ref.get("runtime") or runtime),
        l1_summaries_provider=lambda: _get_recent_l1_summaries(runtime_ref.get("runtime") or runtime, limit=12),
        world_state_provider=lambda: _l2_world_state(runtime_ref.get("runtime") or runtime),
        obligations_provider=lambda: _pending_l2_obligations(runtime_ref.get("runtime") or runtime, limit=12),
        recent_failures_provider=lambda: _recent_l2_failures(runtime_ref.get("runtime") or runtime, limit=8),
        event_publisher=_publish_cognition_event,
        task_manager=task_manager,
        execution_engine=execution_engine,
        capability_catalog=capability_catalog,
    )
    l2_mind._l3_reasoner = l3_reasoner

    try:
        pc_poll_interval = int(os.getenv("AEGIS_USER_STATE_PC_POLL_INTERVAL_SECONDS", "2"))
        user_state_manager.start_pc_poller(
            server_executor,
            status_manager=status_manager,
            interval_seconds=pc_poll_interval,
        )
        personal_data_core.start_background(server_executor)
    except Exception:
        logger.debug("Failed to start user-state PC poller", exc_info=True)

    runtime = AegisRuntime(
        config=config,
        data_dir=data_dir,
        settings_store=settings_store,
        audit_log=audit_log,
        event_bus=event_bus,
        tool_registry=tool_registry,
        folder_registry=folder_registry,
        capability_catalog=capability_catalog,
        capability_index=capability_index,
        capability_retriever=capability_retriever,
        policy_engine=policy_engine,
        server_executor=server_executor,
        tool_broker=tool_broker,
        llm_router=llm_router,
        llm_gateway=llm_gateway,
        prompt_registry=prompt_registry,
        settings_resolver=settings_resolver,
        context_builder=context_builder,
        interaction_router=interaction_router,
        session_manager=session_manager,
        event_manager=event_manager,
        audit_manager=audit_manager,
        status_manager=status_manager,
        task_manager=task_manager,
        execution_engine=execution_engine,
        verification_service=verification_service,
        notification_manager=notification_manager,
        memory_manager=memory_manager,
        sleep_manager=sleep_manager,
        android_manager=android_manager,
        user_state_manager=user_state_manager,
        user_model_store=user_model_store,
        user_understanding_service=user_understanding_service,
        hook_engine=hook_engine,
        commitment_manager=commitment_manager,
        situation_model=situation_model,
        delegation_policy=delegation_policy,
        social_proxy=social_proxy,
        social_manager=social_manager,
        initiative_engine=initiative_engine,
        continuation_manager=continuation_manager,
        exploration_agenda=exploration_agenda,
        preference_store=preference_store,
        identity=identity,
        daily_planning_manager=daily_planning_manager,
        behavioral_evaluation=behavioral_evaluation,
        interruption_controller=interruption_controller,
        repair_manager=repair_manager,
        presentation_manager=presentation_manager,
        agent_state=agent_state,
        goal_service=goal_service,
        saved_view_manager=SavedViewManager(data_dir, audit_manager),
        operation_store=operation_store,
        confirmation_store=confirmation_store,
        personal_data_core=personal_data_core,
        l1_router=l1_router,
        l1_executor=l1_executor,
        l2_mind=l2_mind,
        l3_reasoner=l3_reasoner,
        _lock=threading.RLock(),
    )
    runtime_ref["runtime"] = runtime

    # Phase 1: OpenHands agent backend bootstrap. No-op unless `agents.enabled=True`.
    # LocalBackend は default で常駐 (dependency なし). `enabled=False` なら `agent_backend`
    # フィールドは `None` のままになり、`ai-server.agent.*` のステップは
    # "agent backend is not registered" で失敗する (capability を隠す機構は持たない —
    # 供給者の居なかった feature flag は削除した; PROJECT_STATUS_REVIEW.md A-12 参照).
    try:
        from aegis_ai.agents.backends import (
            clear_backends as _clear_agent_backends,
            get_backend as _get_agent_backend,
            register_backend as _register_agent_backend,
        )
        from aegis_ai.agents.backends.local import LocalBackend as _LocalAgentBackend
        from aegis_ai.agents.profiles import (
            AgentProfileRegistry as _AgentProfileRegistry,
        )
        from aegis_ai.agents.runtime.router import AgentRouter as _AgentRouter

        _clear_agent_backends()
        _register_agent_backend(_LocalAgentBackend())
        # Phase 5: load agent profile registry (always present, possibly empty).
        # Audit sink is a thin wrapper that logs to the runtime audit log when
        # available; production code wires a real sink in Phase 8.
        _audit_sink = getattr(runtime, "audit_log", None)
        if _audit_sink is not None and not hasattr(_audit_sink, "__call__"):

            def _audit_sink(message: str) -> None:
                logger.info("[agent_router] %s", message)

        try:
            _profiles = _AgentProfileRegistry.from_yaml()
            if _profiles.load_warnings:
                for w in _profiles.load_warnings:
                    logger.warning("agent profile YAML: %s", w)
            _router = _AgentRouter(
                registry=_profiles,
                fallback_id="general",
                audit_sink=_audit_sink,
                backend_resolver=_get_agent_backend,
            )
            runtime.agent_profiles = _profiles
            runtime.agent_router = _router
        except Exception:
            logger.debug("Agent profile registry bootstrap failed", exc_info=True)
            runtime.agent_profiles = _AgentProfileRegistry()
            runtime.agent_router = _AgentRouter(registry=runtime.agent_profiles)

        settings = settings_store.get()
        if settings.agents.enabled:
            backend = _get_agent_backend(settings.agents.backend)
            if backend is None:
                logger.warning(
                    "agents.enabled=True but backend=%r is not registered; agent_backend stays None",
                    settings.agents.backend,
                )
            runtime.agent_backend = backend
        else:
            runtime.agent_backend = None
            logger.info("Agent runtime disabled (agents.enabled=false)")
    except Exception:
        logger.debug("Agent runtime bootstrap skipped", exc_info=True)
        runtime.agent_backend = None

    def _evaluate_immediate_event(event):
        event_type = str(getattr(event, "event_type", "") or "")
        if not _should_route_to_l1_immediate(event_type):
            return
        rt = runtime_ref.get("runtime")
        if rt is None:
            # ``runtime_ref`` is populated before this subscription is created,
            # so this is unreachable in practice. Spelled out rather than left
            # implicit: the old inline body would have recorded a trigger with a
            # bare ``detail`` here, which is not worth reproducing.
            return
        _submit_background_l1(rt, event=event)

    def _handle_background_l1_event(event):
        rt = runtime_ref.get("runtime")
        decision = _run_l1_pipeline_for_event(rt, event) if rt is not None else None
        if rt is None or decision is None:
            return
        action = getattr(getattr(decision, "action", None), "type", "")
        action_value = str(getattr(action, "value", action))
        if action_value not in {"escalate", "observe"}:
            return
        detail = _parse_event_payload_for_l1(event)
        observation = getattr(decision, "observation", None)
        detail["l1"] = {
            "meaning": str(getattr(observation, "meaning", "") or ""),
            "value": float(getattr(observation, "value", 0.0) or 0.0),
            "priority": float(getattr(observation, "priority", 0.0) or 0.0),
            "required_intelligence": str(
                getattr(
                    getattr(observation, "required_intelligence", ""),
                    "value",
                    getattr(observation, "required_intelligence", "low"),
                )
            ),
            "confidence": float(getattr(observation, "confidence", 0.0) or 0.0),
            "action_type": action_value,
            "summary_bucket": str(getattr(observation, "raw", {}).get("summary_bucket", "background") or "background"),
            "observed_action": str(getattr(observation, "raw", {}).get("observed_action", "") or ""),
            "possible_intent": str(getattr(observation, "raw", {}).get("possible_intent", "") or ""),
        }
        _submit_background_l2(
            rt,
            trigger=str(getattr(event, "event_type", "") or "background"),
            detail=detail,
        )

    runtime._l1_event_subscription = event_manager.subscribe(  # type: ignore[attr-defined]
        _handle_background_l1_event,
        lambda event: _should_route_to_l1_background(
            str(getattr(event, "event_type", "") or "")
        ),
    )
    runtime._initiative_event_subscription = event_manager.subscribe(  # type: ignore[attr-defined]
        _evaluate_immediate_event,
        lambda event: _should_route_to_l1_immediate(
            str(getattr(event, "event_type", "") or "")
        ),
    )
    # The advertised event-driven core, finally constructed (DELEGATION.md section 4 item
    # 24, branch 1 -- the owner selected "build it, including the task-consumption path").
    # Until now `TriggerEngine`, `Scheduler` and `EventView` were fully written and
    # constructed nowhere, and `config.trigger_enabled` was read only by the startup log
    # line -- a flag whose only reader changed nothing. Constructing the engine here gives
    # that flag its behavioural reader, and `EventView` is built with BOTH halves so it is
    # not the silent no-op a bare `EventView()` is (see the pin's last test).
    runtime.trigger_engine = None
    runtime.scheduler = None
    runtime.event_view = None
    if config.trigger_enabled:
        from aegis_ai.observability.event_view import EventView
        from aegis_ai.scheduler import Scheduler
        from trigger_engine import TriggerEngine, create_default_rules

        trigger_engine = TriggerEngine()
        for rule in create_default_rules():
            trigger_engine.add_rule(rule)
        runtime.trigger_engine = trigger_engine
        runtime.scheduler = Scheduler()
        runtime.event_view = EventView(event_bus=event_bus, trigger_engine=trigger_engine)
        # Subscribed with no filter: the engine's own rules decide what matters, and a
        # filter here would keep events out of `stats.events_received`.
        runtime._trigger_event_subscription = event_manager.subscribe(  # type: ignore[attr-defined]
            trigger_engine.on_event,
        )
        logger.info(
            "Trigger engine: %d rules subscribed to the event bus",
            len(trigger_engine.list_rules()),
        )
    else:
        logger.info("Trigger engine: disabled by config.trigger_enabled")
    status_manager.start_background_checks()
    hook_engine.start()
    social_manager.resume_pending_processing()
    return runtime


def _create_autonomous_loop(runtime: AegisRuntime) -> Any:
    from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
    from aegis_ai.autonomous.curiosity_exploration import CuriosityDrivenExplorationSystem
    from aegis_ai.autonomous.spontaneous_observation import SpontaneousObservationSystem
    from aegis_ai.desire.desire_system import DesireSystem
    from aegis_ai.health.alert_manager import HealthAlertManager
    from aegis_ai.memory.action_trace import ActionTraceMemory
    from aegis_ai.memory.association_memory import AssociationMemory
    from aegis_ai.mind.affect_system import AffectSystem

    settings = runtime.settings_store.get()
    data_dir = runtime.data_dir
    memory_dir = os.path.join(data_dir, "memory")
    mm = runtime.memory_manager

    desire = DesireSystem(data_dir=os.path.join(data_dir, "desires"), llm_provider=runtime.llm_gateway)
    affect = AffectSystem(data_dir=data_dir)
    action_trace = ActionTraceMemory(path=os.path.join(memory_dir, "action_traces.jsonl"))
    association_mem = AssociationMemory(path=os.path.join(memory_dir, "associations.jsonl"))

    # Wire action_trace to MemoryManager
    mm._action_trace = action_trace

    advanced_memory = mm.get_backend("advanced")
    experiential = mm.get_backend("experiential")
    lesson_mem = mm.get_backend("lesson")
    workflow_mem = mm.get_backend("workflow")
    skill_mem = mm.get_backend("skill")
    episodic_mem = mm.get_backend("episodic")
    semantic_mem = mm.get_backend("semantic")
    person_mem = mm.get_backend("person")

    from aegis_ai.reflection.reflection_engine import ReflectionEngine

    loop = AutonomousLoop(
        llm_provider=runtime.llm_gateway,
        desire_system=desire,
        memory_system=advanced_memory,
        reflection_engine=ReflectionEngine(memory_store=mm.get_backend("store")),
        tool_broker=runtime.tool_broker,
        experiential_memory=experiential,
        affect_system=affect,
        action_trace=action_trace,
        skill_memory=skill_mem,
        workflow_memory=workflow_mem,
        lesson_memory=lesson_mem,
        policy_engine=runtime.policy_engine,
        audit_log=runtime.audit_log,
        task_manager=runtime.task_manager,
        confirmation_store=runtime.confirmation_store,
        status_manager=runtime.status_manager,
        settings_resolver=runtime.settings_resolver,
        data_dir=os.path.join(data_dir, "autonomous"),
        desire_threshold=4.0,
        max_tasks_per_cycle=max(1, settings.autonomous.max_tasks_per_cycle),
        fallback_interval_seconds=max(1, settings.autonomous.evaluation_interval_seconds),
    )
    if getattr(runtime, "l2_mind", None) is not None:
        runtime.l2_mind.desire_system = desire
        loop.set_l2_reasoning_handler(
            lambda trigger="periodic_cycle", force_desire=False, pending_observations=None: _run_l2_pipeline(
                runtime,
                trigger=trigger,
                detail={
                    "type": trigger,
                    "source": "autonomous_loop",
                    "pending_observations": list(pending_observations or []),
                    "force_desire": bool(force_desire),
                },
            ),
            should_run=lambda force_desire=False: bool(force_desire)
            or runtime.l2_mind.should_run_cycle()
            or bool(getattr(loop, "_pending_actionable_observations", [])),
            event_handler=lambda event_type, detail: _run_l2_pipeline(
                runtime,
                trigger=event_type,
                detail=detail,
            ),
        )
    loop._capability_retriever = runtime.capability_retriever
    loop._min_execution_interval_ms = max(1, settings.autonomous.min_action_interval_seconds) * 1000
    loop._min_llm_interval_ms = max(1, settings.autonomous.min_llm_interval_seconds) * 1000
    loop._initiative_engine = runtime.initiative_engine
    loop._continuation_manager = runtime.continuation_manager
    loop._agent_state = runtime.agent_state
    loop._goal_service = runtime.goal_service
    loop._user_understanding_service = runtime.user_understanding_service
    loop._social_manager = runtime.social_manager
    loop._operation_store = getattr(runtime, "operation_store", None)
    loop._sleep_manager = runtime.sleep_manager
    loop._memory_manager = runtime.memory_manager
    # §4 item 24 branch 1: hand the loop the TriggerEngine built in ``_build_runtime`` so
    # it drains the engine's queued TaskRequests. ``getattr`` because the engine is absent
    # when ``config.trigger_enabled`` is false -- and then the loop drains nothing.
    loop._trigger_engine = getattr(runtime, "trigger_engine", None)

    # §4 item 8 / §3.1 hole 3: the burden metric is judged by the judgment LLM and the
    # user is asked to check the judgement periodically. The loop owns the cadence; the
    # metric is a plain object with no clock of its own. `JUDGMENT_PROFILE` is
    # `jev_decision`, which resolves to the one allowlisted host (`api.typesafe.ai`) —
    # a profile the gate denies would degrade to Mock, and the check is skipped for a
    # Mock judgement, so a denied profile would make this wiring inert.
    from aegis_ai.burden import BurdenMetric

    loop.set_burden_metric(BurdenMetric(runtime.llm_gateway))

    loop.set_health_alert_manager(
        HealthAlertManager(
            data_dir=os.path.join(data_dir, "health"),
            tool_broker=runtime.tool_broker,
            llm_provider=runtime.llm_gateway,
            status_manager=runtime.status_manager,
            data_path=data_dir,
        )
    )
    import inspect

    observation_kwargs = {
        "llm": runtime.llm_gateway,
        "broker": runtime.tool_broker,
        "desire_system": desire,
        "affect_system": affect,
        "episodic_memory": episodic_mem,
        "semantic_memory": semantic_mem,
        "person_memory": person_mem,
        "action_trace": action_trace,
        "status_manager": runtime.status_manager,
        "task_manager": getattr(runtime, "task_manager", None),
        "agent_state": getattr(runtime, "agent_state", None),
        "user_state_manager": getattr(runtime, "user_state_manager", None),
        "data_dir": os.path.join(data_dir, "autonomous"),
    }
    observation_params = inspect.signature(SpontaneousObservationSystem.__init__).parameters
    if not any(p.kind == inspect.Parameter.VAR_KEYWORD for p in observation_params.values()):
        observation_kwargs = {
            key: value for key, value in observation_kwargs.items() if key in observation_params
        }
    loop.set_observation_system(SpontaneousObservationSystem(**observation_kwargs))
    curiosity_system = CuriosityDrivenExplorationSystem(
            llm=runtime.llm_gateway,
            desire_system=desire,
            episodic_memory=episodic_mem,
            semantic_memory=semantic_mem,
            association_memory=association_mem,
            action_trace=action_trace,
            person_memory=person_mem,
            tool_broker=runtime.tool_broker,
            skill_memory=skill_mem,
            data_dir=os.path.join(data_dir, "autonomous"),
    )
    curiosity_system._agenda = runtime.exploration_agenda
    loop.set_curiosity_system(curiosity_system)

    # Wire SleepManager to SleepConsolidationSystem
    from aegis_ai.memory.sleep_consolidation import SleepConsolidationSystem
    consolidation_system = SleepConsolidationSystem(
        episodic=episodic_mem,
        semantic=semantic_mem,
        person=person_mem,
        association=association_mem,
        experiential=experiential,
        action_trace=action_trace,
        lesson=lesson_mem,
        workflow=workflow_mem,
        skill=skill_mem,
        llm=runtime.llm_gateway,
        data_dir=memory_dir,
    )
    runtime.sleep_manager._consolidation_system = consolidation_system

    return loop
