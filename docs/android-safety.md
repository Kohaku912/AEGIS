# Android Server — Safety & Privacy

> **Status**: Code-backed Android companion safety model
> **Related**: `docs/android-server.md`, `docs/architecture.md` §7

## Safety Level Classification

### Level 0 — READ_ONLY (auto-allowed)

| Capability | Permission | Redaction |
|-----------|-----------|-----------|
| `android.get_notifications` | NotificationListenerService | **Required** — OTP, cards, emails, phones |
| `android.get_current_app` | — | None |
| `android.get_device_info` | — | None |
| `android.get_screenshot` | MediaProjection | Treat as ephemeral — may contain sensitive content |
| `android.get_ui_tree` | AccessibilityService | Password fields flagged as `is_password: true` |

### Level 1 — SAFE_ACTION (auto-allowed, audited)

| Capability | Notes |
|-----------|-------|
| `android.show_overlay` | アプリ内 Overlay表示 |
| `android.hide_overlay` | Overlay非表示 |
| `android.open_app` | アプリ起動 |
| `android.press_home` | ホームボタン押下 |

### Level 2 — APPROVAL_REQUIRED

| Capability | Approval Flow |
|-----------|---------------|
| `android.tap` | Approval UI → execute |
| `android.swipe` | Approval UI → execute |
| `android.type_text` | Approval UI → password field check → execute |

### Explicitly Denied (always DENY)

| Capability | Reason |
|-----------|--------|
| `android.send_sms` | SMS送信 — 外部送信 |
| `android.send_dm` | DM送信 — 外部送信 |
| `android.post_sns` | SNS投稿 — 外部送信 |
| `android.access_contacts` | 連絡先 — プライバシー |
| `android.make_call` | 通話 — 外部操作 |
| `android.type_password` | パスワード自動入力 — セキュリティ |
| `android.click_payment_button` | 決済 — 金銭操作 |
| `android.captcha_bypass` | CAPTCHA回避 — 規約違反 |
| `android.tos_bypass` | ToS回避 — 規約違反 |

## Notification Content Handling

### Redaction

All notification text passes through `NotificationFilter.redact()`:

| Pattern | Replacement | Example |
|---------|-------------|---------|
| Credit card numbers | `[CARD_REDACTED]` | `4111 1111 1111 1111` |
| Email addresses | `[EMAIL_REDACTED]` | `test@example.com` |
| International phone numbers | `[PHONE_REDACTED]` | `+819012345678` |
| Passwords/tokens in text | `[REDACTED]` | `password: secret123` |
| OTP codes (4-8 digit) | `[OTP_REDACTED]` | `Code: 123456` |

### Denylist — Blocked Apps

Notifications from these apps are **never forwarded**:

| Package | Reason |
|---------|--------|
| `com.google.android.apps.authenticator` | 2FA codes |
| `com.azure.authenticator` | 2FA codes |
| `com.duosecurity.duomobile` | 2FA codes |
| `com.aegis.android` | Self (prevent echo) |
| `android` / `com.android.systemui` | System noise |

### Allowlist — Always Allowed

| Package | Reason |
|---------|--------|
| `com.android.messaging` | SMS/Messages |
| `com.google.android.gm` | Gmail |
| `com.slack` / `com.discord` | Chat |
| `jp.naver.line.android` | LINE |
| `com.twitter.android` / `com.whatsapp` / `com.telegram.messenger` | SNS |

## Screenshot Safety

- Screenshots capture the **entire visible screen** — including sensitive content
- Screenshots are **never transmitted externally** — they stay on the local network
- In mock mode, screenshots return `[MOCK_SCREENSHOT]` — no real screen capture
- Screenshots should be treated as **ephemeral** — not persisted long-term

## UI Tree Safety

- UI tree may contain sensitive text (form fields, displayed content)
- Password fields are flagged with `is_password: true`
- `android.type_text` checks for password fields and denies if detected
- UI tree data should not be logged without redaction

## Password Field Protection

The `contains_password_field()` function recursively checks the UI tree:

```python
def contains_password_field(ui_tree: dict) -> bool:
    if ui_tree.get("is_password"):
        return True
    for child in ui_tree.get("children", []):
        if contains_password_field(child):
            return True
    return False
```

When a password field is detected:
1. `android.type_text` returns error: "Cannot type into password fields"
2. The action is blocked at the client level (before PolicyEngine)
3. The event is logged to AuditLog

## Permission Requirements

| Permission | User Action | Risk |
|-----------|-------------|------|
| NotificationListenerService | Settings → Notification access | Low — read-only |
| MediaProjection | App prompt → Allow each session | Medium — screen capture |
| AccessibilityService | Settings → Accessibility | High — UI interaction |
| アプリ内 Overlay | No special permission | Low — display only |

### Permission Missing Handling

When a required permission is not granted:
1. Android Server pushes `android.permission_missing` event (URGENT)
2. TriggerEngine wakes AI
3. Support Agent can suggest setup instructions
4. The capability is still registered but invocation returns permission error

## Data Flow

```
Android Device
  ├── NotificationListenerService → notifications
  ├── MediaProjection → screenshots
  ├── AccessibilityService → UI tree, tap, swipe
  └── アプリ内 Overlay → overlay display
        ↓
AegisGrpcClient (gRPC)
        ↓
AEGIS Core
  ├── NotificationFilter (redaction, denylist, allowlist)
  ├── EventBus → TriggerEngine → ContextBuilder
  ├── ToolBroker → PolicyEngine → Approval UI (Level 2)
  └── AuditLog
```

## Testing Safety

- CI tests use `MockAndroidProvider` — no real device calls
- Local tests with real device are marked `@pytest.mark.android_local`
- `MockAndroidProvider.call_log` tracks all invocations for audit
- No secrets, tokens, or credentials in test fixtures
- Password field detection is tested with mock UI tree
