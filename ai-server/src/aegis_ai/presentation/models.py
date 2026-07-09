"""Presentation Engine data models.

Safety, safety_level, and requires_approval are intentionally absent from
PresentationSpec — safety enforcement belongs to the *source* capability,
not to the presentation layer.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


# ── Enums ────────────────────────────────────────────────────────


class PresentationStatus(Enum):
    """Lifecycle states for a presentation."""

    PENDING = "pending"
    QUEUED = "queued"
    ACTIVE = "active"
    DELIVERED = "delivered"
    DISMISSED = "dismissed"
    EXPIRED = "expired"
    FAILED = "failed"


class Modality(Enum):
    """Allowed rendering modalities.

    Only these exact values are accepted — arbitrary HTML/JS is never generated.
    """

    TEXT_CARD = "text_card"
    CHART_PANEL = "chart_panel"
    DIAGRAM_PANEL = "diagram_panel"
    GLTF_MODEL = "gltf_model"
    OVERLAY_SHORT = "overlay_short"
    IMAGE = "image"
    VIDEO = "video"
    SPEECH = "speech"
    HUD = "hud"


class Importance(Enum):
    """Presentation urgency / importance level."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Placement(Enum):
    """Where the presentation should appear."""

    DASHBOARD = "dashboard"
    PC_OVERLAY = "pc_overlay"
    ANDROID_OVERLAY = "android_overlay"
    XR_SCENE = "xr_scene"
    AUTO = "auto"


class InteractionMode(Enum):
    """User interaction model for the presentation."""

    NONE = "none"
    DISMISS_ONLY = "dismiss_only"
    ACTION_BUTTONS = "action_buttons"
    EXPANDABLE = "expandable"


# ── Sub-specs ────────────────────────────────────────────────────


@dataclass
class DeliverySpec:
    """How the presentation should be delivered."""

    targets: list[str] = field(default_factory=lambda: ["dashboard"])
    ttl_ms: int = 3_600_000  # 1 hour default
    retry_count: int = 0
    retry_interval_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "targets": self.targets,
            "ttl_ms": self.ttl_ms,
            "retry_count": self.retry_count,
            "retry_interval_ms": self.retry_interval_ms,
        }


@dataclass
class PlacementSpec:
    """Where the presentation appears within a target surface."""

    zone: str = "main"
    priority: int = 0
    persistent: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "zone": self.zone,
            "priority": self.priority,
            "persistent": self.persistent,
        }


@dataclass
class InteractionSpec:
    """How the user can interact with the presentation."""

    mode: InteractionMode = InteractionMode.DISMISS_ONLY
    actions: list[dict[str, Any]] = field(default_factory=list)
    callback_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode.value,
            "actions": self.actions,
            "callback_id": self.callback_id,
        }


@dataclass
class LifecycleSpec:
    """TTL and auto-expiry behaviour."""

    expires_at_ms: int = 0
    auto_dismiss_on_read: bool = False
    max_revisions: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "expires_at_ms": self.expires_at_ms,
            "auto_dismiss_on_read": self.auto_dismiss_on_read,
            "max_revisions": self.max_revisions,
        }


# ── Main spec ────────────────────────────────────────────────────


