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
│  │ :8090 /chat  │  └──────────────┘         │
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

Ids are **three segments**: `pc-server.<app>.<action>`. The two-segment forms below
(`pc.get_screenshot`, `pc.mouse_click`) are historical and resolve under no alias rule. The full
58-capability inventory is in [`pc-server.md`](pc-server.md).

### Observe — `read_only` / `low`

| Capability | Description |
|-----------|-------------|
| `pc-server.screenshot.get_screenshot` | Capture screen as PNG |
| `pc-server.window.get_active_window` | Get foreground window info |
| `pc-server.window.list_windows` | List all visible windows |
| `pc-server.clipboard.get_clipboard` | Read clipboard (redacted) |
| `pc-server.system.get_os_info` | Get OS information |
| `pc-server.system.get_screen_size` | Get screen resolution |
| `pc-server.file.list` | List a directory |
| `pc-server.file.read` | Read a file — **no path check**, see [`pc-server.md`](pc-server.md) |

### Action — `safe` / `safe_action`

| Capability | Description |
|-----------|-------------|
| `pc-server.system.show_overlay` | Display text overlay |
| `pc-server.overlay.show_rich` | Rich overlay |
| `pc-server.system.launch_app` | Launch application |
| `pc-server.window.close_window` | Close a window (sends `WM_CLOSE`) |
| `pc-server.window.resize` | Resize a window |
| `pc-server.input.mouse_move` | Move mouse cursor |
| `pc-server.input.mouse_click` | Click at coordinates |
| `pc-server.input.keyboard_type` | Type text |
| `pc-server.input.press_hotkey` | Press a keyboard shortcut |
| `pc-server.clipboard.set` | Write the clipboard |
| `pc-server.approval.overlay` | Show the PC confirmation overlay (gates nothing) |

### Elevated — `audited_action` / `high`

| Capability | Description |
|-----------|-------------|
| `pc-server.file.write` | Write a file — **no path check** |
| `pc-server.shell.execute` | Run a shell command |
| `pc-server.shell.powershell` | Run a PowerShell command |

> **Nothing is "approval required."** The forced gate was removed 2026-09-28. There is no
> `hide_overlay` capability either — overlays dismiss themselves or on ESC.

## Command Protocol

PC Server listens on TCP port 50052 with a newline-delimited text protocol. The `tcp_command`
template for every capability is in [`pc-server.md`](pc-server.md); these are the ones the
startup banner advertises.

| Command | Response |
|---------|----------|
| `health\n` | JSON health status |
| `screenshot\n` | JSON screenshot result |
| `active_window\n` | JSON active window info |
| `windows\n` | JSON window list |
| `os_info\n` | JSON OS info |
| `screen_size\n` | JSON screen size |
| `clipboard\n` | JSON clipboard content (redacted) |
| `show_overlay <text>\n` | JSON overlay status |
| `launch_app <path>\n` | JSON launch result |
| `mouse_move <x>,<y>\n` | JSON move result |
| `mouse_click <x>,<y>,<button>\n` | JSON click result |
| `keyboard_type <text>\n` | JSON type result |
| `press_hotkey <keys>\n` | JSON hotkey result |
| `capabilities\n` | JSON capability list |
| `quit\n` | Close connection |

Mouse, keyboard and launch commands are **runtime-enabled**: without `--enable-real-pc-actions`
they return a mock result. There is no `approval_required` response.

## Safety

- Real mouse/keyboard actions: **disabled by default**, enabled by `--enable-real-pc-actions`
- Observe capabilities: auto-allowed
- Overlay / launch / window: safe action (Level 1)
- Mouse click / keyboard: elevated tier (Level 2) — a **label only**; nobody is asked
- Password input: never auto-execute
- File delete: **not implemented** (no `pc-server` delete capability exists)
- Shell: implemented as `pc-server.shell.execute` / `.powershell` (`high`)
- File read/write: **no path restriction** — the denylist is an observation filter only
- Default bind is `127.0.0.1`; pass `--bind 0.0.0.0` to expose it

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
  --bind <ADDR>                Bind address (default: 127.0.0.1)
  --enable-real-pc-actions     Enable real mouse/keyboard actions
  --help                       Show help
```
