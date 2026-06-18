from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from aegis_ai.capability_catalog import CapabilityCatalog
from aegis_ai.capability_index import CapabilityIndex, CapabilityRetriever
from aegis_ai.web import chat_tools


@dataclass
class FakeResponse:
    content: str = ""
    success: bool = True
    error: str = ""
    tool_calls: list[dict[str, Any]] | None = None


class FakeCatalog:
    def list_for_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "browser-server__page__browse",
                    "description": "Browse a page",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "ai-server__memory__save",
                    "description": "Save memory",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
        ]

    def tool_name_to_cap_id(self, tool_name: str) -> str:
        return tool_name.replace("__", ".")

    def resolve(self, cap_id: str) -> object | None:
        return object()


class PromptRecordingLLM:
    def __init__(self) -> None:
        self.prompts: list[str] = []
        self._calls = 0

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 1000,
        context_meta: dict[str, Any] | None = None,
    ) -> FakeResponse:
        self.prompts.append(prompt)
        self._calls += 1
        if self._calls == 1:
            return FakeResponse(
                content='<tool_call>{"name":"browser-server__page__browse","arguments":{"task":"Open example.com"}}</tool_call>'
            )
        return FakeResponse(content="Task complete.")


class NativeToolLLM:
    def __init__(self) -> None:
        self.prompts: list[str] = []
        self._calls = 0

    def generate_with_tools(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_prompt: str = "",
        max_tokens: int = 1000,
        context_meta: dict[str, Any] | None = None,
    ) -> FakeResponse:
        self.prompts.append(prompt)
        self._calls += 1
        if self._calls == 1:
            return FakeResponse(
                tool_calls=[
                    {
                        "function": "browser-server__page__browse",
                        "arguments": {"task": "Search docs"},
                    }
                ]
            )
        if self._calls == 2:
            return FakeResponse(
                tool_calls=[
                    {
                        "function": "ai-server__memory__save",
                        "arguments": {"text": "Important result"},
                    }
                ]
            )
        return FakeResponse(content="Finished all steps.")


class VisionToolLLM:
    def __init__(self) -> None:
        self.prompts: list[str] = []
        self.vision_prompts: list[str] = []
        self._calls = 0

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 1000,
        context_meta: dict[str, Any] | None = None,
    ) -> FakeResponse:
        self.prompts.append(prompt)
        self._calls += 1
        if self._calls == 1:
            return FakeResponse(
                content='<tool_call>{"name":"pc-server__screenshot__get_screenshot","arguments":{}}</tool_call>'
            )
        return FakeResponse(content="Understood.")

    def generate_with_image(
        self,
        prompt: str,
        image_base64: str,
        system_prompt: str = "",
        max_tokens: int = 200,
        temperature: float = 0.7,
        detail: str = "low",
        context_meta: dict[str, Any] | None = None,
    ) -> FakeResponse:
        self.vision_prompts.append(prompt)
        return FakeResponse(content="The browser is open on a signup form with visible input fields.")


def test_follow_up_prompt_preserves_original_request_and_tool_result(monkeypatch) -> None:
    llm = PromptRecordingLLM()
    catalog = FakeCatalog()

    monkeypatch.setattr(
        chat_tools,
        "execute_tool_call",
        lambda catalog, function_name, arguments: {
            "success": True,
            "result": "Opened example.com and found the title.",
            "output": {},
            "error": "",
            "needs_user_input": False,
            "needs_user_input_for": [],
        },
    )

    user_message = "example.com を開いてタイトルを確認して、その内容を覚えてください。"
    result = chat_tools.call_llm_with_tools(
        llm=llm,
        user_message=user_message,
        system_prompt="You are AEGIS.",
        catalog=catalog,
        max_tool_rounds=3,
    )

    assert result["response"] == "Task complete."
    assert len(llm.prompts) == 2
    assert f"Original user request:\n{user_message}" in llm.prompts[1]
    assert "Tool result from browser-server__page__browse:\nSuccess: True\nOpened example.com and found the title." in llm.prompts[1]


