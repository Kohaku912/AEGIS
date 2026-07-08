# PC Server — Safety Design

> **Status**: Code-backed PC server safety model
> **Related**: [`pc-server.md`](pc-server.md), [`architecture.md`](architecture.md) §7

## Safety Level Classification

### Level 0 — READ_ONLY (auto-allowed)

| Capability | Redaction | Notes |
|-----------|-----------|-------|
| `pc.get_screenshot` | None (image data) | Captures entire screen — treat as ephemeral |
| `pc.get_active_window` | None | Title, process, PID |
| `pc.list_windows` | None | All visible windows |
| `pc.get_clipboard` | **Required** — secrets redacted | May contain passwords, tokens |
| `pc.get_os_info` | None | OS version, hostname |
| `pc.list_directory` | Sensitive paths excluded | .ssh, .aws, etc. |
| `pc.read_file` | Path safety check | Denylist: .ssh, .env, .pem, credentials |

### Level 1 — SAFE_ACTION (auto-allowed, audited)

| Capability | Side Effects | Notes |
|-----------|-------------|-------|
| `pc.mouse_move` | Cursor movement | No click, no input |
| `pc.launch_app` | Process creation | Launches application |
| `pc.focus_window` | Window focus change | Brings window to front |
| `pc.move_window` | Window position | Moves window coordinates |
| `pc.resize_window` | Window size | Changes window dimensions |
| `pc.show_overlay` | Visual display | Tauri overlay notification |
| `pc.hide_overlay` | Visual display | Hides overlay |

### Level 2 — APPROVAL_REQUIRED

| Capability | Side Effects | Approval Flow |
|-----------|-------------|---------------|
| `pc.mouse_click` | Mouse input | Approval UI → execute |
| `pc.keyboard_type` | Keyboard input | Approval UI → execute |
| `pc.press_hotkey` | Keyboard input | Approval UI → execute |
| `pc.close_window` | Window close | Approval UI → execute |
| `pc.write_clipboard` | Clipboard mutation | Approval UI → execute |
| `pc.write_file` | File system mutation | Approval UI → path check → execute |

### Explicitly Denied (always DENY)

| Capability | Reason |
|-----------|--------|
| `pc.delete_file` | Destructive — file deletion |
| `pc.bulk_delete` | Destructive — mass deletion |
| `pc.read_secret_file` | Credential access |
| `pc.write_system_config` | System modification |
| `pc.run_shell_command` | Unrestricted execution |
| `pc.type_password` | Credential automation |
| `pc.click_payment_button` | Financial operation |
| `pc.modify_policy_config` | Policy bypass |

## Secret Redaction

Clipboard content is scanned for:
- Passwords / tokens / API keys in key=value or JSON format
- Authorization headers
- SSH private keys (PEM format)
- JWT tokens
- AWS access keys (AKIA...)
- Database connection strings with credentials
- PEM certificates

All detected secrets are replaced with `[REDACTED]`.

## File Safety

### Denylist (always blocked)

| Category | Patterns |
|----------|---------|
| SSH | `.ssh/`, `id_rsa`, `id_ed25519`, `id_ecdsa` |
| Cloud credentials | `.aws/`, `.gcloud/`, `.azure/` |
| Certificates | `.pem`, `.key`, `.crt`, `.p12`, `.pfx` |
| Environment | `.env` |
| Credentials | `credentials.json`, `credentials.xml` |
| Secrets | `token`, `secret`, `password` |
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

## Approval UI Integration

When a Level 2 action is requested:

1. ToolBroker calls PolicyEngine.evaluate()
2. PolicyEngine returns ASK_APPROVAL
3. ToolBroker creates ApprovalRequest via ApprovalStore
4. Approval UI presents the request to the user
5. User approves/rejects
6. If approved, ToolBroker.invoke_tool_approved() executes
7. Action result is pushed to EventBus
8. All decisions are logged to AuditLog

## Screenshot & Clipboard Warnings

### Screenshots

- Screenshots capture the **entire visible screen** — including sensitive content
- Screenshots are **never transmitted externally** — they stay on the local network
- In mock mode, screenshots return `[MOCK_SCREENSHOT]` — no real screen capture
- Screenshots should be treated as **ephemeral**

### Clipboard

- Clipboard content is **redacted for secrets** before being returned
- Clipboard reads are **read-only** — write requires approval
- Clipboard data should not be logged or stored without redaction

## Testing Safety

- CI tests use `MockPCProvider` — no real OS calls, no real screenshots
- Local tests with real OS calls are marked `@pytest.mark.pc_local`
- `MockPCProvider.call_log` tracks all invocations for audit verification
- No secrets, tokens, or credentials should appear in test fixtures
- Mouse/keyboard actions are NEVER executed in CI — mock only
