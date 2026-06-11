# Settings — AEGIS Configuration Management

> **Status**: Implemented
> **Related**: `docs/permissions.md`, `docs/architecture.md` §5, §7

## Overview

AEGIS Settings provides user-configurable management of servers, capabilities,
autonomous behavior, memory, notifications, and privacy. All changes are
validated and audited.

**Critical constraint**: Settings CANNOT weaken PolicyEngine safety decisions.
Forbidden operations remain denied regardless of settings.

## Settings Sections

### 1. Server Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `browser_server_enabled` | true | Enable Browser Server |
| `pc_server_enabled` | true | Enable PC Server |
| `android_server_enabled` | true | Enable Android Server |
| `room_server_enabled` | true | Enable Room Server |
| `dev_server_enabled` | true | Enable Dev Server |
| `health_check_interval_seconds` | 30 | Health check interval |
| `reconnect_policy` | "exponential" | Reconnection strategy |

### 2. Capability Permissions

| Setting | Default | Description |
|---------|---------|-------------|
| `disabled_capabilities` | [] | Capability IDs that are disabled |
| `per_capability` | {} | Per-capability permission overrides |
| `allowlist` | [] | Explicitly allowed capabilities |
| `denylist` | [] | Explicitly denied capabilities |

### 3. Autonomous Behavior

| Setting | Default | Description |
|---------|---------|-------------|
| `autonomous_loop_enabled` | true | Enable autonomous loop |
| `support_agent_enabled` | true | Enable support agent |
| `research_watch_enabled` | true | Enable periodic research |
| `self_dev_proposal_enabled` | true | Enable self-dev proposals |
| `daily_briefing_enabled` | true | Enable daily briefing |
| `max_autonomous_runs_per_hour` | 20 | Rate limit |
| `cooldown_seconds` | 60 | Cooldown between runs |

### 4. Memory Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `episodic_retention_days` | 90 | How long to keep episodes |
| `semantic_memory_enabled` | true | Enable semantic memory |
| `procedural_learning_enabled` | true | Enable procedural learning |
| `reflection_enabled` | true | Enable reflection loop |
| `sensitive_data_storage_enabled` | false | Store sensitive data |

### 5. Notification Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `approval_notification_enabled` | true | Notify on approval requests |
| `support_suggestions_enabled` | true | Support agent suggestions |
| `daily_briefing_notification` | true | Daily briefing notifications |
| `quiet_hours_enabled` | false | Quiet hours mode |
| `quiet_hours_start` | "22:00" | Quiet hours start |
| `quiet_hours_end` | "08:00" | Quiet hours end |

### 6. Privacy Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `screenshot_retention_hours` | 24 | Screenshot retention |
| `clipboard_capture_enabled` | true | Clipboard capture |
| `camera_snapshot_enabled` | false | Camera snapshot (disabled by default) |
| `external_llm_allowed` | true | External LLM API |
| `web_search_allowed` | true | Web search |

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

## Safety Rules

- Forbidden capabilities CANNOT be re-enabled
- Camera snapshot requires explicit confirmation
- All changes are audited
- Settings CANNOT weaken PolicyEngine
- Level 3 (FORBIDDEN) cannot be made allowed
