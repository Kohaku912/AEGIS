from __future__ import annotations

from types import SimpleNamespace

from aegis_ai.desire.fulfillment import TaskEffect, evaluate_task_result


class _EvaluatorLLM:
    def __init__(self, content: str) -> None:
        self.content = content
        self.calls = 0

    def generate(self, **kwargs):
        self.calls += 1
        return SimpleNamespace(success=True, content=self.content)


def test_llm_evaluator_controls_task_effect() -> None:
    llm = _EvaluatorLLM(
        '{"task_effect":"needs_followup","summary":"Found an actionable item",'
        '"desire_delta_hint":{"social":0.4}}'
    )

    result = evaluate_task_result(
        capability_id="ai-server.agora.read_posts",
        tool_success=True,
        output={"result": {"unread_count": 2, "posts": [{"id": 1}]}},
        desire_name="social",
        llm_provider=llm,
        capability_metadata={"operation_category": "read"},
    )

    assert llm.calls == 1
    assert result.task_effect == TaskEffect.NEEDS_FOLLOWUP
    assert result.pressure_reduction == 0.0
    assert result.desire_delta_hint == {"social": 0.4}


def test_llm_evaluator_controls_pressure_reduction_and_score() -> None:
    llm = _EvaluatorLLM(
        '{"task_effect":"useful","fulfillment_score":0.8,"pressure_reduction":0.6,'
        '"summary":"The action made progress","confidence":0.7,'
        '"desire_delta_hint":{"growth":0.5}}'
    )

    result = evaluate_task_result(
        capability_id="dynamic-server.anything.run",
        tool_success=True,
        output={"ok": True, "items": [{"title": "Example"}]},
        desire_name="growth",
        llm_provider=llm,
        capability_metadata={"operation_category": "dynamic_research"},
    )

    assert result.task_effect == TaskEffect.USEFUL
    assert result.fulfillment_score == 0.8
    assert result.pressure_reduction == 0.6
    assert result.confidence == 0.7
    assert result.desire_delta_hint == {"growth": 0.5}


def test_without_llm_evaluator_is_blocked_and_no_delta() -> None:
    result = evaluate_task_result(
        capability_id="ai-server.agora.read_posts",
        tool_success=True,
        output={"result": {"unread_count": 2, "posts": [{"id": 1}]}},
        desire_name="social",
    )

    assert result.task_effect == TaskEffect.BLOCKED
    assert result.pressure_reduction == 0.0
    assert result.desire_delta_hint == {}
    assert result.details["reason"] == "evaluator_unavailable"


def test_llm_failure_is_blocked_even_when_tool_failed() -> None:
    llm = _EvaluatorLLM("")
    llm.generate = lambda **kwargs: SimpleNamespace(success=False, content="", error="offline")

    result = evaluate_task_result(
        capability_id="dynamic-server.anything.run",
        tool_success=False,
        output={"ok": False, "error": "backend unavailable"},
        desire_name="growth",
        llm_provider=llm,
    )

    assert result.task_effect == TaskEffect.BLOCKED
    assert result.tool_success is False
    assert result.pressure_reduction == 0.0
    assert result.desire_delta_hint == {}


def test_invalid_llm_json_is_blocked() -> None:
    llm = _EvaluatorLLM("not json")

    result = evaluate_task_result(
        capability_id="dynamic-server.anything.run",
        tool_success=True,
        output={"ok": True},
        desire_name="growth",
        llm_provider=llm,
    )

    assert result.task_effect == TaskEffect.BLOCKED
    assert result.pressure_reduction == 0.0
    assert result.desire_delta_hint == {}


def test_fulfillment_source_has_no_capability_id_branching() -> None:
    import inspect
    from aegis_ai.desire import fulfillment

    source = inspect.getsource(fulfillment)

    assert ".endswith(" not in source
    assert ".startswith(" not in source
    assert " in capability_id" not in source
    assert "capability_id ==" not in source