def test_call_llm_with_tools_uses_native_tool_calling_for_multi_step_sequences(monkeypatch) -> None:
    llm = NativeToolLLM()
    catalog = FakeCatalog()

    def fake_execute_tool_call(catalog, function_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if function_name == "browser-server__page__browse":
            return {
                "success": True,
                "result": "Found documentation page.",
                "output": {},
                "error": "",
                "needs_user_input": False,
                "needs_user_input_for": [],
            }
        return {
            "success": True,
            "result": "Saved to memory.",
            "output": {},
            "error": "",
            "needs_user_input": False,
            "needs_user_input_for": [],
        }

    monkeypatch.setattr(chat_tools, "execute_tool_call", fake_execute_tool_call)

    result = chat_tools.call_llm_with_tools(
        llm=llm,
        user_message="調べて重要なら記憶してください。",
        system_prompt="You are AEGIS.",
        catalog=catalog,
        max_tool_rounds=4,
    )

    assert result["response"] == "Finished all steps."
    assert [call["function"] for call in result["tool_calls"]] == [
        "browser-server__page__browse",
        "ai-server__memory__save",
    ]


def test_tool_prompt_prefers_file_write_capability() -> None:
    prompt = chat_tools._build_tool_loop_prompt(
        user_message="アカウント情報を保存してください。",
        tool_list="- pc-server__file__write: Write File",
        conversation_history=[],
    )

    assert "prefer pc-server__file__write" in prompt
    assert "Use shell tools only when a dedicated capability cannot perform the task." in prompt


def test_screenshot_tool_result_is_summarized_for_follow_up_prompt(monkeypatch) -> None:
    llm = VisionToolLLM()
    catalog = FakeCatalog()

    monkeypatch.setattr(
        catalog,
        "list_for_tools",
        lambda: [
            {
                "type": "function",
                "function": {
                    "name": "pc-server__screenshot__get_screenshot",
                    "description": "Take screenshot",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        ],
    )

    monkeypatch.setattr(
        chat_tools,
        "execute_tool_call",
        lambda catalog, function_name, arguments: {
            "success": True,
            "result": "Screenshot captured (1920x1080).",
            "output": {"width": 1920, "height": 1080, "image_base64": "ZmFrZQ=="},
            "error": "",
            "needs_user_input": False,
            "needs_user_input_for": [],
        },
    )

    monkeypatch.setattr(
        chat_tools,
        "_get_vision_llm",
        lambda llm, *, runtime=None: llm,
    )

    result = chat_tools.call_llm_with_tools(
        llm=llm,
        user_message="画面を見てください。",
        system_prompt="You are AEGIS.",
        catalog=catalog,
        max_tool_rounds=2,
    )

    assert result["response"] == "Understood."
    assert llm.vision_prompts
    assert "The browser is open on a signup form with visible input fields." in llm.prompts[1]


def _write_chat_cap(root: Path, index: int) -> None:
    app_id = f"dummy{index}"
    path = root / "builtin" / "ai-server" / app_id / "run.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({
            "title": f"Dummy {index}",
            "description": f"Dummy capability {index}",
            "server_id": "ai-server",
            "app_id": app_id,
            "action": "run",
            "risk": {"level": "low", "requires_approval": False},
            "input_schema": {"type": "object", "properties": {"value": {"type": "string"}}},
        }),
        encoding="utf-8",
    )


def test_get_tools_for_chat_uses_retriever_not_full_catalog(tmp_path: Path) -> None:
    caps_dir = tmp_path / "capabilities"
    for i in range(40):
        _write_chat_cap(caps_dir, i)
    catalog = CapabilityCatalog(str(caps_dir))
    retriever = CapabilityRetriever(catalog, CapabilityIndex(catalog, enable_chroma=False))
    runtime = SimpleNamespace(capability_retriever=retriever)

    tools = chat_tools.get_tools_for_chat(
        catalog,
        user_message="dummy task",
        runtime=runtime,
    )
    names = {tool["function"]["name"] for tool in tools}

    assert len(tools) == 11
    assert "ask_user" in names
    assert "capability__search" in names
    assert "capability__describe" in names


def test_meta_tool_call_does_not_use_tool_broker(tmp_path: Path) -> None:
    caps_dir = tmp_path / "capabilities"
    _write_chat_cap(caps_dir, 1)
    catalog = CapabilityCatalog(str(caps_dir))
    retriever = CapabilityRetriever(catalog, CapabilityIndex(catalog, enable_chroma=False))

    class FailingBroker:
        def execute(self, request):
            raise AssertionError("meta tools must not call ToolBroker")

    runtime = SimpleNamespace(capability_retriever=retriever, tool_broker=FailingBroker())
    result = chat_tools.execute_tool_call(
        catalog,
        "capability__describe",
        {"capability_id": "ai-server.dummy1.run"},
        runtime=runtime,
    )

    assert result["success"] is True
    assert result["output"]["described_capability_id"] == "ai-server.dummy1.run"
