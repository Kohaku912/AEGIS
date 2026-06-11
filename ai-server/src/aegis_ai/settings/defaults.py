"""Default settings for AEGIS."""

from __future__ import annotations

from aegis_ai.settings.models import AEGISSettings


def create_default_settings() -> AEGISSettings:
    """Create default AEGIS settings with safe defaults."""
    return AEGISSettings()
