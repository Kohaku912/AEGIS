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
    assert result.desire_delta_hint == {"social": 0.4}


def test_structured_unread_zero_is_no_effect_without_text_keywords() -> None:
    result = evaluate_task_result(
        capability_id="ai-server.agora.read_posts",
        tool_success=True,
        output={"result": {"unread_count": 0, "posts": []}},
        desire_name="social",
    )

    assert result.task_effect == TaskEffect.NO_EFFECT
    assert result.desire_delta_hint == {"social": 0.0}


def test_structured_nonempty_result_is_useful_without_text_keywords() -> None:
    result = evaluate_task_result(
        capability_id="browser-server.page.browse",
        tool_success=True,
        output={"ok": True, "items": [{"title": "Example"}]},
        desire_name="growth",
        capability_metadata={"operation_category": "research"},
    )

    assert result.task_effect == TaskEffect.USEFUL
    assert result.desire_delta_hint["growth"] > 0


def test_structured_failure_flag_is_failed() -> None:
    result = evaluate_task_result(
        capability_id="ai-server.memory.search",
        tool_success=True,
        output={"ok": False, "error": "backend unavailable"},
        desire_name="growth",
    )

    assert result.task_effect == TaskEffect.FAILED
    assert result.desire_delta_hint["growth"] < 0
