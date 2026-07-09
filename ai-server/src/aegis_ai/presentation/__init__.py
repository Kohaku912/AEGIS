"""Presentation Engine — AEGIS output layer for rich user-facing content.

The Presentation Engine is NOT a state viewer.  It is the layer that delivers
information AEGIS decided the user should see, in the format best suited to
the content: text cards, charts, diagrams, 3D models, overlays, etc.

Safety is never attached to the *presentation* itself — safety enforcement
happens when the content is *sourced* through an existing capability.
"""

from aegis_ai.presentation.manager import PresentationManager
from aegis_ai.presentation.models import (
    DeliverySpec,
    InteractionSpec,
    LifecycleSpec,
    PlacementSpec,
    PresentationSpec,
    PresentationStatus,
)

__all__ = [
    "DeliverySpec",
    "InteractionSpec",
    "LifecycleSpec",
    "PlacementSpec",
    "PresentationManager",
    "PresentationSpec",
    "PresentationStatus",
]
