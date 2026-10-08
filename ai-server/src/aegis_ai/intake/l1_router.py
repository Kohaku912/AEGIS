"""L1 Router — DASHBOARD_V3_PLAN.md Phase L2.

instruction.md v3 で定義された L1 (常時稼働 / 知覚 / ルーティング) 層。

旧 `IntakeRouter` を置き換える (その v1 intake 経路は 2026-10-08 に削除 —
DELEGATION.md §4 item 47)。L1 LLM に対して event を JSON 構造化出力で
解釈させる。`required_intelligence == HIGH` の場合は L2 への escalation を
生成する。

- `observe(event) -> L1Observation`: L1 LLM で意味理解
- `decide(observation) -> L1Decision`: observation から L1 行動を決定
- `escalate(observation) -> L1Escalation`: L2 escalation 作成
- `route(event) -> L1Decision`: observe + decide の convenience
- `should_escalate(observation) -> bool`: escalation 必要か判定

L1 は risk="low" な Capability のみ直接実行可 (Phase L3 で実装)。
それ以外は L2 経由 (AGENTS.md Hard Stops と整合)。
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from aegis_ai.intake.l1_models import (
    L1Action,
    L1ActionType,
    L1Decision,
    L1Escalation,
    L1Observation,
    RequiredIntelligence,
)
from aegis_ai.llm.gateway import LLMGateway

logger = logging.getLogger("aegis_ai.intake.l1_router")


def _safe_float(value: Any, default: float) -> float:
    """Coerce an LLM-provided value to ``float`` without ever raising.

    L1 reads a JSON object produced by an LLM, so numeric fields may arrive as
    ``null`` or as a non-numeric string. Falling back to ``default`` keeps
    ``observe()`` from crashing on a malformed response.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# L1 system prompt (DASHBOARD_V3_PLAN.md Phase L2):
# - 短く保つ (L1 は常時稼働するので token 効率最優先)
# - JSON 出力強制
_L1_SYSTEM_PROMPT = """\
You are L1 (Perception / Router) of AEGIS. Your role is to OBSERVE and CLASSIFY
incoming events and decide whether they require L2 (Autonomous Mind) escalation.

You must respond with valid JSON in this exact schema:
{
  "meaning": "<one-line interpretation of the event>",
  "value": <float 0.0-1.0, how much AEGIS should care>,
  "priority": <float 0.0-1.0, urgency>,
  "required_intelligence": "low" | "medium" | "high",
  "confidence": <float 0.0-1.0>,
  "summary_bucket": "important_change" | "user_state" | "task_candidate" | "memory_candidate" | "anomaly" | "background",
  "observed_action": "<what was observed>",
  "possible_intent": "<best-effort likely intent or situation shift>",
  "should_execute_directly": <bool>,
  "candidate_capability_id": "<capability id only if the event already provides one>",
  "candidate_args": <object>
}

Rules:
- "low" intelligence = a simple capability call can handle it
- "medium" = L1 can decide, but consider context
- "high" = requires deeper reasoning, MUST escalate to L2
- Be conservative with "value" and "priority" (most events are low)
- Be honest with "confidence" (low if uncertain)
- Act as an information compressor: prefer the best bucket for downstream summary
- Treat user/device observations as probabilities, not certainties
- Only emit `candidate_capability_id` when the event already includes a structured capability hint
"""

_PRIORITY_EVENT_KEYS = (
    "type",
    "event_id",
    "source",
    "source_type",
    "message",
    "summary",
    "title",
    "topic",
    "activity",
    "window_title",
    "app",
    "status",
    "task_id",
    "approval_id",
    "capability_id",
    "capability_args",
    "args",
    "candidate_capabilities",
    "execute_directly",
    "direct_handle",
    "observed_action",
)


def _summarize_event(event: dict[str, Any]) -> str:
    """event dict を LLM prompt 用に短い文字列に変換."""
    parts: list[str] = []
    for key in ("type", "source_type", "event_id", "source", "message", "summary", "topic", "task_type"):
        if event.get(key):
            parts.append(f"{key}={event[key]}")
    if not parts:
        # フォールバック: dict の先頭 3 キー
        for i, (k, v) in enumerate(event.items()):
            if i >= 3:
                break
            parts.append(f"{k}={v}")
    return " | ".join(parts) if parts else "<empty event>"


