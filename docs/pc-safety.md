# PC Server — Safety Design

> ⚠️ **Goal change (2026-09-27); constraint re-scoped 2026-09-30**: the only constraint is now
> **"*unpermitted* user information must not leave the local environment"** — outbound connections are
> allowed, and user information may be sent externally **with the user's permission**.
> Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. There is no approval gate in this server, and none of its capabilities
> requires one. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).
>
> **Rewritten 2026-09-28 to match the code.** An earlier revision used a `pc.<action>` capability-ID
> convention that resolves under no alias rule (`CapabilityCatalog` derives only `app.action` and
> `<prefix>.app.action`), described an "Approval UI → execute" flow that no longer exists, and
> documented a file **allowlist** that was never implemented. Corrections are marked inline.

> **Status**: rewritten 2026-09-28 to match the code
> **Related**: [`pc-server.md`](pc-server.md), [`architecture.md`](architecture.md) §7

## Safety tiers are descriptive, not gates

The `Level 0–3` labels below come from the proto `SafetyLevel` enum, which is still live. It is a
**classification only**: nothing gates on it. `LEVEL_2_APPROVAL` survives as a historical tier name
and no longer implies that anyone is asked before a capability runs.

| Tier | Enum | `RiskLevel` | `PolicyDecision` |
|------|------|-------------|------------------|
| 0 | `LEVEL_0_READ` | `READ_ONLY` | `ALLOW` |
| 1 | `LEVEL_1_SAFE_ACT` | `SAFE_ACTION` | `ALLOW_WITH_AUDIT` |
| 2 | `LEVEL_2_APPROVAL` | `APPROVAL_REQUIRED` | `ALLOW_WITH_AUDIT` |
| 3 | `LEVEL_3_RESTRICTED` | `HIGH_RISK` / `FORBIDDEN` | `ALLOW_WITH_AUDIT` / `DENY` |

The tier for a capability is derived from its manifest `risk.level` label via
`capability_catalog._RISK_LABEL_TO_NAME`. **A label missing from that dict silently resolves to
`READ_ONLY`, i.e. `ALLOW`** — the least scrutinised decision. `audited_action` was missing until
2026-09-28 and is now mapped to `SAFE_ACTION`; `test_manifest_schemas.py` fails if a manifest ever
uses an unregistered label.

## Tier 0 — `READ_ONLY`

| Capability | Manifest label | Notes |
|-----------|----------------|-------|
| `pc-server.screenshot.get_screenshot` | `low` | Captures the entire screen — treat as ephemeral |
| `pc-server.window.get_active_window` | `low` | Title, process, PID |
| `pc-server.window.list_windows` | `low` | All visible windows |
| `pc-server.clipboard.get_clipboard` | `low` | **Redacted** — may contain passwords, tokens |
| `pc-server.system.get_os_info` | `low` | OS version, hostname |
| `pc-server.file.list` | `read_only` | Excludes sensitive paths (see below) |
| `pc-server.file.read` | `read_only` | **No path check — see the gap below** |

## Tier 1 — `SAFE_ACTION` (executes with audit)

| Capability | Manifest label | Side effects |
|-----------|----------------|--------------|
| `pc-server.input.mouse_move` | `safe` | Cursor movement — no click, no input |
| `pc-server.system.launch_app` | `safe` | Process creation |
| `pc-server.window.resize` | `safe_action` | Window dimensions |
| `pc-server.system.show_overlay` | `safe` | Tauri overlay notification |
| `pc-server.input.mouse_click` | `safe` | Mouse input |
| `pc-server.input.keyboard_type` | `safe` | Keyboard input |
| `pc-server.input.press_hotkey` | `safe` | Keyboard input |
| `pc-server.window.close_window` | `safe` | Window close |
| `pc-server.clipboard.set` | `safe_action` | Clipboard mutation |
| `pc-server.file.write` | `audited_action` | File system mutation |

`pc-server.overlay.show_rich` also sits at this tier (`safe`); `pc-server.overlay.show_display` is
tier 0 (`low`).

> **Tier 2 is empty for the PC server.** Every capability that this document previously listed under
> "APPROVAL_REQUIRED" (`mouse_click`, `keyboard_type`, `press_hotkey`, `close_window`,
> `write_clipboard`, `write_file`) resolves to tier 1. There is no PC capability that lands on
> `APPROVAL_REQUIRED`.

> The earlier revision also listed `pc.focus_window`, `pc.move_window` and `pc.hide_overlay`. **None
> of those exist** — there is no focus, move, or hide capability. The real window operations are
> `get_active_window`, `list_windows`, `close_window` and `resize`.

## Explicitly denied (never buildable)

