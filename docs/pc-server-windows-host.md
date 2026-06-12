# PC Server — Windows Host Execution

## Overview

PC Server runs directly on Windows host for full OS-native access to
screen, mouse, keyboard, and overlay. It connects to the AI Server
running in Docker via gRPC/TCP.

## Architecture

```
┌─────────────────────────────────────────────┐
│  Docker                                     │
│  ┌──────────────┐  ┌──────────────┐         │
│  │ ai-server    │  │ browser-     │         │
│  │ :50051       │  │ server       │         │
│  │ :8090 (dash) │  │ :50053       │         │
│  │ :8091 (chat) │  └──────────────┘         │
│  └──────┬───────┘                           │
│         │ TCP (host.docker.internal:50052)   │
└─────────┼───────────────────────────────────┘
          │
┌─────────┼───────────────────────────────────┐
│  Windows Host                                │
│  ┌──────────────┐                           │
│  │ pc-server    │                           │
│  │ (Rust)       │                           │
│  │ :50052       │                           │
│  └──────────────┘                           │
│  Screen, Mouse, Keyboard, Overlay           │
└─────────────────────────────────────────────┘
```

## Quick Start

### 1. Start PC Server (Windows)

```powershell
.\scripts\start-pc-server-host.ps1
```

Or manually:
```powershell
cd pc-server
cargo run --release -- --port 50052 --bind 0.0.0.0
```

### 2. Start Docker Services

```powershell
.\scripts\start-docker-real.ps1 -RealBrowser
```

Or manually:
```powershell
docker compose --profile pc-host --profile real-browser up -d
```

### 3. Run Integration Tests

```powershell
.\scripts\test-real-integration.ps1
```

## Windows Firewall

Docker containers need to reach pc-server on the host.
Run as Administrator:

```powershell
New-NetFirewallRule -DisplayName "AEGIS PC Server" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 50052 `
  -Action Allow `
  -Profile Private
```

**Note**: Use `-Profile Private` to restrict to local network only.

## Docker Connection

AI Server connects to PC Server via `host.docker.internal:50052`.

This is configured in:
- `.env`: `PC_SERVER_HOST=host.docker.internal`
- `docker-compose.yml`: `extra_hosts: host.docker.internal:host-gateway`

## Command-Line Options

```
aegis-pc-server [OPTIONS]

Options:
  --port <PORT>                Health endpoint port (default: 50052)
  --bind <ADDR>                Bind address (default: 0.0.0.0)
  --enable-real-pc-actions     Enable real mouse/keyboard (requires approval)
  --help                       Show help
```

## Health Protocol

PC Server listens on TCP port 50052 with a simple text protocol:

| Command | Response |
|---------|----------|
| `health\n` | JSON health status |
| `screenshot\n` | JSON screenshot result |
| `active_window\n` | JSON active window info |
| `windows\n` | JSON window list |
| `os_info\n` | JSON OS info |
| `quit\n` | Close connection |

## Capabilities

### Observe (Level 0 — no approval)

| Capability | Description |
|-----------|-------------|
| `pc.get_os_info` | OS information |
| `pc.get_screenshot` | Capture screen |
| `pc.get_active_window` | Active window info |
| `pc.list_windows` | All windows |
| `pc.get_clipboard` | Clipboard (redacted) |

### Action (Level 2 — approval required)

| Capability | Description |
|-----------|-------------|
| `pc.mouse_click` | Click at coordinates |
| `pc.keyboard_type` | Type text |
| `pc.press_hotkey` | Press hotkey |
| `pc.close_window` | Close window |

## Safety

- Observe capabilities: Auto-allowed
- Action capabilities: Approval UI required
- `--enable-real-pc-actions` flag required for real mouse/keyboard
- Keyboard/mouse: Default mock in tests
- CI: Never executes real PC operations
