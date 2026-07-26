"""Behaviour acceptance tests for the executable AEGIS mission contract."""

from __future__ import annotations

from types import SimpleNamespace

from aegis_ai.agency import (
    DEFAULT_MISSION_CONTRACT,
    AgentState,
    GoalGraph,
    GoalLifecycleService,
    GoalOutcome,
    GoalVerification,
)
from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
from aegis_ai.evaluation.behavioral import BehavioralEvaluation
from aegis_ai.llm_task_interpreter import LLMTaskInterpreter
from aegis_ai.personal_ai.delegation import DelegationPolicyStore
from aegis_ai.personal_ai.repair import RepairManager
from aegis_ai.task.execution_engine import TaskExecutionEngine
from aegis_ai.task.task_manager import TaskManager
from aegis_ai.task_plan import PlanStep, RiskCategory, StepStatus, TaskPlan
from aegis_schema.models import RiskLevel
from tool_broker import InvokeStatus, ToolExecutionRequest


class _Commitments:
    def list_commitments(self, status: str = ""):
        assert status == "open"
        return [
            {
                "commitment_id": "commit_1",
                "title": "Deliver the promised report",
                "status": "open",
                "priority": "high",
                "due_at_ms": 200,
            }
        ]


class _Social:
    def list_items(self, status: str = "", limit: int = 200):
        return [
            {
                "item_id": "social_1",
                "author": "Sam",
                "body": "Can you confirm the result?",
                "status": "received",
                "urgency": 0.9,
                "received_at": 100,
            }
        ]


class _Repair:
    def list_history(self, limit: int = 50):
        return [
            {
                "repair_id": "incident_1",
                "category": "server_down",
                "error": "Primary service unavailable",
                "timestamp": 300,
                "final_result": "not_retryable",
            }
        ][-limit:]


def _goal_graph() -> GoalGraph:
    return GoalGraph(
        goal_id="goal_1",
        outcome=GoalOutcome(
            description="A report exists",
            success_condition="The report is verified",
            value_to_user="The promise is fulfilled",
        ),
        obligation_ids=["commit_1"],
        verification=[
            GoalVerification(
                verification_id="verify_1",
                criterion="Report generation completed",
                linked_step_ids=["step_1"],
            )
        ],
        presentation={"report_when": "terminal", "audience": "user"},
    )


def test_contract_defines_human_reliability_acceptance_cases():
    case_ids = {item.case_id for item in DEFAULT_MISSION_CONTRACT.acceptance_cases}
    assert {
        "remember_commitment",
        "adapt_to_events",
        "finish_outcome",
        "situational_restraint",
        "repair_method",
        "apply_correction",
        "delegation_boundary",
    }.issubset(case_ids)


def test_agent_state_prioritizes_incident_commitment_then_social():
    state = AgentState(
        commitment_manager=_Commitments(),
        social_manager=_Social(),
        repair_manager=_Repair(),
    )

    snapshot = state.snapshot("What should I do next?")

    assert [item.kind for item in snapshot.obligations] == [
        "incident",
        "commitment",
        "social_obligation",
    ]
    assert snapshot.obligations[1].obligation_id == "commit_1"


def test_goal_graph_round_trip_keeps_outcome_verification_and_presentation():
    plan = TaskPlan(
        plan_id="plan_1",
        user_goal="Create the report",
        goal_graph=_goal_graph(),
        steps=[
            PlanStep(
                step_id="step_1",
                description="Create report",
                status=StepStatus.COMPLETED,
            )
        ],
    )

    restored = TaskPlan.from_dict(plan.to_dict())

    assert restored.goal_graph is not None
    assert restored.goal_graph.outcome.success_condition == "The report is verified"
    assert restored.goal_graph.presentation["audience"] == "user"


