"""L3 Deep Reasoner テスト — DASHBOARD_V3_PLAN.md Phase L5.

`L3Reasoner` の plan 解析 / read_only 判定 / fallback / event publish を検証する。
`LLMGateway` / `CapabilityCatalog` は mock で代替。
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# fakes
# ---------------------------------------------------------------------------
@dataclass
class _FakeResponse:
    success: bool = True
    content: str = "{}"
    error: str | None = None


@dataclass
class _FakeGateway:
    responses: list[_FakeResponse]
    captured: list[dict[str, Any]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.captured is None:
            self.captured = []

    def request(self, **kwargs: Any) -> _FakeResponse:
        self.captured.append(kwargs)
        if not self.responses:
            return _FakeResponse(success=False, error="no_response")
        return self.responses.pop(0)


@dataclass
class _FakeManifest:
    capability_id: str
    risk_level: str = "READ_ONLY"
    metadata: dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


@dataclass
class _FakeCatalog:
    manifests: dict[str, _FakeManifest]

    def resolve(self, cap_id: str) -> _FakeManifest | None:
        return self.manifests.get(cap_id)


def _patched_gateway(monkeypatch: pytest.MonkeyPatch, fake: _FakeGateway) -> None:
    from aegis_ai.llm import l3_reasoner

    monkeypatch.setattr(l3_reasoner.L3Reasoner, "_get_gateway", lambda self: fake)


# ---------------------------------------------------------------------------
# import smoke
# ---------------------------------------------------------------------------
class TestImports:
    def test_l3_reasoner_importable(self) -> None:
        from aegis_ai.llm import L3Reasoner

        assert L3Reasoner is not None

    def test_l3_models_importable(self) -> None:
        from aegis_ai.llm import L3Action, L3Plan, L3Problem, L3Result, L3Step

        assert L3Action is not None
        assert L3Plan is not None
        assert L3Problem is not None
        assert L3Result is not None
        assert L3Step is not None

    def test_is_read_only_capability_importable(self) -> None:
        from aegis_ai.llm import is_read_only_capability

        assert callable(is_read_only_capability)


# ---------------------------------------------------------------------------
# is_read_only_capability
# ---------------------------------------------------------------------------
class TestIsReadOnlyCapability:
    def test_read_capability_id(self) -> None:
        from aegis_ai.llm import is_read_only_capability

        assert is_read_only_capability("pc-server.file.read_file") is True
        assert is_read_only_capability("browser-server.page.browse") is True
        assert is_read_only_capability("ai-server.memory.search") is True
        assert is_read_only_capability("web.search.query") is True

    def test_write_capability_id(self) -> None:
        from aegis_ai.llm import is_read_only_capability

        assert is_read_only_capability("pc-server.shell.powershell") is False
        assert is_read_only_capability("pc-server.mouse.click") is False
        assert is_read_only_capability("pc-server.keyboard.type") is False
        assert is_read_only_capability("file.write_to_file") is False
        assert is_read_only_capability("file.delete_file") is False

    def test_empty_id_returns_false(self) -> None:
        from aegis_ai.llm import is_read_only_capability

        assert is_read_only_capability("") is False

    def test_unknown_id_defaults_to_write(self) -> None:
        """どちらもマッチしない capability_id は安全側 (write) とみなす."""
        from aegis_ai.llm import is_read_only_capability

        assert is_read_only_capability("weird.unknown.action") is False

    def test_catalog_side_effect_read(self) -> None:
        from aegis_ai.llm import is_read_only_capability

        cat = _FakeCatalog(
            {
                "custom.read": _FakeManifest(
                    "custom.read",
                    risk_level="HIGH_RISK",  # risk_level は HIGH_RISK だが
                    metadata={"side_effect": "read"},  # metadata が read なので OK
                )
            }
        )
        assert is_read_only_capability("custom.read", catalog=cat) is True

    def test_catalog_side_effect_write(self) -> None:
        from aegis_ai.llm import is_read_only_capability

        cat = _FakeCatalog(
            {
                "custom.write": _FakeManifest(
                    "custom.write",
                    risk_level="READ_ONLY",  # risk_level は READ_ONLY だが
                    metadata={"side_effect": "mutate"},  # metadata が mutate なので write
                )
            }
        )
        assert is_read_only_capability("custom.write", catalog=cat) is False

    def test_catalog_risk_level_write(self) -> None:
        from aegis_ai.llm import is_read_only_capability

        cat = _FakeCatalog(
            {
                "custom.action": _FakeManifest(
                    "custom.action", risk_level="HIGH_RISK", metadata={}
                )
            }
        )
        assert is_read_only_capability("custom.action", catalog=cat) is False

    def test_catalog_risk_level_read(self) -> None:
        from aegis_ai.llm import is_read_only_capability

        cat = _FakeCatalog(
            {
                "custom.action": _FakeManifest(
                    "custom.action", risk_level="SAFE_ACTION", metadata={}
                )
            }
        )
        assert is_read_only_capability("custom.action", catalog=cat) is True

    def test_catalog_resolve_failure_falls_through(self) -> None:
        from aegis_ai.llm import is_read_only_capability

        # resolve が raise してもキーワード判定に fall through
        class RaisingCatalog:
            def resolve(self, cap_id: str) -> Any:
                raise RuntimeError("boom")

        # 書き込み capability_id なので False
        assert is_read_only_capability("shell.exec", catalog=RaisingCatalog()) is False
        # 読み取り capability_id なので True
        assert is_read_only_capability("memory.read", catalog=RaisingCatalog()) is True


# ---------------------------------------------------------------------------
# L3Models payloads
# ---------------------------------------------------------------------------
class TestModelsPayloads:
    def test_l3_problem_to_payload(self) -> None:
        from aegis_ai.llm import L3Problem

        p = L3Problem(
            problem="test",
            context={"k": "v"},
            l1_observations=[{"event_id": "e1"}],
            constraints={"max_cost": 0.1},
            reason="r",
        )
        payload = p.to_payload()
        assert payload["problem"] == "test"
        assert payload["context"] == {"k": "v"}
        assert payload["l1_observations"] == [{"event_id": "e1"}]
        assert payload["constraints"] == {"max_cost": 0.1}
        assert payload["reason"] == "r"

    def test_l3_step_to_payload(self) -> None:
        from aegis_ai.llm import L3Step

        s = L3Step(
            order=1,
            capability_id="cap.read",
            args={"x": 1},
            read_only=True,
            reason="r",
            depends_on=[0],
        )
        d = s.__dict__ if hasattr(s, "__dict__") else None
        # dataclass なので直接 dict 変換 (to_payload は plan 経由)
        assert s.order == 1
        assert s.capability_id == "cap.read"
        assert s.read_only is True
        assert s.depends_on == [0]

    def test_l3_plan_read_only(self) -> None:
        from aegis_ai.llm import L3Plan, L3Step

        plan = L3Plan(
            steps=[
                L3Step(order=1, capability_id="cap.read", read_only=True),
                L3Step(order=2, capability_id="cap.list", read_only=True),
            ]
        )
        assert plan.read_only_plan is True

    def test_l3_plan_with_write_step_not_read_only(self) -> None:
        from aegis_ai.llm import L3Plan, L3Step

        plan = L3Plan(
            steps=[
                L3Step(order=1, capability_id="cap.read", read_only=True),
                L3Step(order=2, capability_id="cap.write", read_only=False),
            ]
        )
        assert plan.read_only_plan is False

    def test_l3_result_to_payload(self) -> None:
        from aegis_ai.llm import L3Action, L3Plan, L3Problem, L3Result, L3Step

        r = L3Result(
            problem=L3Problem(problem="p"),
            plan=L3Plan(steps=[L3Step(order=1, capability_id="cap.read", read_only=True)]),
            recommended_action=L3Action.TASK,
            confidence=0.8,
            reasoning_summary="ok",
        )
        p = r.to_payload()
        assert p["problem"]["problem"] == "p"
        assert p["plan"]["steps"][0]["capability_id"] == "cap.read"
        assert p["recommended_action"] == "task"
        assert p["confidence"] == 0.8


# ---------------------------------------------------------------------------
# L3Reasoner.reason()
# ---------------------------------------------------------------------------
class TestReason:
    def _problem(self) -> Any:
        from aegis_ai.llm import L3Problem

        return L3Problem(problem="test", reason="because")

    def test_disabled_returns_none(self) -> None:
        from aegis_ai.llm import L3Reasoner

        r = L3Reasoner(enabled=False)
        assert r.reason(self._problem()) is None

    def test_success_parses_plan(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.llm import L3Action, L3Reasoner

        payload = {
            "plan": {
                "steps": [
                    {
                        "order": 1,
                        "capability_id": "cap.read",
                        "args": {},
                        "read_only": True,
                        "reason": "fetch",
                    },
                    {
                        "order": 2,
                        "capability_id": "memory.search",
                        "args": {"q": "x"},
                        "read_only": True,
                        "reason": "search",
                    },
                ],
                "assumptions": ["a1"],
                "risks": ["r1"],
                "recommendations": ["rec1"],
            },
            "recommended_action": "task",
            "confidence": 0.85,
            "reasoning_summary": "do it",
        }
        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps(payload))])
        _patched_gateway(monkeypatch, fake)
        reasoner = L3Reasoner()
        result = reasoner.reason(self._problem())
        assert result is not None
        assert result.recommended_action == L3Action.TASK
        assert result.confidence == 0.85
        assert len(result.plan.steps) == 2
        assert result.plan.read_only_plan is True
        # layer=L3 を使う
        assert fake.captured[0]["layer"] == "L3"
        assert fake.captured[0]["json_mode"] is True
        assert fake.captured[0]["context_meta"]["caller"] == "l3_reasoner"

    def test_write_steps_downgrade_to_abort(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.llm import L3Action, L3Reasoner

        payload = {
            "plan": {
                "steps": [
                    {
                        "order": 1,
                        "capability_id": "cap.read",
                        "read_only": True,
                    },
                    {
                        "order": 2,
                        "capability_id": "shell.write_file",
                        "read_only": False,
                    },
                ]
            },
            "recommended_action": "task",
            "confidence": 0.9,
            "reasoning_summary": "ok",
        }
        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps(payload))])
        _patched_gateway(monkeypatch, fake)
        reasoner = L3Reasoner()
        result = reasoner.reason(self._problem())
        assert result is not None
        # read_only_only=True なら write step がある plan は ABORT に強制
        assert result.recommended_action == L3Action.ABORT
        assert result.plan.read_only_plan is False

    def test_json_parse_failure_returns_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.llm import L3Reasoner

        fake = _FakeGateway(responses=[_FakeResponse(content="not json {")])
        _patched_gateway(monkeypatch, fake)
        reasoner = L3Reasoner()
        assert reasoner.reason(self._problem()) is None

    def test_gateway_failure_returns_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.llm import L3Reasoner

        fake = _FakeGateway(responses=[_FakeResponse(success=False, error="upstream")])
        _patched_gateway(monkeypatch, fake)
        reasoner = L3Reasoner()
        assert reasoner.reason(self._problem()) is None

    def test_gateway_exception_returns_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.llm import L3Reasoner, l3_reasoner

        class RaisingGateway:
            def request(self, **kwargs: Any) -> Any:
                raise RuntimeError("boom")

        monkeypatch.setattr(
            l3_reasoner.L3Reasoner, "_get_gateway", lambda self: RaisingGateway()
        )
        reasoner = L3Reasoner()
        assert reasoner.reason(self._problem()) is None

    def test_invalid_recommended_action_falls_back_to_abort(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.llm import L3Action, L3Reasoner

        payload = {
            "plan": {"steps": []},
            "recommended_action": "garbage",
            "confidence": 0.5,
        }
        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps(payload))])
        _patched_gateway(monkeypatch, fake)
        reasoner = L3Reasoner()
        result = reasoner.reason(self._problem())
        assert result is not None
        assert result.recommended_action == L3Action.ABORT

    def test_confidence_clamped(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.llm import L3Reasoner

        payload = {
            "plan": {"steps": []},
            "recommended_action": "task",
            "confidence": 5.0,  # 範囲外
        }
        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps(payload))])
        _patched_gateway(monkeypatch, fake)
        reasoner = L3Reasoner()
        result = reasoner.reason(self._problem())
        assert result is not None
        assert 0.0 <= result.confidence <= 1.0
        assert result.confidence == 1.0  # 1.0 にクランプ

    def test_step_read_only_revalidated(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """LLM が read_only=True と嘘をついても is_read_only_capability で再判定される."""
        from aegis_ai.llm import L3Reasoner

        payload = {
            "plan": {
                "steps": [
                    {
                        "order": 1,
                        "capability_id": "shell.write_file",
                        "read_only": True,  # 嘘
                    }
                ]
            },
            "recommended_action": "task",
            "confidence": 0.5,
        }
        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps(payload))])
        _patched_gateway(monkeypatch, fake)
        reasoner = L3Reasoner()
        result = reasoner.reason(self._problem())
        assert result is not None
        # shell.write_file は write capability → read_only=False に再判定
        assert result.plan.steps[0].read_only is False
        # 全体プランは read_only ではない → ABORT に downgrade
        from aegis_ai.llm import L3Action

        assert result.recommended_action == L3Action.ABORT


# ---------------------------------------------------------------------------
# event publish
# ---------------------------------------------------------------------------
class TestEventPublish:
    def _problem(self) -> Any:
        from aegis_ai.llm import L3Problem

        return L3Problem(problem="p")

    def test_l3_invoked_and_completed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.llm import L3Reasoner

        published: list[tuple[str, dict[str, Any]]] = []

        def publisher(event_type: str, payload: dict[str, Any]) -> None:
            published.append((event_type, payload))

        payload = {
            "plan": {"steps": []},
            "recommended_action": "task",
            "confidence": 0.5,
        }
        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps(payload))])
        _patched_gateway(monkeypatch, fake)
        reasoner = L3Reasoner(event_publisher=publisher)
        reasoner.reason(self._problem())
        types = [t for t, _ in published]
        assert "l3.invoked" in types
        assert "l3.completed" in types

    def test_l3_failed_on_gateway_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.llm import L3Reasoner

        published: list[tuple[str, dict[str, Any]]] = []

        def publisher(event_type: str, payload: dict[str, Any]) -> None:
            published.append((event_type, payload))

        fake = _FakeGateway(responses=[_FakeResponse(success=False, error="upstream")])
        _patched_gateway(monkeypatch, fake)
        reasoner = L3Reasoner(event_publisher=publisher)
        reasoner.reason(self._problem())
        types = [t for t, _ in published]
        assert "l3.invoked" in types
        assert "l3.failed" in types

    def test_l3_failed_on_parse_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.llm import L3Reasoner

        published: list[tuple[str, dict[str, Any]]] = []

        def publisher(event_type: str, payload: dict[str, Any]) -> None:
            published.append((event_type, payload))

        fake = _FakeGateway(responses=[_FakeResponse(content="not json")])
        _patched_gateway(monkeypatch, fake)
        reasoner = L3Reasoner(event_publisher=publisher)
        reasoner.reason(self._problem())
        types = [t for t, _ in published]
        assert "l3.failed" in types


# ---------------------------------------------------------------------------
# L2AutonomousMind.escalate_to_l3
# ---------------------------------------------------------------------------
class TestL2EscalateToL3:
    def test_disabled_returns_none(self) -> None:
        from aegis_ai.autonomous import L2AutonomousMind

        mind = L2AutonomousMind(enabled=False)
        assert mind.escalate_to_l3("p") is None

    def test_success_returns_l3_result(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from aegis_ai.autonomous import L2AutonomousMind
        from aegis_ai.llm import L3Action

        payload = {
            "plan": {"steps": []},
            "recommended_action": "task",
            "confidence": 0.7,
        }
        fake = _FakeGateway(responses=[_FakeResponse(content=json.dumps(payload))])
        _patched_gateway(monkeypatch, fake)
        mind = L2AutonomousMind()
        result = mind.escalate_to_l3("complex problem", reason="low confidence")
        assert result is not None
        assert result.recommended_action == L3Action.TASK
        assert result.problem.problem == "complex problem"
        assert result.problem.reason == "low confidence"
        # layer=L3 経由で呼ばれた
        assert fake.captured[0]["layer"] == "L3"


# ---------------------------------------------------------------------------
# package exports
# ---------------------------------------------------------------------------
class TestPackageExports:
    def test_llm_package_exports_l3(self) -> None:
        import aegis_ai.llm as llm_mod

        assert hasattr(llm_mod, "L3Reasoner")
        assert hasattr(llm_mod, "L3Problem")
        assert hasattr(llm_mod, "L3Result")
        assert hasattr(llm_mod, "L3Plan")
        assert hasattr(llm_mod, "L3Step")
        assert hasattr(llm_mod, "L3Action")
        assert hasattr(llm_mod, "is_read_only_capability")
