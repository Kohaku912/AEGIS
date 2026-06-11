# PC Server — Safety Design

> **Status**: Phase 4.1  
> **Related**: [`pc-server.md`](pc-server.md)

## Safety Level Assignment

All Phase 4.1 capabilities are **LEVEL_0_READ** — observe only, no side effects.

| Capability | Level | Redaction |
|-----------|-------|-----------|
| `pc.get_screenshot` | 0 | None (image data) |
| `pc.get_active_window` | 0 | None |
| `pc.list_windows` | 0 | None |
| `pc.get_clipboard` | 0 | **Required** — secrets redacted |
| `pc.get_os_info` | 0 | None |
| `pc.list_directory` | 0 | Sensitive paths excluded |

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

## Directory Restrictions

The `is_sensitive_directory()` guard prevents monitoring of:
- `.ssh`, `.gnupg`, `.aws`, `.gcloud`, `.azure`
- System crypto stores
- `/etc/ssl`, `/etc/ssh`

The `is_credential_file()` guard excludes:
- `.pem`, `.key`, `.crt`, `credentials`, `.env`
- `id_rsa`, `id_ed25519`, `token`, `secret`, `password`

## Future Actions (not yet implemented)

Action capabilities (mouse, keyboard, file write, app launch, overlay) will be added in future phases after PolicyEngine and Approval UI verification.
