# PC Server — Design & Usage

> ⚠️ **Goal change (2026-09-27)**: the only constraint is now **"the user's information must never
> leave the local environment."** Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. Any "requires approval" / "Level 2" language below is a **risk annotation**,
> not a gate. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).

> **Status**: Code-backed PC server (newline-delimited TCP JSON, Windows-native)
> **Language**: Rust (`pc-server/`)
> **OS**: Windows only
> **Related**: [`pc-safety.md`](pc-safety.md), [`pc-server-windows-host.md`](pc-server-windows-host.md)

## Overview

The PC Server gives AEGIS PC observation **and** action capabilities. It runs as a host-native Rust
process (not in Docker) and listens on `:50052`. The transport is a newline-delimited **TCP JSON**
command router — not gRPC, and there is no `pc_server.proto`.

## Implemented Capabilities

The authoritative inventory is the **58 manifests** under
`ai-server/capabilities/builtin/pc-server/`. A capability's id is derived as
`server_id.app_id.action` — always three segments. Two-segment forms such as `pc.mouse_click` or
`pc.get_screenshot` are **not** valid ids and resolve under no alias rule.

Risk labels below are the manifest `risk.level`. See [`pc-safety.md`](pc-safety.md) for what each
tier does and does not gate.

### `read_only` — 14

| Capability | TCP command |
|---|---|
| `pc-server.clipboard.image` | `clipboard_image` |
| `pc-server.file.list` | `list_files {path}\|{recursive}` |
| `pc-server.file.read` | `read_file {path}\|{max_bytes}` |
| `pc-server.file.search` | `search_files {path}\|{pattern}` |
| `pc-server.network.info` | `network_info` |
| `pc-server.process.list` | `list_processes` |
| `pc-server.registry.list_keys` | `list_registry_keys {key}` |
| `pc-server.registry.read` | `read_registry {key}\|{value_name}` |
| `pc-server.service.list` | `list_services` |
| `pc-server.system.event_log` | `event_log {log_name}\|{count}` |
| `pc-server.system.installed_software` | `installed_software` |
| `pc-server.system.performance_counters` | `performance_counters` |
| `pc-server.system.windows_features` | `windows_features` |
| `pc-server.task.list` | `list_scheduled_tasks` |

### `low` — 15

| Capability | TCP command |
|---|---|
| `pc-server.clipboard.get_clipboard` | `clipboard` |
| `pc-server.discord.get_channels` | `discord_get_channels` |
| `pc-server.discord.get_guild` | `discord_get_guild` |
| `pc-server.discord.get_guilds` | `discord_get_guilds` |
| `pc-server.discord.get_selected_voice_channel` | `discord_get_selected_voice_channel` |
| `pc-server.discord.get_voice_settings` | `discord_get_voice_settings` |
| `pc-server.discord.status` | `discord_status` |
| `pc-server.overlay.show_display` | `show_display {title}\|{body}\|{duration}` |
| `pc-server.personal_data.drain` | `personal_data_drain` |
| `pc-server.screenshot.get_screenshot` | `screenshot` |
| `pc-server.system.get_os_info` | `os_info` |
| `pc-server.system.get_screen_size` | `screen_size` |
| `pc-server.user_activity.snapshot` | `user_activity_snapshot` |
| `pc-server.window.get_active_window` | `active_window` |
| `pc-server.window.list_windows` | `windows` |

### `safe` — 22

| Capability | TCP command |
|---|---|
| `pc-server.app.show_url` | `open_url {url}` |
| `pc-server.approval.overlay` | `overlay_approval {action}` |
| `pc-server.discord.join_voice_by_name` | `discord_join_voice_by_name` |
| `pc-server.discord.join_voice_channel` | `discord_join_voice_channel` |
| `pc-server.discord.leave_voice_channel` | `discord_leave_voice_channel` |
| `pc-server.discord.select_text_channel` | `discord_select_text_channel` |
| `pc-server.discord.set_activity` | `discord_set_activity` |
| `pc-server.discord.set_voice_settings` | `discord_set_voice_settings` |
| `pc-server.input.keyboard_type` | `keyboard_type {text}` |
| `pc-server.input.mouse_click` | `mouse_click {x},{y},{button}` |
| `pc-server.input.mouse_move` | `mouse_move {x},{y}` |
| `pc-server.input.press_hotkey` | `press_hotkey {keys}` |
| `pc-server.mouse.drag` | `mouse_drag {from_x},{from_y},{to_x},{to_y}` |
| `pc-server.overlay.show_rich` | `show_rich_overlay` |
| `pc-server.process.kill` | `kill_process {pid}` |
| `pc-server.screen.get_ui_tree` | `ui_tree {include_invisible}` |
| `pc-server.service.start` | `start_service {name}` |
| `pc-server.service.stop` | `stop_service {name}` |
| `pc-server.system.empty_recycle_bin` | `empty_recycle_bin` |
| `pc-server.system.launch_app` | `launch_app {app_path}` |
| `pc-server.system.show_overlay` | `show_overlay {text}` |
| `pc-server.window.close_window` | `close_window {title}` |

