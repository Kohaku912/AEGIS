from __future__ import annotations

from types import SimpleNamespace

from aegis_ai.context_builder import ContextBuilder
from aegis_ai.personal_ai.commitments import CommitmentManager
from aegis_ai.personal_ai.delegation import DelegationPolicyStore
from aegis_ai.personal_ai.hooks import HookEngine
from aegis_ai.personal_ai.interruption import InterruptionController
from aegis_ai.personal_ai.repair import RepairManager
from aegis_ai.personal_ai.situation import SituationModel
from aegis_ai.user_model import UserModelStore
from aegis_schema.models import Capability, Event, EventPriority, RiskLevel, ServerType
from policy_engine import PolicyEngine
from tool_broker import InvokeStatus, ToolBroker, ToolExecutionRequest
from tool_registry import ToolRegistry


class FakeCatalog:
    def resolve(self, capability_id: str):
        return SimpleNamespace(capability_id=capability_id, risk_level="low", requires_approval=False)


class FakeBroker:
    def __init__(self, output):
        self.output = output
        self.calls = 0

    def execute(self, request):
        self.calls += 1
        return SimpleNamespace(success=True, output=self.output, error="", status=SimpleNamespace(value="success"))


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
    assert hook_engine.get_hook(item["related_hook_id"]) is not None

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
