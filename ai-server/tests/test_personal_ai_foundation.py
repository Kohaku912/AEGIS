from __future__ import annotations

from types import SimpleNamespace

from aegis_ai.context_builder import ContextBuilder
from aegis_ai.personal_ai.commitments import CommitmentManager
from aegis_ai.personal_ai.delegation import DelegationPolicyStore
from aegis_ai.personal_ai.hooks import HookEngine
from aegis_ai.personal_ai.interruption import InterruptionController
from aegis_ai.personal_ai.repair import RepairManager
from aegis_ai.personal_ai.situation import SituationModel
from aegis_ai.personal_ai.social_proxy import SocialProxy
from aegis_ai.core_capabilities import AegisCoreCapabilityClient
from aegis_ai.user_model import UserModelStore
from aegis_ai.capability_catalog import CapabilityCatalog
from aegis_ai.approval import ApprovalQueue
from aegis_schema.models import Capability, Event, EventPriority, RiskLevel, ServerType
from policy_engine import PolicyEngine
from server_executor import ServerExecutor
from tool_broker import InvokeStatus, ToolBroker, ToolExecutionRequest
from tool_registry import ToolRegistry


class FakeCatalog:
    def resolve(self, capability_id: str):
        return SimpleNamespace(capability_id=capability_id, risk_level="low", requires_approval=False)


class FakeBroker:
    def __init__(self, output, success=True, error=""):
        self.output = output
        self.success = success
        self.error = error
        self.calls = 0

    def execute(self, request):
        self.calls += 1
        return SimpleNamespace(success=self.success, output=self.output, error=self.error, status=SimpleNamespace(value="success" if self.success else "execution_error"))


class FakeManifest:
    def __init__(self, capability_id, server_id="ai-server", input_schema=None):
        self.capability_id = capability_id
        self.server_id = server_id
        self.input_schema = input_schema or {"type": "object", "properties": {}}


class FakeCatalogForExecutor:
    def __init__(self, server_id="ai-server"):
        self.server_id = server_id

    def resolve(self, capability_id: str):
        return FakeManifest(capability_id, server_id=self.server_id)


class FakeEventManager:
    def __init__(self):
        self.events = []
        self.subscribers = []

    def publish(self, event):
        self.events.append(event)
        return True

    def subscribe(self, handler, event_filter=None):
        self.subscribers.append(handler)
        return "sub"


class FakeLoop:
    def __init__(self):
        self.triggers = []

    def trigger(self, reason="", context=None):
        self.triggers.append({"reason": reason, "context": context or {}})
        return {"running": False}


def test_user_model_persists_and_context_builder_injects_relevant_context(tmp_path):
    store = UserModelStore(data_dir=str(tmp_path / "user_model"))
    store.update({
        "preferred_tone": "casual",
        "common_apps": ["Discord", "VS Code"],
        "long_term_goals": [{"title": "Improve AEGIS"}],
    })

    reloaded = UserModelStore(data_dir=str(tmp_path / "user_model"))
    situation = SituationModel(data_dir=str(tmp_path / "personal_ai"))
    situation.update_from_observation("test", {"app": "VS Code"})
    ctx = ContextBuilder(user_model_store=reloaded, situation_model=situation).build(triggering_query="VS Code")

    assert reloaded.get().preferred_tone == "casual"
    assert "common_app=VS Code" in ctx.dialogue_policy
    assert "Current situation:" in ctx.dialogue_policy


def test_hook_engine_only_triggers_autonomous_on_condition_match(tmp_path):
    events = FakeEventManager()
    loop = FakeLoop()
    broker = FakeBroker({"ok": True, "count": 1})
    engine = HookEngine(
        data_dir=str(tmp_path),
        tool_broker=broker,
        capability_catalog=FakeCatalog(),
        event_manager=events,
        autonomous_loop_getter=lambda: loop,
    )
    engine.upsert_hook({
        "hook_id": "h1",
        "name": "Count watch",
        "kind": "interval",
        "capability_id": "ai-server.workspace.list_files",
        "condition": {"path": "count", "op": "gt", "value": 10},
        "interval_seconds": 1,
        "cooldown_seconds": 0,
    })

    result = engine.run_due_once()[0]
    assert result["matched"] is False
    assert loop.triggers == []

    broker.output = {"ok": True, "count": 11}
    engine._hooks["h1"].next_run_ms = 0
    result = engine.run_due_once()[0]
    assert result["matched"] is True
    assert events.events[-1].event_type == "self_call"
    assert loop.triggers[-1]["reason"] == "Hook matched: Count watch"