### `safe_action` — 4

| Capability | TCP command |
|---|---|
| `pc-server.clipboard.set` | `set_clipboard {text}` |
| `pc-server.mouse.scroll` | `mouse_scroll {amount}` |
| `pc-server.system.lock` | `lock_workstation` |
| `pc-server.window.resize` | `resize_window {title},{width},{height}` |

### `audited_action` — 1

| Capability | TCP command |
|---|---|
| `pc-server.file.write` | `write_file {path}\|{content}\|{append}` |

### `high` — 2

| Capability | TCP command |
|---|---|
| `pc-server.shell.execute` | `execute_shell {command}\|{working_dir}` |
| `pc-server.shell.powershell` | `execute_powershell {command}\|{working_dir}` |

### Nothing is `forbidden`

No PC capability carries a `critical` / `forbidden` risk label. There is also no capability named
`pc.delete_file`, `pc.bulk_delete`, `pc.read_secret_file`, `pc.write_system_config`,
`pc.run_shell_command`, `pc.type_password`, `pc.click_payment_button` or `pc.modify_policy_config`
— those appeared in an earlier revision of this document and do not exist.

The hard stops live in `PolicyEngine.EXPLICIT_DENY_PATTERNS` and match on **id patterns**:
`.*\.purchase.*`, `pc\.click_payment.*`, `.*\.bypass_egress.*`, `.*\.modify_policy.*`, and similar.
Those patterns name ids that no PC manifest defines, which is the point — the deny is defense in
depth against a capability being added later, not a description of today's inventory.

### `pc-server.approval.overlay` — the confirmation surface

`overlay_approval.rs` draws a click-through Win32 overlay (Y = approve, N = reject, ESC = cancel)
and returns the answer to the caller. It is the PC-side *"ask the user"* surface: AEGIS chooses
when to show it, and **the reply gates nothing**. It keeps its historical `approval` name on the
wire. See [`approval-ui.md`](approval-ui.md).

## Transport & Protocol

Newline-delimited text commands over TCP on `:50052`, one JSON object per response. Each manifest
carries its own `tcp_command` template (the tables above). The health endpoint and the command
router share the port.

## Technology Decisions

| Item | Choice |
|------|--------|
| Mouse / keyboard | Rust OS-native Win32 `SendInput` |
| Overlay | **Win32 API directly** (`overlay_approval.rs`, `#[cfg(target_os = "windows")]`) — *not* Tauri |
| Screen capture | `screenshots` crate |
| Clipboard | `arboard` |
| Window control | `x-win` |
| System info | `sysinfo`, `hostname`, `local-ip-address` |
| File operations | Integrated in PC Server (no separate service) |
| OS | Windows only |

## Safety

- **Real actions are off by default.** Without `--enable-real-pc-actions`, mouse/keyboard commands
  run in mock mode.
- **The default bind is `127.0.0.1`**, not `0.0.0.0`. Exposing the server to the LAN requires
  passing `--bind` explicitly.
- **No PC capability is gated.** `requires_approval` in `safety.rs` is a descriptive annotation;
  the forced approval gate was removed 2026-09-28. `Level2Approval` names a tier, not a prompt.
- **Clipboard content is redacted** for secrets before it is returned (`redaction.rs`).
- **File read/write is not path-restricted** — see below. This is the most important thing on this
  page.
- Action result events are pushed to the EventBus for audit.

## File Access — what is actually restricted

There are two predicates in `pc-server/src/redaction.rs`, both **substring** (`contains`) matches
against the lowercased path — not globs, not prefix matches.

