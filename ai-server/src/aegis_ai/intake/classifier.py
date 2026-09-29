"""Intake classifier — Phase 4 (instruction.md §11, §36).

小型 LLM (既定 `local_chat`) で event を分類し、`IntakeResult` を返す。

設計判断:
- LLM 呼び出しはオプション。`_router` 未注入時は **フォールバック** で
  `requires_agent=False` を返す (DoD: LLM 無しでも intake は動く).
- LLM プロンプトは最小: 「この observation は Agent (OpenHands) を起動する
  価値があるか? 0-1 のスコアと理由だけ返せ」. レスポンスは JSON.
- レスポンスは **緩く** パースする. JSON 失敗時は `fallback_requires_agent`
  設定に従う.
- import 境界: openhands SDK には触らない. LLM 呼び出しは
  `LLMRouter.route(LLMRequest(...))` 経由.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from aegis_ai.intake.models import IntakeDecision, IntakeResult
from aegis_ai.llm.json_utils import extract_json_object

logger = logging.getLogger("aegis_ai.intake.classifier")


def _safe_float(value: Any, default: float) -> float:
    """Coerce an LLM-provided value to ``float`` without ever raising.

    LLM JSON is untrusted input: a field may arrive as ``null`` or as a
    non-numeric string (e.g. ``"high"``). Returning the default keeps the
    intake pipeline alive instead of crashing on a malformed response.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

# classifier 用プロンプト (instruction.md §11 を簡略化).
# 「Agent delegate に進む価値があるか?」を 0-1 で聞く.
_CLASSIFIER_PROMPT = (
    "You are an intake filter for an autonomous AI assistant.\n"
    "Decide if the following observation requires delegating to a full Agent "
    "(OpenHands, multi-step, file/shell access) or can be handled by a small "
    "LLM task interpreter.\n\n"
    "Observation:\n{observation}\n\n"
    "Respond ONLY with JSON in this exact form:\n"
    "{{\n"
    '  "requires_agent_score": <float 0-1>,\n'
    '  "importance": <float 0-1>,\n'
    '  "novelty": <float 0-1>,\n'
    '  "task_type": "<one of: research_summary, code_generation, classification, '
    'conversation, observation, command>",\n'
    '  "capabilities": [<canonical capability_id strings>],\n'
    '  "stop_conditions": [<short strings>],\n'
    '  "reason": "<one short sentence>",\n'
    '  "confidence": <float 0-1>\n'
    "}}\n"
)


@dataclass
class IntakeClassifier:
    """小型 LLM ベースの intake classifier.

    Attributes:
        llm_router: `LLMRouter` 互換オブジェクト (`route(LLMRequest)`).
            None の場合は LLM を呼ばず `fallback_requires_agent` の値を返す.
        profile_id: LLM プロファイル ID (LLMSettingsResolver で解決).
        fallback_requires_agent: LLM 失敗時のデフォルト.
    """

    llm_router: Any = None
    profile_id: str = "local_chat"
    fallback_requires_agent: bool = False
    max_observation_chars: int = 1024

    def classify(
        self,
        event: dict[str, Any],
        *,
        event_id: str = "",
    ) -> IntakeResult:
        """event dict → `IntakeResult`."""
        eid = event_id or str(event.get("id") or event.get("event_id") or "ev")
        if self.llm_router is None:
            return self._fallback(eid, "no_llm_router_configured")

        observation = self._format_observation(event)
        prompt = _CLASSIFIER_PROMPT.format(observation=observation)
        try:
            response = self._call_llm(prompt)
        except Exception as exc:  # noqa: BLE001
            logger.warning("intake classifier LLM call failed: %r", exc)
            return self._fallback(eid, f"llm_call_failed: {exc!r}")

        if not getattr(response, "success", False):
            return self._fallback(
                eid, f"llm_response_failed: {getattr(response, 'error', 'unknown')}"
            )

        parsed = self._parse_response(getattr(response, "content", "") or "")
        if parsed is None:
            return self._fallback(eid, "llm_response_unparseable")

        return IntakeResult(
            event_id=eid,
            decision=self._decision_from_score(parsed["requires_agent_score"]),
            requires_agent_score=float(parsed["requires_agent_score"]),
            importance=float(parsed["importance"]),
            novelty=float(parsed["novelty"]),
            task_type=str(parsed.get("task_type") or ""),
            capabilities=list(parsed.get("capabilities") or []),
            stop_conditions=list(parsed.get("stop_conditions") or []),
            reason=str(parsed.get("reason") or ""),
            confidence=float(parsed.get("confidence") or 0.0),
            raw={
                "model_used": getattr(response, "model_used", ""),
                "provider_used": getattr(response, "provider_used", ""),
                "tokens_used": getattr(response, "tokens_used", 0),
            },
        )

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _format_observation(self, event: dict[str, Any]) -> str:
        parts: list[str] = []
        for key in ("source", "kind", "description", "text", "safe_message", "reason"):
            value = event.get(key)
            if value:
                parts.append(f"{key}: {value}")
        s = "\n".join(parts) or str(event)[: self.max_observation_chars]
        return s[: self.max_observation_chars]

    def _call_llm(self, prompt: str) -> Any:
        """`LLMRouter.route(LLMRequest(...))` を呼ぶ薄いラッパ.

        `LLMRequest` / `LLMRouter` は `aegis_ai.llm.router` で定義。
        呼び出し時に import して依存方向を最小限にする。
        """
        from aegis_ai.llm.router import LLMRequest, TaskType

        request = LLMRequest(
            task_type=TaskType.SMALL_FAST_TASK,
            prompt=prompt,
            system_prompt="intake classifier",
            json_mode=True,
            caller="intake.classifier",
        )
        return self.llm_router.route(request)

    @staticmethod
    def _decision_from_score(score: float) -> IntakeDecision:
        if score >= 0.7:
            return IntakeDecision.REQUIRES_AGENT
        if score >= 0.3:
            return IntakeDecision.LOCAL_INTERPRET
        return IntakeDecision.DEFER

    @staticmethod
    def _parse_response(content: str) -> dict[str, Any] | None:
        """LLM レスポンスを JSON として緩くパースする.

        コードブロック (```json ... ```) で囲まれていても OK。
        失敗時は None.
        """
        if not content:
            return None
        try:
            data = extract_json_object(content)
        except Exception:  # noqa: BLE001
            logger.debug("intake classifier failed to parse: %r", content[:200])
            return None
        # 必須フィールドをデフォルトで埋める
        return {
            "requires_agent_score": _safe_float(data.get("requires_agent_score"), 0.0),
            "importance": _safe_float(data.get("importance"), 0.0),
            "novelty": _safe_float(data.get("novelty"), 1.0),
            "task_type": str(data.get("task_type", "") or ""),
            "capabilities": data.get("capabilities") if isinstance(data.get("capabilities"), list) else [],
            "stop_conditions": data.get("stop_conditions") if isinstance(data.get("stop_conditions"), list) else [],
            "reason": str(data.get("reason", "") or ""),
            "confidence": _safe_float(data.get("confidence"), 0.0),
        }

    def _fallback(self, event_id: str, reason: str) -> IntakeResult:
        decision = (
            IntakeDecision.REQUIRES_AGENT
            if self.fallback_requires_agent
            else IntakeDecision.LOCAL_INTERPRET
        )
        return IntakeResult(
            event_id=event_id,
            decision=decision,
            requires_agent_score=1.0 if self.fallback_requires_agent else 0.0,
            importance=0.0,
            novelty=1.0,
            reason=f"fallback: {reason}",
            confidence=0.0,
        )


__all__ = ["IntakeClassifier"]
