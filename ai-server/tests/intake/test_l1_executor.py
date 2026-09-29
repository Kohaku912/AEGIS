"""L1 Executor テスト — DASHBOARD_V3_PLAN.md Phase L3.

`L1Executor` のリスク判定 / 実行 / 結果 wrap を検証する。
`ToolBroker` / `CapabilityCatalog` は mock で代替し、AEGIS 本体ロジックを
ピンポイントでテストする (統合は他テストの責任)。
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import pytest


@dataclass
class _FakeManifest:
    capability_id: str
    risk_level: str = "READ_ONLY"


@dataclass
class _FakeCatalog:
    manifests: dict[str, _FakeManifest]

    def resolve(self, cap_id: str) -> _FakeManifest | None:
        return self.manifests.get(cap_id)


@dataclass
class _FakeResponse:
    success: bool = True
    result: Any = None
    error: str | None = None


@dataclass
class _FakeBroker:
    responses: dict[str, _FakeResponse]
    captured: list[dict[str, Any]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.captured is None:
            self.captured = []

    def execute(self, request: Any) -> _FakeResponse:  # pragma: no cover — patched
        cap_id = getattr(request, "capability_id", "?")
        ctx = getattr(request, "metadata", None) or getattr(request, "context", None) or {}
        self.captured.append({"capability_id": cap_id, "context": dict(ctx)})
        if cap_id in self.responses:
            return self.responses[cap_id]
        return _FakeResponse(success=False, error="not_found")


def _make_broker(**responses: Any) -> _FakeBroker:
    return _FakeBroker(
        responses={
            cap: (resp if isinstance(resp, _FakeResponse) else _FakeResponse(success=True, result=resp))
            for cap, resp in responses.items()
        }
    )


def _patched_broker(monkeypatch: pytest.MonkeyPatch, fake: _FakeBroker) -> None:
    """L1Executor._get_broker を fake 返却に差し替え."""
    from aegis_ai.intake import l1_executor

    monkeypatch.setattr(l1_executor.L1Executor, "_get_broker", lambda self: fake)


# ---------------------------------------------------------------------------
# import smoke
# ---------------------------------------------------------------------------
class TestImports:
    def test_l1_executor_importable(self) -> None:
        from aegis_ai.intake import L1Executor

        assert L1Executor is not None

    def test_l1_action_result_importable(self) -> None:
        from aegis_ai.intake import L1ActionResult

        assert L1ActionResult is not None
        result = L1ActionResult(capability_id="x", success=True, result={"v": 1})
        assert result.capability_id == "x"
        payload = result.to_payload()
        assert payload["capability_id"] == "x"
        assert payload["success"] is True
        assert payload["bypassed_approval"] is True


# ---------------------------------------------------------------------------
# is_callable / get_risk_level / resolve
# ---------------------------------------------------------------------------
class TestRiskChecks:
    def _make(self, *, catalog: _FakeCatalog, **kw: Any):  # type: ignore[no-untyped-def]
        from aegis_ai.intake import L1Executor

        return L1Executor(capability_catalog=catalog, **kw)

    def test_is_callable_low_risk(self) -> None:
        cat = _FakeCatalog({"cap.a": _FakeManifest("cap.a", "READ_ONLY")})
        ex = self._make(catalog=cat)
        assert ex.is_callable("cap.a") is True

    def test_is_callable_safe_action(self) -> None:
        cat = _FakeCatalog({"cap.a": _FakeManifest("cap.a", "SAFE_ACTION")})
        ex = self._make(catalog=cat)
        assert ex.is_callable("cap.a") is True

    def test_not_callable_approval_required(self) -> None:
        cat = _FakeCatalog({"cap.a": _FakeManifest("cap.a", "APPROVAL_REQUIRED")})
        ex = self._make(catalog=cat)
        assert ex.is_callable("cap.a") is False

    def test_not_callable_high_risk(self) -> None:
        cat = _FakeCatalog({"cap.a": _FakeManifest("cap.a", "HIGH_RISK")})
        ex = self._make(catalog=cat)
        assert ex.is_callable("cap.a") is False

    def test_not_callable_unknown(self) -> None:
        cat = _FakeCatalog({})
        ex = self._make(catalog=cat)
        assert ex.is_callable("cap.missing") is False

    def test_disabled_blocks_all(self) -> None:
        cat = _FakeCatalog({"cap.a": _FakeManifest("cap.a", "READ_ONLY")})
        ex = self._make(catalog=cat, enabled=False)
        assert ex.is_callable("cap.a") is False

    def test_get_risk_level_normalizes(self) -> None:
        cat = _FakeCatalog(
            {
                "cap.low": _FakeManifest("cap.low", "READ_ONLY"),
                "cap.safe": _FakeManifest("cap.safe", "SAFE_ACTION"),
                "cap.med": _FakeManifest("cap.med", "APPROVAL_REQUIRED"),
            }
        )
        ex = self._make(catalog=cat)
        assert ex.get_risk_level("cap.low") == "READ_ONLY"
        assert ex.get_risk_level("cap.safe") == "SAFE_ACTION"
        assert ex.get_risk_level("cap.med") == "APPROVAL_REQUIRED"
        assert ex.get_risk_level("cap.missing") is None

    def test_custom_allowed_risk_levels(self) -> None:
        # medium も許可する設定
        cat = _FakeCatalog(
            {
                "cap.low": _FakeManifest("cap.low", "READ_ONLY"),
                "cap.med": _FakeManifest("cap.med", "APPROVAL_REQUIRED"),
            }
        )
        from aegis_ai.intake import L1Executor

        ex = L1Executor(
            capability_catalog=cat,
            allowed_risk_levels=frozenset({"low", "medium"}),
        )
        assert ex.is_callable("cap.low") is True
        assert ex.is_callable("cap.med") is True


# ---------------------------------------------------------------------------
# execute() の挙動
# ---------------------------------------------------------------------------
class TestExecute:
    def _make(self, *, catalog: _FakeCatalog, **kw: Any):  # type: ignore[no-untyped-def]
        from aegis_ai.intake import L1Executor

        return L1Executor(capability_catalog=catalog, **kw)

    def test_execute_low_risk_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cat = _FakeCatalog({"cap.read": _FakeManifest("cap.read", "READ_ONLY")})
        broker = _make_broker(**{"cap.read": {"ok": True}})
        _patched_broker(monkeypatch, broker)
        ex = self._make(catalog=cat)

        result = ex.execute("cap.read", {"x": 1}, event_id="ev-1")
        assert result.success is True
        assert result.capability_id == "cap.read"
        assert result.event_id == "ev-1"
        assert result.risk_level == "READ_ONLY"
        assert result.error is None
        assert result.bypassed_approval is True
        assert result.duration_ms >= 0
        # broker に context 付きで渡っている
        assert len(broker.captured) == 1
        assert broker.captured[0]["capability_id"] == "cap.read"
        ctx = broker.captured[0]["context"]
        assert ctx.get("caller") == "l1"
        assert ctx.get("layer") == "L1"

    def test_execute_blocks_high_risk_without_calling_broker(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cat = _FakeCatalog({"cap.danger": _FakeManifest("cap.danger", "HIGH_RISK")})
        broker = _make_broker()
        _patched_broker(monkeypatch, broker)
        ex = self._make(catalog=cat)

        result = ex.execute("cap.danger", {}, event_id="ev-2")
        assert result.success is False
        assert "not callable from L1" in (result.error or "")
        assert result.risk_level == "HIGH_RISK"
        assert broker.captured == []

    def test_execute_unknown_capability(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cat = _FakeCatalog({})
        broker = _make_broker()
        _patched_broker(monkeypatch, broker)
        ex = self._make(catalog=cat)

        result = ex.execute("cap.missing", {}, event_id="ev-3")
        assert result.success is False
        assert "not callable from L1" in (result.error or "")
        assert result.risk_level == "unknown"
        assert broker.captured == []

    def test_execute_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cat = _FakeCatalog({"cap.read": _FakeManifest("cap.read", "READ_ONLY")})
        broker = _make_broker(cap={"ok": True})
        _patched_broker(monkeypatch, broker)
        ex = self._make(catalog=cat, enabled=False)

        result = ex.execute("cap.read", {}, event_id="ev-4")
        assert result.success is False
        assert "disabled" in (result.error or "")
        assert broker.captured == []

    def test_execute_broker_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cat = _FakeCatalog({"cap.read": _FakeManifest("cap.read", "READ_ONLY")})

        class RaisingBroker:
            def execute(self, request: Any) -> Any:
                raise RuntimeError("boom")

        from aegis_ai.intake import l1_executor

        monkeypatch.setattr(l1_executor.L1Executor, "_get_broker", lambda self: RaisingBroker())
        ex = self._make(catalog=cat)

        result = ex.execute("cap.read", {}, event_id="ev-5")
        assert result.success is False
        assert "broker.execute raised" in (result.error or "")
        assert "boom" in (result.error or "")

    def test_execute_broker_returns_failure(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cat = _FakeCatalog({"cap.read": _FakeManifest("cap.read", "READ_ONLY")})
        broker = _make_broker(**{"cap.read": _FakeResponse(success=False, error="denied")})
        _patched_broker(monkeypatch, broker)
        ex = self._make(catalog=cat)

        result = ex.execute("cap.read", {}, event_id="ev-6")
        assert result.success is False
        assert result.error == "denied"

    def test_execute_result_wraps_non_dict(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cat = _FakeCatalog({"cap.read": _FakeManifest("cap.read", "READ_ONLY")})
        broker = _make_broker(**{"cap.read": _FakeResponse(success=True, result=[1, 2, 3])})
        _patched_broker(monkeypatch, broker)
        ex = self._make(catalog=cat)

        result = ex.execute("cap.read", {}, event_id="ev-7")
        assert result.success is True
        assert result.result == {"value": [1, 2, 3]}


# ---------------------------------------------------------------------------
# integration: intake/__init__.py で export されている
# ---------------------------------------------------------------------------
class TestPackageExports:
    def test_intake_package_exports_l1_executor(self) -> None:
        import aegis_ai.intake as intake

        assert hasattr(intake, "L1Executor")
        assert "L1Executor" in intake.__all__

    def test_intake_package_exports_l1_action_result(self) -> None:
        import aegis_ai.intake as intake

        assert hasattr(intake, "L1ActionResult")
        assert "L1ActionResult" in intake.__all__
