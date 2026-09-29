"""L1 Executor — DASHBOARD_V3_PLAN.md Phase L3.

L1 (常時稼働 / 知覚 / ルーティング) 層から Capability を直接呼び出す薄いファサード。

設計原則 (DASHBOARD_V3_PLAN.md §6 / instruction.md §38):
- L1 から呼び出せる Capability は **risk="low"** のみ。
  Policy engine を経由しない前段リスクチェック (`is_callable` / `get_risk_level`)。
  ただし実際の実行は `ToolBroker.execute()` を経由するため、Policy / Approval / Audit
  の最終判定は **broker 側に委ねる**。L1 executor は「L1 から直接 invoke して良い
  Capability か」のみ保証する。
- 危険な Capability (risk="medium" 以上) は L1 から実行しない (False 返却)。
  L2 (Autonomous Mind) 経由で実行する必要がある。
- 実行結果は `L1ActionResult` に wrap され、EventBus に `l1.capability.completed`
  として publish できる構造 (Phase L3 DoD)。
- 依存最小化: `capability_catalog` / `tool_broker` は optional。
  None のときは `CapabilityCatalog.instance()` / `ToolBroker.instance()` にフォールバック。
  ただし agent bypass リスクを下げるため singleton 経由を推奨 (instruction.md §38.1)。
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from aegis_ai.intake.l1_models import L1ActionResult

logger = logging.getLogger("aegis_ai.intake.l1_executor")

# L1 から直接呼び出して良い risk_level (catalog 表記)。
# デフォルトは "low" / "safe" (両方 READ_ONLY / SAFE_ACTION 相当)。
# 危険な capability (APPROVAL_REQUIRED / HIGH_RISK / FORBIDDEN) は L2 経由必須。
_DEFAULT_ALLOWED_RISK: frozenset[str] = frozenset({"low", "safe"})


@dataclass
class L1Executor:
    """L1 → Capability 薄い実行ファサード.

    Attributes:
        capability_catalog: 解決用 catalog (None なら singleton を使う)
        tool_broker: 実行用 broker (None なら singleton を使う)
        allowed_risk_levels: L1 から直接呼んで OK な risk level の集合
        enabled: master switch. False のとき execute は常に失敗を返す
    """

    capability_catalog: Any = None  # aegis_ai.capability_catalog.CapabilityCatalog | None
    tool_broker: Any = None  # tool_broker.ToolBroker | None
    allowed_risk_levels: frozenset[str] = field(default_factory=lambda: _DEFAULT_ALLOWED_RISK)
    enabled: bool = True

    # ------------------------------------------------------------------
    # catalog / broker resolution
    # ------------------------------------------------------------------
    def _get_catalog(self) -> Any:
        if self.capability_catalog is not None:
            return self.capability_catalog
        from aegis_ai.capability_catalog import CapabilityCatalog

        catalog = CapabilityCatalog.instance()
        if catalog is None:
            raise RuntimeError(
                "No CapabilityCatalog registered. "
                "Set AegisRuntime first or pass capability_catalog explicitly."
            )
        return catalog

    def _get_broker(self) -> Any:
        if self.tool_broker is not None:
            return self.tool_broker
        from tool_broker import ToolBroker

        broker = ToolBroker.instance()
        if broker is None:
            # Fallback for isolated tests: fresh broker with empty registry.
            from aegis_ai.tool_registry import ToolRegistry

            return ToolBroker(registry=ToolRegistry())
        return broker

    # ------------------------------------------------------------------
    # risk-aware capability resolution
    # ------------------------------------------------------------------
    def resolve(self, capability_id: str) -> Any | None:
        """capability_id を catalog で解決. 不存在 / alias は None."""
        catalog = self._get_catalog()
        return catalog.resolve(capability_id)

    def get_risk_level(self, capability_id: str) -> str | None:
        """capability の risk_level を取得. 不存在は None."""
        manifest = self.resolve(capability_id)
        if manifest is None:
            return None
        # CapabilityManifest は risk_level (enum name) / manifest_risk_level を持つ
        return getattr(manifest, "risk_level", None) or getattr(manifest, "manifest_risk_level", None)

    def is_callable(self, capability_id: str) -> bool:
        """L1 から直接呼び出して良い capability か.

        - catalog に存在
        - risk_level が `allowed_risk_levels` 内
        - executor enabled
        """
        if not self.enabled:
            return False
        risk = self.get_risk_level(capability_id)
        if risk is None:
            return False
        # risk_level は READ_ONLY / SAFE_ACTION / APPROVAL_REQUIRED / HIGH_RISK / FORBIDDEN
        # allowed_risk_levels は "low" / "safe" 表記なので、catalog 表記に正規化して照合。
        return self._normalize_risk(risk) in self._normalize_allowed()

    def _normalize_risk(self, risk: str) -> str:
        """catalog 表記 (READ_ONLY 等) を LLM 表記 (low / safe / etc.) に正規化."""
        if not risk:
            return ""
        r = str(risk).strip().upper()
        if r in {"READ_ONLY"}:
            return "low"
        if r in {"SAFE_ACTION"}:
            return "safe"
        if r in {"APPROVAL_REQUIRED"}:
            return "medium"
        if r in {"HIGH_RISK"}:
            return "high"
        if r in {"FORBIDDEN"}:
            return "critical"
        return str(risk).strip().lower()

    def _normalize_allowed(self) -> frozenset[str]:
        return frozenset(self._normalize_risk(r) for r in self.allowed_risk_levels)

    # ------------------------------------------------------------------
    # execution
    # ------------------------------------------------------------------
    def execute(
        self,
        capability_id: str,
        args: dict[str, Any] | None = None,
        *,
        event_id: str = "",
    ) -> L1ActionResult:
        """capability を L1 から直接実行.

        - `is_callable(capability_id)` が False なら即失敗 (L2 経由強制)
        - 実実行は `ToolBroker.execute()` を経由 (Policy / Approval / Audit 適用)
        - 結果を `L1ActionResult` に wrap
        """
        if not self.enabled:
            return L1ActionResult(
                capability_id=capability_id,
                event_id=event_id,
                success=False,
                error="L1Executor disabled",
                risk_level="",
            )

        if not self.is_callable(capability_id):
            risk = self.get_risk_level(capability_id) or "unknown"
            return L1ActionResult(
                capability_id=capability_id,
                event_id=event_id,
                success=False,
                error=(
                    f"Capability '{capability_id}' is not callable from L1 "
                    f"(risk_level={risk}; allowed={sorted(self.allowed_risk_levels)}). "
                    "Use L2 for medium/high risk capabilities."
                ),
                risk_level=risk,
            )

        args = dict(args or {})
        broker = self._get_broker()
        from tool_broker import ToolExecutionRequest

        request = ToolExecutionRequest(
            capability_id=capability_id,
            arguments=args,
        )
        # context に caller=l1 を必ず残す (Audit / policy 判定用)
        # ToolExecutionRequest は `metadata` dict を持つのでそこに layer 識別を残す。
        if hasattr(request, "metadata") and isinstance(request.metadata, dict):
            request.metadata.setdefault("caller", "l1")
            request.metadata.setdefault("layer", "L1")
        elif hasattr(request, "context") and isinstance(request.context, dict):
            request.context.setdefault("caller", "l1")
            request.context.setdefault("layer", "L1")

        risk = self.get_risk_level(capability_id) or "low"
        started = time.monotonic()
        try:
            response = broker.execute(request)
        except Exception as exc:  # noqa: BLE001 — surface to LLM as L1ActionResult
            logger.exception("L1Executor.execute failed for %s", capability_id)
            return L1ActionResult(
                capability_id=capability_id,
                event_id=event_id,
                success=False,
                error=f"broker.execute raised: {exc!r}",
                risk_level=risk,
                duration_ms=int((time.monotonic() - started) * 1000),
            )
        duration_ms = int((time.monotonic() - started) * 1000)

        # ToolBroker response: status / result / error 等を持つ想定
        success = bool(getattr(response, "success", False))
        result: dict[str, Any] | None = getattr(response, "result", None)
        if result is not None and not isinstance(result, dict):
            result = {"value": result}
        error: str | None = getattr(response, "error", None) if not success else None
        return L1ActionResult(
            capability_id=capability_id,
            event_id=event_id,
            success=success,
            result=result,
            error=error,
            risk_level=risk,
            duration_ms=duration_ms,
            bypassed_approval=True,  # L1 直接実行 (risk=low)
        )


__all__ = ["L1Executor"]
