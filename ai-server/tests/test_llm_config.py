"""Tests for LLM config infrastructure: PromptRegistry, LLMSettingsResolver, LLMGateway, AuditEntry."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest
import yaml

from aegis_ai.audit import AuditEntry, AuditLog
from aegis_ai.llm.settings_resolver import LLMSettings, LLMSettingsResolver
from aegis_ai.llm.prompt_registry import PromptRegistry
from aegis_ai.llm.gateway import LLMGateway
from aegis_ai.llm.router import LLMResponse


# ── Fixtures ──────────────────────────────────────────────────

@pytest.fixture()
def llm_yaml(tmp_path: Path) -> Path:
    data = {
        "version": "1.0.0",
        "profiles": {
            "chat_balanced": {
                "provider": "openai",
                "model": "deepseek-v4-flash",
                "max_tokens": 4096,
                "temperature": 0.7,
                "reasoning_level": "medium",
                "timeout_seconds": 30,
                "max_tool_rounds": 5,
            },
            "json_generation": {
                "provider": "openai",
                "model": "deepseek-v4-flash",
                "max_tokens": 4096,
                "temperature": 0.1,
                "reasoning_level": "medium",
                "timeout_seconds": 30,
                "max_tool_rounds": 3,
            },
        },
        "safety": {
            "allowed_models": ["deepseek-v4-flash", "gpt-4o"],
            "max_tokens_upper_bound": 128000,
            "max_temperature": 2.0,
            "min_temperature": 0.0,
        },
    }
    p = tmp_path / "llm.yaml"
    p.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return p


@pytest.fixture()
def prompts_yaml(tmp_path: Path) -> Path:
    data = {
        "version": "1.0.0",
        "prompts": {
            "chat.system": {
                "version": "1.0.0",
                "editable": True,
                "protected": False,
                "template": "You are AEGIS. User: {{user_name}}",
            },
            "safety.core": {
                "version": "1.0.0",
                "editable": False,
                "protected": True,
                "template": "SAFETY CONSTRAINTS: Do not bypass.",
            },
        },
    }
    p = tmp_path / "prompts.yaml"
    p.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return p


# ── LLMSettingsResolver ──────────────────────────────────────

class TestLLMSettingsResolver:

    def test_resolve_default_profile(self, llm_yaml: Path) -> None:
        sr = LLMSettingsResolver(str(llm_yaml))
        settings = sr.resolve(profile_id="chat_balanced")
        assert settings.provider == "openai"
        assert settings.model == "deepseek-v4-flash"
        assert settings.max_tokens == 4096
        assert settings.temperature == 0.7

    def test_resolve_unknown_profile_raises(self, llm_yaml: Path) -> None:
        sr = LLMSettingsResolver(str(llm_yaml))
        with pytest.raises(KeyError):
            sr.resolve(profile_id="nonexistent")

    def test_validate_valid_settings(self, llm_yaml: Path) -> None:
        sr = LLMSettingsResolver(str(llm_yaml))
        settings = LLMSettings(max_tokens=2048, temperature=0.5, model="deepseek-v4-flash")
        assert sr.validate(settings) is True

    def test_validate_rejects_excessive_max_tokens(self, llm_yaml: Path) -> None:
        sr = LLMSettingsResolver(str(llm_yaml))
        settings = LLMSettings(max_tokens=999999)
        assert sr.validate(settings) is False

    def test_validate_rejects_unknown_model(self, llm_yaml: Path) -> None:
        sr = LLMSettingsResolver(str(llm_yaml))
        settings = LLMSettings(model="unknown-model")
        assert sr.validate(settings) is False

    def test_validate_rejects_temperature_out_of_range(self, llm_yaml: Path) -> None:
        sr = LLMSettingsResolver(str(llm_yaml))
        assert sr.validate(LLMSettings(temperature=-0.1)) is False
        assert sr.validate(LLMSettings(temperature=3.0)) is False

    def test_get_allowed_models(self, llm_yaml: Path) -> None:
        sr = LLMSettingsResolver(str(llm_yaml))
        models = sr.get_allowed_models()
        assert "deepseek-v4-flash" in models
        assert "gpt-4o" in models

    def test_get_max_tokens_upper_bound(self, llm_yaml: Path) -> None:
        sr = LLMSettingsResolver(str(llm_yaml))
        assert sr.get_max_tokens_upper_bound() == 128000

    def test_reload_when_no_change(self, llm_yaml: Path) -> None:
        sr = LLMSettingsResolver(str(llm_yaml))
        assert sr.reload() is True


# ── PromptRegistry ────────────────────────────────────────────

class TestPromptRegistry:

    def test_get_prompt(self, prompts_yaml: Path) -> None:
        pr = PromptRegistry(str(prompts_yaml))
        prompt = pr.get("chat.system")
        assert prompt["template"] == "You are AEGIS. User: {{user_name}}"
        assert prompt["version"] == "1.0.0"
        assert prompt["editable"] is True
        assert prompt["protected"] is False

    def test_get_unknown_prompt_raises(self, prompts_yaml: Path) -> None:
        pr = PromptRegistry(str(prompts_yaml))
        with pytest.raises(KeyError):
            pr.get("nonexistent")

    def test_render_with_variables(self, prompts_yaml: Path) -> None:
        pr = PromptRegistry(str(prompts_yaml))
        rendered = pr.render("chat.system", user_name="TestUser")
        assert "TestUser" in rendered
        assert "{{user_name}}" not in rendered

    def test_get_metadata(self, prompts_yaml: Path) -> None:
        pr = PromptRegistry(str(prompts_yaml))
        meta = pr.get_metadata("chat.system")
        assert meta["prompt_id"] == "chat.system"
        assert meta["version"] == "1.0.0"
        assert "hash" in meta

    def test_list_prompts(self, prompts_yaml: Path) -> None:
        pr = PromptRegistry(str(prompts_yaml))
        prompts = pr.list_prompts()
        ids = [p["prompt_id"] for p in prompts]
        assert "chat.system" in ids
        assert "safety.core" in ids

    def test_update_prompt_rejects_protected(self, prompts_yaml: Path) -> None:
        pr = PromptRegistry(str(prompts_yaml))
        result = pr.update_prompt("safety.core", "malicious prompt")
        assert result is False
        prompt = pr.get("safety.core")
        assert prompt["template"] == "SAFETY CONSTRAINTS: Do not bypass."

    def test_update_editable_prompt(self, prompts_yaml: Path) -> None:
        pr = PromptRegistry(str(prompts_yaml))
        result = pr.update_prompt("chat.system", "New template for {{user_name}}")
        assert result is True
        prompt = pr.get("chat.system")
        assert prompt["template"] == "New template for {{user_name}}"

    def test_reload_when_no_change(self, prompts_yaml: Path) -> None:
        pr = PromptRegistry(str(prompts_yaml))
        assert pr.reload() is True


# ── LLMGateway ───────────────────────────────────────────────

class _FakeRouter:
    def route(self, request):
        return LLMResponse(content="ok", model_used="test", tokens_used=10, success=True)

    def route_with_tools(self, request, tools):
        return LLMResponse(content="ok", model_used="test", tokens_used=10, success=True)

    def route_with_image(self, request, image_base64, detail="low"):
        return LLMResponse(content="ok", model_used="test", tokens_used=10, success=True)

    def route_with_media(self, request, image_base64s, detail="low", media_kind="image"):
        return LLMResponse(content="ok", model_used="test", tokens_used=10, success=True)


class TestLLMGateway:

    def test_generate_with_profile(self, llm_yaml: Path) -> None:
        sr = LLMSettingsResolver(str(llm_yaml))
        gw = LLMGateway(router=_FakeRouter(), settings_resolver=sr)
        resp = gw.generate("Hello", profile="chat_balanced")
        assert resp.success is True
        assert resp.content == "ok"

    def test_generate_with_explicit_overrides(self, llm_yaml: Path) -> None:
        sr = LLMSettingsResolver(str(llm_yaml))
        gw = LLMGateway(router=_FakeRouter(), settings_resolver=sr)
        resp = gw.generate("Hello", max_tokens=100, temperature=0.1)
        assert resp.success is True

    def test_generate_json(self, llm_yaml: Path) -> None:
        class JsonRouter(_FakeRouter):
            def route(self, request):
                return LLMResponse(content='{"key": "value"}', model_used="test", tokens_used=10, success=True)

        sr = LLMSettingsResolver(str(llm_yaml))
        gw = LLMGateway(router=JsonRouter(), settings_resolver=sr)
        result = gw.generate_json("Hello", profile="chat_balanced")
        assert result["key"] == "value"

    def test_generate_with_tools(self, llm_yaml: Path) -> None:
        sr = LLMSettingsResolver(str(llm_yaml))
        gw = LLMGateway(router=_FakeRouter(), settings_resolver=sr)
        resp = gw.generate_with_tools("Hello", tools=[{"name": "test"}], profile="chat_balanced")
        assert resp.success is True

    def test_audit_log_recording(self, llm_yaml: Path, tmp_path: Path) -> None:
        sr = LLMSettingsResolver(str(llm_yaml))
        audit = AuditLog(path=str(tmp_path / "test_audit.jsonl"))
        gw = LLMGateway(router=_FakeRouter(), settings_resolver=sr, audit_log=audit)
        gw.generate("Hello", profile="chat_balanced")
        entries = audit.read_all()
        assert len(entries) == 1
        assert entries[0]["action"] == "llm_call"
        assert entries[0]["profile_id"] == "chat_balanced"
        assert entries[0]["model"] == "deepseek-v4-flash"
        assert entries[0]["max_tokens"] == 4096

    def test_unknown_profile_uses_defaults(self) -> None:
        gw = LLMGateway(router=_FakeRouter(), settings_resolver=None)
        resp = gw.generate("Hello")
        assert resp.success is True


# ── AuditEntry ────────────────────────────────────────────────

class TestAuditEntry:

    def test_llm_fields_default_empty(self) -> None:
        entry = AuditEntry(action="test")
        assert entry.profile_id == ""
        assert entry.model == ""
        assert entry.max_tokens == 0

    def test_llm_fields_populated(self) -> None:
        entry = AuditEntry(
            action="llm_call",
            profile_id="chat_balanced",
            model="deepseek-v4-flash",
            max_tokens=4096,
            temperature=0.7,
            tokens_used=100,
            duration_ms=500,
        )
        assert entry.profile_id == "chat_balanced"
        assert entry.model == "deepseek-v4-flash"
        assert entry.max_tokens == 4096
        assert entry.tokens_used == 100

    def test_audit_log_serializes_llm_fields(self, tmp_path: Path) -> None:
        log = AuditLog(path=str(tmp_path / "test.jsonl"))
        log.append(AuditEntry(
            action="llm_call",
            profile_id="tool_planning",
            model="deepseek-v4-flash",
            max_tokens=2048,
            tokens_used=50,
        ))
        records = log.read_all()
        assert len(records) == 1
        assert records[0]["profile_id"] == "tool_planning"
        assert records[0]["model"] == "deepseek-v4-flash"
        assert records[0]["max_tokens"] == 2048
        assert records[0]["tokens_used"] == 50

    def test_audit_log_omits_empty_llm_fields(self, tmp_path: Path) -> None:
        log = AuditLog(path=str(tmp_path / "test.jsonl"))
        log.append(AuditEntry(action="policy_decision", decision="ALLOW"))
        records = log.read_all()
        assert len(records) == 1
        assert "profile_id" not in records[0]
        assert "model" not in records[0]