def _compact_json_payload(payload: dict[str, Any], *, max_keys: int = 24, max_chars: int = 2400) -> str:
    trimmed = dict(payload or {})
    if len(trimmed) > max_keys:
        keys = list(trimmed.keys())[:max_keys]
        trimmed = {key: trimmed.get(key) for key in keys}
    try:
        rendered = json.dumps(trimmed, ensure_ascii=False, sort_keys=True)
    except Exception:
        rendered = repr(trimmed)
    return rendered[:max_chars]


def _event_focus_payload(event: dict[str, Any]) -> dict[str, Any]:
    focus: dict[str, Any] = {}
    event = dict(event or {})
    for key in _PRIORITY_EVENT_KEYS:
        value = event.get(key)
        if value in (None, "", [], {}):
            continue
        focus[key] = value
    if len(focus) < 24:
        for key, value in event.items():
            if key in focus or value in (None, "", [], {}):
                continue
            focus[key] = value
            if len(focus) >= 24:
                break
    return focus


def _event_prompt_json(event: dict[str, Any]) -> str:
    """LLM に見せる event JSON を長さ制限付きで整形."""
    return _compact_json_payload(_event_focus_payload(event))


def _l1_unavailable_observation(*, event_id: str, error: str) -> L1Observation:
    return L1Observation(
        event_id=event_id,
        meaning="<l1 unavailable>",
        value=1.0,
        priority=1.0,
        required_intelligence=RequiredIntelligence.HIGH,
        confidence=0.0,
        raw={
            "error": error,
            "summary_bucket": "anomaly",
            "observed_action": "L1 observation unavailable",
            "possible_intent": "L1 routing path requires repair",
            "should_execute_directly": False,
            "candidate_capability_id": "",
            "candidate_args": {},
        },
    )


