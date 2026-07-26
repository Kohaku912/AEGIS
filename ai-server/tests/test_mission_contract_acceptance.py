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
from aegis_ai.personal_ai.delegation import DelegationPolicyStore
from aegis_ai.personal_ai.repair import RepairManager
from aegis_ai.task.execution_engine import TaskExecutionEngine
from aegis_ai.task.task_manager import TaskManager
from aegis_ai.task_plan import PlanStep, StepStatus, TaskPlan
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
    manager = TaskManager(data_dir=str(tmp_path))
    task = manager.create_task("Create report", goal="Verified report")
    manager.start_task(task["task_id"])
    engine = TaskExecutionEngine(task_manager=manager)
    plan = TaskPlan(
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
