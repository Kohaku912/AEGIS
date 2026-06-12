# PC Server — Windows Host Execution

## Overview

PC Server runs directly on Windows host for full OS-native access to
screen, mouse, keyboard, and overlay. AI Server running in Docker
connects to PC Server via TCP.

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
.\scripts\start-beta-docker.ps1 -Build
```

### 3. Test Integration

```powershell
.\scripts\test-pc-host.ps1
```

## Capabilities

### Observe (Level 0 — no approval)

| Capability | Description |
|-----------|-------------|
| `pc.get_screenshot` | Capture screen as PNG |
| `pc.get_active_window` | Get foreground window info |
| `pc.list_windows` | List all visible windows |
| `pc.get_clipboard` | Read clipboard (redacted) |
| `pc.get_os_info` | Get OS information |
| `pc.get_screen_size` | Get screen resolution |

### Action (Level 1 — safe action)

| Capability | Description |
|-----------|-------------|
| `pc.show_overlay` | Display text overlay |
| `pc.hide_overlay` | Remove overlay |
| `pc.launch_app` | Launch application |
| `pc.focus_window` | Bring window to front |
| `pc.mouse_move` | Move mouse cursor |

### Approval Required (Level 2)

| Capability | Description |
|-----------|-------------|
| `pc.mouse_click` | Click at coordinates |
| `pc.keyboard_type` | Type text |
| `pc.press_hotkey` | Press keyboard shortcut |

## Command Protocol

PC Server listens on TCP port 50052 with a simple text protocol:

| Command | Response |
|---------|----------|
| `health\n` | JSON health status |
| `screenshot\n` | JSON screenshot result |
| `active_window\n` | JSON active window info |
| `windows\n` | JSON window list |
| `os_info\n` | JSON OS info |
| `screen_size\n` | JSON screen size |
| `clipboard\n` | JSON clipboard content |
| `show_overlay <text>\n` | JSON overlay status |
| `hide_overlay\n` | JSON overlay status |
| `capabilities\n` | JSON capability list |
| `mouse_click\n` | JSON approval_required |
| `keyboard_type\n` | JSON approval_required |
| `quit\n` | Close connection |

## Safety

- Observe capabilities: Auto-allowed
- Overlay/focus/launch: Safe action (Level 1)
- Mouse click/keyboard: Approval UI required (Level 2)
- Password input: Never auto-execute
- File delete: Not implemented
- Shell unrestricted: Not implemented

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

## Command-Line Options

```
aegis-pc-server [OPTIONS]

Options:
  --port <PORT>                Health endpoint port (default: 50052)
  --bind <ADDR>                Bind address (default: 0.0.0.0)
  --enable-real-pc-actions     Enable real mouse/keyboard (requires approval)
  --help                       Show help
```