@dataclass
class PresentationSpec:
    """Full specification for a single presentation.

    This is the canonical data shape stored in the object store and sent
    to rendering adapters.

    NOTE: ``safety``, ``safety_level``, ``requires_approval`` are
    **intentionally absent** — safety belongs to the source capability.
    """

    presentation_id: str = ""
    source: str = ""
    intent: str = ""
    importance: Importance = Importance.NORMAL
    modality: Modality = Modality.TEXT_CARD
    title: str = ""
    summary: str = ""
    content: dict[str, Any] = field(default_factory=dict)
    delivery: DeliverySpec = field(default_factory=DeliverySpec)
    placement: PlacementSpec = field(default_factory=PlacementSpec)
    interaction: InteractionSpec = field(default_factory=InteractionSpec)
    lifecycle: LifecycleSpec = field(default_factory=LifecycleSpec)
    # bookkeeping
    status: PresentationStatus = PresentationStatus.PENDING
    created_at_ms: int = 0
    updated_at_ms: int = 0
    revision: int = 0
    user_actions: list[dict[str, Any]] = field(default_factory=list)
    delivery_state: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    # ── Serialisation helpers ────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        return {
            "presentation_id": self.presentation_id,
            "source": self.source,
            "intent": self.intent,
            "importance": self.importance.value,
            "modality": self.modality.value,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "delivery": self.delivery.to_dict(),
            "placement": self.placement.to_dict(),
            "interaction": self.interaction.to_dict(),
            "lifecycle": self.lifecycle.to_dict(),
            "status": self.status.value,
            "created_at_ms": self.created_at_ms,
            "updated_at_ms": self.updated_at_ms,
            "revision": self.revision,
            "user_actions": self.user_actions,
            "delivery_state": self.delivery_state,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PresentationSpec:
        """Reconstruct from a JSON-safe dict."""
        return cls(
            presentation_id=data.get("presentation_id", ""),
            source=data.get("source", ""),
            intent=data.get("intent", ""),
            importance=Importance(data.get("importance", "normal")),
            modality=Modality(data.get("modality", "text_card")),
            title=data.get("title", ""),
            summary=data.get("summary", ""),
            content=data.get("content", {}),
            delivery=DeliverySpec(**data.get("delivery", {})),
            placement=PlacementSpec(**data.get("placement", {})),
            interaction=InteractionSpec(
                mode=InteractionMode(data.get("interaction", {}).get("mode", "dismiss_only")),
                actions=data.get("interaction", {}).get("actions", []),
                callback_id=data.get("interaction", {}).get("callback_id", ""),
            ),
            lifecycle=LifecycleSpec(**data.get("lifecycle", {})),
            status=PresentationStatus(data.get("status", "pending")),
            created_at_ms=data.get("created_at_ms", 0),
            updated_at_ms=data.get("updated_at_ms", 0),
            revision=data.get("revision", 0),
            user_actions=data.get("user_actions", []),
            delivery_state=data.get("delivery_state", {}),
            metadata=data.get("metadata", {}),
        )


# ── Presentation request (what callers submit) ───────────────────


@dataclass
class PresentationRequest:
    """Lightweight request submitted by AEGIS internal callers.

    The PresentationPlanner / PresentationManager converts this into a
    full PresentationSpec before persisting.
    """

    source: str = ""
    intent: str = ""
    importance: str = "normal"
    modality: str = "text_card"
    title: str = ""
    summary: str = ""
    content: dict[str, Any] = field(default_factory=dict)
    targets: list[str] = field(default_factory=lambda: ["dashboard"])
    ttl_ms: int = 3_600_000
    placement_zone: str = "main"
    interaction_mode: str = "dismiss_only"
    actions: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        importance = self.importance.value if isinstance(self.importance, Importance) else self.importance
        modality = self.modality.value if isinstance(self.modality, Modality) else self.modality
        interaction_mode = (
            self.interaction_mode.value if isinstance(self.interaction_mode, InteractionMode) else self.interaction_mode
        )
        return {
            "source": self.source,
            "intent": self.intent,
            "importance": importance,
            "modality": modality,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "targets": self.targets,
            "ttl_ms": self.ttl_ms,
            "placement_zone": self.placement_zone,
            "interaction_mode": interaction_mode,
            "actions": self.actions,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PresentationRequest:
        importance = data.get("importance", "normal")
        if isinstance(importance, Importance):
            importance = importance.value
        modality = data.get("modality", "text_card")
        if isinstance(modality, Modality):
            modality = modality.value
        interaction_mode = data.get("interaction_mode", "dismiss_only")
        if isinstance(interaction_mode, InteractionMode):
            interaction_mode = interaction_mode.value
        return cls(
            source=data.get("source", ""),
            intent=data.get("intent", ""),
            importance=importance,
            modality=modality,
            title=data.get("title", ""),
            summary=data.get("summary", ""),
            content=data.get("content", {}),
            targets=data.get("targets", ["dashboard"]),
            ttl_ms=data.get("ttl_ms", 3_600_000),
            placement_zone=data.get("placement_zone", "main"),
            interaction_mode=interaction_mode,
            actions=data.get("actions", []),
            metadata=data.get("metadata", {}),
        )
