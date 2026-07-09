"""Presentation Planner — converts a PresentationRequest into a PresentationSpec.

The planner is intentionally deterministic right now — no LLM call.
Future versions may use the LLM to choose modality, importance, or content
layout. For the MVP the mapping is mechanical.
"""

from __future__ import annotations

import inspect
import json
import time
import uuid
from typing import Any

from aegis_ai.presentation.models import (
    DeliverySpec,
    Importance,
    InteractionMode,
    InteractionSpec,
    LifecycleSpec,
    Modality,
    Placement,
    PlacementSpec,
    PresentationRequest,
    PresentationSpec,
    PresentationStatus,
)
from aegis_ai.presentation.schemas import normalize_content


_VALID_MODALITIES = {m.value for m in Modality}
# Keep this derived from Modality so new modalities auto-register here.
_VALID_IMPORTANCES = {i.value for i in Importance}
_VALID_INTERACTIONS = {i.value for i in InteractionMode}
_VALID_TARGETS = {
    Placement.DASHBOARD.value,
    Placement.PC_OVERLAY.value,
    Placement.ANDROID_OVERLAY.value,
    Placement.XR_SCENE.value,
}


def plan_presentation(request: PresentationRequest) -> PresentationSpec:
    """Convert a lightweight request into a fully-specified PresentationSpec.

    Validation is lenient — unknown values fall back to safe defaults rather
    than raising, so callers don't need to be perfectly precise.
    """
    now_ms = int(time.time() * 1000)
    pres_id = f"pres_{uuid.uuid4().hex[:12]}"

    modality_raw = request.modality.value if isinstance(request.modality, Modality) else request.modality
    importance_raw = request.importance.value if isinstance(request.importance, Importance) else request.importance
    interaction_raw = request.interaction_mode.value if isinstance(request.interaction_mode, InteractionMode) else request.interaction_mode

    modality_str = modality_raw if modality_raw in _VALID_MODALITIES else "text_card"
    importance_str = importance_raw if importance_raw in _VALID_IMPORTANCES else "normal"
    interaction_str = interaction_raw if interaction_raw in _VALID_INTERACTIONS else "dismiss_only"

    ttl_ms = max(1_000, request.ttl_ms)  # at least 1 second

    return PresentationSpec(
        presentation_id=pres_id,
        source=request.source,
        intent=request.intent,
        importance=Importance(importance_str),
        modality=Modality(modality_str),
        title=request.title,
        summary=request.summary,
        content=request.content,
        delivery=DeliverySpec(
            targets=request.targets,
            ttl_ms=ttl_ms,
        ),
        placement=PlacementSpec(zone=request.placement_zone),
        interaction=InteractionSpec(
            mode=InteractionMode(interaction_str),
            actions=request.actions,
        ),
        lifecycle=LifecycleSpec(expires_at_ms=now_ms + ttl_ms),
        status=PresentationStatus.PENDING,
        created_at_ms=now_ms,
        updated_at_ms=now_ms,
        revision=0,
        metadata=request.metadata,
    )


