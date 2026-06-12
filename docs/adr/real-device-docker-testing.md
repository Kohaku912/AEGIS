# ADR-0003: Real Device Docker Testing

## Status

Accepted

## Context

AEGIS needs to support real device testing for browser automation and PC control.
The challenge is that Docker containers cannot easily access Windows host hardware
(screens, mouse, keyboard, overlays), while browser automation works well in Docker.

## Decision

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  Docker Compose                                      │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │  ai-server   │  │ browser-     │                 │
│  │  (Python)    │──│ server       │                 │
│  │  :50051      │  │ (Python)     │                 │
│  └──────────────┘  └──────────────┘                 │
│         │                                           │
│         │ gRPC (host.docker.internal:50052)          │
└─────────┼───────────────────────────────────────────┘
          │
┌─────────┼───────────────────────────────────────────┐
│  Windows Host                                        │
│  ┌──────────────┐                                   │
│  │  pc-server   │                                   │
│  │  (Rust)      │                                   │
│  │  :50052      │                                   │
│  └──────────────┘                                   │
└─────────────────────────────────────────────────────┘
```

### Service Placement

| Service | Runs In | Reason |
|---------|---------|--------|
| ai-server | Docker | Python, portable, easy to containerize |
| browser-server | Docker | browser-use + Chromium in container, headless |
| pc-server | Windows Host | Needs OS-native screen/mouse/keyboard access |
| mock-pc-server | Docker (optional) | For CI testing without real PC |
| mock-android-server | Docker (optional) | For CI testing |
| mock-room-server | Docker (optional) | For CI testing |

### Docker Compose Profiles

- **mock**: All services with mock providers (CI)
- **real-browser**: ai-server + browser-server with real Chromium
- **windows-pc-host**: ai-server in Docker + pc-server on Windows host

### Connection Methods

- Docker internal: `ai-server:50051`
- Host PC server: `host.docker.internal:50052`
- External: `{HOST_IP}:50052`

### Test Separation

- **CI mock tests**: `pytest -m "not real_browser and not pc_local"`
- **Real browser tests**: `pytest -m real_browser`
- **PC local tests**: `pytest -m pc_local` (Windows host only)

## Consequences

- Browser automation runs reliably in Docker with headless Chromium
- PC control requires Windows host but provides full OS access
- CI remains fast with mock-only tests
- Real device tests are opt-in via markers

## Related

- docs/docker-real-browser.md
- docs/pc-server-windows-host.md
- docs/testing-real-devices.md
