# Android Server — Design & Usage

> **Status**: Code-backed mobile companion app (outbound client to AI Server)
> **Language**: Kotlin (Android)

## Production Connection And UI

Production uses the saved host or Intent extras with the Ubuntu Tailscale
IP/MagicDNS host; LAN IP and USB reverse are diagnostic fallbacks. Compose v2
provides Home, Chat, Approvals, Tasks, Devices, Permissions, and Settings.
Phone widths use four primary destinations plus More; widths of 600dp and above
use a navigation rail. `scripts/test-android-real.ps1` records Wi-Fi off/on,
screen-off, Core/app restart, reconnect count, heartbeat failures, and network
evidence. CI skips `android_local`; release acceptance requires a real-device
report.
> **Permissions**: MediaProjection, AccessibilityService, Overlay (ユーザー明示的有効化)

## Overview

The Android Server provides AEGIS with mobile device observation AND action capabilities.
The runtime is an Android app that syncs notifications, screenshots, UI tree, overlays, and gestures back to the core AI Server.

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
| `android.press_back` | AccessibilityService | ✅ Mock |
| `android.get_location` | LocationProvider | ✅ Mock |

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
cd ai-server
AEGIS_ANDROID_LOCAL=1 pytest -m android_local -v
```

The current local test path uses the installed Android companion app and the
AI Server reverse-stream connection. The older ADB provider remains available
for read-only diagnostics, but it is not the canonical Runtime execution path.

### Kotlin Unit Tests

```bash
cd android-server && ./gradlew test
```

## gRPC Connection

Current production Core connection (same address on LAN and cellular):

| Network | Host | Port | TLS |
|---------|------|------|-----|
| Home LAN Wi‑Fi | `192.168.50.41` | `50051` | plaintext |
| Cellular / away | `192.168.50.41` | `50051` | plaintext via Cloudflare One (WARP) private network |

Off-LAN requires Cloudflare One enrolled to team **`kawaharahome`**. Setup:
`infra/cloudflared/README.md`. Public `grpc.*` hostnames are not used (Free plan
blocks `application/grpc`).

For an emulator, use `10.0.2.2:50051`.

For a real device, use the app settings or start it with intent extras:

```powershell
adb shell am start -n com.aegis.android/.MainActivity `
  --es host 192.168.50.41 --ei port 50051 `
  --es pairing_token <token> `
  --ez auto_connect true
```

If USB reverse is supported:

```powershell
adb reverse tcp:50051 tcp:50051
adb shell am start -n com.aegis.android/.MainActivity --es host 127.0.0.1 --ei port 50051 --ez auto_connect true
```

## Current Android App Runtime

- The Android app uses a Compose dashboard with `State`, `Home`, and `Action` tabs; Home is the default tab.
- Home keeps only minimal status dots, missing-permission warnings, and shared chat.
- Chat is gRPC-only and shares Dashboard history through `data/chat_history.jsonl` plus reverse-stream `chat_update` pushes.
- Foreground service reconnects to AEGIS Core with backoff after stream disconnects, heartbeat failures, or send failures.
- Notification chat actions use the same Core chat path and must preserve approval/audit metadata.
- `UNIMPLEMENTED` or method-not-found chat errors mean the running AI Core is stale and must be rebuilt/restarted with the current proto/server code.
