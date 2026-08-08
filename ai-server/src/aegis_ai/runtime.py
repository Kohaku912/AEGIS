"""Process-wide AEGIS runtime singleton.

All user-facing entry points share one AegisRuntime instance so they use the
same LLM router, tool broker, policy engine, event bus, registry, and audit log.
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
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
    verification_service: Any = None
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
        subscription = getattr(self, "_initiative_event_subscription", "")
        if subscription and self.event_manager is not None:
            try:
                self.event_manager.unsubscribe(subscription)
            except Exception:
                logger.debug("Failed to unsubscribe initiative event handler", exc_info=True)
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
            if event_manager is not None:
                from aegis_schema.models import Event

                event_manager.publish(
                    Event(
                        event_type=f"approval.{event_dict.get('event_type', 'updated')}",
                        source="approval_manager",
                        payload={
                            "approval_id": getattr(req, "approval_id", ""),
                            "capability_id": getattr(req, "capability_id", ""),
                            "task_id": getattr(req, "task_id", ""),
                            "state": getattr(req, "status", ""),
                        },
                    )
                )
        except Exception:
            logger.debug("Approval fanout failed", exc_info=True)

    approval_manager.on_state_change(_on_approval_state_change)

    policy_engine = PolicyEngine(approval_store=approval_store, data_dir=data_dir)

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
        approval_queue=approval_queue,
        approval_manager=approval_manager,
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
        if not is_production_mode():
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
    tool_broker.set_continuation_manager(continuation_manager)
    approval_manager.on_state_change(social_manager.handle_approval_event)
    approval_manager.on_state_change(continuation_manager.handle_approval_event)
    approval_manager.on_state_change(preference_store.handle_approval_event)

    def _record_initiative_approval_stage(event: dict[str, Any]) -> None:
        event_type = str(event.get("event_type") or "")
        request = event.get("request")
        detail = {
            "approval_id": str(event.get("approval_id") or ""),
            "capability_id": str(getattr(request, "capability_id", "") or ""),
            "channel": str(event.get("channel") or ""),
        }
        if event_type in {"approved", "rejected", "surface_rejected"}:
            initiative_engine.record_stage("user_acknowledged", detail)
        if event_type == "executed":
            initiative_engine.record_stage("actions_executed", detail)
            metadata = getattr(request, "metadata", {}) if request is not None else {}
            result = metadata.get("execution_result", {}) if isinstance(metadata, dict) else {}
            if str(result.get("verification_status") or "") == "passed":
                initiative_engine.record_stage("actions_verified", detail)

    approval_manager.on_state_change(_record_initiative_approval_stage)
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
                "social_manager": social_manager,
                "llm_provider": llm_gateway,
            },
        ),
    )

    from aegis_ai.approval.channels.android import AndroidApprovalChannel
    from aegis_ai.approval.channels.pc_overlay import PcOverlayApprovalChannel
    from aegis_ai.approval.channels.room import RoomApprovalChannel

    approval_fanout.register_channel(
        PcOverlayApprovalChannel(
            server_executor=server_executor,
            approval_manager=approval_manager,
        )
    )
    approval_fanout.register_channel(RoomApprovalChannel(server_executor=server_executor))
    approval_fanout.register_channel(AndroidApprovalChannel(android_manager=android_manager))

    verification_service._android = android_manager
    execution_engine = TaskExecutionEngine(
        task_manager=task_manager,
        tool_broker=tool_broker,
        approval_manager=approval_manager,
        llm_gateway=llm_gateway,
        prompt_registry=prompt_registry,
        settings_resolver=settings_resolver,
        verification_service=verification_service,
        event_manager=event_manager,
        audit_manager=audit_manager,
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
    )
    behavioral_evaluation.set_memory_manager(memory_manager)
    context_builder._agent_state = agent_state
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
    tool_broker.set_repair_manager(repair_manager)
    execution_engine._repair_manager = repair_manager
    sleep_manager = SleepManager(
        memory_manager=memory_manager,
        event_manager=event_manager,
        audit_manager=audit_manager,
        llm_gateway=llm_gateway,
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
        verification_service=verification_service,
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
        _lock=threading.RLock(),
    )
    runtime_ref["runtime"] = runtime

    immediate_event_types = {
        "social.inbox.received",
        "approval.approved",
        "approval.rejected",
        "task.completed",
        "task.failed",
        "status.changed",
        "commitment.due",
        "browser.discovery",
        "android.permission.changed",
    }
    # Debounce high-frequency Android activity noise (observe_more spam).
    _android_debounce_ms = int(os.environ.get("AEGIS_ANDROID_EVENT_DEBOUNCE_MS", "60000"))
    _last_android_trigger_ms: dict[str, int] = {}

    def _evaluate_immediate_event(event):
        event_type = str(getattr(event, "event_type", "") or "")
        if event_type not in immediate_event_types:
            return
        now_ms = int(time.time() * 1000)
        if event_type.startswith("android.user_activity") or event_type.startswith("android.foreground_app"):
            last = _last_android_trigger_ms.get(event_type, 0)
            if now_ms - last < _android_debounce_ms:
                return
            _last_android_trigger_ms[event_type] = now_ms
        payload = getattr(event, "payload", {})
        detail = dict(payload) if isinstance(payload, dict) else {}
        initiative_engine.record_trigger(event_type, detail)
        loop = getattr(runtime_ref.get("runtime"), "autonomous_loop", None)
        if loop is not None and hasattr(loop, "evaluate_event"):
            loop.evaluate_event(event_type, detail)

    runtime._initiative_event_subscription = event_manager.subscribe(  # type: ignore[attr-defined]
        _evaluate_immediate_event,
        lambda event: str(getattr(event, "event_type", "") or "") in immediate_event_types,
    )
    runtime._dashboard_approval_channel = dashboard_approval_channel
    runtime._approval_fanout = approval_fanout
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
        max_tasks_per_cycle=max(1, settings.autonomous.max_tasks_per_cycle),
        fallback_interval_seconds=max(1, settings.autonomous.evaluation_interval_seconds),
    )
    loop._capability_retriever = runtime.capability_retriever
    loop._min_execution_interval_ms = max(1, settings.autonomous.min_action_interval_seconds) * 1000
    loop._min_llm_interval_ms = max(1, settings.autonomous.min_llm_interval_seconds) * 1000
    loop._initiative_engine = runtime.initiative_engine
    loop._continuation_manager = runtime.continuation_manager
    loop._agent_state = runtime.agent_state
    loop._goal_service = runtime.goal_service
    loop._social_manager = runtime.social_manager
    loop._operation_store = getattr(runtime, "operation_store", None)
    loop._sleep_manager = runtime.sleep_manager
    loop._memory_manager = runtime.memory_manager

    loop.set_health_alert_manager(
        HealthAlertManager(
            data_dir=os.path.join(data_dir, "health"),
            tool_broker=runtime.tool_broker,
            llm_provider=runtime.llm_gateway,
            status_manager=runtime.status_manager,
            data_path=data_dir,
        )
    )
    if getattr(runtime, "approval_manager", None) is not None:
        if hasattr(loop, "set_approval_manager"):
            loop.set_approval_manager(runtime.approval_manager)
        else:
            loop._approval_manager = runtime.approval_manager

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
        "approval_manager": getattr(runtime, "approval_manager", None),
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
