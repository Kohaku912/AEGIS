from __future__ import annotations

from aegis_ai.capability_index import CapabilitySelection
from aegis_ai.context_builder import ContextBuilder
from aegis_ai.llm_task_interpreter import LLMTaskInterpreter


class FakeRetriever:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def select_for_request(
        self,
        user_message: str,
        session_context: dict,
        top_k_schema: int = 8,
        top_k_summary: int = 30,
        allowed_ids: set[str] | None = None,
    ) -> CapabilitySelection:
        self.queries.append(user_message)
        return CapabilitySelection(
            always_direct_tools=[],
            retrieved_schema_tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "pc-server__screenshot__get_screenshot",
                        "description": "Screenshot: Capture screen",
                        "parameters": {"type": "object", "properties": {}},
                    },
                }
            ],
            lightweight_catalog=[
                {
                    "id": "pc-server.screenshot.get_screenshot",
                    "title": "Screenshot",
                    "tags": ["screenshot"],
                    "risk": "low",
                    "short_desc": "Capture screen",
                }
            ],
            all_candidate_ids=["pc-server.screenshot.get_screenshot"],
            scores={},
        )


def test_context_builder_uses_capability_retriever() -> None:
    retriever = FakeRetriever()
    ctx = ContextBuilder(capability_retriever=retriever).build(triggering_query="画面を見て")

    assert retriever.queries == ["画面を見て"]
    assert ctx.available_capability_ids == ["pc-server.screenshot.get_screenshot"]


def test_llm_task_interpreter_uses_retriever_for_capability_context() -> None:
    retriever = FakeRetriever()
    interpreter = LLMTaskInterpreter(capability_retriever=retriever)

    text = interpreter._build_capability_list("画面を見て")

    assert retriever.queries == ["画面を見て"]
    assert "Full schema candidates" in text
    assert "pc-server.screenshot.get_screenshot" in text
    assert "Lightweight catalog" in text