@dataclass
class L1Router:
    """L1 ルータ.

    Attributes:
        llm_gateway: L1 LLM 呼び出しに使う LLMGateway.
        min_value_for_action: 行動を起こす最小 value (これ未満は IGNORE)
        min_priority_for_escalation: escalation する最小 priority
        enabled: master switch. False のときは observe せず L1Observation デフォルトを返す.
    """

    llm_gateway: LLMGateway
    min_value_for_action: float = 0.3
    min_priority_for_escalation: float = 0.6
    enabled: bool = True

    def should_escalate(self, observation: L1Observation) -> bool:
        """L2 escalation が必要かを判定.

        Returns:
            True if required_intelligence == HIGH or
                 (priority >= min_priority_for_escalation and value >= min_value_for_action)
        """
        if observation.required_intelligence == RequiredIntelligence.HIGH:
            return True
        if (
            observation.priority >= self.min_priority_for_escalation
            and observation.value >= self.min_value_for_action
        ):
            return True
        return False

    def observe(
        self,
        event: dict[str, Any],
        *,
        event_id: str = "",
        context_capsule: dict[str, Any] | None = None,
    ) -> L1Observation:
        """L1 LLM に event を解釈させ、L1Observation を返す.

        Args:
            event: 観測対象の event dict
            event_id: event の ID (省略時は event["event_id"] を使用)

        Returns:
            L1Observation (LLM が失敗した場合はデフォルト値)
        """
        eid = event_id or str(event.get("event_id") or event.get("id") or "ev")
        if not self.enabled:
            return L1Observation(
                event_id=eid,
                meaning="<l1 disabled>",
                value=0.0,
                priority=0.0,
                required_intelligence=RequiredIntelligence.LOW,
                confidence=0.0,
            )

        prompt = (
            f"event: {_summarize_event(event)}\n"
            f"event_json: {_event_prompt_json(event)}\n"
            f"event_id: {eid}"
        )
        l1_state = {
            "event_id": eid,
            "event_summary": _summarize_event(event),
            "event_focus": _event_focus_payload(event),
            "aegis_context": dict(context_capsule or {}),
        }
        try:
            result = self.llm_gateway.request_json(
                layer="L1",
                prompt=prompt,
                system_prompt=_L1_SYSTEM_PROMPT,
                max_tokens=512,
                temperature=0.1,
                context_meta={
                    "event_id": eid,
                    "source": "l1_router.observe",
                    "l1_state": l1_state,
                },
            )
        except Exception as exc:
            logger.warning("L1Router.observe LLM call failed: %s", exc)
            return _l1_unavailable_observation(event_id=eid, error=str(exc))

        if "error" in result:
            logger.debug("L1Router.observe returned error: %s", result)
            return _l1_unavailable_observation(event_id=eid, error=str(result.get("error", "")))

        try:
            required_intel = RequiredIntelligence(str(result.get("required_intelligence", "low")).lower())
        except ValueError:
            required_intel = RequiredIntelligence.LOW

        raw = dict(result)
        raw["_event"] = dict(event)
        return L1Observation(
            event_id=eid,
            meaning=str(result.get("meaning", "")),
            value=_safe_float(result.get("value"), 0.0),
            priority=_safe_float(result.get("priority"), 0.0),
            required_intelligence=required_intel,
            confidence=_safe_float(result.get("confidence"), 0.0),
            raw=raw,
        )

    def decide(self, observation: L1Observation) -> L1Decision:
        """observation から L1Decision を生成.

        ルール:
        - required_intelligence == HIGH → ESCALATE
        - priority/value 高 → ESCALATE
        - value 低 → IGNORE
        - それ以外 → OBSERVE (後で再評価)
        """
        if self.should_escalate(observation):
            action = L1Action(
                type=L1ActionType.ESCALATE,
                reason=f"required_intelligence={observation.required_intelligence.value} "
                       f"value={observation.value:.2f} priority={observation.priority:.2f}",
            )
            return L1Decision(
                event_id=observation.event_id,
                action=action,
                reasoning="L1 escalates to L2 for deeper reasoning",
                observation=observation,
            )

        event = (
            dict(observation.raw.get("_event") or {})
            if isinstance(getattr(observation, "raw", None), dict)
            else {}
        )
        candidate_capability_id = str(
            observation.raw.get("candidate_capability_id")
            or event.get("capability_id")
            or (
                event.get("candidate_capabilities", [""])[0]
                if isinstance(event.get("candidate_capabilities"), list)
                and event.get("candidate_capabilities")
                else ""
            )
        ).strip()
        candidate_args = observation.raw.get("candidate_args")
        if not isinstance(candidate_args, dict):
            candidate_args = event.get("capability_args")
        if not isinstance(candidate_args, dict):
            candidate_args = event.get("args")
        if not isinstance(candidate_args, dict):
            candidate_args = {}

        direct_signal = bool(
            observation.raw.get("should_execute_directly")
            or event.get("execute_directly")
            or event.get("direct_handle")
        )
        if (
            direct_signal
            and candidate_capability_id
            and observation.required_intelligence == RequiredIntelligence.LOW
            and observation.value >= self.min_value_for_action
            and observation.confidence >= 0.5
        ):
            action = L1Action(
                type=L1ActionType.CAPABILITY,
                capability_id=candidate_capability_id,
                args=dict(candidate_args),
                reason=(
                    "low-intelligence structured direct handle "
                    f"value={observation.value:.2f} confidence={observation.confidence:.2f}"
                ),
            )
            return L1Decision(
                event_id=observation.event_id,
                action=action,
                reasoning="L1 handles a structured low-risk capability directly",
                observation=observation,
            )

        if observation.value < self.min_value_for_action:
            action = L1Action(
                type=L1ActionType.IGNORE,
                reason=f"value={observation.value:.2f} < min_value_for_action={self.min_value_for_action}",
            )
            return L1Decision(
                event_id=observation.event_id,
                action=action,
                reasoning="L1 ignores low-value event",
                observation=observation,
            )

        # それ以外 (low / medium intelligence) は observe (後で再評価)
        action = L1Action(
            type=L1ActionType.OBSERVE,
                reason=(
                    f"intelligence={observation.required_intelligence.value} "
                    f"value={observation.value:.2f} bucket={observation.raw.get('summary_bucket', 'background')}"
                ),
        )
        return L1Decision(
            event_id=observation.event_id,
            action=action,
            reasoning="L1 observes and defers decision to L2 routine",
            observation=observation,
        )

    def escalate(self, observation: L1Observation, *, reason: str = "") -> L1Escalation:
        """observation から L1Escalation を作成."""
        return L1Escalation(
            event_id=observation.event_id,
            reason=reason or f"required_intelligence={observation.required_intelligence.value}",
            problem=observation.meaning or "<no meaning>",
            context={
                "value": observation.value,
                "priority": observation.priority,
                "confidence": observation.confidence,
                "raw": observation.raw,
            },
            required_intelligence=observation.required_intelligence,
        )

    def route(self, event: dict[str, Any], *, event_id: str = "") -> L1Decision:
        """observe + decide の convenience."""
        observation = self.observe(event, event_id=event_id)
        return self.decide(observation)


__all__ = ["L1Router"]
