"""Collection / retention policy from settings."""

from __future__ import annotations

from typing import Any

from aegis_ai.personal_data.models import CollectionPolicy


def policy_from_settings(settings: Any | None) -> CollectionPolicy:
    privacy = getattr(settings, "privacy", None) if settings is not None else None
    if privacy is None:
        return CollectionPolicy()
    return CollectionPolicy(
        enabled=bool(getattr(privacy, "personal_data_enabled", True)),
        pc_uia_enabled=bool(getattr(privacy, "personal_data_pc_uia_enabled", True)),
        android_a11y_enabled=bool(getattr(privacy, "personal_data_android_a11y_enabled", True)),
        camera_enabled=bool(getattr(privacy, "personal_data_camera_enabled", False)),
        mic_enabled=bool(getattr(privacy, "personal_data_mic_enabled", False)),
        value_capture_enabled=bool(getattr(privacy, "personal_data_value_capture_enabled", True)),
        screenshot_on_change=bool(getattr(privacy, "personal_data_screenshot_on_change", True)),
        event_retention_days=int(getattr(privacy, "personal_data_event_retention_days", 3650)),
        screenshot_retention_hours=int(
            getattr(privacy, "personal_data_screenshot_retention_hours", None)
            or getattr(privacy, "screenshot_retention_hours", 24)
        ),
        media_retention_hours=int(getattr(privacy, "personal_data_media_retention_hours", 72)),
        notification_raw_text=bool(getattr(privacy, "personal_data_notification_raw_text", True)),
    )
