"""Process-wide AEGIS runtime singleton.

All user-facing entry points share one AegisRuntime instance so they use the
same LLM router, tool broker, policy engine, event bus, registry, and audit log.
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
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
    approval_store: Any
    approval_queue: Any
    approval_manager: Any
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
    notification_manager: Any = None
    memory_manager: Any = None
    sleep_manager: Any = None
    android_manager: Any = None
    user_state_manager: Any = None
    user_model_store: Any = None
    hook_engine: Any = None
    commitment_manager: Any = None
    situation_model: Any = None
    delegation_policy: Any = None
    social_proxy: Any = None
    interruption_controller: Any = None
    repair_manager: Any = None
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

    @property
    def _legacy_approval_store(self) -> Any:
        import warnings
        warnings.warn("Direct approval_store access is deprecated. Use approval_manager instead.", DeprecationWarning, stacklevel=2)
        return self.approval_store

    @property
    def _legacy_approval_queue(self) -> Any:
        import warnings
        warnings.warn("Direct approval_queue access is deprecated. Use approval_manager instead.", DeprecationWarning, stacklevel=2)
        return self.approval_queue


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
    from aegis_ai.llm.prompt_registry import PromptRegistry
    from aegis_ai.llm.settings_resolver import LLMSettingsResolver
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
    from aegis_ai.approval.approval_manager import ApprovalManager
    from aegis_ai.approval.channels.dashboard import DashboardApprovalChannel
    from aegis_ai.approval.fanout import ApprovalFanout, ApprovalEvent
    approval_manager = ApprovalManager(approval_queue=approval_queue, audit_log=audit_log)
    approval_fanout = ApprovalFanout(audit_log=audit_log)
    dashboard_approval_channel = DashboardApprovalChannel()
    approval_fanout.register_channel(dashboard_approval_channel)

    def _on_approval_state_change(event_dict):
        """Fanout approval events to all channels."""
        try:
            req = event_dict.get("request")
            event = ApprovalEvent.from_request(
                req,
                event_type=event_dict.get("event_type", ""),
                channel=event_dict.get("channel", ""),
                user=event_dict.get("user", ""),
            )
            loop = asyncio.new_event_loop()
            try:
                if event_dict.get("event_type") == "created":
                    results = loop.run_until_complete(approval_fanout.fanout(event))
                else:
                    results = loop.run_until_complete(approval_fanout.fanout_update(event))
                if req is not None and hasattr(approval_manager, "record_surface_delivery"):
                    approval_manager.record_surface_delivery(req.approval_id, results)
            finally:
                loop.close()
        except Exception:
            logger.debug("Approval fanout failed", exc_info=True)

    approval_manager.on_state_change(_on_approval_state_change)

    policy_engine = PolicyEngine(approval_store=approval_store, data_dir=data_dir)

    capability_catalog = CapabilityCatalog(
        capabilities_dir=str(base_dir / "capabilities"),
        apps_dir=str(base_dir / "apps"),
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
    tool_broker = ToolBroker(
        registry=tool_registry,
        policy_engine=policy_engine,
        audit_log=audit_log,
        approval_queue=approval_queue,
        approval_manager=approval_manager,
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

    prompt_registry = PromptRegistry(str(base_dir / "config" / "prompts.yaml"))
    settings_resolver = LLMSettingsResolver(str(base_dir / "config" / "llm.yaml"))
    llm_gateway = LLMGateway(
        router=llm_router,
        settings_resolver=settings_resolver,
        prompt_registry=prompt_registry,
        audit_log=audit_log,
    )

    from aegis_ai.user_model import UserModelStore

    user_model_store = UserModelStore(data_dir=os.path.join(data_dir, "user_model"))

    context_builder = ContextBuilder(
        event_bus=event_bus,
        tool_broker=tool_broker,
        multimodal_llm=llm_gateway,
        capability_retriever=capability_retriever,
        settings_resolver=settings_resolver,
        user_model_store=user_model_store,
    )
    session_manager = SessionManager()
    interaction_router = InteractionRouter(
        llm_provider=llm_gateway,
        context_builder=context_builder,
        capability_catalog=capability_catalog,
        capability_retriever=capability_retriever,
        tool_broker=tool_broker,
        approval_store=approval_store,
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
    from aegis_ai.memory.action_trace import ActionTraceMemory
    from aegis_ai.memory.association_memory import AssociationMemory

    memory_dir = os.path.join(data_dir, "memory")
    advanced_memory = AdvancedMemory(data_dir=memory_dir, llm_provider=llm_gateway)
    episodic_memory = EpisodicMemory(path=os.path.join(memory_dir, "episodic.jsonl"))
    semantic_memory = SemanticMemory(path=os.path.join(memory_dir, "semantic.jsonl"))
    skill_memory = SkillMemory(path=os.path.join(memory_dir, "skills.jsonl"))
    lesson_memory = LessonMemory(path=os.path.join(memory_dir, "lessons.jsonl"))
    workflow_memory = WorkflowMemory(path=os.path.join(memory_dir, "workflows.jsonl"))
    experiential_memory = ExperientialMemory(data_dir=memory_dir, llm_provider=llm_gateway)
    person_memory = PersonMemory(path=os.path.join(memory_dir, "persons.jsonl"))

    event_manager = EventManager(event_bus=event_bus, data_dir=data_dir)
    audit_manager = AuditManager(audit_log=audit_log, data_dir=data_dir)
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
    context_builder._situation_model = situation_model
    context_builder._user_state_manager = user_state_manager
    context_builder._delegation_policy = delegation_policy
    context_builder._commitment_manager = commitment_manager
    from aegis_ai.integrations.android.manager import AndroidServerManager

    android_manager = AndroidServerManager(
        data_dir=data_dir,
        event_manager=event_manager,
        status_manager=status_manager,
        approval_manager=approval_manager,
    )
    server_executor.register_client("android-server", android_manager)

    from aegis_ai.integrations.room import RoomServerGrpcClient

    server_executor.register_client("room-server", RoomServerGrpcClient())

    from aegis_ai.integrations.dev import DevServerGrpcClient

    server_executor.register_client("dev-server", DevServerGrpcClient())

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
                "llm_provider": llm_gateway,
            },
        ),
    )

    from aegis_ai.approval.channels.android import AndroidApprovalChannel
    from aegis_ai.approval.channels.pc_overlay import PcOverlayApprovalChannel
    from aegis_ai.approval.channels.room import RoomApprovalChannel

    approval_fanout.register_channel(PcOverlayApprovalChannel(server_executor=server_executor))
    approval_fanout.register_channel(RoomApprovalChannel(server_executor=server_executor))
    approval_fanout.register_channel(AndroidApprovalChannel(android_manager=android_manager))

    execution_engine = TaskExecutionEngine(
        task_manager=task_manager,
        tool_broker=tool_broker,
        approval_manager=approval_manager,
        llm_gateway=llm_gateway,
        prompt_registry=prompt_registry,
        settings_resolver=settings_resolver,
    )

    interaction_router._task_manager = task_manager
    interaction_router._execution_engine = execution_engine

    approval_manager._task_manager = task_manager
    approval_manager._execution_engine = execution_engine
    approval_manager.on_state_change(approval_manager._task_manager_callback)

    memory_manager = MemoryManager(
        advanced_memory=advanced_memory,
        episodic_memory=episodic_memory,
        semantic_memory=semantic_memory,
        skill_memory=skill_memory,
        lesson_memory=lesson_memory,
        workflow_memory=workflow_memory,
        experiential_memory=experiential_memory,
        person_memory=person_memory,
        llm_gateway=llm_gateway,
        event_manager=event_manager,
    )
    from aegis_ai.personal_ai import RepairManager

    repair_manager = RepairManager(
        data_dir=personal_dir,
        tool_broker=tool_broker,
        audit_manager=audit_manager,
        memory_manager=memory_manager,
    )
    core_client = server_executor._clients.get("ai-server")
    if core_client is not None and hasattr(core_client, "_personal"):
        core_client._personal["memory_manager"] = memory_manager
        core_client._personal["repair_manager"] = repair_manager
    tool_broker.set_repair_manager(repair_manager)
    sleep_manager = SleepManager(
        memory_manager=memory_manager,
        event_manager=event_manager,
        audit_manager=audit_manager,
        llm_gateway=llm_gateway,
    )
    if core_client is not None and hasattr(core_client, "_personal"):
        core_client._personal["sleep_manager"] = sleep_manager

    try:
        pc_poll_interval = int(os.getenv("AEGIS_USER_STATE_PC_POLL_INTERVAL_SECONDS", "2"))
        user_state_manager.start_pc_poller(
            server_executor,
            status_manager=status_manager,
            interval_seconds=pc_poll_interval,
        )
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
        approval_store=approval_store,
        approval_queue=approval_queue,
        approval_manager=approval_manager,
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
        notification_manager=notification_manager,
        memory_manager=memory_manager,
        sleep_manager=sleep_manager,
        android_manager=android_manager,
        user_state_manager=user_state_manager,
        user_model_store=user_model_store,
        hook_engine=hook_engine,
        commitment_manager=commitment_manager,
        situation_model=situation_model,
        delegation_policy=delegation_policy,
        social_proxy=social_proxy,
        interruption_controller=interruption_controller,
        repair_manager=repair_manager,
        _lock=threading.RLock(),
    )
    runtime_ref["runtime"] = runtime
    runtime._dashboard_approval_channel = dashboard_approval_channel
    runtime._approval_fanout = approval_fanout
    status_manager.start_background_checks()
    hook_engine.start()
    return runtime


def _create_autonomous_loop(runtime: AegisRuntime) -> Any:
    from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
    from aegis_ai.autonomous.curiosity_exploration import CuriosityDrivenExplorationSystem
    from aegis_ai.autonomous.spontaneous_observation import SpontaneousObservationSystem
    from aegis_ai.desire.desire_system import DesireSystem
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
        audit_log=runtime.audit_log,
        task_manager=runtime.task_manager,
        status_manager=runtime.status_manager,
        settings_resolver=runtime.settings_resolver,
        data_dir=os.path.join(data_dir, "autonomous"),
        desire_threshold=4.0,
        max_tasks_per_cycle=max(1, min(4, settings.autonomous.max_autonomous_runs_per_hour)),
        fallback_interval_seconds=max(1, settings.autonomous.cooldown_seconds),
    )
    loop._capability_retriever = runtime.capability_retriever
    loop._min_execution_interval_ms = max(1, settings.autonomous.cooldown_seconds) * 1000

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
    from aegis_ai.health.alert_manager import HealthAlertManager

    loop.set_health_alert_manager(
        HealthAlertManager(
            data_dir=os.path.join(data_dir, "health"),
            tool_broker=runtime.tool_broker,
            llm_provider=runtime.llm_gateway,
            status_manager=runtime.status_manager,
            data_path=data_dir,
        )
    )

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
