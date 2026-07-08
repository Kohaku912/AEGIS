# PC Server — AGENTS.md

## Purpose

The PC Server handles **Windows operations** for AEGIS:
- Screenshot capture
- Active window information
- Window listing
- Clipboard access
- OS information
- Screen size
- Mouse and keyboard control (with approval)
- File operations (read, list, search)
- Process management
- Network information
- Disk information
- Overlay approval UI (Y/N key)

## Technology Stack

- **Language**: Rust
- **Port**: 50052 (TCP)
- **Platform**: Windows only
- **Testing**: cargo test

## Directory Structure

```
pc-server/
├── src/
│   ├── main.rs           # Entry point, TCP server
│   ├── observe.rs        # Read-only operations (screenshot, windows, etc.)
│   ├── observe_ext.rs    # Extended observe (files, processes, network)
│   ├── action.rs         # Write operations (mouse, keyboard)
│   ├── overlay_approval.rs # Overlay approval UI
│   ├── safety.rs         # Capability definitions
│   ├── health.rs         # TCP command handler
│   └── redaction.rs      # Secret redaction
├── tests/                # Test files
└── Cargo.toml            # Dependencies
```

## Capabilities (40+ total)

### Observe (Level 0: Read-only) — 15 capabilities
- `pc.get_screenshot` - Capture screen
- `pc.get_active_window` - Get foreground window
- `pc.list_windows` - List all windows
- `pc.get_clipboard` - Read clipboard
- `pc.get_os_info` - OS information
- `pc.get_screen_size` - Screen resolution
- `pc.list_directory` - List files
- `pc.read_file` - Read file content
- `pc.search_files` - Search files
- `pc.list_processes` - List processes
- `pc.network_info` - Network info
- `pc.disk_info` - Disk info
- `pc.running_apps` - Running apps
- `pc.env_vars` - Environment variables
- `pc.cwd` - Current directory

### Action (Level 1: Safe) — 9 capabilities
- `pc.show_overlay` - Show overlay
- `pc.hide_overlay` - Hide overlay
- `pc.launch_app` - Launch app
- `pc.focus_window` - Focus window
- `pc.resize_window` - Resize window
- `pc.minimize_window` - Minimize window
- `pc.maximize_window` - Maximize window
- `pc.mouse_move` - Move mouse
- `pc.mouse_scroll` - Scroll
- `pc.show_overlay` - Show overlay
- `pc.hide_overlay` - Hide overlay
- `pc.launch_app` - Launch app
- `pc.focus_window` - Focus window
- `pc.resize_window` - Resize window
- `pc.minimize_window` - Minimize window
- `pc.maximize_window` - Maximize window

### System / Shell / Integration
- `pc.shell_execute` - Run PowerShell / cmd commands
- `pc.read_registry` - Read registry values
- `pc.discord_connect` - Discord IPC / OAuth helpers
- `pc.get_health` - Standalone health check

### Approval (Level 2) — 10 capabilities
- `pc.mouse_click` - Click (approval)
- `pc.keyboard_type` - Type text (approval)
- `pc.press_hotkey` - Press hotkey (approval)
- `pc.close_window` - Close window (approval)
- `pc.mouse_drag` - Drag mouse (approval)
- `pc.write_file` - Write file (approval)
- `pc.delete_file` - Delete file (approval)
- `pc.kill_process` - Kill process (approval)
- `pc.overlay_approval` - Show approval dialog

## Key Components

### Observe Module (`src/observe.rs`)

**Features**:
- `screenshots` crate (v0.6) for screenshot capture
- `x-win` crate (v1.10) for active_window/list_windows
- `arboard` crate (v3.4) for clipboard access
- `sysinfo` crate (v0.30) for OS info

**API**:
- `get_screenshot()` — Capture screen as BMP
- `get_active_window()` — Get active window info
- `list_windows()` — List all open windows
- `get_clipboard()` — Get clipboard contents
- `get_os_info()` — Get OS information
- `get_screen_size()` — Get screen resolution

### Action Module (`src/action.rs`)

**Features**:
- `windows-sys` crate for SendInput API
- Mouse click/move
- Keyboard typing
- Hotkey support

**API**:
- `mouse_click(x, y)` — Click at coordinates
- `keyboard_type(text)` — Type text
- `press_hotkey(keys)` — Press hotkey combination

**Safety**:
- All actions gated behind `--enable-real-pc-actions` flag
- Requires explicit approval for Level 2 operations

## TCP Protocol

The PC Server listens on port 50052 (TCP, not gRPC).

**Commands** (newline-terminated):
- `health` — Health check
- `screenshot` — Capture screenshot
- `active_window` — Get active window info
- `windows` — List all windows
- `os_info` — Get OS information
- `screen_size` — Get screen resolution
- `clipboard` — Get clipboard contents

**Response**: JSON + newline

## Running

```bash
# Build
cd pc-server
cargo build

# Run
cargo run -- --port 50052 --bind 0.0.0.0 --enable-real-pc-actions

# Test
cargo test
```

## Test Status

- **Total tests**: real-device / integration coverage across observe + action paths
- **Screenshot**: ✅ Working
- **Active window**: ✅ Working
- **Window list**: ✅ Working
- **Clipboard**: ✅ Working
- **OS info**: ✅ Working
- **Screen size**: ✅ Working

## Key Design Decisions

1. **Real Windows API**: Uses actual Windows APIs, not mocks
2. **Safety flag**: Actions require `--enable-real-pc-actions` flag
3. **TCP protocol**: Simple newline-terminated JSON protocol
4. **BMP encoding**: Screenshots encoded as BMP (no compression library needed)
5. **Approval required**: Mouse/keyboard operations require Level 2 approval

## Dependencies

```toml
[dependencies]
screenshots = "0.6"
x-win = "1.10"
arboard = "3.4"
sysinfo = "0.30"
windows-sys = "0.59"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```