def _build_v2_prompt(request: PresentationRequest) -> tuple[str, str]:
    system_prompt = (
        "You are AEGIS's presentation planner. Choose the best presentation modality and delivery targets "
        "from the allowed lists. Return JSON only with keys modality, targets, and content. "
        f"Allowed modalities: {sorted(_VALID_MODALITIES)}. "
        f"Allowed targets: {sorted(_VALID_TARGETS)}. "
        "Do not invent HTML, JavaScript, or any other arbitrary markup. "
        "Use the request content as the payload source and return a content object suited to the selected modality."
    )
    prompt = json.dumps(
        {
            "request": request.to_dict(),
            "instructions": {
                "choose_modality": "Pick the best modality for the content.",
                "choose_targets": "Pick the best target or targets for delivery.",
                "return_shape": {
                    "modality": "one of the allowed modality values",
                    "targets": ["one or more allowed target values"],
                    "content": "object matched to the selected modality",
                },
            },
        },
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    return system_prompt, prompt


def _coerce_llm_payload(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw

    content = getattr(raw, "content", raw)
    if isinstance(content, dict):
        return content
    if not isinstance(content, str):
        return None

    text = content.strip()
    if not text:
        return None
    if text.startswith("```"):
        lines = text.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _sanitize_targets(targets: Any) -> list[str] | None:
    if isinstance(targets, str):
        targets = [targets]
    if not isinstance(targets, list):
        return None

    cleaned: list[str] = []
    for target in targets:
        if not isinstance(target, str) or target not in _VALID_TARGETS:
            return None
        if target not in cleaned:
            cleaned.append(target)
    return cleaned or None


def _build_spec_from_v2_payload(request: PresentationRequest, payload: dict[str, Any]) -> PresentationSpec | None:
    modality = payload.get("modality")
    if not isinstance(modality, str) or modality not in _VALID_MODALITIES:
        return None

    targets = _sanitize_targets(payload.get("targets"))
    if targets is None:
        return None

    content_payload = payload.get("content", request.content)
    if content_payload is None:
        content_payload = request.content
    if not isinstance(content_payload, dict):
        return None

    ttl_ms = max(1_000, request.ttl_ms)
    now_ms = int(time.time() * 1000)
    pres_id = f"pres_{uuid.uuid4().hex[:12]}"

    importance_str = request.importance if request.importance in _VALID_IMPORTANCES else "normal"
    interaction_str = request.interaction_mode if request.interaction_mode in _VALID_INTERACTIONS else "dismiss_only"

    return PresentationSpec(
        presentation_id=pres_id,
        source=request.source,
        intent=request.intent,
        importance=Importance(importance_str),
        modality=Modality(modality),
        title=request.title,
        summary=request.summary,
        content=normalize_content(modality, content_payload),
        delivery=DeliverySpec(
            targets=targets,
            ttl_ms=ttl_ms,
        ),
        placement=PlacementSpec(zone=request.placement_zone),
        interaction=InteractionSpec(
            mode=InteractionMode(interaction_str),
            actions=request.actions,
        ),
        lifecycle=LifecycleSpec(expires_at_ms=now_ms + ttl_ms),
        status=PresentationStatus.PENDING,
        created_at_ms=now_ms,
        updated_at_ms=now_ms,
        revision=0,
        metadata=request.metadata,
    )


async def plan_presentation_v2(request: PresentationRequest, llm_router=None) -> PresentationSpec:
    """Plan a presentation with optional LLM-based modality and target selection."""
    if llm_router is None:
        return plan_presentation(request)

    system_prompt, prompt = _build_v2_prompt(request)
    request_meta = {"caller": "presentation.planner.v2"}

    try:
        raw_response: Any
        if hasattr(llm_router, "generate_json"):
            raw_response = llm_router.generate_json(
                prompt,
                system_prompt=system_prompt,
                context_meta=request_meta,
            )
            if inspect.isawaitable(raw_response):
                raw_response = await raw_response
        elif hasattr(llm_router, "generate"):
            raw_response = llm_router.generate(
                prompt,
                system_prompt=system_prompt,
                context_meta=request_meta,
                json_mode=True,
            )
            if inspect.isawaitable(raw_response):
                raw_response = await raw_response
        elif hasattr(llm_router, "route"):
            from aegis_ai.llm.router import LLMRequest, PrivacyLevel, TaskType

            llm_request = LLMRequest(
                task_type=TaskType.PLANNING,
                prompt=prompt,
                system_prompt=system_prompt,
                privacy_level=PrivacyLevel.INTERNAL,
                max_tokens=500,
                temperature=0.2,
                caller="presentation.planner.v2",
                context_meta=request_meta,
                json_mode=True,
            )
            raw_response = llm_router.route(llm_request)
            if inspect.isawaitable(raw_response):
                raw_response = await raw_response
        else:
            return plan_presentation(request)

        payload = _coerce_llm_payload(raw_response)
        if payload is None:
            return plan_presentation(request)

        spec = _build_spec_from_v2_payload(request, payload)
        if spec is None:
            return plan_presentation(request)
        return spec
    except Exception:
        return plan_presentation(request)