| Predicate | Patterns |
|---|---|
| `is_sensitive_directory` | `.ssh`, `.gnupg`, `.aws`, `.gcloud`, `.azure`, `AppData\Roaming\Microsoft\Crypto`, `/etc/ssl`, `/etc/ssh` |
| `is_credential_file` | `.pem`, `.key`, `.crt`, `credentials`, `.env`, `id_rsa`, `id_ed25519`, `token`, `secret`, `password` |

They feed `observe_ext.rs::is_observation_excluded`, which is called from **exactly two places** —
`collect_files` and `collect_files_recursive`. In other words:

> **They hide paths from directory listings. They are an observation filter, not an access control.**

`read_file()` (`observe_ext.rs:180`) and `write_file()` (`system_ops.rs:159`) apply **no check at
all**. `pc-server.file.read` can read `~/.ssh/id_rsa`; `pc-server.file.write` can write to it. The
redaction layer never sees those calls.

Also note what the lists do **not** contain, despite earlier revisions of this document claiming
otherwise: `.git/`, `node_modules/`, `id_ecdsa`, `.p12`, `.pfx`. And because the match is a
substring, `token` matches any path containing that text (e.g. a `tokenizer.py`).

### There is no allowlist

An earlier revision listed `workspace/`, `projects/`, `documents/`, `downloads/`, `desktop/`,
`tmp/` as an allowlist. **No such allowlist exists in the code.** The only mention of `Documents`
in the tree is a test asserting it is *not* treated as sensitive.

## Two capability registries — which is authoritative

| Registry | Location | Status |
|---|---|---|
| **Manifests** | `ai-server/capabilities/builtin/pc-server/*.json` | **Authoritative.** 58 entries, drives the catalog, policy and the LLM tool list. |
| Rust `safety::get_capabilities()` | `pc-server/src/safety.rs` | **Descriptive.** ~46 entries with stale two-segment ids (`pc.get_screenshot`, `pc.focus_window`, `pc.hide_overlay`) and some ids with no manifest (`pc.disk_info`, `pc.running_apps`, `pc.env_vars`, `pc.cwd`, `pc.minimize_window`, `pc.maximize_window`, `pc.delete_file`). Served over TCP by the `capabilities` command and counted into the health payload (`health.rs:80`), but **never** read into the catalog — `PCServerClient.register()` registers whatever the caller passes, and defaults to `[]`. |

If the two disagree, the manifest wins.

> **Known follow-up (owner decision):** `safety.rs`'s ids are wrong, and it is wire-visible. Renaming
> ~46 ids is a decision (rename outright vs. keep the old strings as aliases), not a doc fix, so it
> has been left as-is and documented here instead.

## Testing

```bash
cd pc-server
cargo test
cargo clippy --all-targets
```

The Rust unit tests are the PC Server's own coverage.

**There are no Python E2E test files for the PC server.** An earlier revision of this document
referenced `tests/test_pc_observe_e2e.py` and `tests/test_pc_action_e2e.py` and tabulated 13 test
classes (`TestMouseClick`, `TestPathSafety`, `TestDangerousActions`, …). None of those files or
classes exist. The `pc_local` marker *is* registered in `pyproject.toml`, but nothing currently
uses it.

## Python Integration (AEGIS Core)

The PC Server integrates with AEGIS Core via `ai-server/src/pc_server_client.py`.

```python
from pc_server_client import MockPCProvider, PCServerClient

provider = MockPCProvider(available=True)
client = PCServerClient(event_bus, registry, provider, tool_broker=broker)
client.register()

result = client.invoke_capability("pc-server.system.launch_app", {"app_path": "notepad.exe"})
```

`invoke_capability()` returns a plain `dict` — the parsed JSON response — not a result object.
`ToolBroker.invoke_tool()` is the path that produces an `InvokeStatus`.

> **`InvokeStatus.APPROVAL_NEEDED` does not exist.** An earlier revision showed
> `result.status == InvokeStatus.APPROVAL_NEEDED` for a mouse click. The live `InvokeStatus` values
> are `SUCCESS`, `FAILED`, `DENIED`, `TIMEOUT`, `CANCELLED`, `DRY_RUN`, `UNAVAILABLE`, `NOT_FOUND`,
> `IDEMPOTENT_HIT`, `EXECUTION_ERROR`. There is no approval status, because nothing waits for one.
