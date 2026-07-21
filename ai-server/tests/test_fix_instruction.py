from __future__ import annotations

import asyncio
import importlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock


def test_agora_real_probe_requires_persisted_replied_post_id(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "e2e" / "agora-real-probe.py"
    spec = importlib.util.spec_from_file_location("agora_real_probe", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    inbox_path = tmp_path / "social_inbox.json"
    inbox_path.write_text(
        json.dumps(
            {
                "items": [
                    {"channel": "agora", "status": "awaiting_approval", "reply_id": ""},
                    {
                        "channel": "agora",
                        "status": "replied",
                        "reply_id": "post_42",
                        "updated_at": 2,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    evidence = module._reply_evidence(inbox_path)

    assert evidence["verified_reply_count"] == 1
    assert evidence["latest_reply_id"] == "post_42"


def test_autonomous_capability_options_include_approval_proposals(tmp_path: Path) -> None:
    from aegis_ai.capability_catalog import CapabilityCatalog
    from policy_engine import PolicyEngine
    from tool_broker import ToolBroker
    from tool_registry import ToolRegistry

    catalog = CapabilityCatalog("capabilities", "apps", data_dir=str(tmp_path))
    registry = ToolRegistry()
    for capability in catalog.to_tool_registry_capabilities():
        registry.register_capability(capability)
    broker = ToolBroker(
        registry=registry,
        policy_engine=PolicyEngine(data_dir=str(tmp_path)),
        catalog=catalog,
        folder_registry=catalog._cap_reg,
    )

    options = {item.capability_id: item for item in broker.list_autonomous_capability_options()}

    assert options["browser-server.page.read"].disposition.value == "execute_safe"
    assert options["browser-server.form.submit"].disposition.value == "propose_for_approval"
    assert options["ai-server.agora.post"].disposition.value == "propose_for_approval"


def test_initiative_engine_records_action_and_non_action(tmp_path: Path) -> None:
    from aegis_ai.autonomous.initiative_engine import InitiativeEngine
    from aegis_ai.autonomous.models import ActionCandidate, CapabilityDisposition

    engine = InitiativeEngine(str(tmp_path))
    useful = ActionCandidate(
        candidate_id="c1",
        goal="continue task",
        why_now="deadline",
        trigger="commitment.due",
        expected_benefit=0.9,
        urgency=0.8,
        relevance=0.8,
        risk=0.2,
        uncertainty=0.1,
        candidate_capabilities=["test.action"],
        requires_approval=True,
    )
    weak = ActionCandidate(
        candidate_id="c2",
        goal="optional",
        why_now="none",
        trigger="homeostatic",
        expected_benefit=0.1,
        risk=0.4,
        uncertainty=0.4,
        candidate_capabilities=["test.read"],
    )

    assert engine.evaluate(useful, CapabilityDisposition.PROPOSE_FOR_APPROVAL)[0].value == "propose_approval"
    assert engine.evaluate(weak, CapabilityDisposition.EXECUTE_SAFE)[0].value == "ignore_with_reason"
    diagnostics = InitiativeEngine(str(tmp_path)).diagnostics()
    assert diagnostics["funnel"]["approval_proposals_selected"] == 1
    assert diagnostics["no_action_reasons"]


def test_immediate_event_is_evaluated_without_calling_llm(tmp_path: Path) -> None:
    from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
    from aegis_ai.autonomous.initiative_engine import InitiativeEngine

    llm = MagicMock()
    loop = AutonomousLoop(llm_provider=llm, data_dir=str(tmp_path / "loop"))
    loop._initiative_engine = InitiativeEngine(str(tmp_path / "initiative"))

    result = loop.evaluate_event(
        "status.changed",
        {"server_id": "pc-server", "urgency": 0.8, "safe_message": "PC disconnected"},
    )

    assert result["queued"] is True
    assert result["decision"] == "observe_more"
    llm.generate.assert_not_called()
    assert loop._pending_actionable_observations[0]["source"] == "status.changed"


def test_continuation_survives_restart_and_tracks_approval(tmp_path: Path) -> None:
    from aegis_ai.autonomous.continuation_manager import ContinuationManager

    manager = ContinuationManager(str(tmp_path))
    record = manager.create(
        "reply to post",
        task_id="task_1",
        capability_id="ai-server.agora.post",
        source_desire="social",
        conversation_id="thread_1",
        stage="selected",
    )
    manager.advance(
        record.continuation_id,
        stage="awaiting_approval",
        state="open",
        approval_id="appr_1",
        waiting_for="user",
    )

    restored = ContinuationManager(str(tmp_path))
    assert restored.find_by_approval("appr_1").task_id == "task_1"
    restored.handle_approval_event({"approval_id": "appr_1", "event_type": "approved"})
    assert restored.find_by_approval("appr_1").stage == "approved"


def test_continuation_tracks_presentation_and_learning(tmp_path: Path, monkeypatch) -> None:
    import aegis_ai.runtime as runtime_module
    from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
    from aegis_ai.autonomous.continuation_manager import ContinuationManager

    continuation_manager = ContinuationManager(str(tmp_path / "continuations"))
    continuation = continuation_manager.create(
        "research a current failure",
        capability_id="browser-server.search.query",
        stage="verified",
        state="completed",
    )
    presentations: list[object] = []
    runtime = SimpleNamespace(
        presentation_manager=SimpleNamespace(present=lambda request: presentations.append(request)),
        situation_model=None,
    )
    monkeypatch.setattr(runtime_module, "get_runtime", lambda: runtime)

    loop = AutonomousLoop(data_dir=str(tmp_path / "loop"))
    loop._continuation_manager = continuation_manager
    loop._experiential = SimpleNamespace(record_experience=lambda **_kwargs: None)
    task = {
        "action": "Compare current verification evidence",
        "capability_id": "browser-server.search.query",
        "desire": "growth",
    }
    result = {
        "success": True,
        "result": "Compared three current sources and recorded the relevant evidence.",
        "full_output": {
            "continuation_id": continuation.continuation_id,
            "sources": ["source-1", "source-2", "source-3"],
        },
    }

    loop._present_autonomous_result(task, result)
    assert presentations
    assert presentations[0].metadata["continuation_id"] == continuation.continuation_id
    assert continuation_manager.get(continuation.continuation_id).stage == "presented"

    loop._record_experiences([task], [result])
    restored = ContinuationManager(str(tmp_path / "continuations")).get(continuation.continuation_id)
    assert restored is not None
    assert restored.stage == "learned"
    assert [entry["stage"] for entry in restored.history][-2:] == ["presented", "learned"]


def test_social_inbox_approval_to_verified_reply(tmp_path: Path) -> None:
    from aegis_ai.social.manager import SocialManager
    from tool_broker import InvokeStatus, ToolExecutionResult

    class Llm:
        def generate(self, **_kwargs):
            return SimpleNamespace(
                success=True,
                content=json.dumps(
                    {
                        "decision": "reply",
                        "reason": "A direct question warrants a response.",
                        "directed_to_aegis": True,
                        "mentions_user": False,
                        "question_detected": True,
                        "reply_expected": True,
                        "relevance": 0.9,
                        "urgency": 0.5,
                        "sentiment": "neutral",
                        "draft_body": "Thanks. Here is the answer.",
                    }
                ),
            )

    class Broker:
        def execute(self, request):
            self.request = request
            return ToolExecutionResult(
                request_id="req_1",
                status=InvokeStatus.APPROVAL_NEEDED,
                approval_id="appr_1",
            )

    cursors: list[int] = []
    broker = Broker()
    manager = SocialManager(data_dir=str(tmp_path), llm=Llm(), tool_broker=broker)
    manager.set_cursor_updater("agora", cursors.append)
    items = manager.ingest(
        "agora",
        [{"id": 41, "thread_id": 3, "author": "Kai", "body": "Could you explain?"}],
    )
    processed = manager.process_new_items(items)

    assert processed[0].status.value == "awaiting_approval"
    assert broker.request.capability_id == "ai-server.agora.post"
    assert cursors == []
    request = SimpleNamespace(
        metadata={
            "social_inbox_item_id": processed[0].item_id,
            "execution_result": {"ok": True, "post": {"id": 99}},
        }
    )
    manager.handle_approval_event({"request": request, "event_type": "executed"})

    restored = SocialManager(data_dir=str(tmp_path))
    assert restored.list_items()[0]["status"] == "replied"
    assert restored.list_items()[0]["reply_id"] == "99"
    assert cursors == [41]


def test_social_terminal_failure_advances_cursor(tmp_path: Path) -> None:
    from aegis_ai.social.manager import SocialManager

    cursors: list[int] = []
    manager = SocialManager(data_dir=str(tmp_path))
    manager.set_cursor_updater("agora", cursors.append)
    items = manager.ingest(
        "agora",
        [{"id": 42, "thread_id": 3, "author": "Kai", "body": "A message"}],
    )

    failed = manager.process_new_items(items)

    assert failed[0].status.value == "failed"
    assert failed[0].decision_reason == "LLM unavailable; social intent was not guessed."
    assert cursors == [42]
    status = manager.get_status()
    assert status["channels"]["agora"]["available"] is True
    assert status["channels"]["discord"]["available"] is False


def test_social_inbox_preserves_thread_and_relationship_context(tmp_path: Path) -> None:
    from aegis_ai.social.manager import SocialManager

    manager = SocialManager(data_dir=str(tmp_path))
    manager.set_relationship_provider(
        lambda item: {"person_id": "person_kai", "relationship": "collaborator"}
    )
    first = manager.ingest(
        "agora",
        [{"id": 50, "thread_id": 8, "author": "Kai", "body": "First turn"}],
    )[0]
    manager.triage(first.item_id)
    second = manager.ingest(
        "agora",
        [{"id": 51, "thread_id": 8, "author": "Kai", "body": "Second turn"}],
    )[0]

    manager.process_new_items([second])
    saved = next(
        item for item in manager.list_items() if item["external_message_id"] == "51"
    )

    assert saved["relationship"]["person_id"] == "person_kai"
    assert saved["conversation_context"]["recent_items"][0]["body"] == "First turn"


def test_autonomous_approval_is_a_waiting_state_not_execution_failure(tmp_path: Path) -> None:
    from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
    from tool_broker import InvokeStatus, ToolExecutionResult

    class Broker:
        def __init__(self) -> None:
            self.requests = []

        def execute(self, request):
            self.requests.append(request)
            return ToolExecutionResult(
                request_id=request.request_id,
                status=InvokeStatus.APPROVAL_NEEDED,
                approval_id="appr_waiting",
            )

    class Tasks:
        def __init__(self) -> None:
            self.waiting = []
            self.failed = []
            self.completed = []

        def create_task(self, **_kwargs):
            return {"task_id": "task_auto"}

        def start_task(self, _task_id):
            return None

        def wait_for_approval(self, task_id, approval_id, step_id=""):
            self.waiting.append((task_id, approval_id, step_id))

        def fail_task(self, task_id, error=""):
            self.failed.append((task_id, error))

        def complete_task(self, task_id, result_summary=""):
            self.completed.append((task_id, result_summary))

    broker = Broker()
    tasks = Tasks()
    loop = AutonomousLoop(
        tool_broker=broker,
        task_manager=tasks,
        data_dir=str(tmp_path / "loop"),
    )

    results = loop._execute_tasks(
        [
            {
                "desire": "social",
                "action": "Reply to a social obligation",
                "capability_id": "ai-server.agora.post",
                "arguments": {"body": "Draft", "thread_id": 1},
                "initiative_decision": "propose_approval",
            }
        ]
    )

    assert len(broker.requests) == 1
    assert results[0]["success"] is False
    assert results[0]["full_output"]["action_state"] == "awaiting_approval"
    assert tasks.waiting == [("task_auto", "appr_waiting", "")]
    assert tasks.failed == []
    assert tasks.completed == []


def test_pc_overlay_requires_real_delivery_ack() -> None:
    from aegis_ai.approval.channels.pc_overlay import PcOverlayApprovalChannel
    from aegis_ai.approval.fanout import ApprovalEvent

    event = ApprovalEvent(
        approval_id="appr_1",
        event_type="created",
        request_summary={"title": "Approval", "body": "Review action"},
        state="pending",
    )
    executor = MagicMock()
    channel = PcOverlayApprovalChannel(executor)

    executor.execute_capability.return_value = {"error": "unreachable"}
    assert asyncio.run(channel.deliver(event)) is False
    executor.execute_capability.return_value = {
        "ok": True,
        "shown": True,
        "delivery_id": "delivery_1",
    }
    assert asyncio.run(channel.deliver(event)) is True


def test_approval_surface_delivery_evidence_is_persisted(tmp_path: Path) -> None:
    from aegis_ai.approval.approval_manager import ApprovalManager
    from aegis_ai.approval.approval_queue import ApprovalQueue
    from aegis_schema.models import RiskLevel
    from policy_engine import PolicyDecision, PolicyResult
    from tool_broker import ExecutionSource, ToolExecutionRequest

    manager = ApprovalManager(ApprovalQueue(data_dir=str(tmp_path / "approvals")))
    request = ToolExecutionRequest(
        capability_id="pc-server.app.show_url",
        arguments={
            "url": "https://example.test",
            "viewer": "user_visible",
            "purpose": "present",
        },
        source=ExecutionSource.AUTONOMOUS,
    )
    approval = manager.create_request(
        request,
        PolicyResult(
            decision=PolicyDecision.ASK_APPROVAL,
            reason="User-visible handoff requires approval",
            capability_id=request.capability_id,
            risk_level=RiskLevel.APPROVAL_REQUIRED,
        ),
    )

    manager.record_surface_delivery(
        approval.approval_id,
        {"dashboard": True, "pc_overlay": False, "android": True},
    )

    restored = ApprovalManager(ApprovalQueue(data_dir=str(tmp_path / "approvals")))
    evidence = restored.get(approval.approval_id).surface_delivery_evidence
    assert evidence["dashboard"]["attempted"] is True
    assert evidence["pc_overlay"]["failed"] is True
    assert evidence["pc_overlay"]["last_error"] == "delivery failed"
    assert evidence["android"]["delivered"] is True


def test_browser_capabilities_are_split_and_bounded() -> None:
    from aegis_ai.capability_catalog import CapabilityCatalog

    catalog = CapabilityCatalog("capabilities", "apps")
    read = catalog.resolve("browser-server.page.read")
    submit = catalog.resolve("browser-server.form.submit")
    upload = catalog.resolve("browser-server.file.upload")

    assert read is not None and read.requires_approval is False
    assert submit is not None and submit.requires_approval is True
    assert upload is not None and upload.requires_approval is True
    for manifest in (read, submit, upload):
        required = set(manifest.input_schema.get("required", []))
        assert {"viewer", "purpose", "success_condition", "stop_condition"} <= required
        assert catalog._exec_reg.get(manifest) is not None


def test_shared_browser_session_returns_structured_device_handoff(
    monkeypatch,
) -> None:
    browser_src = Path(__file__).resolve().parents[2] / "browser-server" / "src"
    sys.path.insert(0, str(browser_src))
    try:
        browser_main = importlib.import_module("aegis_browser.main")
        fake_result = SimpleNamespace(
            status=SimpleNamespace(name="COMPLETED"),
            result_text="Research complete",
            extracted_data={"source_count": 2},
            duration_ms=12,
            error=None,
            needs_user_input_for=None,
        )
        monkeypatch.setattr(
            browser_main,
            "get_browser_agent",
            lambda: SimpleNamespace(run_task=lambda _task: fake_result),
        )
        handler = object.__new__(browser_main.BrowserHandler)

        result = handler._handle_capability(
            "page.read",
            {
                "task": "Read the selected source",
                "viewer": "shared",
                "purpose": "collaborative_review",
                "success_condition": "Relevant evidence is extracted",
                "stop_condition": "Two sources have been compared",
                "handoff_url": "https://example.test/review",
            },
        )

        assert result["status"] == "COMPLETED"
        assert result["handoff"] == {
            "required": True,
            "viewer": "user_visible",
            "kind": "show_url",
            "preferred_server_ids": ["pc-server", "android-server"],
            "url": "https://example.test/review",
            "purpose": "collaborative_review",
            "source_operation": "page.read",
        }
    finally:
        sys.path.remove(str(browser_src))


def test_presentation_routing_uses_structured_situation() -> None:
    from aegis_ai.presentation.routing_policy import (
        PresentationRoutingContext,
        PresentationRoutingPolicy,
    )

    policy = PresentationRoutingPolicy()
    normal = policy.decide(PresentationRoutingContext())
    mobile_approval = policy.decide(
        PresentationRoutingContext(
            importance="high",
            requires_action=True,
            user_presence="away",
            active_device="android",
        )
    )
    private = policy.decide(
        PresentationRoutingContext(
            urgency="critical",
            privacy="sensitive",
            active_device="pc",
        )
    )

    assert normal.targets == ("dashboard",)
    assert mobile_approval.targets[0] == "android"
    assert private.targets == ("pc",)
    assert private.display_eligible is False


def test_exploration_agenda_requires_grounding_and_two_sources(tmp_path: Path) -> None:
    import pytest

    from aegis_ai.autonomous.exploration_agenda import ExplorationAgenda

    agenda = ExplorationAgenda(str(tmp_path))
    with pytest.raises(ValueError):
        agenda.add("random topic", "question")
    item = agenda.add(
        "verification reliability",
        "failure",
        related_failure="task_1",
        question="Why did verification fail?",
        why_now="A current task failed.",
    )
    with pytest.raises(ValueError):
        agenda.record_result(
            item.agenda_id,
            sources=["one"],
            what_was_learned="",
            source_quality={},
            what_changed="",
            next_question="",
            stop_reason="budget",
            verification={},
            budgets={},
        )


def test_grounded_exploration_uses_private_browser_and_records_sources(tmp_path: Path) -> None:
    from aegis_ai.autonomous.curiosity_exploration import (
        CuriosityDrivenExplorationSystem,
        ExplorationCandidate,
    )
    from aegis_ai.autonomous.exploration_agenda import ExplorationAgenda
    from tool_broker import InvokeStatus, ToolExecutionResult

    manifest = SimpleNamespace(
        capability_id="browser-server.search.query",
        server_id="browser-server",
        app_id="search",
        enabled=True,
        side_effects=[],
    )

    class Broker:
        def __init__(self) -> None:
            self._catalog = SimpleNamespace(list_all=lambda: [manifest])
            self.requests = []

        def execute(self, request):
            self.requests.append(request)
            return ToolExecutionResult(
                status=InvokeStatus.SUCCESS,
                output={
                    "status": "COMPLETED",
                    "data": {
                        "sources": [
                            {"url": "https://source-one.test"},
                            {"url": "https://source-two.test"},
                        ],
                        "findings": "Both sources support the operational conclusion.",
                        "source_quality": {"independent": True},
                    },
                },
                verification_status="passed",
            )

    class Llm:
        def generate(self, **_kwargs):
            return SimpleNamespace(
                success=True,
                content=json.dumps(
                    {
                        "findings": "The comparison changed the implementation choice.",
                        "new_knowledge": ["Two independent sources agree."],
                        "new_questions": ["Can the result be reproduced locally?"],
                    }
                ),
            )

    agenda = ExplorationAgenda(str(tmp_path / "agenda"))
    item = agenda.add(
        "verification reliability",
        "failure",
        related_failure="task_1",
        question="Why did verification fail?",
        why_now="A current task failed.",
    )
    broker = Broker()
    system = CuriosityDrivenExplorationSystem(
        llm=Llm(),
        tool_broker=broker,
        data_dir=str(tmp_path / "autonomous"),
    )
    system._agenda = agenda
    candidate = ExplorationCandidate(
        candidate_id="candidate_1",
        topic="verification reliability",
        description="A current task failed.",
        source="failure",
        grounding={"related_failure": "task_1"},
        agenda_id=item.agenda_id,
    )

    result = system.explore(candidate)

    assert result.success is True
    assert len(result.sources) == 2
    assert broker.requests[0].arguments["viewer"] == "agent_private"
    assert agenda.list()[0]["status"] == "completed"
    assert agenda.list()[0]["stop_reason"] == "success_condition_met"


def test_conditional_preferences_keep_context(tmp_path: Path) -> None:
    from aegis_ai.personal_ai.preference_learning import ConditionalPreferenceStore

    store = ConditionalPreferenceStore(str(tmp_path))
    store.record(
        "dismissed",
        target="autonomous_result",
        time_bucket="night",
        content_type="research",
        risk_level="low",
        surface="pc",
    )
    evidence = ConditionalPreferenceStore(str(tmp_path)).list()
    assert evidence[0]["confidence"] < 1.0
    assert evidence[0]["conditions"]["time_bucket"] == "night"
    assert evidence[0]["conditions"]["surface"] == "pc"

    store.handle_approval_event(
        {
            "event_type": "modified",
            "channel": "dashboard",
            "request": SimpleNamespace(
                capability_id="browser-server.social.post",
                tool_name="social.post",
                risk_level="approval_required",
                approval_id="appr_edit",
                source="autonomous",
                source_desire="social",
            ),
        }
    )
    assert store.list()[-1]["feedback"] == "edited"


def test_daily_plan_is_grounded_in_commitments_and_continuations(tmp_path: Path) -> None:
    from aegis_ai.personal_ai.daily_planning import DailyPlanningManager

    class Llm:
        def generate(self, **kwargs):
            self.prompt = kwargs["prompt"]
            return SimpleNamespace(
                success=True,
                content=json.dumps(
                    {
                        "summary": "Finish the open commitment first.",
                        "items": [
                            {
                                "goal": "Finish report",
                                "why_today": "Commitment is open",
                                "source_id": "commitment_1",
                                "next_action": "Review current draft",
                                "requires_approval": False,
                                "success_condition": "Draft is reviewed",
                                "stop_condition": "Stop after review",
                            }
                        ],
                    }
                ),
            )

    llm = Llm()
    manager = DailyPlanningManager(
        str(tmp_path),
        llm=llm,
        commitment_manager=SimpleNamespace(
            list_commitments=lambda status: [
                {"commitment_id": "commitment_1", "status": status, "title": "Finish report"}
            ]
        ),
        continuation_manager=SimpleNamespace(
            list_open=lambda: [{"continuation_id": "cont_1", "goal": "Review draft"}]
        ),
    )

    plan = manager.generate("2026-07-19")

    assert plan["commitment_ids"] == ["commitment_1"]
    assert plan["continuation_ids"] == ["cont_1"]
    assert "commitment_1" in llm.prompt
    assert DailyPlanningManager(str(tmp_path)).get("2026-07-19") == plan


def test_presentation_feedback_updates_conditional_preferences(tmp_path: Path) -> None:
    from aegis_ai.personal_ai.preference_learning import ConditionalPreferenceStore
    from aegis_ai.presentation.device_router import DashboardAdapter, DeviceRouter
    from aegis_ai.presentation.manager import PresentationManager
    from aegis_ai.presentation.models import PresentationRequest
    from aegis_ai.presentation.object_store import PresentationObjectStore

    preferences = ConditionalPreferenceStore(str(tmp_path / "preferences"))
    manager = PresentationManager(
        object_store=PresentationObjectStore(data_dir=str(tmp_path)),
        device_router=DeviceRouter(dashboard_adapter=DashboardAdapter()),
        conditional_preference_store=preferences,
        data_dir=str(tmp_path),
    )
    result = manager.present(
        PresentationRequest(
            source="autonomous_loop",
            intent="research_result",
            title="Research result",
            summary="Two sources compared",
            content={"text": "Evidence"},
            targets=["dashboard"],
        )
    )
    presentation_id = result["presentation"]["presentation_id"]

    manager.user_action(presentation_id, {"type": "open"})
    manager.dismiss(presentation_id)

    evidence = preferences.list()
    assert [item["feedback"] for item in evidence] == ["opened", "dismissed"]
    assert evidence[0]["conditions"]["target"] == "research_result"
