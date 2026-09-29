# Android Server — AGENTS.md

> ⚠️ **Goal change (2026-09-27)**: the only constraint is now **"the user's information must never
> leave the local environment."** Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. The L0–L3 "Approval" column below is now a **risk annotation**, not a gate.
> Note: these L0–L3 are **autonomy levels** — distinct from the L1/L2/L3 **LLM 3-layer** architecture.
> See [`docs/GOAL-CHANGE.md`](../docs/GOAL-CHANGE.md).

## Purpose

The Android Server is the **mobile companion app** for AEGIS:
- Notification sync
- Device state monitoring
- App control
- Screenshot capture
- UI interaction

## Technology Stack

- **Language**: Kotlin
- **Framework**: Android Native
- **Port**: 50054 (contract port; runtime connects outbound to AI Server on 50051)
- **Testing**: JUnit

## Directory Structure

```
android-server/
├── app/
│   └── src/main/
│       ├── java/com/aegis/android/
│       │   ├── MainActivity.kt
│       │   ├── AegisConfig.kt
│       │   ├── AegisForegroundService.kt
│       │   ├── BootCompletedReceiver.kt
│       │   ├── grpc/
│       │   │   ├── AegisGrpcClient.kt
│       │   │   └── AndroidCapabilityDispatcher.kt
│       │   ├── service/
│       │   │   ├── ScreenshotService.kt
│       │   │   └── AegisAccessibilityService.kt
│       │   ├── provider/
│       │   │   ├── ScreenshotProvider.kt
│       │   │   ├── UITreeProvider.kt
│       │   │   ├── DeviceProvider.kt
│       │   │   ├── LocationProvider.kt
│       │   │   └── UserActivityCollector.kt
│       │   ├── notification/
│       │   │   └── AegisNotificationListener.kt
│       │   ├── overlay/
│       │   │   └── OverlayController.kt
│       │   └── ui/                     # Compose UI (V2)
│       │       ├── AegisMobileV2App.kt
│       │       ├── designsystem/       # AegisTheme, AegisComponents, GeneratedTokens
│       │       ├── feature/            # home, chat, tasks, devices, approvals,
│       │       │                       # permissions, settings — one *Screen.kt each
│       │       └── model/              # MobileUiModels.kt
│       ├── proto/aegis/                # byte-identical mirror of protos/aegis/
│       └── AndroidManifest.xml
├── gradle/ + gradlew.bat + gradle.properties
├── settings.gradle.kts
└── build.gradle.kts
```

> The `ui/feature/approvals/` screen is the **voluntary confirmation** surface — AEGIS asking the
> user. It is not an approval gate; the forced gate was removed on 2026-09-28.

## Key Components

### AegisGrpcClient / Dispatcher

**Features**:
- outbound gRPC client to AI Server
- capability dispatching for notifications, screenshots, UI tree, gestures, overlays, and app control
- event and notification sync back to the core

### Capabilities

**Observe (L0)**:
- `get_notifications()` — Get recent notifications
- `get_current_app()` — Get current app info
- `get_device_info()` — Get device information
- `take_screenshot()` — Capture screen
- `get_ui_tree()` — Accessibility UI tree
- `get_location()` — Location snapshot

**Action (L1)**:
- `open_app(package)` — Open app
- `press_home()` — Press home button
- `press_back()` — Navigate back
- `show_overlay()` — Display overlay

**Risk-annotated (L2)**:
- `tap(x, y)` — Tap at coordinates
- `swipe(direction)` — Swipe gesture
- `type_text(text)` — Type text
- `request_approval()` — Legacy approval flow (retiring; not a constraint)

## Safety Model

> ⚠️ **Approval is no longer a constraint.** The "Approval" column records the **risk annotation**
> AEGIS attaches to each level. L2 actions are **auto-executed** and recorded for post-hoc visibility.
> "Blocked" entries remain blocked.

| Level | Operations | Annotation |
|-------|-----------|------------|
| L0 | Notifications, device info, screenshot | Low risk |
| L1 | Open app, press home, back, overlay | Safe action |
| L2 | Tap, swipe, type text | Higher risk — auto-executed, audited |
| Blocked | SMS send, contacts, calls | Forbidden |

## Key Design Decisions

1. **Kotlin Native**: User chose Option A (Kotlin Native)
2. **gRPC communication**: All communication via gRPC
3. **Safety levels**: Risk annotation model (was: graduated approval)
4. **Password protection**: Password fields blocked from type_text
5. **Local only**: The Android app talks to the AI Server on the LAN; no data is sent outside the
   local environment
