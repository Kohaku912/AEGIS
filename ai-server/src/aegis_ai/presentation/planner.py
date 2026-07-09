"""Presentation Planner — converts a PresentationRequest into a PresentationSpec.

The planner is intentionally deterministic right now — no LLM call.
Future versions may use the LLM to choose modality, importance, or content
layout.  For the MVP the mapping is mechanical.
"""

from __future__ import annotations

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
    PlacementSpec,
    PresentationRequest,
    PresentationSpec,
    PresentationStatus,
)


_VALID_MODALITIES = {m.value for m in Modality}
_VALID_IMPORTANCES = {i.value for i in Importance}
_VALID_INTERACTIONS = {i.value for i in InteractionMode}


def plan_presentation(request: PresentationRequest) -> PresentationSpec:
    """Convert a lightweight request into a fully-specified PresentationSpec.

    Validation is lenient — unknown values fall back to safe defaults rather
    than raising, so callers don't need to be perfectly precise.
    """
    now_ms = int(time.time() * 1000)
    pres_id = f"pres_{uuid.uuid4().hex[:12]}"

    modality_str = request.modality if request.modality in _VALID_MODALITIES else "text_card"
    importance_str = request.importance if request.importance in _VALID_IMPORTANCES else "normal"
    interaction_str = request.interaction_mode if request.interaction_mode in _VALID_INTERACTIONS else "dismiss_only"

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
