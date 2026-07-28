import json
from aegis_ai.audit.audit_log import sanitize_audit_detail
from aegis_ai.llm.providers.openai_provider import OpenAIProvider


def test_sanitize_audit_detail_truncates_prompt_preview():
    detail = sanitize_audit_detail({"prompt_preview": "x" * 50_000, "tokens": 12})
    assert detail["tokens"] == 12
    assert len(detail["prompt_preview"]) <= 500
    assert detail["prompt_preview_chars"] == 50_000


def test_openai_provider_clamps_prompt_and_previews_for_audit(monkeypatch):
    logged = {}

    class _FakeCompletions:
        def create(self, **kwargs):
            class _Msg:
                content = "ok"
                tool_calls = None

            class _Choice:
                message = _Msg()

            class _Usage:
                prompt_tokens = 1
                completion_tokens = 1
                total_tokens = 2

            class _Resp:
                choices = [_Choice()]
                usage = _Usage()

            return _Resp()

    class _FakeClient:
        def __init__(self, *args, **kwargs):
            self.chat = type("C", (), {"completions": _FakeCompletions()})()

    monkeypatch.setattr("aegis_ai.llm.providers.openai_provider.OpenAI", _FakeClient)

    class _Audit:
        def append(self, entry):
            logged["detail"] = entry.detail

    provider = OpenAIProvider(model="mock", api_key="x", audit_log=_Audit())
    huge = "p" * 100_000
    result = provider.generate(prompt=huge, max_tokens=16)
    assert result.success is True
    assert len(logged["detail"]["prompt_preview"]) <= 500
    assert logged["detail"]["prompt_chars"] <= 48_000
