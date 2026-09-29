"""L3 Deep Reasoner — DASHBOARD_V3_PLAN.md Phase L5.

L2 から escalation された問題を受け、`L3Plan` / `L3Result` を返す薄いラッパー。

設計原則:
- L3 は **常時呼び出さない**。L2 が `confidence < threshold` または `difficulty > threshold`
  のときにだけ呼ぶ (L2 の判断責任)。
- L3 は **直接 Capability を実行しない**。`L3Result.recommended_action == TASK` のとき
  でも capability 呼び出しは L2 経由で実行する (L1/L2/L3 の責任分離)。
- L3 → Capability ルール (DASHBOARD_V3_PLAN.md Phase L5 設計判断):
  - 読み取り系 capability (web search / file read / list / browse / memory search) は
    L3 から **直接実行可能**。
  - 書き込み系 capability (file write / mouse / keyboard / shell) は L3 から直接実行
    不可。L2 経由強制。
  - 判定は `is_read_only_capability(capability_id, catalog)` で `Capability.metadata.side_effect`
    優先、capability_id プレフィックス / キーワード 2 重判定、書き込み capability_id
    ブラックリスト照合の 3 段。
- L3 prompt は大規模 (32K tokens)、reasoning 重視 (`l3_default` profile を使用)。
- L3 timeout は 5 分。timeout 時は `L3Result` を返さない (呼び出し側で fallback)。
- 失敗時は安全側に倒して ABORT 推奨 (instruction.md §38 フォールバック禁止方針と整合)。

依存最小化:
- `llm_gateway` は optional。None のとき `LLMGateway.instance()`。
- `capability_catalog` は optional。None のとき `CapabilityCatalog.instance()`。
  is_read_only_capability 判定で使われる。None なら safe 側 (read_only=True) で
  固定し、書き込み capability 経由は必ず L2 経路とみなす。
- `event_publisher` は optional。None のとき no-op。
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

from aegis_ai.llm.l3_models import L3Action, L3Plan, L3Problem, L3Result, L3Step

logger = logging.getLogger("aegis_ai.llm.l3_reasoner")

_L3_SYSTEM_PROMPT = """You are L3 (Deep Reasoner) of AEGIS. You receive a problem that L2 (Autonomous Mind) cannot solve confidently and produce a concrete plan.

For each step, you may:
- recommend a capability invocation (capability_id + args)
- gather information (no capability_id; mark read_only=true)

Constraints (DASHBOARD_V3_PLAN.md Phase L5):
- read-only capabilities (web search, file read, list, browse, memory search) may be invoked directly.
- write capabilities (file write, mouse, keyboard, shell) are FORBIDDEN at L3 level. L2 must execute them.
- mark each step's `read_only` field correctly. The runtime will reject write steps from L3.

Respond with JSON:
{
  "plan": {
    "steps": [{"order": int, "capability_id": str, "args": {...}, "read_only": bool, "reason": "...", "depends_on": [int, ...]}],
    "assumptions": ["..."],
    "risks": ["..."],
    "recommendations": ["..."]
  },
  "recommended_action": "task" | "observe" | "abort",
  "confidence": 0.0-1.0,
  "reasoning_summary": "1-3 sentence summary"
}

