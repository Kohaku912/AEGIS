# Android Server — Design & Usage

> **Status**: Phase 4.2 + Action capabilities (screenshot, UI tree, overlay, basic actions)
> **Language**: Kotlin (Android)
> **Permissions**: MediaProjection, AccessibilityService, Overlay (ユーザー明示的有効化)

## Overview

The Android Server provides AEGIS with mobile device observation AND action capabilities.
Actions go through ToolBroker → PolicyEngine → Approval UI (for Level 2).

## Implemented Capabilities

### Observe (Level 0 — READ_ONLY)

| Capability | Permission | Status |
|-----------|-----------|--------|
| `android.get_notifications` | NotificationListenerService | ✅ Mock + ADB |
| `android.get_current_app` | — | ✅ Mock + ADB |
| `android.get_device_info` | — | ✅ Mock + ADB |
| `android.get_screenshot` | MediaProjection | ✅ Mock |
| `android.get_ui_tree` | AccessibilityService | ✅ Mock |

### Action (Level 1 — SAFE_ACTION)

| Capability | Permission | Status |
|-----------|-----------|--------|
| `android.show_overlay` | アプリ内 Overlay | ✅ Mock |
| `android.hide_overlay` | アプリ内 Overlay | ✅ Mock |
| `android.open_app` | — | ✅ Mock |
| `android.press_home` | AccessibilityService | ✅ Mock |

### Action (Level 2 — APPROVAL_REQUIRED)

| Capability | Permission | Status |
|-----------|-----------|--------|
| `android.tap` | AccessibilityService | ✅ Mock + Approval UI |
| `android.swipe` | AccessibilityService | ✅ Mock + Approval UI |
| `android.type_text` | AccessibilityService | ✅ Mock + Approval UI + password deny |

### Explicitly Denied

| Capability | Reason |
|-----------|--------|
| `android.send_sms` | SMS送信禁止 |
| `android.send_dm` | DM送信禁止 |
| `android.post_sns` | SNS投稿禁止 |
| `android.access_contacts` | 連絡先取得禁止 |
| `android.make_call` | 通話操作禁止 |
| `android.type_password` | パスワード入力禁止 |
| `android.click_payment_button` | 決済操作禁止 |

## Technology Decisions

| 項目 | 選択 |
|------|------|
| Screenshot | **MediaProjection** |
| UI tree / tap / swipe | **AccessibilityService** |
| Overlay | **アプリ内 Overlay** |
| LINE/SNS plugin | **汎用通知/画面観測のみ** |

## Permission Requirements

| Permission | Required For | User Action |
|-----------|-------------|-------------|
| NotificationListenerService | Notification sync | Settings → Notification access → ON |
| MediaProjection | Screenshot capture | App prompt → Allow |
| AccessibilityService | UI tree, tap, swipe, type_text | Settings → Accessibility → ON |
| アプリ内 Overlay | Overlay display | No special permission needed |

### Permission Missing Events

When a required permission is not granted, the Android Server pushes
`android.permission_missing` events to EventBus (URGENT priority, wakes AI).

## Security

- MediaProjection requires user to explicitly allow each capture session
- AccessibilityService requires user to enable in Settings
- tap/swipe/type_text require Approval UI before execution
- type_text is denied for password fields
- Notification content is redacted for secrets (OTP, cards, emails, phones)
- Sensitive apps (banking, 2FA, password managers) are denylisted
- Raw screenshots are not stored long-term without user approval

## Password Field Protection

The `contains_password_field()` function checks the UI tree for password fields.
If a password field is detected, `android.type_text` is denied at the client level
(before even reaching PolicyEngine).

## Testing

### Python E2E Tests (CI-safe, mock provider)

```bash
cd ai-server

# Observe E2E
pytest tests/test_android_observe_e2e.py -v

# Action E2E
pytest tests/test_android_action_e2e.py -v

# All Android tests
pytest tests/test_android_observe_e2e.py tests/test_android_action_e2e.py -v
```

### ADB Provider (local, real device)

```bash
cd ai-server && pytest -m android_local -v
```

### Kotlin Unit Tests

```bash
cd android-server && ./gradlew test
```

## gRPC Connection

Default connection: `10.0.2.2:50051` (Android emulator → host machine)

For real device, update the host in `AegisGrpcClient.kt` or use the app's settings.
