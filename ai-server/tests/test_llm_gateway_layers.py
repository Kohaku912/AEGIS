"""Tests for LLM Layer profiles (DASHBOARD_V3_PLAN.md Phase L1).

LLMGateway.request(layer, ...) / LLMGateway.request_json(layer, ...) が
正しい profile (l1_default / l2_default / l3_default) を解決し、
context_meta に layer 情報を自動付与することを検証。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from aegis_ai.llm.gateway import LLMGateway
from aegis_ai.llm.layer_profiles import (
    LAYER_DESCRIPTIONS,
    LAYER_L1,
    LAYER_L2,
    LAYER_L3,
    LAYER_TO_PROFILE,
    VALID_LAYERS,
    is_valid_layer,
    layer_description,
    layer_to_profile,
)
from aegis_ai.llm.router import LLMResponse
from aegis_ai.llm.settings_resolver import LLMSettingsResolver


# ── Fixtures ──────────────────────────────────────────────────


@pytest.fixture()
def llm_yaml_with_layers(tmp_path: Path) -> Path:
    """L1/L2/L3 profile を含む llm.yaml fixture."""
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
            "l1_default": {
                "provider": "openai",
                "model": "deepseek-v4-flash",
                "max_tokens": 1024,
                "temperature": 0.3,
                "reasoning_level": "low",
                "timeout_seconds": 15,
                "max_tool_rounds": 3,
            },
            "l2_default": {
                "provider": "openai",
                "model": "deepseek-v4-flash",
                "max_tokens": 4096,
                "temperature": 0.5,
                "reasoning_level": "medium",
                "timeout_seconds": 60,
                "max_tool_rounds": 5,
            },
            "l3_default": {
                "provider": "openai",
                "model": "deepseek-v4-flash",
                "max_tokens": 8192,
                "temperature": 0.4,
                "reasoning_level": "high",
                "timeout_seconds": 120,
                "max_tool_rounds": 5,
            },
        },
        "safety": {
            "allowed_models": ["deepseek-v4-flash"],
            "max_tokens_upper_bound": 128000,
            "max_temperature": 2.0,
            "min_temperature": 0.0,
        },
    }
    p = tmp_path / "llm.yaml"
    p.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    return p


class _CapturingRouter:
    """gateway.generate 内部で呼ばれる router.route の引数を捕捉する fake."""

    def __init__(self) -> None:
        self.last_request: Any = None
        self.response = LLMResponse(content="ok", success=True)

    def route(self, request: Any) -> LLMResponse:
        self.last_request = request
        return self.response

    def route_with_tools(self, request: Any, tools: list) -> LLMResponse:
        self.last_request = request
        return self.response

    def route_with_image(self, request: Any, image_base64: str, detail: str = "low") -> LLMResponse:
        self.last_request = request
        return self.response

    def route_with_media(self, request: Any, image_base64s: list, detail: str = "low", media_kind: str = "image") -> LLMResponse:
        self.last_request = request
        return self.response


@pytest.fixture()
def gateway_factory(llm_yaml_with_layers: Path):
    """(router) -> LLMGateway を返す factory. settings_resolver はレイヤ profile を含む yaml を読み込む."""

    def _make(router: Any | None = None) -> LLMGateway:
        sr = LLMSettingsResolver(str(llm_yaml_with_layers))
        gw = LLMGateway(router=router or _CapturingRouter(), settings_resolver=sr)
        return gw

    return _make


# ── layer_profiles 単体テスト ────────────────────────────────


class TestLayerProfiles:
    def test_valid_layers_constant(self) -> None:
        """VALID_LAYERS は L1/L2/L3 の 3 つ."""
        assert VALID_LAYERS == frozenset({"L1", "L2", "L3"})

    def test_is_valid_layer(self) -> None:
        """is_valid_layer は L1/L2/L3 で True、それ以外 False."""
        assert is_valid_layer("L1") is True
        assert is_valid_layer("L2") is True
        assert is_valid_layer("L3") is True
        assert is_valid_layer("l1") is False  # 大文字小文字区別
        assert is_valid_layer("L0") is False
        assert is_valid_layer("L4") is False
        assert is_valid_layer("") is False
        assert is_valid_layer("l2_default") is False

    def test_layer_to_profile(self) -> None:
        """layer_to_profile は layer → profile_id を返す."""
        assert layer_to_profile("L1") == "l1_default"
        assert layer_to_profile("L2") == "l2_default"
        assert layer_to_profile("L3") == "l3_default"
        # LAYER_TO_PROFILE との一致
        for layer in ("L1", "L2", "L3"):
            assert LAYER_TO_PROFILE[layer] == layer_to_profile(layer)

    def test_layer_to_profile_invalid_raises(self) -> None:
        """不正な layer は ValueError."""
        with pytest.raises(ValueError) as exc:
            layer_to_profile("L0")
        assert "Invalid LLM layer" in str(exc.value)
        assert "L1" in str(exc.value)
        assert "L2" in str(exc.value)
        assert "L3" in str(exc.value)

    def test_layer_description(self) -> None:
        """layer_description は人間向け description を返す."""
        for layer in ("L1", "L2", "L3"):
            desc = layer_description(layer)
            assert desc == LAYER_DESCRIPTIONS[layer]
            assert isinstance(desc, str)
            assert len(desc) > 0
        # 不正な layer は fallback 文字列
        assert "Unknown" in layer_description("L99")


# ── LLMGateway.request() テスト ───────────────────────────────


class TestLLMGatewayRequest:
    def test_l1_layer_resolves_l1_default_profile(self, gateway_factory) -> None:
        """L1 を request すると l1_default profile が解決される."""
        router = _CapturingRouter()
        gw = gateway_factory(router=router)
        resp = gw.request("L1", "hello")
        assert resp.success is True
        # router.route が呼ばれ、context_meta に layer=L1 が入る
        assert router.last_request is not None
        meta = router.last_request.context_meta or {}
        assert meta.get("layer") == "L1"
        assert meta.get("caller") == "gateway.L1"
        assert meta.get("llm_layer_description") == LAYER_DESCRIPTIONS["L1"]

    def test_l2_layer_resolves_l2_default_profile(self, gateway_factory) -> None:
        """L2 を request すると l2_default profile が解決される."""
        router = _CapturingRouter()
        gw = gateway_factory(router=router)
        resp = gw.request("L2", "decide something")
        assert resp.success is True
        meta = router.last_request.context_meta or {}
        assert meta.get("layer") == "L2"
        assert meta.get("caller") == "gateway.L2"

    def test_l3_layer_resolves_l3_default_profile(self, gateway_factory) -> None:
        """L3 を request すると l3_default profile が解決される."""
        router = _CapturingRouter()
        gw = gateway_factory(router=router)
        resp = gw.request("L3", "deeply analyze X")
        assert resp.success is True
        meta = router.last_request.context_meta or {}
        assert meta.get("layer") == "L3"
        assert meta.get("caller") == "gateway.L3"

    def test_invalid_layer_raises(self, gateway_factory) -> None:
        """不正な layer は ValueError."""
        gw = gateway_factory()
        with pytest.raises(ValueError) as exc:
            gw.request("L0", "x")
        assert "Invalid LLM layer" in str(exc.value)
        with pytest.raises(ValueError):
            gw.request("foo", "x")
        with pytest.raises(ValueError):
            gw.request("", "x")

    def test_request_with_json_mode(self, gateway_factory) -> None:
        """json_mode=True で request → router.request.json_mode=True になる."""
        router = _CapturingRouter()
        gw = gateway_factory(router=router)
        resp = gw.request("L1", "structured prompt", json_mode=True)
        assert resp.success is True
        # json_mode=True で request される
        assert router.last_request.json_mode is True

    def test_request_with_context_meta_merges_layer(self, gateway_factory) -> None:
        """context_meta に layer / caller が自動付与される (上書きしない)."""
        router = _CapturingRouter()
        gw = gateway_factory(router=router)
        gw.request(
            "L2",
            "do something",
            context_meta={"task_id": "task-1", "request_id": "req-1"},
        )
        meta = router.last_request.context_meta or {}
        # 自動付与
        assert meta.get("layer") == "L2"
        assert meta.get("caller") == "gateway.L2"
        # 引数で渡したものは維持
        assert meta.get("task_id") == "task-1"
        assert meta.get("request_id") == "req-1"

    def test_generate_enriches_provider_context_meta_with_profile(self, gateway_factory, monkeypatch) -> None:
        """provider 直呼びでも profile_id / provider / model を落とさない."""
        class _Provider:
            def __init__(self) -> None:
                self.last_context_meta: dict[str, Any] | None = None

            def generate(
                self,
                *,
                prompt: str,
                system_prompt: str = "",
                max_tokens: int = 0,
                temperature: float = 0.0,
                context_meta: dict[str, Any] | None = None,
                json_mode: bool = False,
            ) -> LLMResponse:
                self.last_context_meta = dict(context_meta or {})
                return LLMResponse(content="ok", success=True)

        router = _CapturingRouter()
        gw = gateway_factory(router=router)
        provider = _Provider()
        monkeypatch.setattr(gw, "_get_provider_for_profile", lambda settings: provider)

        response = gw.generate(
            "observe this",
            context_meta={"request_id": "req-provider-meta"},
            profile="l1_default",
        )

        assert response.success is True
        assert provider.last_context_meta is not None
        assert provider.last_context_meta["request_id"] == "req-provider-meta"
        assert provider.last_context_meta["profile_id"] == "l1_default"
        assert provider.last_context_meta["profile"] == "l1_default"
        assert provider.last_context_meta["provider"] == "openai"
        assert provider.last_context_meta["model"] == "deepseek-v4-flash"

    def test_request_json_returns_dict(self, gateway_factory) -> None:
        """request_json は JSON 形式のレスポンスを dict として返す."""
        router = _CapturingRouter()
        router.response = LLMResponse(content='{"foo": "bar", "n": 42}', success=True)
        gw = gateway_factory(router=router)
        result = gw.request_json("L1", "give me json")
        assert result == {"foo": "bar", "n": 42}

    def test_request_json_handles_parse_error(self, gateway_factory) -> None:
        """request_json は parse 失敗時に error dict を返す."""
        router = _CapturingRouter()
        router.response = LLMResponse(content="not json", success=True)
        gw = gateway_factory(router=router)
        result = gw.request_json("L1", "give me json")
        assert result.get("error") == "json_parse_failed"
        assert result.get("raw") == "not json"