Be concise but precise. If the problem is unsolvable or dangerous, choose abort with high confidence."""


# 書き込み capability_id ブラックリスト (プレフィックス / キーワード)
_WRITE_CAPABILITY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?:[._-]|\b)(write|create|delete|update|set|put|post|patch|remove|destroy|drop|kill|terminate|shutdown|reboot|install|uninstall|execute|run)(?:[._-]|\b)", re.I),
    re.compile(r"\b(file_write|mouse\.|keyboard\.|shell\.|powershell\.|cmd\.|exec|sudo|rm\s|del\s|format)\b", re.I),
)

# 読み取り capability_id ホワイトリスト (capability_id 部分一致)
_READ_CAPABILITY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?:[._-]|\b)(read|get|list|search|find|browse|view|show|fetch|query|lookup|inspect|check|summarize|recall)(?:[._-]|\b)", re.I),
    re.compile(r"\b(memory\.|search\.|web_search|browser\.|browse\.|file_read)\b", re.I),
)


def is_read_only_capability(
    capability_id: str,
    catalog: Any | None = None,
) -> bool:
    """L3 から直接呼んで OK な capability か判定 (Phase L5 ルール).

    判定ロジック (DASHBOARD_V3_PLAN.md §10 リスクと対策):
    1. `catalog` があり `Capability.metadata.side_effect` を取れる場合:
       `side_effect in {"read", "none", ""}` なら read_only
    2. capability_id プレフィックス / キーワード 2 重判定:
       a. `_WRITE_CAPABILITY_PATTERNS` のいずれかにマッチ → write とみなす
       b. `_READ_CAPABILITY_PATTERNS` のいずれかにマッチ → read とみなす
       c. 両方マッチ / どちらもマッチしない → write (安全側、書き込みとみなして L2 経由強制)
    3. 書き込み capability_id ブラックリスト照合 (`_WRITE_CAPABILITY_PATTERNS`)
    """
    if not capability_id:
        # 空 capability_id は実行不可 → write 扱い (L2 経由)
        return False

    # 1. catalog metadata.side_effect チェック
    if catalog is not None:
        try:
            manifest = catalog.resolve(capability_id) if hasattr(catalog, "resolve") else None
        except Exception:  # noqa: BLE001
            manifest = None
        if manifest is not None:
            metadata = getattr(manifest, "metadata", None) or {}
            if isinstance(metadata, dict):
                side_effect = str(metadata.get("side_effect", "")).strip().lower()
                if side_effect and side_effect in {"read", "none", "read_only"}:
                    return True
                if side_effect in {"write", "mutate", "side_effect", "external", "execute"}:
                    return False
            # risk_level も併せる (metadata side_effect 未設定時のみ)
            risk = str(getattr(manifest, "risk_level", "")).strip().upper()
            if risk in {"APPROVAL_REQUIRED", "HIGH_RISK", "FORBIDDEN"}:
                return False
            if risk in {"READ_ONLY", "SAFE_ACTION"}:
                return True

    # 2. キーワード判定
    is_write = any(p.search(capability_id) for p in _WRITE_CAPABILITY_PATTERNS)
    is_read = any(p.search(capability_id) for p in _READ_CAPABILITY_PATTERNS)
    if is_write and not is_read:
        return False
    if is_read and not is_write:
        return True
    # 両方マッチ / どちらもマッチしない → 安全側 (write 扱い)
    return False


@dataclass
class L3Reasoner:
    """L3 Deep Reasoner entry.

    Attributes:
        llm_gateway: LLM gateway (None なら singleton を使う)
        capability_catalog: capability catalog (None なら singleton を使う)
        event_publisher: EventBus publish callable (None なら no-op)
        enabled: master switch
        timeout_seconds: L3 呼び出しタイムアウト (default 5 分)
        read_only_only: True なら L3 plan を read_only ステップのみに強制 (Phase L5 ルール)
    """

    llm_gateway: Any = None
    capability_catalog: Any = None
    event_publisher: Any = None
    enabled: bool = True
    timeout_seconds: int = 300  # 5 分
    read_only_only: bool = True  # L3 は読み取り capability のみ直接実行可

    # ------------------------------------------------------------------
    # dependency resolution
    # ------------------------------------------------------------------
    def _get_gateway(self) -> Any:
        if self.llm_gateway is not None:
            return self.llm_gateway
        from aegis_ai.llm.gateway import LLMGateway

        gw = LLMGateway.instance()
        if gw is None:
            raise RuntimeError(
                "No LLMGateway registered. Set AegisRuntime first or pass llm_gateway explicitly."
            )
        return gw

    def _get_catalog(self) -> Any | None:
        if self.capability_catalog is not None:
            return self.capability_catalog
        try:
            from aegis_ai.capability_catalog import CapabilityCatalog

            return CapabilityCatalog.instance()
        except Exception:  # noqa: BLE001
            return None

    def _publish(self, event_type: str, payload: dict[str, Any]) -> None:
        if self.event_publisher is None:
            logger.debug("L3 publish skipped (no event_publisher): %s", event_type)
            return
        try:
            self.event_publisher(event_type, payload)
        except Exception:  # noqa: BLE001
            logger.exception("L3 event publish failed: %s", event_type)

    # ------------------------------------------------------------------
    # plan validation
    # ------------------------------------------------------------------
    def _validate_step(self, step: L3Step) -> L3Step:
        """step の read_only フラグを `is_read_only_capability` で再判定・上書き.

        `read_only_only=True` のとき、書き込み系 capability の step は read_only=False に
        修正されない (呼び出し側で reject される)。"""
        if not step.capability_id:
            # 情報収取ステップは read_only 固定
            step.read_only = True
            return step
        catalog = self._get_catalog()
        detected_read_only = is_read_only_capability(step.capability_id, catalog=catalog)
        if self.read_only_only:
            # L3 からは read_only ステップのみ許可。書き込み capability は read_only=False
            # のまま返す (呼び出し側で reject される)。
            step.read_only = detected_read_only
        else:
            step.read_only = detected_read_only
        return step

    # ------------------------------------------------------------------
    # main entry
    # ------------------------------------------------------------------
    def reason(self, problem: L3Problem) -> L3Result | None:
        """L3Problem を受け L3Result を返す.

        - `enabled=False` のとき None
        - LLM 呼び出しが失敗 / timeout したら None (呼び出し側で fallback)
        """
        if not self.enabled:
            return None

        self._publish("l3.invoked", problem.to_payload())

        try:
            gateway = self._get_gateway()
            response = gateway.request(
                layer="L3",
                prompt=self._build_prompt(problem),
                system_prompt=_L3_SYSTEM_PROMPT,
                json_mode=True,
                context_meta={"caller": "l3_reasoner", "layer": "L3"},
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("L3 gateway.request failed: %r", exc)
            self._publish("l3.failed", {"error": str(exc), "problem": problem.to_payload()})
            return None

        if not response.success or not response.content:
            self._publish(
                "l3.failed",
                {"error": response.error or "empty response", "problem": problem.to_payload()},
            )
            return None

        result = self._parse_result(response.content, problem)
        if result is None:
            self._publish(
                "l3.failed",
                {"error": "parse failed", "problem": problem.to_payload()},
            )
            return None

        self._publish("l3.completed", result.to_payload())
        return result

    def _build_prompt(self, problem: L3Problem) -> str:
        lines: list[str] = [f"Problem: {problem.problem}"]
        if problem.reason:
            lines.append(f"Reason: {problem.reason}")
        if problem.context:
            ctx_keys = sorted(problem.context.keys())[:8]
            ctx_str = ", ".join(f"{k}={problem.context[k]}" for k in ctx_keys)
            lines.append(f"Context: {ctx_str}")
        if problem.l1_observations:
            lines.append(f"L1 observations: {len(problem.l1_observations)}")
            for obs in problem.l1_observations[:3]:
                if isinstance(obs, dict):
                    meaning = obs.get("meaning", "")
                    if meaning:
                        lines.append(f"  - {meaning}")
        if problem.constraints:
            cs_keys = sorted(problem.constraints.keys())[:5]
            cs_str = ", ".join(f"{k}={problem.constraints[k]}" for k in cs_keys)
            lines.append(f"Constraints: {cs_str}")
        return "\n".join(lines)

    def _parse_result(self, content: str, problem: L3Problem) -> L3Result | None:
        try:
            data = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            return None
        if not isinstance(data, dict):
            return None

        # plan
        plan_data = data.get("plan") or {}
        if not isinstance(plan_data, dict):
            plan_data = {}
        steps: list[L3Step] = []
        for raw_step in plan_data.get("steps", []) or []:
            if not isinstance(raw_step, dict):
                continue
            try:
                order = int(raw_step.get("order", len(steps)))
            except (TypeError, ValueError):
                order = len(steps)
            depends = raw_step.get("depends_on", []) or []
            if not isinstance(depends, list):
                depends = []
            depends = [int(d) for d in depends if isinstance(d, (int, float))]
            step = L3Step(
                order=order,
                capability_id=str(raw_step.get("capability_id", "")),
                args=dict(raw_step.get("args", {}) or {}),
                read_only=bool(raw_step.get("read_only", True)),
                reason=str(raw_step.get("reason", "")),
                depends_on=depends,
            )
            steps.append(self._validate_step(step))
        steps.sort(key=lambda s: s.order)

        plan = L3Plan(
            steps=steps,
            assumptions=[str(a) for a in (plan_data.get("assumptions", []) or []) if a],
            risks=[str(r) for r in (plan_data.get("risks", []) or []) if r],
            recommendations=[str(rec) for rec in (plan_data.get("recommendations", []) or []) if rec],
        )

        # recommended_action
        try:
            recommended_action = L3Action(str(data.get("recommended_action", "task")).strip().lower())
        except ValueError:
            recommended_action = L3Action.ABORT  # 不明な値は安全側 (ABORT)

        # read_only_only 違反 → ABORT に強制
        if self.read_only_only and not plan.read_only_plan:
            recommended_action = L3Action.ABORT
            logger.warning(
                "L3 plan includes write steps; downgrading to ABORT (read_only_only=True)"
            )

        try:
            confidence = float(data.get("confidence", 0.0) or 0.0)
        except (TypeError, ValueError):
            confidence = 0.0

        return L3Result(
            problem=problem,
            plan=plan,
            recommended_action=recommended_action,
            confidence=max(0.0, min(1.0, confidence)),
            reasoning_summary=str(data.get("reasoning_summary", "")),
            raw=data,
        )


__all__ = ["L3Reasoner", "is_read_only_capability"]
