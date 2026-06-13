# Android Server — AGENTS.md

## Purpose

The Android Server handles **mobile device operations** for AEGIS:
- Notification sync
- Device state monitoring
- App control
- Screenshot capture
- UI interaction

## Technology Stack

- **Language**: Kotlin
- **Framework**: Android Native
- **Port**: 50054 (gRPC)
- **Testing**: JUnit

## Directory Structure

```
android-server/
├── app/
│   └── src/main/
│       ├── java/com/aegis/android/
│       │   ├── MainActivity.kt
│       │   ├── server/
│       │   │   └── AegisServer.kt
│       │   └── capabilities/
│       │       ├── NotificationCapability.kt
│       │       ├── DeviceStateCapability.kt
│       │       └── ScreenshotCapability.kt
│       └── AndroidManifest.xml
└── build.gradle.kts
```

## Key Components

### AegisServer (`server/AegisServer.kt`)

**Features**:
- gRPC server on port 50054
- Capability registration
- Event handling

### Capabilities

**Observe (L0)**:
- `get_notifications()` — Get recent notifications
- `get_current_app()` — Get current app info
- `get_device_info()` — Get device information
- `take_screenshot()` — Capture screen

**Action (L1)**:
- `open_app(package)` — Open app
- `press_home()` — Press home button

**Approval (L2)**:
- `tap(x, y)` — Tap at coordinates
- `swipe(direction)` — Swipe gesture
- `type_text(text)` — Type text

## Safety Model

| Level | Operations | Approval |
|-------|-----------|----------|
| L0 | Notifications, device info, screenshot | Auto-allowed |
| L1 | Open app, press home | Safe action |
| L2 | Tap, swipe, type text | Requires approval |
| Blocked | SMS send, contacts, calls | Forbidden |

## Key Design Decisions

1. **Kotlin Native**: User chose Option A (Kotlin Native)
2. **gRPC communication**: All communication via gRPC
3. **Safety levels**: Graduated safety model
4. **Password protection**: Password fields blocked from type_text