These ids used to be listed in `settings/validation.py`'s `FORBIDDEN_CAPABILITIES`, which was
**deleted on 2026-09-29** (B-12 / A-1) — it named no live capability and its guard read a key space
nobody writes. **They cannot be constructed because no manifest declares them**: the broker rejects
an unregistered id before any risk check runs. Note that `tool_broker._capability_from_manifest`'s
`RiskLevel.FORBIDDEN` raise is **not** the mechanism here: **no manifest in the catalog carries
`forbidden`** (measured 2026-09-29), so that raise cannot fire. See
[`permissions.md`](permissions.md#the-forbidden-capability-list-was-deleted-b-12--a-1):

| Capability | Reason |
|-----------|--------|
| `pc-server.file.delete` | Destructive — file deletion |
| `pc-server.file.bulk_delete` | Destructive — mass deletion |
| `pc-server.file.read_secret` | Credential access |
| `pc-server.system.write_config` | System modification |
| `pc-server.system.run_shell` | Unrestricted execution |
| `pc-server.input.type_password` | Credential automation |
| `pc-server.input.click_payment_button` | Financial operation |
| `pc-server.system.modify_policy` | Policy bypass |

## Voluntary confirmation

There is no forced approval step. When AEGIS *chooses* to confirm a consequential action with the
user, the surface is:

**`pc-server.approval.overlay`** — "Show overlay approval dialog with Y/N key input"
(`requires_approval: false`, `ownership_scope: user`). It is an ordinary capability AEGIS may invoke;
it is not a precondition any other capability must satisfy.

> The previous "Approval UI Integration" section described a flow — `PolicyEngine` returning
> `ASK_APPROVAL` → `ApprovalStore` creating an `ApprovalRequest` → `ToolBroker.invoke_tool_approved()`
> → `AuditLog` — that was **deleted on 2026-09-28**. `ASK_APPROVAL`, `ApprovalStore` and
> `invoke_tool_approved` no longer exist in the decision path (`invoke_tool_approved` survives only as
> an `evaluation/` scenario step name).

## Secret redaction

Implemented in `pc-server/src/redaction.rs` (`redact_secrets`, `redact_headers`). Patterns:

- `password` / `passwd` / `secret` / `token` / `api_key` / `apikey` in `key=value` or `key: value`
- `Authorization` headers
- SSH private keys (`-----BEGIN … PRIVATE KEY-----`) → `[SSH_PRIVATE_KEY_REDACTED]`
- PEM certificates → `[PEM_CERTIFICATE_REDACTED]`
- JWT tokens (`eyJ…`) → `[JWT_REDACTED]`
- AWS access keys (`AKIA…`) → `[AWS_KEY_REDACTED]`
- Connection strings with credentials (`scheme://user:pass@`) → password replaced

## File path handling — and a real gap

`redaction.rs` defines two **substring** predicates (not globs):

| Predicate | Patterns |
|-----------|----------|
| `is_sensitive_directory` | `.ssh`, `.gnupg`, `.aws`, `.gcloud`, `.azure`, `AppData\Roaming\Microsoft\Crypto`, `/etc/ssl`, `/etc/ssh` |
| `is_credential_file` | `.pem`, `.key`, `.crt`, `credentials`, `.env`, `id_rsa`, `id_ed25519`, `token`, `secret`, `password` |

They are combined into `observe_ext.rs::is_observation_excluded`, which is called from exactly two
places: `collect_files` and `collect_files_recursive`. **The exclusion therefore filters directory
*listings* — it is not a read or write permission gate.**

- `read_file()` (`observe_ext.rs:180`) applies **no** exclusion check: it reads any path that exists.
- `write_file()` (`system_ops.rs:159`) applies **no** exclusion check either.
- **There is no allowlist.** The previous revision's "Allowlist (read and write allowed)" table
  (`workspace/`, `projects/`, `documents/`, `downloads/`, `desktop/`, `tmp/`, `temp/`) described
  nothing that exists; the only mention of `Documents` in the tree is a test asserting it is *not*
  sensitive.
- `.git/`, `node_modules/`, `id_ecdsa`, `.p12` and `.pfx` were also listed previously and are **not**
  in either predicate.

So `pc-server.file.read` can read `~/.ssh/id_rsa`; the id `pc-server.file.read_secret` is forbidden,
but `file.read` targeting a secret path is not. **Whether `file.read` should refuse sensitive paths is
an open decision** — the code does not do it today, and this document previously claimed it did.

## Screenshots and clipboard

### Screenshots

- Capture the **entire visible screen**, including sensitive content — treat as ephemeral.
- They are **never transmitted externally**; this is the single constraint, not a policy setting.
- In mock mode they return `[MOCK_SCREENSHOT]` — no real capture occurs.

### Clipboard

- Content is **redacted for secrets** before being returned.
- Reads are read-only; `pc-server.clipboard.set` is the (tier 1) write path.
- Clipboard data should not be logged or stored without redaction.

## Testing

- `MockPCProvider` lives in `ai-server/src/pc_server_client.py` and is used by
  `ai-server/tests/test_os_notification.py` — no real OS calls, no real screenshots.
- The `pc_local` marker is registered in `ai-server/pyproject.toml` for tests needing a real Windows host.
- Mouse/keyboard actions are never executed in CI — mock only.
- No secrets, tokens, or credentials should appear in test fixtures.
