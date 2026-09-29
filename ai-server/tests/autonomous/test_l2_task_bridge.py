from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from aegis_ai.autonomous import L2Action, L2ActionType, L2AutonomousMind, L2Context, L2Decision


@dataclass
class _FakeTaskManager:
    created: list[dict[str, Any]]

    def __init__(self) -> None:
        self.created = []

    def create_task(
        self,
        title: str,
        goal: str = "",
        source: str = "system",
        priority: int = 0,
        parent_task_id: str = "",
        goal_graph: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        task = {"task_id": f"task_{len(self.created) + 1}", "title": title, "goal": goal, "source": source}
        self.created.append(task)
        return task


@dataclass
class _FakeExecutionEngine:
    calls: list[tuple[str, Any]]

    def __init__(self) -> None:
        self.calls = []

    def execute_task(self, task_id: str, plan: Any) -> Any:
        self.calls.append((task_id, plan))
        return SimpleNamespace(text=f"executed:{task_id}")


class _FakeCatalog:
    def resolve(self, capability_id: str) -> Any:
        return SimpleNamespace(risk_level="READ_ONLY", manifest_risk_level="READ_ONLY", requires_approval=False)


def test_run_once_materializes_task_decision_via_manager_bridge(monkeypatch) -> None:
    task_manager = _FakeTaskManager()
    execution_engine = _FakeExecutionEngine()
    mind = L2AutonomousMind(
        task_manager=task_manager,
        execution_engine=execution_engine,
        capability_catalog=_FakeCatalog(),
    )
    decision = L2Decision(
        action=L2Action(
            type=L2ActionType.TASK,
            task_spec={
                "capability_id": "ai-server.memory.search",
                "args": {"query": "latest commitments"},
                "goal": "Look up relevant memory",
            },
            reason="Need concrete supporting context",
        ),
        plan="Search memory for relevant commitments",
        confidence=0.8,
        context=L2Context(),
    )
    monkeypatch.setattr(mind, "decide", lambda context=None: decision)

    result = mind.run_once(L2Context())

    assert result["handled"] is True
    assert result["task_id"] == "task_1"
    assert execution_engine.calls[0][0] == "task_1"
    assert execution_engine.calls[0][1].steps[0].capability_id == "ai-server.memory.search"


def test_run_once_validates_l3_result_through_task_manager(monkeypatch) -> None:
    task_manager = _FakeTaskManager()
    execution_engine = _FakeExecutionEngine()
    mind = L2AutonomousMind(
        task_manager=task_manager,
        execution_engine=execution_engine,
        capability_catalog=_FakeCatalog(),
    )
    decision = L2Decision(
        action=L2Action(
            type=L2ActionType.ESCALATE_L3,
            l3_problem={"problem": "Complex multi-step diagnosis"},
            reason="Need deeper reasoning",
        ),
        plan="Ask L3 for a plan",
        confidence=0.3,
        escalate_to_l3=True,
        context=L2Context(l1_summaries=[{"meaning": "Browser server degraded"}]),
    )
    monkeypatch.setattr(mind, "decide", lambda context=None: decision)
    monkeypatch.setattr(
        mind,
        "escalate_to_l3",
        lambda *args, **kwargs: SimpleNamespace(
            recommended_action=SimpleNamespace(value="task"),
            reasoning_summary="Inspect status and memory before acting",
            plan=SimpleNamespace(
                steps=[
                    SimpleNamespace(
                        capability_id="ai-server.memory.search",
                        args={"query": "browser failures"},
                        reason="Collect prior failure evidence",
                    ),
                    SimpleNamespace(
                        capability_id="pc-server.system.get_os_info",
                        args={},
                        reason="Check host state",
                    ),
                ],
                assumptions=[],
                risks=[],
            ),
        ),
    )

    result = mind.run_once(L2Context())

    assert result["handled"] is True
    assert result["l3_invoked"] is True
    assert result["l3_recommended_action"] == "task"
    assert len(execution_engine.calls[0][1].steps) == 2
