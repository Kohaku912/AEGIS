# PC Server — Design & Usage

> **Status**: Code-backed PC server (TCP JSON, Windows-native)
> **Language**: Rust (user decision per Phase 4 technology options)
> **OS**: Windows専用（ユーザー選択済み）

## Overview

The PC Server provides AEGIS with PC observation AND action capabilities.
The runtime uses a newline-delimited TCP JSON command router, Windows-native input APIs, overlay UI, shell/system helpers, and Discord IPC helpers.

## Implemented Capabilities

### Observe (Level 0 — READ_ONLY)

| Capability | Safety Level | Status |
|-----------|-------------|--------|
| `pc.get_screenshot` | LEVEL_0_READ | ✅ Mock |
| `pc.get_active_window` | LEVEL_0_READ | ✅ Mock |
| `pc.list_windows` | LEVEL_0_READ | ✅ Mock |
| `pc.get_clipboard` | LEVEL_0_READ | ✅ Mock + redaction |
| `pc.get_os_info` | LEVEL_0_READ | ✅ Working |
| `pc.list_directory` | LEVEL_0_READ | ✅ Mock |
| `pc.read_file` | LEVEL_0_READ | ✅ Mock + path safety |

### Action (Level 1 — SAFE_ACTION, auto-allowed)

| Capability | Safety Level | Status |
|-----------|-------------|--------|
| `pc.mouse_move` | LEVEL_1_SAFE_ACT | ✅ Mock |
| `pc.launch_app` | LEVEL_1_SAFE_ACT | ✅ Mock |
| `pc.focus_window` | LEVEL_1_SAFE_ACT | ✅ Mock |
| `pc.move_window` | LEVEL_1_SAFE_ACT | ✅ Mock |
| `pc.resize_window` | LEVEL_1_SAFE_ACT | ✅ Mock |
| `pc.show_overlay` | LEVEL_1_SAFE_ACT | ✅ Mock overlay |
| `pc.hide_overlay` | LEVEL_1_SAFE_ACT | ✅ Mock |

### Action (Level 2 — APPROVAL_REQUIRED)

| Capability | Safety Level | Status |
|-----------|-------------|--------|
| `pc.mouse_click` | LEVEL_2_APPROVAL | ✅ Mock + Approval UI |
| `pc.keyboard_type` | LEVEL_2_APPROVAL | ✅ Mock + Approval UI |
| `pc.press_hotkey` | LEVEL_2_APPROVAL | ✅ Mock + Approval UI |
| `pc.close_window` | LEVEL_2_APPROVAL | ✅ Mock + Approval UI |
| `pc.write_clipboard` | LEVEL_2_APPROVAL | ✅ Mock + Approval UI |
| `pc.write_file` | LEVEL_2_APPROVAL | ✅ Mock + Approval UI + path safety |

### Explicitly Denied (Level 3)

| Capability | Status |
|-----------|--------|
| `pc.delete_file` | ❌ DENY |
| `pc.bulk_delete` | ❌ DENY |
| `pc.read_secret_file` | ❌ DENY |
| `pc.write_system_config` | ❌ DENY |
| `pc.run_shell_command` | ❌ DENY |
| `pc.type_password` | ❌ DENY |
| `pc.click_payment_button` | ❌ DENY |
| `pc.modify_policy_config` | ❌ DENY |

## Technology Decisions

| 項目 | 選択 |
|------|------|
| Mouse/Keyboard | Rust OS-native API直接 (Windows SendInput) |
| Overlay | Tauri |
| File操作 | PC Server内に統合 |
| OS | Windows専用 |

## Security

- All Level 2 actions require Approval UI before execution
- File read/write: denylist for .ssh, .aws, .env, .pem, credentials, etc.
- File write: allowlist directories (workspace, projects, documents, downloads, desktop, tmp)
- Clipboard content is redacted for secrets
- Sensitive directories excluded from file monitoring
- Mock mode by default — real OS APIs gated behind platform features
- Action result events pushed to EventBus for audit

## File Safety

### Denylist (always blocked)

| Category | Examples |
|----------|---------|
| SSH | `.ssh/`, `id_rsa`, `id_ed25519` |
| Cloud credentials | `.aws/`, `.gcloud/`, `.azure/` |
| Certificates | `.pem`, `.key`, `.crt`, `.p12` |
| Environment | `.env` |
| Credentials | `credentials.json`, `token`, `secret`, `password` |
| System | `.git/`, `node_modules/` |

### Allowlist (read and write allowed)

| Directory | Purpose |
|-----------|---------|
| `workspace/` | Development workspace |
| `projects/` | Project files |
| `documents/` | User documents |
| `downloads/` | Downloaded files |
| `desktop/` | Desktop files |
| `tmp/`, `temp/` | Temporary files |

## Testing

### Python E2E Tests (CI-safe, mock provider)

```bash
cd ai-server

# Observe E2E
pytest tests/test_pc_observe_e2e.py -v

# Action E2E
pytest tests/test_pc_action_e2e.py -v

# All PC tests
pytest tests/test_pc_observe_e2e.py tests/test_pc_action_e2e.py -v
```

### Real provider (local only)

```bash
cd ai-server && pytest -m pc_local -v
```

### Rust unit tests

```bash
cd pc-server && cargo test && cargo clippy
```

## Python Integration (AEGIS Core)

The PC Server integrates with AEGIS Core via a Python adapter (`ai-server/src/pc_server_client.py`).

### Mock Provider (CI)

`MockPCProvider` returns deterministic fake data without OS calls:

```python
from pc_server_client import MockPCProvider, PCServerClient

provider = MockPCProvider(available=True)
client = PCServerClient(event_bus, registry, provider, tool_broker=broker)
client.register()

# Level 1 — auto-allowed
result = client.invoke_capability("pc.launch_app", {"app_path": "notepad.exe"})

# Level 2 — requires approval via ToolBroker
result = broker.invoke_tool("pc.mouse_click", {"x": 500, "y": 300})
# result.status == InvokeStatus.APPROVAL_NEEDED
```

### Action Result Events

After executing an action, push the result to EventBus:

```python
client.push_action_result_event("pc.launch_app", True, {"pid": 12345})
```

### E2E Test Coverage

| テストクラス | テスト数 | カバー範囲 |
|---|---|---|
| TestCapabilityRegistration | 4 | Action/Observe登録、risk level |
| TestLaunchApp | 3 | Level 1 auto-allow |
| TestOverlay | 4 | Level 1 show/hide |
| TestMouseClick | 3 | Level 2 approval flow |
| TestKeyboardType | 3 | Level 2 approval flow |
| TestFileWrite | 6 | Level 2 + allowlist/denylist |
| TestFileRead | 4 | Path safety |
| TestDangerousActions | 5 | Explicit deny |
| TestPathSafety | 8 | Allowlist/denylist |
| TestAuditLog | 2 | Audit recording |
| TestActionResultEvents | 2 | EventBus push |
| TestProviderUnavailable | 1 | Graceful failure |
| TestFullE2EFlow | 3 | Full E2E (Level 1, Level 2, deny) |
