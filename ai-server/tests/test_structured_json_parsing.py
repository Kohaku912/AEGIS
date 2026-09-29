from __future__ import annotations

from types import SimpleNamespace

from aegis_ai.desire.desire_system import DesireSystem
from aegis_ai.observation.multimodal_state_analyzer import MultimodalStateAnalyzer


class _FakeLLM:
    def __init__(self, content: str, *, success: bool = True) -> None:
        self._content = content
        self._success = success

    def generate(self, **kwargs):
        return SimpleNamespace(success=self._success, content=self._content, error="")


def test_multimodal_state_analyzer_parses_wrapped_json_with_braces() -> None:
    analyzer = MultimodalStateAnalyzer(
        llm_client=_FakeLLM(
            'Analysis follows.\n'
            '{"state_summary":"Login screen","task_relevant_elements":["email field"],'
            '"current_progress":"waiting","success_signals":[],"failure_signals":[],'
            '"blocking_issues":["message contained {brace} token"],'
            '"next_safe_actions":["fill email"],"requires_user_help":false,'
            '"sensitivity_flags":[],"confidence":0.77}\n'
            "End."
        )
    )

    result = analyzer.analyze(
        observation_summary="screen text",
        action_goal="login",
        expected_outcome="signed in",
    )

    assert result.state_summary == "Login screen"
    assert result.blocking_issues == ["message contained {brace} token"]
    assert result.confidence == 0.77


def test_desire_system_llm_update_parses_markdown_wrapped_json(tmp_path) -> None:
    llm = _FakeLLM(
        "```json\n"
        '{"desire_updates":{"growth":{"delta":0.6,"reason":"learned from {new} info"}}}\n'
        "```"
    )
    system = DesireSystem(data_dir=str(tmp_path / "desire"), llm_provider=llm)
    before = system.get_desire("growth").value

    result = system.update_after_action("research", "found useful information")

    assert "error" not in result
    assert result["updates"]["growth"]["delta"] == 0.6
    assert system.get_desire("growth").value > before
