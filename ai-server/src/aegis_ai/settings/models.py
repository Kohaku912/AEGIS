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
    denylist: list[str] = Field(
        default_factory=list,
        description="Capability IDs explicitly denied (always blocked)",
    )


class AutonomousSettings(BaseModel):
    """Autonomous behavior settings."""

    autonomous_loop_enabled: bool = Field(default=True)
    support_agent_enabled: bool = Field(default=True)

    max_autonomous_runs_per_hour: int = Field(default=20, ge=1, le=100)
    cooldown_seconds: int = Field(default=60, ge=0, le=3600)
    evaluation_interval_seconds: int = Field(default=60, ge=1, le=3600)
    min_action_interval_seconds: int = Field(default=60, ge=0, le=86400)
    max_tasks_per_cycle: int = Field(default=8, ge=1, le=20)
    min_llm_interval_seconds: int = Field(default=0, ge=0, le=86400)
    quiet_hours: str = Field(default="22:00-08:00")


class AgentSettings(BaseModel):
    """Agent runtime settings (instruction.md §36).

    `enabled=False` is the safe default. When False, the agent_backend field
    on `AegisRuntime` stays `None`, so an `ai-server.agent.*` step fails with
    "agent backend is not registered" instead of running.

    Note what this switch does **not** do: it does not hide the agent
    capability from the LLM-facing list. `CapabilityCatalog.list_for_llm`
    lists every enabled capability unconditionally — a manifest-declared
    feature flag once gated that and was removed as never-supplied, since no
    caller ever passed a flag set (PROJECT_STATUS_REVIEW.md row A-12).
    """

    enabled: bool = Field(
        default=False,
        description="Master switch for the AEGIS agent runtime. Default OFF.",
    )
    backend: str = Field(
        default="local",
        description="Agent backend name registered in aegis_ai.agents.backends.",
    )
    timeout_seconds: int = Field(
        default=600,
        ge=1,
        le=86400,
        description="Default per-task timeout in seconds.",
    )


class IntakeSettings(BaseModel):
    """Intake filter settings (instruction.md §36 Phase 4).

    全 Event をそのまま Agent に投げず、小型 LLM で「Agent 不要」を早期判定する経路の
    ための設定。`enabled=False` で Intake を OFF にして既存挙動に戻す。

    注: この節の値は live な経路からは読まれない — 実行時に構築されるのは
    `L1Router`/`L1Executor` で、どちらも設定を取らない。
    """

    enabled: bool = Field(
        default=True,
        description="Master switch for the intake filter. When False, intake is skipped and "
        "all observations flow through the existing autonomous loop.",
    )
    requires_agent_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="intake.classifier() が返した `requires_agent_score` がこの値以上のときだけ "
        "Agent delegate 経路に進む。それ以下は LLMTaskInterpreter 既存経路。",
    )
    fallback_requires_agent: bool = Field(
        default=False,
        description="LLM 呼び出しに失敗したときのフォールバック値。False にすると安全側 (Agent 起動しない)。",
    )


class MemorySettings(BaseModel):
    """Memory system settings."""

    episodic_retention_days: int = Field(default=90, ge=1, le=365)


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
    personal_data_enabled: bool = Field(default=True)
    personal_data_pc_uia_enabled: bool = Field(default=True)
    personal_data_android_a11y_enabled: bool = Field(default=True)
    personal_data_camera_enabled: bool = Field(default=False)
    personal_data_mic_enabled: bool = Field(default=False)
    personal_data_value_capture_enabled: bool = Field(default=True)
    personal_data_screenshot_on_change: bool = Field(default=True)
    personal_data_event_retention_days: int = Field(default=3650, ge=1, le=36500)
    personal_data_screenshot_retention_hours: int = Field(default=24, ge=0, le=8760)
    personal_data_media_retention_hours: int = Field(default=72, ge=0, le=8760)
    personal_data_notification_raw_text: bool = Field(default=True)
    # ── Egress (the single constraint) ──────────────────────────────────────
    # All external transmission is denied by default. See aegis_ai/egress/.
    # These flags are *additional* locks: an external destination requires the
    # master switch AND a matching feature flag AND an allowlist entry.
    external_egress_allowed: bool = Field(
        default=False, description="Master switch for any external egress (default: closed)"
    )
    egress_allowed_hosts: list[str] = Field(
        default_factory=list, description="Explicit external-host allowlist (default: empty)"
    )
    external_llm_allowed: bool = Field(
        default=False, description="Allow cloud LLM calls (default: closed — use local Ollama)"
    )
    web_search_allowed: bool = Field(
        default=False, description="Allow external web search (default: closed)"
    )
    external_messaging_allowed: bool = Field(
        default=False,
        description=(
            "Allow outbound messaging (LINE/Discord/Email) to allowlisted hosts (default: closed). "
            "A message body is always the user's own content, so the standing path needs the master "
            "switch AND this flag AND an allowlist entry; a recorded (host, purpose) grant also works."
        ),
    )


class VoiceSettings(BaseModel):
    """Voice I/O settings — **default disabled**.

    The providers are real, not stubs: ``stt_provider`` selects the local
    faster-whisper engine and ``tts_provider`` dispatches between a local OS
    engine and a permission-gated external one. A request that names a *local*
    provider is never served by the cloud engine.
    """

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
    agents: AgentSettings = Field(default_factory=AgentSettings)
    intake: IntakeSettings = Field(default_factory=IntakeSettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