def test_task_cannot_complete_until_goal_level_verification_passes(tmp_path):
    class Verifier:
        def generate(self, **_kwargs):
            return SimpleNamespace(
                success=True,
                content=(
                    '{"status":"achieved","reason":"Outcome exists",'
                    '"evidence":["independent report inspection"]}'
                ),
            )

    manager = TaskManager(data_dir=str(tmp_path))
    task = manager.create_task("Create report", goal="Verified report")
    manager.start_task(task["task_id"])
    service = GoalLifecycleService(task_manager=manager, llm_gateway=Verifier())
    engine = TaskExecutionEngine(task_manager=manager, goal_service=service)
    plan = TaskPlan(
        user_goal="Verified report",
        goal_graph=_goal_graph(),
        steps=[
            PlanStep(
                step_id="step_1",
                description="Create report",
                status=StepStatus.COMPLETED,
            )
        ],
    )

    engine.apply_task_state(task["task_id"], plan)

    saved = manager.get_task(task["task_id"])
    assert saved["status"] == "completed"
    assert saved["goal_graph"]["verification"][0]["status"] == "passed"
    assert saved["goal_graph"]["verification"][0]["evidence"] == [
        "independent report inspection"
    ]


def test_completed_steps_without_independent_outcome_evidence_pause_goal(tmp_path):
    manager = TaskManager(data_dir=str(tmp_path))
    task = manager.create_task("Create report", goal="Verified report")
    manager.start_task(task["task_id"])
    engine = TaskExecutionEngine(task_manager=manager)
    plan = TaskPlan(
        user_goal="Verified report",
        goal_graph=_goal_graph(),
        steps=[
            PlanStep(
                step_id="step_1",
                description="Create report",
                status=StepStatus.COMPLETED,
                result={"tool_success": True},
            )
        ],
    )

    engine.apply_task_state(task["task_id"], plan)

    saved = manager.get_task(task["task_id"])
    assert saved["status"] == "paused"
    assert saved["goal_graph"]["verification"][0]["status"] == "pending"
    assert saved["goal_graph"]["verification"][0]["evidence"]


def test_malformed_goal_contract_is_not_marked_complete(tmp_path):
    manager = TaskManager(data_dir=str(tmp_path))
    task = manager.create_task("Unknown outcome")
    manager.start_task(task["task_id"])
    engine = TaskExecutionEngine(task_manager=manager)
    plan = TaskPlan(
        goal_graph=GoalGraph(goal_id="invalid"),
        steps=[PlanStep(step_id="step_1", status=StepStatus.COMPLETED)],
    )

    engine.apply_task_state(task["task_id"], plan)

    saved = manager.get_task(task["task_id"])
    assert saved["status"] == "failed"
    assert "Mission contract violation" in saved["error"]


def test_delegation_uses_declared_dimensions_not_capability_words(tmp_path):
    policy = DelegationPolicyStore(data_dir=str(tmp_path))

    public = policy.evaluate(
        "neutral.capability.execute",
        operation_context={
            "operation_category": "general",
            "scope": "external",
            "audience": "public",
            "content_sensitivity": "normal",
            "reversibility": "irreversible",
        },
    )
    private = policy.evaluate(
        "looks.like.delete.but.is.declared.safe",
        operation_context={
            "operation_category": "general",
            "scope": "aegis",
            "audience": "private",
            "content_sensitivity": "normal",
            "reversibility": "reversible",
        },
    )

    assert public.decision == "approval_required"
    assert public.dimensions["audience"] == "public"
    assert private.decision == "no_match"


def test_chat_goal_is_completed_only_after_llm_outcome_verification(tmp_path):
    class Verifier:
        def generate(self, **_kwargs):
            return SimpleNamespace(
                success=True,
                content=(
                    '{"status":"achieved","reason":"Requested result was delivered","evidence":["verified output"]}'
                ),
            )

    manager = TaskManager(data_dir=str(tmp_path))
    service = GoalLifecycleService(task_manager=manager, llm_gateway=Verifier())
    task = service.create_chat_task("Provide the verified result")

    evaluation = service.finalize_chat_task(
        task["task_id"],
        user_goal="Provide the verified result",
        response="The verified result is ready.",
        tool_results=[{"success": True, "result": "verified output"}],
    )

    saved = manager.get_task(task["task_id"])
    assert evaluation.status == "achieved"
    assert saved["status"] == "completed"
    assert saved["goal_graph"]["verification"][0]["status"] == "passed"


