# Notification Gateway — Outbound Communication

> ⚠️ **Goal change (2026-09-27); constraint re-scoped 2026-09-30**: the only constraint is now
> **"*unpermitted* user information must not leave the local environment"** — outbound connections are
> allowed, and user information may be sent externally **with the user's permission**.
> Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. Any "requires approval" / "Level 2" language below is a **risk annotation**,
> not a gate. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).


> ⚠️ **2026-10-04 実測 — この文書の大半は実装より先を書いていた。**
> `src/` の全モジュールを `ast` で走査した結果、**構築される通知クラスは
> `NotificationManager` ただ 1 つ**である（`runtime.py` が
> `NotificationManager(event_manager=event_manager)` として作る）。次の 9 つは
> **どこからも生成されない**: `NotificationRouter`、`NotificationPreferences`、
> `QuietHoursManager`、`NotificationDigest`、6 つのチャネルクラス
> （Dashboard / WebChat / CLI / LINE / Discord / Email）、`OsNotificationProvider`。
> したがって以下の記述は**現時点で動いていない** ——
> **§Quiet Hours**（判定は一度も走らない）、**§Preferences**（7 フィールドは読まれない）、
> **§Overview** の Web Chat / CLI / OS notification の各行、**§Safety** の
> "Quiet hours respected" / "All notifications audited" / "Spam prevention"。
> 生きているのは `NotificationManager` の `create_notification` / `mark_read` /
> `dismiss` / `list_unread` と、それを読む `GET /api/notifications` 系 3 ルート
> （`web/manager_routes.py:314,329,341`）だけである。
> 正は [`feature-catalog.md`](feature-catalog.md) §7・§8（宣言のみ）と §9（文書との食い違い）。
> ピン: `ai-server/tests/test_notification_settings_are_read_only_by_dead_code.py`（22 テスト、
> 変異 9/9 検出）。


> **Status**: Implemented (2026-06-17)
> **Related**: `docs/interaction-hub.md`, `docs/settings.md`

## Overview

The Notification Gateway sends notifications to users through local channels:
- **Dashboard** — stored for display on Operations Dashboard
- **Web Chat** — sent to active chat sessions
- **CLI** — displayed in terminal
- **OS notification** — PC Server overlay, or a logged fallback when no overlay is available

External channels (**LINE**, **Discord**, **Email**) are implemented senders, refused by the egress
gate until the user permits the destination. They are not stubs; see
[`external-integrations.md`](external-integrations.md).

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
