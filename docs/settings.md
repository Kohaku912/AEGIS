# Settings — AEGIS Configuration Management

> ⚠️ **Goal change (2026-09-27); constraint re-scoped 2026-09-30**: the only constraint is now
> **"*unpermitted* user information must not leave the local environment"** — outbound connections are
> allowed, and user information may be sent externally **with the user's permission**.
> Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. Any "requires approval" / "Level 2" language below is a **risk annotation**,
> not a gate. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).


> **Status**: Implemented
> **Related**: `docs/permissions.md`, `docs/architecture.md` §5, §7

## Overview

AEGIS Settings provides user-configurable management of servers, capabilities,
autonomous behavior, memory, notifications, and privacy. All changes are
validated and audited.

**Critical constraint**: Settings CANNOT weaken PolicyEngine safety decisions.
Forbidden operations remain denied regardless of settings.

## Settings Sections

> **Measured 2026-09-30** from `AEGISSettings()` — every table below lists the fields the
> models actually declare, with the default each one resolves to. The tables were previously
> hand-maintained and had drifted: they listed nine fields that B-6 deleted, omitted the
> `agents` / `intake` / `voice` sections entirely, and gave `external_llm_allowed` and
> `web_search_allowed` as `true` when both default to `false`. The model is the source of
> truth; if a row here disagrees with `src/aegis_ai/settings/models.py`, the row is wrong.

### 1. Server Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `browser_server_enabled` | true | Enable Browser Server |
| `pc_server_enabled` | true | Enable PC Server |
| `android_server_enabled` | true | Enable Android Server |
| `room_server_enabled` | true | Enable Room Server |
| `dev_server_enabled` | true | Enable Dev Server |

### 2. Capability Permissions

| Setting | Default | Description |
|---------|---------|-------------|
| `disabled_capabilities` | [] | Capability IDs that are disabled |
| `per_capability` | {} | Per-capability permission overrides |
| `denylist` | [] | Explicitly denied capabilities |

### 3. Autonomous Behavior

| Setting | Default | Description |
|---------|---------|-------------|
| `autonomous_loop_enabled` | true | Enable autonomous loop |
| `support_agent_enabled` | true | Enable support agent |
| `max_autonomous_runs_per_hour` | 20 | **Declared** rate limit. Measured 2026-09-29: read only by the settings validator (`> 100` rejected) and the field's own `le=100`; **the autonomous loop never consults it** (B-6 in `PROJECT_STATUS_REVIEW.md`) |
| `cooldown_seconds` | 60 | Cooldown between runs |
| `evaluation_interval_seconds` | 60 | Evaluation interval |
| `min_action_interval_seconds` | 60 | Minimum interval between actions |
| `max_tasks_per_cycle` | 8 | Maximum tasks per cycle |
| `min_llm_interval_seconds` | 0 | Minimum interval between LLM calls |
| `quiet_hours` | "22:00-08:00" | Quiet hours window |

### 4. Agent Runtime

| Setting | Default | Description |
|---------|---------|-------------|
| `enabled` | **false** | Master switch for the AEGIS agent runtime. Default OFF — with it off, an `ai-server.agent.*` step fails with "agent backend is not registered" rather than running |
| `backend` | "local" | Agent backend name registered in `aegis_ai.agents.backends` |
| `timeout_seconds` | 600 | Default per-task timeout |

### 5. Intake Filter

> The values in this section are **not read by the live path**: the components constructed
> at runtime are `L1Router` / `L1Executor`, and neither takes settings. See B-6 in
> `PROJECT_STATUS_REVIEW.md`.

| Setting | Default | Description |
|---------|---------|-------------|
| `enabled` | true | Master switch for the intake filter |
| `requires_agent_threshold` | 0.5 | `requires_agent_score` at or above this value takes the Agent-delegate path |
| `fallback_requires_agent` | false | Value used when the LLM call fails; `false` is the safe side (no agent) |

### 6. Memory Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `episodic_retention_days` | 90 | How long to keep episodes. Reaches real purge arithmetic — `backup/retention.py` turns it into the prune cutoff |