def test_repeated_repair_changes_from_retry_to_escalation(tmp_path):
    class FailingBroker:
        def __init__(self):
            self.calls = 0

        def execute(self, _request):
            self.calls += 1
            return SimpleNamespace(
                success=False,
                status=SimpleNamespace(value=InvokeStatus.EXECUTION_ERROR.value),
                error="temporary timeout",
            )

    broker = FailingBroker()
    manager = RepairManager(data_dir=str(tmp_path), tool_broker=broker)
    request = ToolExecutionRequest(
        capability_id="ai-server.workspace.read_file",
        risk_level=RiskLevel.READ_ONLY,
    )
    failure = SimpleNamespace(
        success=False,
        status=SimpleNamespace(value=InvokeStatus.EXECUTION_ERROR.value),
        error="temporary timeout",
    )

    first = manager.maybe_retry(request, failure, max_attempts=2)
    second = manager.maybe_retry(request, failure, max_attempts=2)

    assert first["strategy"]["method"] == "retry_once"
    assert len(first["attempts"]) == 1
    assert second["strategy"]["method"] == "rollback_or_escalate"
    assert second["attempts"] == []
    assert second["final_result"] == "needs_followup"


def test_new_events_change_the_shared_decision_context():
    class Situation:
        def __init__(self):
            self.state = {"activity": "focused"}

        def get_state(self):
            return dict(self.state)

    situation = Situation()
    state = AgentState(situation_model=situation)
    before = state.snapshot("plan")
    situation.state = {"activity": "away", "new_event": "meeting_started"}
    after = state.snapshot("plan")

    assert before.situation != after.situation
    assert after.situation["new_event"] == "meeting_started"


def test_learning_opinion_conversation_and_correction_return_to_decisions():
    class Identity:
        def to_context_string(self):
            return "Identity"

        def get_recent_learning(self, limit=20):
            return [{"topic": "deploy", "summary": "Verify after restart"}][-limit:]

        def get_learned_opinions(self, limit=50):
            return [
                {
                    "topic": "reliability",
                    "position": "Outcome checks matter",
                    "evidence": "incident review",
                }
            ][-limit:]

    class Memory:
        def __init__(self):
            self.applied = []

        def get_decision_context_memory(self, limit=20):
            return {
                "learnings": [{"memory_id": "lesson_1", "content": "Change method"}],
                "conversations": [
                    {"user_msg": "Remember the promise", "bot_msg": "I will."}
                ],
                "corrections": [
                    {
                        "memory_id": "correction_1",
                        "title": "Corrected deadline",
                        "content": "Friday",
                    }
                ],
            }

        def mark_corrections_applied(self, memory_ids, context_id):
            self.applied.append((memory_ids, context_id))

    memory = Memory()
    decision = AgentState(identity=Identity(), memory_manager=memory).snapshot("next")

    assert len(decision.learnings) == 2
    assert decision.opinions[0]["position"] == "Outcome checks matter"
    assert decision.conversations[0]["user_msg"] == "Remember the promise"
    assert decision.corrections[0]["memory_id"] == "correction_1"
    assert decision.decision_evidence[0]["kind"] == "correction_applied"
    assert memory.applied[0][0] == ["correction_1"]