def test_commitment_due_creates_hook_and_transition_auditable(tmp_path):
    hook_engine = HookEngine(data_dir=str(tmp_path), tool_broker=FakeBroker({"ok": True}), capability_catalog=FakeCatalog())
    manager = CommitmentManager(data_dir=str(tmp_path), hook_engine=hook_engine)

    item = manager.upsert_commitment({"title": "Check build", "due_at_ms": 1, "priority": "high"})
    assert item["related_hook_id"]
    hook = hook_engine.get_hook(item["related_hook_id"])
    assert hook is not None
    assert hook["capability_id"] == "ai-server.commitment.wakeup"

    transitioned = manager.transition(item["commitment_id"], "completed", reason="done")
    assert transitioned["status"] == "completed"


def test_delegation_policy_requires_approval_for_external_send_and_delete(tmp_path):
    store = DelegationPolicyStore(data_dir=str(tmp_path))

    send = store.evaluate("ai-server.social.send_approved", side_effects=["external_send"])
    delete = store.evaluate("dev-server.file.delete", side_effects=["delete"])
    read = store.evaluate("ai-server.workspace.read_file", side_effects=[])

    assert send.decision == "approval_required"
    assert delete.decision == "approval_required"
    assert read.decision == "no_match"


def test_tool_broker_applies_delegation_after_policy_allow(tmp_path):
    registry = ToolRegistry()
    cap = Capability(
        id="ai-server.social.create_draft",
        name="Create draft",
        description="Create a draft.",
        server_type=ServerType.AI,
        risk_level=RiskLevel.SAFE_ACTION,
        side_effects=["external_send"],
    )
    registry.register_capability(cap)
    broker = ToolBroker(
        registry=registry,
        policy_engine=PolicyEngine(data_dir=str(tmp_path)),
        delegation_policy=DelegationPolicyStore(data_dir=str(tmp_path)),
        catalog=SimpleNamespace(resolve=lambda cid: SimpleNamespace(capability_id=cid, input_schema={"type": "object", "properties": {}})),
    )

    result = broker.execute(ToolExecutionRequest(capability_id=cap.id, arguments={"body": "hello"}))

    assert result.status == InvokeStatus.APPROVAL_NEEDED
    assert result.policy_decision == "ASK_APPROVAL"


def test_social_proxy_send_requires_approved_marker(tmp_path):
    proxy = SocialProxy(data_dir=str(tmp_path))
    draft = proxy.create_draft(channel="discord", body="hello")

    blocked = proxy.send_approved(draft["draft_id"])
    allowed = proxy.send_approved(draft["draft_id"], approved=True, approval_id="appr_1")

    assert blocked["code"] == "APPROVAL_REQUIRED"
    assert allowed["code"] == "UNSUPPORTED_CHANNEL"


def test_social_send_e2e_requires_approval_then_executes_once(tmp_path):
    proxy = SocialProxy(data_dir=str(tmp_path / "personal_ai"))
    draft = proxy.create_draft(channel="discord", body="hello")
    server_executor = ServerExecutor()
    server_executor.set_catalog(FakeCatalogForExecutor("ai-server"))
    server_executor.register_client(
        "ai-server",
        AegisCoreCapabilityClient(
            data_dir=str(tmp_path),
            server_executor=server_executor,
            personal_managers={"social_proxy": proxy},
        ),
    )
    registry = ToolRegistry()
    cap = Capability(
        id="ai-server.social.send_approved",
        name="Send approved social draft",
        description="Send approved social draft.",
        server_type=ServerType.AI,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
        requires_approval=True,
        side_effects=["external_send"],
    )
    registry.register_capability(cap)
    queue = ApprovalQueue(data_dir=str(tmp_path / "approvals"))
    broker = ToolBroker(
        registry=registry,
        policy_engine=PolicyEngine(data_dir=str(tmp_path)),
        approval_queue=queue,
        server_executor=server_executor,
        catalog=FakeCatalogForExecutor("ai-server"),
    )

    first = broker.execute(ToolExecutionRequest(capability_id=cap.id, arguments={"draft_id": draft["draft_id"]}))
    assert first.status == InvokeStatus.APPROVAL_NEEDED
    queue.approve(first.approval_id)
    executed = broker.execute_approved(first.approval_id)
    duplicate = broker.execute_approved(first.approval_id)

    assert executed.status == InvokeStatus.EXECUTION_ERROR
    assert "not implemented" in executed.error
    assert duplicate.status == InvokeStatus.DENIED


