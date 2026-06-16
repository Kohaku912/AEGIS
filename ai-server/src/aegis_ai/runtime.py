"""Process-wide AEGIS runtime singleton.

All user-facing entry points share one AegisRuntime instance so they use the
same LLM router, tool broker, policy engine, event bus, registry, and audit log.
"""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aegis_ai.capability_catalog import CapabilityCatalog
from aegis_ai.config import Config, get_config
from aegis_ai.context_builder import ContextBuilder
from aegis_ai.folder_registry import FolderCapabilityRegistry
from aegis_ai.interaction.router import InteractionRouter
from aegis_ai.interaction.session import SessionManager
from aegis_ai.llm.router import LLMRequest, LLMResponse, LLMRouter, PrivacyLevel, TaskType

logger = logging.getLogger("aegis_ai.runtime")


class LLMGateway:
    """Provider-compatible facade that always routes through LLMRouter."""

    def __init__(self, router: LLMRouter) -> None:
        self._router = router

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        context_meta: dict[str, Any] | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        request = self._request(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            context_meta=context_meta,
            json_mode=json_mode,
        )
        return self._router.route(request)

    def generate_with_tools(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.3,
        context_meta: dict[str, Any] | None = None,
    ) -> LLMResponse:
        request = self._request(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            context_meta=context_meta,
        )
        return self._router.route_with_tools(request, tools)

    def generate_with_image(
        self,
        prompt: str,
        image_base64: str,
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        detail: str = "low",
        context_meta: dict[str, Any] | None = None,
    ) -> LLMResponse:
        request = self._request(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            context_meta=context_meta,
        )
        return self._router.route_with_image(request, image_base64, detail=detail)

    def generate_with_media(
        self,
        prompt: str,
        image_base64s: list[str],
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        detail: str = "low",
        context_meta: dict[str, Any] | None = None,
        media_kind: str = "image",
    ) -> LLMResponse:
        request = self._request(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            context_meta=context_meta,
        )
        return self._router.route_with_media(
            request,
            image_base64s,
            detail=detail,
            media_kind=media_kind,
        )

    @staticmethod
    def _request(
        *,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
        temperature: float,
        context_meta: dict[str, Any] | None = None,
        json_mode: bool = False,
    ) -> LLMRequest:
        meta = context_meta or {}
        return LLMRequest(
            task_type=TaskType.HIGH_REASONING_TASK if json_mode else TaskType.SMALL_FAST_TASK,
            prompt=prompt,
            system_prompt=system_prompt,
            privacy_level=PrivacyLevel.INTERNAL,
            max_tokens=max_tokens,
            temperature=temperature,
            caller=str(meta.get("caller", "runtime")),
            request_id=str(meta.get("request_id", "")),
            context_meta=context_meta,
            json_mode=json_mode,
        )


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
    approval_store: Any
    approval_queue: Any
    policy_engine: Any
    server_executor: Any
    tool_broker: Any
    llm_router: LLMRouter
    llm_gateway: LLMGateway
    context_builder: ContextBuilder
    interaction_router: InteractionRouter
    session_manager: SessionManager
    autonomous_loop: Any = None
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

    def stop(self) -> None:
        """Stop owned background runtime components."""
        loop = self.autonomous_loop
        if loop is not None:
            try:
                loop.stop()
            except Exception:
                logger.debug("Failed to stop autonomous loop", exc_info=True)


_RUNTIME: AegisRuntime | None = None
_RUNTIME_LOCK = threading.RLock()


def get_runtime(config: Config | None = None) -> AegisRuntime:
    """Return the process-wide AEGIS runtime singleton."""
    global _RUNTIME
    with _RUNTIME_LOCK:
        if _RUNTIME is None:
            _RUNTIME = _build_runtime(config or get_config())
        return _RUNTIME


def reset_runtime_for_tests() -> None:
    """Reset the runtime singleton for tests."""
    global _RUNTIME
    with _RUNTIME_LOCK:
        if _RUNTIME is not None:
            _RUNTIME.stop()
        _RUNTIME = None


