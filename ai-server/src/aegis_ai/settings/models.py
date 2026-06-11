"""Settings models — Pydantic models for all AEGIS configuration.

These models define the structure of user-configurable settings.
They do NOT override PolicyEngine safety decisions.

Architecture reference: docs/architecture.md §5, §7
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ServerSettings(BaseModel):
    """Per-server enable/disable and connection settings."""

    browser_server_enabled: bool = Field(default=True, description="Enable Browser Server")
    pc_server_enabled: bool = Field(default=True, description="Enable PC Server")
    android_server_enabled: bool = Field(default=True, description="Enable Android Server")
    room_server_enabled: bool = Field(default=True, description="Enable Room Server")
    dev_server_enabled: bool = Field(default=True, description="Enable Dev Server")

    health_check_interval_seconds: int = Field(default=30, ge=5, le=3600)
    reconnect_policy: str = Field(default="exponential", description="exponential | linear | manual")


class CapabilityPermission(BaseModel):
    """Per-capability permission override."""

    capability_id: str = Field(..., min_length=1)
    enabled: bool = Field(default=True, description="Whether this capability is available")
    max_safety_level: int = Field(default=4, ge=0, le=4, description="Max allowed safety level (0-4)")


class CapabilityPermissions(BaseModel):
    """Capability permission settings."""

    disabled_capabilities: list[str] = Field(
        default_factory=list,
        description="Capability IDs that are disabled",
    )
    per_capability: dict[str, CapabilityPermission] = Field(
        default_factory=dict,
        description="Per-capability permission overrides",
    )
    allowlist: list[str] = Field(
        default_factory=list,
        description="Capability IDs explicitly allowed (bypass other checks)",
    )
    denylist: list[str] = Field(
        default_factory=list,
        description="Capability IDs explicitly denied (always blocked)",
    )


class AutonomousSettings(BaseModel):
    """Autonomous behavior settings."""

    autonomous_loop_enabled: bool = Field(default=True)
    support_agent_enabled: bool = Field(default=True)
    research_watch_enabled: bool = Field(default=True)
    self_dev_proposal_enabled: bool = Field(default=True)
    daily_briefing_enabled: bool = Field(default=True)

    max_autonomous_runs_per_hour: int = Field(default=20, ge=1, le=100)
    max_autonomous_runs_per_day: int = Field(default=100, ge=1, le=1000)
    cooldown_seconds: int = Field(default=60, ge=0, le=3600)


class MemorySettings(BaseModel):
    """Memory system settings."""

    episodic_retention_days: int = Field(default=90, ge=1, le=365)
    semantic_memory_enabled: bool = Field(default=True)
    procedural_learning_enabled: bool = Field(default=True)
    reflection_enabled: bool = Field(default=True)
    sensitive_data_storage_enabled: bool = Field(default=False, description="Store sensitive data in memory")


class NotificationSettings(BaseModel):
    """Notification settings."""

    approval_notification_enabled: bool = Field(default=True)
    support_suggestions_enabled: bool = Field(default=True)
    daily_briefing_notification: bool = Field(default=True)
    error_notification: bool = Field(default=True)

    quiet_hours_enabled: bool = Field(default=False)
    quiet_hours_start: str = Field(default="22:00", description="HH:MM format")
    quiet_hours_end: str = Field(default="08:00", description="HH:MM format")


class PrivacySettings(BaseModel):
    """Privacy and data retention settings."""

    screenshot_retention_hours: int = Field(default=24, ge=0, le=720)
    notification_text_retention_hours: int = Field(default=168, ge=0, le=8760)
    clipboard_capture_enabled: bool = Field(default=True)
    camera_snapshot_enabled: bool = Field(default=False)
    external_llm_allowed: bool = Field(default=True)
    web_search_allowed: bool = Field(default=True)


class VoiceSettings(BaseModel):
    """Voice I/O settings — default disabled, stubs only."""

    voice_enabled: bool = Field(default=False, description="Enable voice I/O")
    stt_provider: str = Field(
        default="none", description="STT provider: none, faster-whisper, whisper-cpp, cloud, os-speech",
    )
    tts_provider: str = Field(
        default="none", description="TTS provider: none, edge-tts, piper, cloud, os-tts",
    )
    record_audio: bool = Field(default=False, description="Record audio (default off)")
    external_voice_api_allowed: bool = Field(default=False, description="Allow external STT/TTS APIs")
    push_to_talk_only: bool = Field(default=True, description="Push-to-talk only (no always-listening)")
    wake_word_enabled: bool = Field(default=False, description="Wake word detection (default off)")
    voice_data_retention_hours: int = Field(default=0, ge=0, le=168, description="Voice data retention (0=never store)")


class AEGISSettings(BaseModel):
    """Root settings object containing all configuration sections."""

    version: str = Field(default="1.0.0", description="Settings schema version")
    servers: ServerSettings = Field(default_factory=ServerSettings)
    capabilities: CapabilityPermissions = Field(default_factory=CapabilityPermissions)
    autonomous: AutonomousSettings = Field(default_factory=AutonomousSettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