def test_interruption_batches_low_priority_but_allows_approval(tmp_path):
    situation = SituationModel(data_dir=str(tmp_path))
    situation.update_from_observation("test", {"mode": "focus"})
    controller = InterruptionController(data_dir=str(tmp_path), situation_model=situation)

    low = controller.before_send({"notification_id": "n1", "category": "general", "severity": "info"})
    approval = controller.before_send({"notification_id": "n2", "category": "approval_required", "severity": "info"})

    assert low["decision"] == "batch_later"
    assert approval["decision"] == "send_now"
    assert controller.get_status()["batched_count"] == 1


def test_repair_manager_classifies_and_records_failures(tmp_path):
    manager = RepairManager(data_dir=str(tmp_path))

    auth = manager.record_failure(capability_id="x", error="token expired", status="failed")
    down = manager.record_failure(capability_id="x", error="connection refused", status="failed")

    assert auth["category"] == "auth"
    assert down["category"] == "server_down"
    assert len(manager.list_history()) >= 2


def test_hook_engine_dedupe_backoff_and_stop(tmp_path):
    events = FakeEventManager()
    loop = FakeLoop()
    broker = FakeBroker({"ok": True, "id": "same", "count": 10})
    engine = HookEngine(
        data_dir=str(tmp_path),
        tool_broker=broker,
        capability_catalog=FakeCatalog(),
        event_manager=events,
        autonomous_loop_getter=lambda: loop,
    )
    engine.upsert_hook({
        "hook_id": "h1",
        "name": "Dedupe watch",
        "kind": "interval",
        "capability_id": "ai-server.workspace.list_files",
        "condition": {"path": "count", "op": "gt", "value": 1},
        "dedupe_key": "id",
        "backoff_seconds": 2,
        "interval_seconds": 1,
        "cooldown_seconds": 0,
    })
    first = engine.run_due_once()[0]
    engine._hooks["h1"].next_run_ms = 0
    second = engine.run_due_once()[0]
    stopped = engine.stop_hook("h1", reason="test")

    assert first["matched"] is True
    assert second["dedupe_skipped"] is True
    assert len(loop.triggers) == 1
    assert stopped["enabled"] is False

    failing = HookEngine(data_dir=str(tmp_path / "fail"), tool_broker=FakeBroker({}, success=False, error="temporary timeout"), capability_catalog=FakeCatalog())
    failing.upsert_hook({
        "hook_id": "hf",
        "name": "Failing",
        "kind": "interval",
        "capability_id": "ai-server.workspace.list_files",
        "condition": {"path": "ok", "op": "eq", "value": True},
        "backoff_seconds": 2,
        "interval_seconds": 1,
    })
    failed = failing.run_due_once()[0]
    assert failed["backoff_seconds"] >= 2
    assert failing.get_hook("hf")["consecutive_failures"] == 1


def test_situation_model_accepts_structured_observation(tmp_path):
    situation = SituationModel(data_dir=str(tmp_path))
    state = situation.update_from_structured_observation(
        "android",
        {"device_type": "android", "activity": "meeting", "foreground_app": "Calendar", "focus_mode": True},
    )
    assert state["state"] == "focused"
    assert state["interruptibility"] == "important_only"
    assert state["structured_observation"]["device_type"] == "android"


def test_repair_manager_retry_and_rollback_strategy(tmp_path):
    class RetryBroker:
        def __init__(self):
            self.calls = []

        def execute(self, request):
            self.calls.append(request.capability_id)
            return SimpleNamespace(success=True, status=SimpleNamespace(value=InvokeStatus.SUCCESS.value), error="", output={"ok": True})

    broker = RetryBroker()
    manager = RepairManager(data_dir=str(tmp_path), tool_broker=broker)
    request = ToolExecutionRequest(
        capability_id="ai-server.workspace.read_file",
        risk_level=RiskLevel.READ_ONLY,
        metadata={"rollback_capability_id": "ai-server.workspace.list_files"},
    )
    failed = SimpleNamespace(success=False, status=SimpleNamespace(value=InvokeStatus.EXECUTION_ERROR.value), error="temporary timeout")
    repair = manager.maybe_retry(request, failed, max_attempts=1)
    rollback = manager.rollback(request, failed, reason="manual")

    assert repair["final_result"] == "recovered"
    assert rollback["attempted"] is True
    assert "ai-server.workspace.list_files" in broker.calls


def test_all_capability_manifests_have_operation_category():
    catalog = CapabilityCatalog(capabilities_dir="capabilities", apps_dir="apps")
    assert catalog.get_folder_registry().errors() == []
    assert all(m.operation_category for m in catalog.list_all())
