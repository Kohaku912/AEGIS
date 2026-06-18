from __future__ import annotations

import json
from types import SimpleNamespace

from aegis_ai.context_builder import ContextBuilder
from aegis_ai.llm.providers.openai_provider import OpenAIProvider
from aegis_schema.models import Event, ServerType


class _FakeMultimodalLLM:
    def __init__(self) -> None:
        self.image_calls: list[dict[str, object]] = []
        self.media_calls: list[dict[str, object]] = []

    def generate_with_image(
        self,
        prompt: str,
        image_base64: str,
        system_prompt: str = "",
        max_tokens: int = 0,
        temperature: float = 0.7,
        detail: str = "low",
        context_meta: dict[str, object] | None = None,
        profile: str | None = None,
    ) -> SimpleNamespace:
        self.image_calls.append(
            {
                "prompt": prompt,
                "image_base64": image_base64,
                "system_prompt": system_prompt,
                "context_meta": context_meta or {},
            }
        )
        return SimpleNamespace(success=True, content="Visible login page with a form and buttons.")

    def generate_with_media(
        self,
        prompt: str,
        image_base64s: list[str],
        system_prompt: str = "",
        max_tokens: int = 0,
        temperature: float = 0.7,
        detail: str = "low",
        context_meta: dict[str, object] | None = None,
        media_kind: str = "image",
        profile: str | None = None,
    ) -> SimpleNamespace:
        self.media_calls.append(
            {
                "prompt": prompt,
                "image_base64s": list(image_base64s),
                "system_prompt": system_prompt,
                "context_meta": context_meta or {},
                "media_kind": media_kind,
            }
        )
        return SimpleNamespace(success=True, content="Video keyframes show a login flow progressing to an error dialog.")


def test_context_builder_summarizes_image_inputs() -> None:
    llm = _FakeMultimodalLLM()
    builder = ContextBuilder(multimodal_llm=llm)

    ctx = builder.build(
        triggering_query="save credentials",
        media_inputs=[
            {
                "kind": "image",
                "image_base64": "ZmFrZS1pbWFnZQ==",
                "caption": "Login screen",
                "source": "browser",
            }
        ],
    )

    assert ctx.recent_media_summaries
    assert "Visible login page" in ctx.recent_media_summaries[0]
    assert llm.image_calls
    assert "save credentials" in llm.image_calls[0]["prompt"]


def test_context_builder_summarizes_video_and_reuses_cache() -> None:
    llm = _FakeMultimodalLLM()
    builder = ContextBuilder(multimodal_llm=llm)
    video_input = {
        "kind": "video",
        "frames_base64": ["frame-a", "frame-b", "frame-c", "frame-d"],
        "caption": "Recording of a login flow",
        "source": "screen-recording",
    }

    ctx1 = builder.build(triggering_query="watch the login process", media_inputs=[video_input])
    ctx2 = builder.build(triggering_query="watch the login process", media_inputs=[video_input])

    assert ctx1.recent_media_summaries
    assert "frames=4" in ctx1.recent_media_summaries[0]
    assert ctx2.recent_media_summaries == ctx1.recent_media_summaries
    assert len(llm.media_calls) == 1
    assert llm.media_calls[0]["media_kind"] == "video"
    assert len(llm.media_calls[0]["image_base64s"]) == 4


def test_context_builder_extracts_media_from_triggering_event_payload() -> None:
    llm = _FakeMultimodalLLM()
    builder = ContextBuilder(multimodal_llm=llm)
    event = Event(
        event_id="evt_1",
        event_type="pc.screen_updated",
        source_server_type=ServerType.PC,
        source_server_id="pc-server-main",
        timestamp_ms=1,
        payload_json=json.dumps(
            {
                "image_base64": "ZmFrZS1zY3JlZW4=",
                "caption": "Desktop screenshot",
            }
        ),
    )

    ctx = builder.build(triggering_events=[event], triggering_query="inspect the screen")

    assert ctx.recent_media_summaries
    assert "Visible login page" in ctx.recent_media_summaries[0]
    assert llm.image_calls


def test_openai_provider_supports_multi_image_media_calls(monkeypatch) -> None:
    provider = OpenAIProvider(
        model="qwen3-vl-flash",
        api_key="test-key",
        base_url="https://example.com",
        audit_log=None,
    )

    captured: dict[str, object] = {}

    def fake_create(**kwargs):
        captured["kwargs"] = kwargs
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="video summary"))],
            usage=SimpleNamespace(total_tokens=12),
        )

    monkeypatch.setattr(provider._client.chat.completions, "create", fake_create)

    result = provider.generate_with_media(
        prompt="Summarize the ordered keyframes.",
        image_base64s=["a", "b", "c", "d"],
        system_prompt="You analyze keyframes.",
        media_kind="video",
    )

    assert result.success is True
    messages = captured["kwargs"]["messages"]
    assert len(messages) == 2
    assert len(messages[1]["content"]) == 5
    assert messages[1]["content"][1]["type"] == "image_url"
    assert messages[1]["content"][4]["type"] == "image_url"