### 7. Notification Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `approval_notification_enabled` | true | Notify on approval requests |
| `support_suggestions_enabled` | true | Support agent suggestions |
| `daily_briefing_notification` | true | Daily briefing notifications |
| `error_notification` | true | Error notifications |
| `quiet_hours_enabled` | false | Quiet hours mode |
| `quiet_hours_start` | "22:00" | Quiet hours start |
| `quiet_hours_end` | "08:00" | Quiet hours end |

### 8. Privacy Settings

The five egress keys at the end of this table are the **locks for the single constraint**:
an external destination requires the master switch **and** a matching feature flag **and**
an allowlist entry. All are closed by default, and the enforcement point is
`aegis_ai/egress/gate.py` — not the settings UI. See [`egress-gate.md`](egress-gate.md).

| Setting | Default | Description |
|---------|---------|-------------|
| `screenshot_retention_hours` | 24 | Screenshot retention |
| `notification_text_retention_hours` | 168 | Notification text retention |
| `clipboard_capture_enabled` | true | Clipboard capture |
| `camera_snapshot_enabled` | false | Camera snapshot (disabled by default) |
| `personal_data_enabled` | true | Personal-data capture master switch |
| `personal_data_pc_uia_enabled` | true | PC UI Automation capture |
| `personal_data_android_a11y_enabled` | true | Android accessibility capture |
| `personal_data_camera_enabled` | false | Personal-data camera capture |
| `personal_data_mic_enabled` | false | Personal-data microphone capture |
| `personal_data_value_capture_enabled` | true | Value capture |
| `personal_data_screenshot_on_change` | true | Screenshot on change |
| `personal_data_event_retention_days` | 3650 | Personal-data event retention |
| `personal_data_screenshot_retention_hours` | 24 | Personal-data screenshot retention |
| `personal_data_media_retention_hours` | 72 | Personal-data media retention |
| `personal_data_notification_raw_text` | true | Keep raw notification text |
| `external_egress_allowed` | **false** | **Master switch** for any external egress |
| `egress_allowed_hosts` | [] | Explicit external-host allowlist |
| `external_llm_allowed` | **false** | Allow cloud LLM calls (use the local engine instead) |
| `web_search_allowed` | **false** | Allow external web search |
| `external_messaging_allowed` | **false** | Allow outbound messaging (LINE/Discord/Email) to allowlisted hosts |

### 9. Voice Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `voice_enabled` | **false** | Enable voice I/O |
| `stt_provider` | "none" | STT provider: none, faster-whisper, whisper-cpp, cloud, os-speech |
| `tts_provider` | "none" | TTS provider: none, edge-tts, piper, cloud, os-tts |
| `record_audio` | false | Record audio (default off) |
| `external_voice_api_allowed` | **false** | Allow external STT/TTS APIs |
| `push_to_talk_only` | true | Push-to-talk only (no always-listening). **Declared but unread**: the field is a pinned default posture, and nothing in `src/` consults it yet |
| `wake_word_enabled` | false | Wake word detection (default off) |
| `voice_data_retention_hours` | 0 | Voice data retention (0 = never store) |

## Web UI

Settings can be viewed and changed via the Web UI:

```
GET  /settings              → view all settings
GET  /settings/<section>    → view a section
POST /settings/<section>    → update a section
POST /settings/reset        → reset to defaults
GET  /settings/export       → export as JSON
POST /settings/import       → import from JSON
GET  /settings/capabilities → list capabilities with status
```

The page **discovers** its controls from the `GET /api/settings` payload rather than
listing them, so a field added or deleted in the models moves the UI with it. The one
hand-written part is the `preferred` list (which controls sort first), and
`tests/test_settings_ui_matches_the_schema.py` keeps every entry naming a real field.

`POST /settings/<section>` **rejects a key the section does not declare** rather than
ignoring it, so a write naming a deleted field now fails loudly.

## Safety Rules

- Forbidden capabilities CANNOT be re-enabled
- Camera snapshot requires explicit confirmation
- All changes are audited
- Settings CANNOT weaken PolicyEngine
- Level 3 (FORBIDDEN) cannot be made allowed