def _build_runtime(config: Config) -> AegisRuntime:
    from approval import ApprovalStore
    from event_bus import EventBus
    from policy_engine import PolicyEngine
    from server_executor import ServerExecutor
    from tool_broker import ToolBroker
    from tool_registry import ToolRegistry

    from aegis_ai.approval import ApprovalQueue
    from aegis_ai.audit import AuditLog
    from aegis_ai.llm.factory import create_llm_provider_from_settings
    from aegis_ai.llm.providers.mock import MockLLMProvider
    from aegis_ai.settings.store import SettingsStore

    base_dir = Path(__file__).resolve().parents[2]
    data_dir = str(base_dir / "data")
    settings_store = SettingsStore(
        path=str(base_dir / "config" / "settings.json"),
        audit_path=str(Path(data_dir) / "settings_audit.jsonl"),
    )
    audit_log = AuditLog(path=os.path.join(data_dir, "audit.jsonl"))
    event_bus = EventBus(dedup_window_ms=config.dedup_window_ms)

    approval_store = ApprovalStore(
        request_timeout_ms=config.approval_timeout_ms,
        approval_validity_ms=config.approval_validity_ms,
    )
    approval_queue = ApprovalQueue(data_dir=os.path.join(data_dir, "approvals"), audit_log=audit_log)
    policy_engine = PolicyEngine(approval_store=approval_store, data_dir=data_dir)

    capability_catalog = CapabilityCatalog(
        capabilities_dir=str(base_dir / "capabilities"),
        apps_dir=str(base_dir / "apps"),
    )
    folder_registry = capability_catalog.get_folder_registry()

    tool_registry = ToolRegistry()
    for capability in capability_catalog.to_tool_registry_capabilities():
        try:
            tool_registry.register_capability(capability)
        except ValueError:
            logger.debug("Skipping non-registerable capability: %s", capability.id, exc_info=True)

    server_executor = ServerExecutor()
    server_executor.set_catalog(capability_catalog)
    tool_broker = ToolBroker(
        registry=tool_registry,
        policy_engine=policy_engine,
        audit_log=audit_log,
        approval_queue=approval_queue,
        server_executor=server_executor,
        folder_registry=folder_registry,
        catalog=capability_catalog,
    )

    llm_router = LLMRouter(settings_store=settings_store, audit_log=audit_log)
    provider = create_llm_provider_from_settings(settings_store, audit_log=audit_log)
    if isinstance(provider, MockLLMProvider):
        llm_router.register_provider("mock", provider)
        llm_router.set_default_provider("mock")
    else:
        llm_router.register_provider("default", provider)
        llm_router.register_provider("mock", MockLLMProvider())
        llm_router.set_default_provider("default")
    llm_gateway = LLMGateway(llm_router)

    context_builder = ContextBuilder(
        event_bus=event_bus,
        tool_broker=tool_broker,
        multimodal_llm=llm_gateway,
    )
    session_manager = SessionManager()
    interaction_router = InteractionRouter(
        llm_provider=llm_gateway,
        context_builder=context_builder,
        capability_catalog=capability_catalog,
        tool_broker=tool_broker,
        approval_store=approval_store,
        audit_log=audit_log,
        settings_store=settings_store,
    )

    return AegisRuntime(
        config=config,
        data_dir=data_dir,
        settings_store=settings_store,
        audit_log=audit_log,
        event_bus=event_bus,
        tool_registry=tool_registry,
        folder_registry=folder_registry,
        capability_catalog=capability_catalog,
        approval_store=approval_store,
        approval_queue=approval_queue,
        policy_engine=policy_engine,
        server_executor=server_executor,
        tool_broker=tool_broker,
        llm_router=llm_router,
        llm_gateway=llm_gateway,
        context_builder=context_builder,
        interaction_router=interaction_router,
        session_manager=session_manager,
        _lock=threading.RLock(),
    )