def test_behavioral_evaluation_counts_active_goals_and_correction_reflection(tmp_path):
    class Diagnostics:
        def diagnostics(self):
            return {"records": [], "funnel": {}}

    class SocialStatus:
        def get_status(self):
            return {"counts": {}, "total": 0}

    correction = SimpleNamespace(
        source="user_correction",
        tags=["correction"],
        structured_data={"applied_count": 1},
    )
    store = SimpleNamespace(list_recent=lambda limit=5000: [correction])
    memory = SimpleNamespace(get_backend=lambda name: store if name == "store" else None)
    tasks = TaskManager(data_dir=str(tmp_path))
    tasks.create_task(
        "Open goal",
        goal_graph=_goal_graph().to_dict(),
    )
    evaluator = BehavioralEvaluation(
        initiative_engine=Diagnostics(),
        continuation_manager=Diagnostics(),
        social_manager=SocialStatus(),
        task_manager=tasks,
        memory_manager=memory,
    )

    snapshot = evaluator.snapshot()

    assert snapshot["goal_achievement"] == 0.0
    assert snapshot["goal_terminal_rate"] == 0.0
    assert snapshot["correction_reflection"] == 1.0


def test_payment_is_approval_scoped_not_permanently_blocked():
    interpreter = LLMTaskInterpreter()
    plan = TaskPlan(
        steps=[
            PlanStep(
                step_id="pay",
                risk_category=RiskCategory.PAYMENT,
                delegation_context={
                    "operation_category": "payment",
                    "scope": "external",
                    "audience": "third_party",
                    "content_sensitivity": "personal",
                    "reversibility": "difficult",
                },
            )
        ]
    )

    interpreter._validate_safety(plan)

    assert plan.steps[0].risk_category == RiskCategory.PAYMENT
    assert plan.steps[0].requires_approval is True
    assert plan.approval_needed is True


def test_financial_service_scope_requires_approval_instead_of_deny(tmp_path):
    from aegis_ai.permissions.service_permission_store import ServicePermissionStore

    store = ServicePermissionStore(path=str(tmp_path / "permissions.json"))

    decision = store.explain_decision("browser", "purchase")

    assert decision.decision == "ask_approval"
    assert decision.requires_approval is True


def test_autonomous_tasks_are_goal_owned_and_require_manifest_verification(tmp_path):
    class Broker:
        def __init__(self, verification_status):
            self.verification_status = verification_status

        def execute(self, _request):
            return SimpleNamespace(
                success=True,
                output={"result": "observable result"},
                verification_status=self.verification_status,
                verification=SimpleNamespace(evidence=["manifest check"]),
            )

    manager = TaskManager(data_dir=str(tmp_path / "tasks"))
    loop = AutonomousLoop(
        tool_broker=Broker("pending"),
        task_manager=manager,
        data_dir=str(tmp_path / "loop"),
    )
    loop._goal_service = GoalLifecycleService(task_manager=manager, llm_gateway=None)
    task = {
        "desire": "user_support",
        "action": "Advance report goal",
        "goal": "The promised report exists",
        "success_condition": "Manifest verification passes",
        "obligation_ids": ["commit_1"],
        "presentation": {"report_when": "terminal", "audience": "agent_private"},
        "capability_id": "ai-server.workspace.read_file",
        "arguments": {},
    }

    pending_result = loop._execute_tasks([task])
    pending_task = manager.list_tasks(limit=1)[0]

    assert pending_result[0]["goal_status"] == "needs_followup"
    assert pending_task["status"] == "paused"
    assert pending_task["goal_graph"]["obligation_ids"] == ["commit_1"]

    loop._broker = Broker("passed")
    achieved_result = loop._execute_tasks([task])
    achieved_task = manager.list_tasks(limit=1)[0]

    assert achieved_result[0]["goal_status"] == "achieved"
    assert achieved_task["status"] == "completed"
    assert achieved_task["goal_graph"]["verification"][0]["status"] == "passed"


def test_interrupted_task_becomes_first_class_incident(tmp_path):
    manager = TaskManager(data_dir=str(tmp_path))
    task = manager.create_task("In progress", goal="Finish work")
    manager.start_task(task["task_id"])

    recovered = TaskManager(data_dir=str(tmp_path))
    saved = recovered.get_task(task["task_id"])
    decision = AgentState(task_manager=recovered).snapshot("what next")

    assert saved["status"] == "failed"
    assert saved["incident_status"] == "open"
    assert decision.obligations[0].kind == "incident"
    assert decision.obligations[0].obligation_id == task["task_id"]
