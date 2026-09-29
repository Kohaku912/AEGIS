from __future__ import annotations

import json
import os
from typing import Any

from aegis_ai.llm.providers.typesafe_provider import TypeSafeProvider


def test_typesafe_provider_maps_l1_observation(monkeypatch) -> None:
    provider = TypeSafeProvider(api_key="test-key")

    def fake_system_one(*, state, questions):
        assert state["event_id"] == "e1"
        assert "required_intelligence" in questions
        assert state["event_json"]["capability_id"] == "room-server.light.turn_on"
        assert state["aegis_context"]["user_state"]["current_activity"] == "coding"
        return {
            "answers": {
                "required_intelligence": {
                    "type": "choice",
                    "choice": "low",
                    "confidence": 0.9,
                },
                "value_band": {
                    "type": "score",
                    "score": 3.2,
                    "confidence": 0.8,
                },
                "priority_band": {
                    "type": "score",
                    "score": 2.0,
                    "confidence": 0.7,
                },
                "summary_bucket": {
                    "type": "choice",
                    "choice": "task_candidate",
                    "confidence": 0.88,
                },
                "intent_class": {
                    "type": "choice",
                    "choice": "immediate_action",
                    "confidence": 0.93,
                },
                "direct_handle": {
                    "type": "noul",
                    "noul": 0.91,
                },
            },
            "usage": {"input_tokens": 10, "output_tokens": 5},
        }

    monkeypatch.setattr(provider, "_system_one", fake_system_one)

    response = provider.generate(
        prompt="event: type=user.message | message=hello\nevent_json: {}\nevent_id: e1",
        system_prompt="You are L1.",
        context_meta={
            "layer": "L1",
            "event_id": "e1",
            "source": "l1_router.observe",
            "l1_state": {
                "event_id": "e1",
                "event_summary": "type=user.message | message=hello",
                "event_focus": {
                    "type": "user.message",
                    "message": "hello",
                    "capability_id": "room-server.light.turn_on",
                    "capability_args": {"room": "bedroom"},
                },
                "aegis_context": {
                    "user_state": {"current_activity": "coding"},
                    "world_state": {"degraded_server_count": 0},
                },
            },
        },
        json_mode=True,
    )

    assert response.success is True
    payload = json.loads(response.content)
    assert payload["required_intelligence"] == "low"
    assert 0.79 < payload["value"] < 0.81
    assert 0.49 < payload["priority"] < 0.51
    assert payload["summary_bucket"] == "task_candidate"
    assert payload["should_execute_directly"] is True
    assert payload["candidate_capability_id"] == "room-server.light.turn_on"
    assert payload["candidate_args"] == {"room": "bedroom"}
    assert payload["possible_intent"] == "Likely direct request to run room-server.light.turn_on"
    assert payload["meaning"] == "hello"


def test_typesafe_provider_legacy_l1_prompt_fallback(monkeypatch) -> None:
    provider = TypeSafeProvider(api_key="test-key")

    def fake_system_one(*, state, questions):
        assert state["event_id"] == "e-legacy"
        assert state["event_json"]["message"] == "legacy hello"
        assert state["aegis_context"] == {}
        return {
            "answers": {
                "required_intelligence": {"type": "choice", "choice": "low", "confidence": 0.8},
                "value_band": {"type": "score", "score": 1.0, "confidence": 0.8},
                "priority_band": {"type": "score", "score": 1.0, "confidence": 0.8},
                "summary_bucket": {"type": "choice", "choice": "background", "confidence": 0.8},
                "intent_class": {"type": "choice", "choice": "background", "confidence": 0.8},
                "direct_handle": {"type": "noul", "noul": 0.1},
            },
            "usage": {"input_tokens": 4, "output_tokens": 2},
        }

    monkeypatch.setattr(provider, "_system_one", fake_system_one)

    response = provider.generate(
        prompt=(
            "event: type=user.message | message=legacy hello\n"
            'event_json: {"type":"user.message","message":"legacy hello"}\n'
            "event_id: e-legacy"
        ),
        system_prompt="You are L1.",
        context_meta={"layer": "L1", "event_id": "e-legacy", "source": "l1_router.observe"},
        json_mode=True,
    )

    assert response.success is True
    payload = json.loads(response.content)
    assert payload["meaning"] == "legacy hello"


