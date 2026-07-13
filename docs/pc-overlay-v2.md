# AEGIS PC Overlay v2

PC Overlay v2 is a small companion surface, not a Dashboard replacement.

## Scope

Allowed overlay purposes:

- Approval prompts from `ApprovalManager`
- Non-interactive notifications from `NotificationManager`
- Emergency or critical health display

Not allowed:

- Capability risk editing
- Settings or secret editing
- Task management
- Dashboard navigation
- Bulk approval

## Visual Language

The Rust GDI overlay mirrors `design-tokens/tokens.json` with COLORREF values:

| Purpose | Token |
| --- | --- |
| Background | `#05090F` / `#0B111B` |
| Text | `#EAF2FF` |
| Muted text | `#8EA0B8` |
| Normal accent | `#29D3FF` |
| Notice / upcoming | `#8B7CFF` |
| Approval / warning | `#FFB84D` |
| Rejection / critical | `#FF5D73` |
| Recovery success | `#2DD4A8` |

Green is not an always-online color. It is used only for explicit approval or
recovery success states.

## Approval Compatibility

Legacy PC approval overlay remains available for compatibility, but all approval
lifecycle state must originate from Core `ApprovalManager` and fan out through
the PC overlay channel. The PC overlay cannot create trusted approval records on
its own.

Removal criteria for the legacy approval mini UI:

- Web v2 Approvals has parity for pending, expiring, high-risk, resolved,
  expired, and failed-after-approval states.
- Android approvals show the same `approval_id`, capability, risk, reason,
  target, preview, task, and timestamps.
- PC overlay is confirmed as a notification/approval/emergency-only surface.

## Testing

Run:

```powershell
cd pc-server
cargo fmt --check
cargo check
```

Real overlay E2E remains approval-gated:

```powershell
.\scripts\e2e\run-pc-real.ps1 -InstallService -RealActions -UninstallAfter
```
