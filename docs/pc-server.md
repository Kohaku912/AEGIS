# PC Server — Design & Usage

> **Status**: Phase 4.1 — Observe-only skeleton (2026-06-11)  
> **Language**: Rust (user decision per Phase 4 technology options)

## Overview

The PC Server provides AEGIS with PC observation capabilities (Level 0 read-only).

## Implemented Capabilities

| Capability | Safety Level | Status |
|-----------|-------------|--------|
| `pc.get_screenshot` | LEVEL_0_READ | ✅ Mock |
| `pc.get_active_window` | LEVEL_0_READ | ✅ Mock |
| `pc.list_windows` | LEVEL_0_READ | ✅ Mock |
| `pc.get_clipboard` | LEVEL_0_READ | ✅ Mock + redaction |
| `pc.get_os_info` | LEVEL_0_READ | ✅ Working |
| `pc.list_directory` | LEVEL_0_READ | ⚠️ Skeleton |

## Not Yet Implemented

| Capability | Reason |
|-----------|--------|
| `pc.mouse_click` | Action — requires PolicyEngine approval verification first |
| `pc.keyboard_type` | Action — requires PolicyEngine approval verification first |
| `pc.file_delete` | Action Level 2 — requires Approval UI |
| `pc.file_write` | Action Level 1 — pending |
| `pc.launch_app` | Action Level 1 — pending |

## Security

- Clipboard content is redacted for secrets (passwords, tokens, API keys, SSH keys, JWT, AWS keys, connection strings)
- Sensitive directories (.ssh, .aws, .gcloud) excluded from file monitoring
- Credential files (.pem, .key, .env, id_rsa) excluded
- Mock mode by default — real OS APIs gated behind platform features

## Running

```bash
cd pc-server
cargo build --release
cargo run
```

## Testing

```bash
cargo test              # 5 redaction tests
cargo clippy            # Lint
```
