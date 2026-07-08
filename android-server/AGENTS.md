# Android Server — AGENTS.md

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
│       │   ├── grpc/
│       │   │   ├── AegisGrpcClient.kt
│       │   │   └── AndroidCapabilityDispatcher.kt
│       │   ├── service/
│       │   │   └── ScreenshotService.kt
│       │   ├── provider/
│       │   │   ├── ScreenshotProvider.kt
│       │   │   ├── UITreeProvider.kt
│       │   │   ├── DeviceProvider.kt
│       │   │   └── LocationProvider.kt
│       │   ├── notification/
│       │   │   └── AegisNotificationListener.kt
│       │   └── overlay/
│       │       └── OverlayController.kt
│       └── AndroidManifest.xml
└── build.gradle.kts
```

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

**Approval (L2)**:
- `tap(x, y)` — Tap at coordinates
- `swipe(direction)` — Swipe gesture
- `type_text(text)` — Type text
- `request_approval()` — Explicit approval flow

## Safety Model

| Level | Operations | Approval |
|-------|-----------|----------|
| L0 | Notifications, device info, screenshot | Auto-allowed |
| L1 | Open app, press home, back, overlay | Safe action |
| L2 | Tap, swipe, type text | Requires approval |
| Blocked | SMS send, contacts, calls | Forbidden |

## Key Design Decisions

1. **Kotlin Native**: User chose Option A (Kotlin Native)
2. **gRPC communication**: All communication via gRPC
3. **Safety levels**: Graduated safety model
4. **Password protection**: Password fields blocked from type_text
