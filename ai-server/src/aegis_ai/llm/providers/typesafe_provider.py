"""TypeSafe System One provider for narrow structured decisions.

This provider is intentionally limited to Jev-shaped tasks where the output is a
typed judgement rather than free-form text generation.
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any
from urllib import error, request

from aegis_ai.llm.router import LLMResponse

logger = logging.getLogger("aegis_ai.llm.providers.typesafe")


class TypeSafeProvider:
    """TypeSafe Jev provider for first-stage structured decisions."""

    def __init__(
        self,
        model: str = "jev-latest",
        api_key: str | None = None,
        base_url: str | None = None,
        audit_log: Any = None,
        timeout_seconds: int = 30,
    ) -> None:
        self._model = model or "jev-latest"
        self._api_key = api_key or os.getenv("TYPESAFE_API_KEY", "")
        self._base_url = (base_url or "https://api.typesafe.ai/v1/systemone").strip()
        self._audit = audit_log
        self._timeout_seconds = max(1, int(timeout_seconds or 30))
        if not self._api_key:
            logger.warning("No TypeSafe API key set. Set TYPESAFE_API_KEY.")

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 0,
        temperature: float = 0.0,
        context_meta: dict[str, Any] | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        del max_tokens, temperature
        start = time.time()
        meta = dict(context_meta or {})
        try:
            if not self._api_key:
                return self._failure_response(
                    start=start,
                    meta=meta,
                    error="TypeSafe API key is not configured",
                )

            if meta.get("layer") == "L1" or meta.get("source") == "l1_router.observe":
                payload = self._run_l1_observation(prompt=prompt, system_prompt=system_prompt, context_meta=meta)
            elif meta.get("caller") == "chat_tools.tool_gate":
                payload = self._run_boolean_gate(
                    state=prompt,
                    key="use_tools",
                    instructions=(
                        "Does the CURRENT user request require any external tool or capability "
                        "execution to answer accurately or complete the task?"
                    ),
                    true_desc="Requires observing external state, looking something up, or taking an external action.",
                    false_desc="Purely conversational and answerable directly without external capabilities.",
                )
            elif meta.get("caller") == "chat_tools.satisfaction_gate":
                payload = self._run_boolean_gate(
                    state=prompt,
                    key="satisfies",
                    instructions=(
                        "Does the assistant response fully satisfy the CURRENT user request without "
                        "any external tool or capability execution?"
                    ),
                    true_desc="The response already contains the completed result or a clear final limitation.",
                    false_desc="The response only promises to act, asks to wait, or is missing required real-world checking.",
                )
            else:
                return self._failure_response(
                    start=start,
                    meta=meta,
                    error=(
                        "TypeSafe provider only supports L1 observation and chat first-stage "
                        "boolean decisions"
                    ),
                )

            usage = dict(payload.get("_usage") or {})
            content = json.dumps(payload["result"], ensure_ascii=False)
            duration_ms = round((time.time() - start) * 1000, 1)
            self._audit_log(
                action="llm_call",
                decision="success",
                detail={
                    "model": self._model,
                    "provider": "typesafe",
                    "duration_ms": duration_ms,
                    "json_mode": json_mode,
                    "usage": usage,
                    **meta,
                },
            )
            return LLMResponse(
                content=content,
                model_used=self._model,
                provider_used="typesafe",
                tokens_used=int(usage.get("input_tokens", 0) or 0) + int(usage.get("output_tokens", 0) or 0),
                input_tokens=int(usage.get("input_tokens", 0) or 0),
                output_tokens=int(usage.get("output_tokens", 0) or 0),
                success=True,
            )
        except Exception as exc:
            return self._failure_response(
                start=start,
                meta=meta,
                error=str(exc),
            )

    def _failure_response(
        self,
        *,
        start: float,
        meta: dict[str, Any],
        error: str,
    ) -> LLMResponse:
        duration_ms = round((time.time() - start) * 1000, 1)
        self._audit_log(
            action="llm_call",
            decision="error",
            detail={
                "model": self._model,
                "provider": "typesafe",
                "error": error,
                "duration_ms": duration_ms,
                "api_key_configured": bool(self._api_key),
                **meta,
            },
        )
        return LLMResponse(
            success=False,
            error=error,
            model_used=self._model,
            provider_used="typesafe",
        )

    def _run_l1_observation(
        self,
        *,
        prompt: str,
        system_prompt: str,
        context_meta: dict[str, Any],
    ) -> dict[str, Any]:
        l1_state = self._extract_l1_state(prompt, context_meta)
        event_summary = str(l1_state.get("event_summary") or "<empty event>")
        event_id = str(l1_state.get("event_id") or context_meta.get("event_id") or "ev")
        event_data = dict(l1_state.get("event_focus") or {})
        aegis_context = dict(l1_state.get("aegis_context") or {})
        state = {
            "event_summary": event_summary,
            "event_id": event_id,
            "event_json": event_data,
            "aegis_context": aegis_context,
            "system_role": system_prompt[:800],
        }
        response = self._system_one(
            state=state,
            questions={
                "required_intelligence": {
                    "type": "choice",
                    "instructions": "How much intelligence is required to handle this event correctly?",
                    "criteria": {
                        "low": "A simple capability call or no action is enough.",
                        "medium": "Needs some contextual judgment but not deep reasoning.",
                        "high": "Needs deeper reasoning, planning, or broad context integration.",
                    },
                },
                "value_band": {
                    "type": "score",
                    "instructions": "How much should AEGIS care about this event overall?",
                    "criteria": [
                        "Negligible and safe to ignore.",
                        "Low value background information.",
                        "Useful and worth noticing.",
                        "Important user-impacting event.",
                        "Critical high-impact event.",
                    ],
                },
                "priority_band": {
                    "type": "score",
                    "instructions": "How urgent is this event right now?",
                    "criteria": [
                        "No urgency.",
                        "Background priority.",
                        "Should be handled this session.",
                        "Urgent and should be handled soon.",
                        "Immediate attention required.",
                    ],
                },
                "summary_bucket": {
                    "type": "choice",
                    "instructions": "Which compressed bucket best fits this event for downstream AEGIS processing?",
                    "criteria": {
                        "important_change": "A meaningful external or internal change that should influence current decisions.",
                        "user_state": "A signal about what the user is doing, needs, or may be intending.",
                        "task_candidate": "Suggests a concrete task, follow-up, or action item.",
                        "memory_candidate": "Worth storing as durable context or later reference.",
                        "anomaly": "Looks risky, broken, contradictory, or otherwise abnormal.",
                        "background": "Low-value background noise or routine telemetry.",
                    },
                },
                "intent_class": {
                    "type": "choice",
                    "instructions": "What is the most likely actionable interpretation of this event?",
                    "criteria": {
                        "immediate_action": "The event indicates a likely near-term request or action opportunity.",
                        "monitor_user": "The event mainly updates user state or current activity understanding.",
                        "route_task": "The event suggests creating or updating a task or workflow.",
                        "remember_context": "The event is mainly useful as memory or context for later decisions.",
                        "investigate_issue": "The event suggests something abnormal that should be investigated.",
                        "background": "The event is routine background noise with no likely action.",
                    },
                },
                "direct_handle": {
                    "type": "noul",
                    "instructions": (
                        "Should AEGIS directly execute a low-risk capability now if the state already contains "
                        "an explicit structured capability hint?"
                    ),
                    "criteria": {
                        "true": "A low-risk direct capability action is explicitly present in the state and should run now.",
                        "false": "Either no explicit capability hint exists, risk is unclear, or the event should be observed/escalated instead.",
                    },
                },
            },
        )
        answers = dict(response.get("answers") or {})
        intelligence = dict(answers.get("required_intelligence") or {})
        value_band = dict(answers.get("value_band") or {})
        priority_band = dict(answers.get("priority_band") or {})
        summary_bucket = dict(answers.get("summary_bucket") or {})
        intent_class = dict(answers.get("intent_class") or {})
        direct_handle = dict(answers.get("direct_handle") or {})
        confidence_values = [
            float(intelligence.get("confidence", 0.0) or 0.0),
            float(value_band.get("confidence", 0.0) or 0.0),
            float(priority_band.get("confidence", 0.0) or 0.0),
            float(summary_bucket.get("confidence", 0.0) or 0.0),
            float(intent_class.get("confidence", 0.0) or 0.0),
        ]
        confidence_values = [value for value in confidence_values if value > 0.0]
        confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
        candidate_capability_id, candidate_args = self._extract_candidate_capability(event_data)
        bucket = str(summary_bucket.get("choice") or "background").lower()
        intent = str(intent_class.get("choice") or "background").lower()
        direct_probability = float(direct_handle.get("noul", 0.0) or 0.0)
        observed_action = self._describe_observed_action(event_data, fallback=event_summary)
        result = {
            "meaning": observed_action[:200] or event_summary[:200],
            "value": self._normalize_score(value_band.get("score"), max_level=4),
            "priority": self._normalize_score(priority_band.get("score"), max_level=4),
            "required_intelligence": str(intelligence.get("choice") or "low").lower(),
            "confidence": round(confidence, 4),
            "summary_bucket": bucket,
            "observed_action": observed_action[:200],
            "possible_intent": self._possible_intent_text(
                intent_class=intent,
                summary_bucket=bucket,
                candidate_capability_id=candidate_capability_id,
            )[:200],
            "should_execute_directly": bool(candidate_capability_id) and direct_probability >= 0.7,
            "candidate_capability_id": candidate_capability_id,
            "candidate_args": candidate_args,
        }
        return {"result": result, "_usage": response.get("usage") or {}}

    def _run_boolean_gate(
        self,
        *,
        state: Any,
        key: str,
        instructions: str,
        true_desc: str,
        false_desc: str,
    ) -> dict[str, Any]:
        response = self._system_one(
            state=state,
            questions={
                key: {
                    "type": "noul",
                    "instructions": instructions,
                    "criteria": {
                        "true": true_desc,
                        "false": false_desc,
                    },
                }
            },
        )
        answer = dict((response.get("answers") or {}).get(key) or {})
        probability = float(answer.get("noul", 0.0) or 0.0)
        result = {
            key: probability >= 0.5,
            "reason": f"typesafe_probability={probability:.3f}",
        }
        return {"result": result, "_usage": response.get("usage") or {}}

    def _system_one(self, *, state: Any, questions: dict[str, Any]) -> dict[str, Any]:
        # Defence in depth (S-4). The gate is also consulted at construction
        # (``llm/factory.py`` and ``llm/gateway.py``, the only two sites), but
        # *this* method is the one that transmits, so it re-checks immediately
        # before building the request. Without it, "the construction path is the
        # only entrance" is a convention rather than an invariant. The gate is
        # read-only over decided permissions; a denial raises, and ``generate``
        # turns that into an audited failure response rather than transmitting.
        from aegis_ai.llm.factory import egress_allows_llm

        if not egress_allows_llm(self._base_url, component="llm.typesafe_provider"):
            raise RuntimeError(f"Egress gate denied TypeSafe destination {self._base_url}")
        payload = json.dumps(
            {
                "model": self._model,
                "state": state,
                "questions": questions,
            },
            ensure_ascii=False,
        ).encode("utf-8")
        req = request.Request(
            self._base_url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        last_error = ""
        for attempt in range(3):
            try:
                with request.urlopen(req, timeout=self._timeout_seconds) as response:
                    body = response.read().decode("utf-8")
                    return json.loads(body)
            except error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                last_error = self._http_error_text(exc.code, body)
                if exc.code in {429, 529} and attempt < 2:
                    time.sleep(0.5 * (2**attempt))
                    continue
                raise RuntimeError(last_error) from exc
            except error.URLError as exc:
                last_error = f"TypeSafe request failed: {exc.reason}"
                if attempt < 2:
                    time.sleep(0.5 * (2**attempt))
                    continue
                raise RuntimeError(last_error) from exc
        raise RuntimeError(last_error or "TypeSafe request failed")

    @staticmethod
    def _normalize_score(score: Any, *, max_level: int) -> float:
        try:
            value = float(score)
        except (TypeError, ValueError):
            return 0.0
        if max_level <= 0:
            return 0.0
        return max(0.0, min(1.0, value / float(max_level)))

    @staticmethod
    def _extract_l1_state(prompt: str, context_meta: dict[str, Any]) -> dict[str, Any]:
        event_summary = str(prompt or "").strip()
        event_id = str(context_meta.get("event_id") or "ev")
        event_data: dict[str, Any] = {}
        for line in str(prompt or "").splitlines():
            if line.startswith("event:"):
                event_summary = line.split(":", 1)[1].strip()
            elif line.startswith("event_json:"):
                raw_json = line.split(":", 1)[1].strip()
                try:
                    parsed = json.loads(raw_json)
                    if isinstance(parsed, dict):
                        event_data = parsed
                except json.JSONDecodeError:
                    event_data = {}
            elif line.startswith("event_id:"):
                event_id = line.split(":", 1)[1].strip() or event_id
        structured = context_meta.get("l1_state")
        if isinstance(structured, dict):
            focus = structured.get("event_focus")
            if not isinstance(focus, dict):
                focus = structured.get("event") if isinstance(structured.get("event"), dict) else {}
            aegis_context = structured.get("aegis_context")
            if not isinstance(aegis_context, dict):
                aegis_context = {}
            resolved_event_id = str(structured.get("event_id") or event_id or "ev")
            resolved_summary = str(structured.get("event_summary") or event_summary or "").strip()
            if not resolved_summary:
                resolved_summary = TypeSafeProvider._describe_observed_action(
                    dict(focus or event_data),
                    fallback=event_summary,
                )
            return {
                "event_summary": resolved_summary or "<empty event>",
                "event_id": resolved_event_id,
                "event_focus": dict(focus or event_data),
                "aegis_context": dict(aegis_context),
            }
        return {
            "event_summary": event_summary or "<empty event>",
            "event_id": event_id,
            "event_focus": event_data,
            "aegis_context": {},
        }

    @staticmethod
    def _extract_candidate_capability(event_data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        capability_id = str(
            event_data.get("capability_id")
            or (
                event_data.get("candidate_capabilities", [""])[0]
                if isinstance(event_data.get("candidate_capabilities"), list)
                and event_data.get("candidate_capabilities")
                else ""
            )
            or ""
        ).strip()
        args = event_data.get("capability_args")
        if not isinstance(args, dict):
            args = event_data.get("args")
        if not isinstance(args, dict):
            args = {}
        return capability_id, dict(args)

    @staticmethod
    def _describe_observed_action(event_data: dict[str, Any], *, fallback: str) -> str:
        for key in (
            "observed_action",
            "message",
            "summary",
            "action",
            "activity",
            "window_title",
            "app",
            "title",
            "topic",
        ):
            value = event_data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        event_type = str(event_data.get("type") or "").strip()
        source = str(event_data.get("source") or "").strip()
        if event_type and source:
            return f"{event_type} from {source}"
        if event_type:
            return event_type
        return fallback.strip()[:200] or "<empty event>"

    @staticmethod
    def _possible_intent_text(
        *,
        intent_class: str,
        summary_bucket: str,
        candidate_capability_id: str,
    ) -> str:
        if candidate_capability_id and intent_class == "immediate_action":
            return f"Likely direct request to run {candidate_capability_id}"
        mapping = {
            "immediate_action": "Likely needs a near-term action or response",
            "monitor_user": "Likely updates current user state or context",
            "route_task": "Likely should create or update a task",
            "remember_context": "Likely should be remembered for later context",
            "investigate_issue": "Likely needs anomaly investigation or validation",
            "background": "Likely routine background information",
        }
        if intent_class in mapping:
            return mapping[intent_class]
        bucket_mapping = {
            "important_change": "Likely important state change",
            "user_state": "Likely user state update",
            "task_candidate": "Likely actionable task candidate",
            "memory_candidate": "Likely memory candidate",
            "anomaly": "Likely anomaly requiring investigation",
            "background": "Likely background telemetry",
        }
        return bucket_mapping.get(summary_bucket, "Likely context update")

    @staticmethod
    def _http_error_text(status_code: int, body: str) -> str:
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {}
        message = ""
        if isinstance(payload, dict):
            message = str(payload.get("message") or payload.get("error") or "").strip()
        if message:
            return f"TypeSafe API error {status_code}: {message}"
        return f"TypeSafe API error {status_code}"

    def _audit_log(self, action: str, decision: str, detail: dict[str, Any]) -> None:
        try:
            if self._audit is not None:
                from aegis_ai.audit import AuditEntry

                usage = detail.get("usage") if isinstance(detail.get("usage"), dict) else {}
                profile_id = str(detail.get("profile_id") or detail.get("profile") or "")
                request_id = str(detail.get("request_id") or "")
                task_id = str(detail.get("task_id") or detail.get("chat_task_id") or "")
                self._audit.append(
                    AuditEntry(
                        action=action,
                        actor="llm",
                        capability_id=f"llm.{self._model}",
                        decision=decision,
                        detail=detail,
                        profile_id=profile_id,
                        model=self._model,
                        provider="typesafe",
                        tokens_used=int(
                            detail.get("tokens_used")
                            or detail.get("total_tokens")
                            or usage.get("total_tokens")
                            or (int(detail.get("input_tokens") or 0) + int(detail.get("output_tokens") or 0))
                        ),
                        duration_ms=int(detail.get("duration_ms") or 0),
                        request_id=request_id,
                        task_id=task_id,
                    )
                )
        except Exception:
            logger.debug("Failed to append TypeSafe audit entry", exc_info=True)