def test_typesafe_provider_maps_chat_boolean_gate(monkeypatch) -> None:
    provider = TypeSafeProvider(api_key="test-key")

    def fake_system_one(*, state, questions):
        assert "CURRENT user request" in state
        assert "use_tools" in questions
        return {
            "answers": {"use_tools": {"type": "noul", "noul": 0.91}},
            "usage": {"input_tokens": 8, "output_tokens": 2},
        }

    monkeypatch.setattr(provider, "_system_one", fake_system_one)

    response = provider.generate(
        prompt="CURRENT user request:\nブラウザを開いてください。",
        context_meta={"caller": "chat_tools.tool_gate"},
        json_mode=True,
    )

    assert response.success is True
    payload = json.loads(response.content)
    assert payload == {
        "use_tools": True,
        "reason": "typesafe_probability=0.910",
    }


def test_typesafe_provider_rejects_unsupported_tasks() -> None:
    provider = TypeSafeProvider(api_key="test-key")

    response = provider.generate(
        prompt="write a paragraph",
        context_meta={"caller": "unsupported"},
    )

    assert response.success is False
    assert "only supports" in response.error


def test_typesafe_provider_audits_missing_api_key() -> None:
    entries: list[Any] = []

    class _Audit:
        def append(self, entry: Any) -> None:
            entries.append(entry)

    os.environ.pop("TYPESAFE_API_KEY", None)
    provider = TypeSafeProvider(api_key="", audit_log=_Audit())

    response = provider.generate(
        prompt="CURRENT user request:\nブラウザを開いてください。",
        context_meta={"caller": "chat_tools.tool_gate", "request_id": "req-jev-missing"},
        json_mode=True,
    )

    assert response.success is False
    assert response.error == "TypeSafe API key is not configured"
    assert len(entries) == 1
    assert entries[0].decision == "error"
    assert entries[0].detail["error"] == "TypeSafe API key is not configured"
    assert entries[0].detail["api_key_configured"] is False


def test_typesafe_provider_success_audit_keeps_l1_source(monkeypatch) -> None:
    entries: list[Any] = []

    class _Audit:
        def append(self, entry: Any) -> None:
            entries.append(entry)

    provider = TypeSafeProvider(api_key="test-key", audit_log=_Audit())

    def fake_system_one(*, state, questions):
        return {
            "answers": {
                "required_intelligence": {"type": "choice", "choice": "low", "confidence": 0.9},
                "value_band": {"type": "score", "score": 1.0, "confidence": 0.9},
                "priority_band": {"type": "score", "score": 1.0, "confidence": 0.9},
                "summary_bucket": {"type": "choice", "choice": "background", "confidence": 0.9},
                "intent_class": {"type": "choice", "choice": "background", "confidence": 0.9},
                "direct_handle": {"type": "noul", "noul": 0.1},
            },
            "usage": {"input_tokens": 3, "output_tokens": 2},
        }

    monkeypatch.setattr(provider, "_system_one", fake_system_one)

    response = provider.generate(
        prompt="event: type=test\n event_json: {}\n event_id: e-audit",
        system_prompt="You are L1.",
        context_meta={
            "layer": "L1",
            "event_id": "e-audit",
            "source": "l1_router.observe",
            "profile_id": "l1_default",
            "request_id": "req-l1-audit",
        },
        json_mode=True,
    )

    assert response.success is True
    assert len(entries) == 1
    assert entries[0].decision == "success"
    assert entries[0].profile_id == "l1_default"
    assert entries[0].request_id == "req-l1-audit"
    assert entries[0].detail["source"] == "l1_router.observe"
