# Notification Gateway — Outbound Communication

> **Status**: Implemented (2026-06-17)
> **Related**: `docs/interaction-hub.md`, `docs/settings.md`

## Overview

The Notification Gateway sends notifications to users through local channels:
- **Dashboard** — stored for display on Operations Dashboard
- **Web Chat** — sent to active chat sessions
- **CLI** — displayed in terminal

External channels (LINE, Discord, Email, OS notifications) are stubs only.

### NotificationManager

**File**: `ai-server/src/aegis_ai/notification/notification_manager.py`

Runtime-managed notification system. Provides:
- **Push**: Create and store notifications
- **Read**: Mark notifications as read
- **Query**: Filter by type, severity, read status
- API: `GET /api/notifications`, `POST /api/notifications/<id>/read`

## Notification Types

| Type | Default Severity | Description |
|------|-----------------|-------------|
| `APPROVAL_REQUIRED` | HIGH | Approval needed for action |
| `SUPPORT_SUGGESTION` | NORMAL | Support agent suggestion |
| `RESEARCH_COMPLETED` | LOW | Research finished |
| `RESEARCH_FAILED` | HIGH | Research failed |
| `SERVER_DISCONNECTED` | HIGH | Server went offline |
| `PERMISSION_MISSING` | HIGH | Android permission missing |
| `SELF_DEV_PROPOSAL` | NORMAL | Self-dev improvement proposal |
| `SELF_DEV_TEST_FAILED` | HIGH | Self-dev test failure |
| `ROOM_ALERT` | CRITICAL | Room sensor alert |
| `SECURITY_ALERT` | CRITICAL | Security event |
| `DAILY_BRIEFING` | LOW | Daily briefing |
| `BUDGET_WARNING` | HIGH | Budget exceeded |

## Severity → Channel Routing

| Severity | Channels |
|----------|---------|
| LOW | Dashboard |
| NORMAL | Dashboard + Web Chat |
| HIGH | Dashboard + Web Chat + CLI |
| CRITICAL | Dashboard + Web Chat + CLI |

## Quiet Hours

Non-critical notifications are deferred during quiet hours.
Critical notifications (ROOM_ALERT, SECURITY_ALERT) bypass quiet hours.

## Preferences

Users can enable/disable notification types via Settings:
- `approval_notification_enabled`
- `support_suggestions_enabled`
- `daily_briefing_notification`
- `error_notification`

## Safety

- External channels are stubs only
- Sensitive content is redacted for external channels
- Spam prevention (max 10 per type)
- Quiet hours respected
- All notifications audited