def _create_autonomous_loop(runtime: AegisRuntime) -> Any:
    from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
    from aegis_ai.autonomous.curiosity_exploration import CuriosityDrivenExplorationSystem
    from aegis_ai.autonomous.spontaneous_observation import SpontaneousObservationSystem
    from aegis_ai.desire.desire_system import DesireSystem
    from aegis_ai.memory.action_trace import ActionTraceMemory
    from aegis_ai.memory.advanced import AdvancedMemory
    from aegis_ai.memory.association_memory import AssociationMemory
    from aegis_ai.memory.episodic_memory import EpisodicMemory
    from aegis_ai.memory.experiential import ExperientialMemory
    from aegis_ai.memory.lesson_memory import LessonMemory
    from aegis_ai.memory.person_memory import PersonMemory
    from aegis_ai.memory.semantic_memory import SemanticMemory
    from aegis_ai.memory.skill_memory import SkillMemory
    from aegis_ai.memory.workflow_memory import WorkflowMemory
    from aegis_ai.mind.affect_system import AffectSystem

    settings = runtime.settings_store.get()
    data_dir = runtime.data_dir
    memory_dir = os.path.join(data_dir, "memory")

    desire = DesireSystem(data_dir=os.path.join(data_dir, "desires"), llm_provider=runtime.llm_gateway)
    experiential = ExperientialMemory(data_dir=memory_dir, llm_provider=runtime.llm_gateway)
    advanced_memory = AdvancedMemory(data_dir=memory_dir, llm_provider=runtime.llm_gateway)
    affect = AffectSystem(data_dir=data_dir)
    action_trace = ActionTraceMemory(path=os.path.join(memory_dir, "action_traces.jsonl"))
    lesson_mem = LessonMemory(path=os.path.join(memory_dir, "lessons.jsonl"))
    workflow_mem = WorkflowMemory(path=os.path.join(memory_dir, "workflows.jsonl"))
    skill_mem = SkillMemory(path=os.path.join(memory_dir, "skills.jsonl"))

    loop = AutonomousLoop(
        llm_provider=runtime.llm_gateway,
        desire_system=desire,
        memory_system=advanced_memory,
        tool_broker=runtime.tool_broker,
        experiential_memory=experiential,
        affect_system=affect,
        action_trace=action_trace,
        skill_memory=skill_mem,
        workflow_memory=workflow_mem,
        lesson_memory=lesson_mem,
        policy_engine=runtime.policy_engine,
        data_dir=os.path.join(data_dir, "autonomous"),
        desire_threshold=4.0,
        max_tasks_per_cycle=max(1, min(4, settings.autonomous.max_autonomous_runs_per_hour)),
        fallback_interval_seconds=max(1, settings.autonomous.cooldown_seconds),
    )
    loop._min_execution_interval_ms = max(1, settings.autonomous.cooldown_seconds) * 1000

    episodic_mem = EpisodicMemory(path=os.path.join(memory_dir, "episodic.jsonl"))
    semantic_mem = SemanticMemory(path=os.path.join(memory_dir, "semantic.jsonl"))
    association_mem = AssociationMemory(path=os.path.join(memory_dir, "associations.jsonl"))
    person_mem = PersonMemory(path=os.path.join(memory_dir, "persons.jsonl"))

    loop.set_observation_system(
        SpontaneousObservationSystem(
            llm=runtime.llm_gateway,
            broker=runtime.tool_broker,
            desire_system=desire,
            affect_system=affect,
            episodic_memory=episodic_mem,
            semantic_memory=semantic_mem,
            person_memory=person_mem,
            action_trace=action_trace,
            data_dir=os.path.join(data_dir, "autonomous"),
        )
    )
    loop.set_curiosity_system(
        CuriosityDrivenExplorationSystem(
            llm=runtime.llm_gateway,
            desire_system=desire,
            episodic_memory=episodic_mem,
            semantic_memory=semantic_mem,
            association_memory=association_mem,
            action_trace=action_trace,
            person_memory=person_mem,
            data_dir=os.path.join(data_dir, "autonomous"),
        )
    )
    return loop
