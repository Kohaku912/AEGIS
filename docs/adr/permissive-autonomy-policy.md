# ADR-0004: Permissive Autonomy Policy

## Status

Accepted — **superseded in part (2026-09-27)**

> ⚠️ **Update (2026-09-27)**: The goal was narrowed to a **single constraint** — the user's
> information must never leave the local environment. **Approval is no longer a constraint.**
>
> ⚠️ **Update (2026-09-30) — the constraint was re-scoped.** Outbound connections are now **allowed**,
> and user information may be sent externally **with the user's permission**. The *unpermitted* case is
> still absolute. The enforcement point is therefore the **voluntary ask**, not a deny-all wall, and
> the bullet below changes accordingly: external publish/send is **permission-gated**, not blocked
> outright. Approval remains **not a constraint** in the forced sense.
>
> This ADR's *approval* distinctions are therefore historical. What survives:
> - **`publish_or_send_external`** — now split: **external** publish/send is **permission-gated** by the
>   **egress gate** (the single constraint, re-scoped 2026-09-30); **local** publish/send is allowed
>   without approval.
> - **`purchase_or_paid_subscription`** — remains a **hard stop** (kept per D1=(b); an irreversible
>   financial loss is a separate axis from privacy).
> - **`captcha_or_anti_bot`** — remains forbidden.
> - Everything else that was "requires approval" becomes **auto** (with post-hoc audit visibility).
>
> **Update (2026-09-28)**: the `autonomy` settings section that was meant to implement these profiles
> has been **deleted**. Nothing read it — 10 of its 11 fields had no reader anywhere in `src/` — so
> the profiles were never configurable in the first place, and its
> `# Always forbidden (structural)` comment claimed a guarantee nothing enforced. The tables below
> are descriptive only; [`docs/permissions.md`](../permissions.md) now lists the layers that actually
> decide. Pinned by
> `tests/test_ineffective_flags.py::test_the_retired_autonomy_profile_stays_retired`.
>
> See [`docs/GOAL-CHANGE.md`](../GOAL-CHANGE.md) and [`IMPROVEMENT_PROPOSAL.md`](../../IMPROVEMENT_PROPOSAL.md) §9.

## Context

The original AEGIS safety design was very conservative — most browser actions required
approval, even reading user-owned accounts. The user wants AEGIS to have higher autonomy
for low-risk operations on user-owned accounts, while maintaining strict controls on
external publishing, payments, and anti-bot evasion.

## Decision

### Autonomy Profiles

| Profile | Description | Default |
|---------|-------------|---------|
| `conservative` | Most actions require approval | - |
| `balanced` | Read-only auto, actions need approval | - |
| `permissive_owner_assisted` | Read + low-risk actions auto, publish/payment gated | **Yes** |

### Permissive Owner Assisted — Allowed Without Approval

1. **read_owned_accounts** — Read SNS/DM/email/notifications/GitHub/blog dashboards
   - Condition: User logged in or explicitly linked
   - SafetyLevel: LEVEL_0_READ

2. **summarize_owned_messages** — Summarize DMs/emails/SNS notifications
   - SafetyLevel: LEVEL_0_READ

3. **draft_reply_or_post** — Create reply/post/blog drafts (not publish)
   - SafetyLevel: LEVEL_0_READ or LEVEL_1_SAFE_ACT

4. **low_risk_signup_free_blog** — Fill signup forms for free services
   - Conditions: Free, no payment, no ID verification, no CAPTCHA, no age gate
   - SafetyLevel: LEVEL_1_SAFE_ACT (permissive) or LEVEL_2_APPROVAL (other profiles)

5. **login_existing_user_account** — Use existing login sessions
   - Password/2FA entry requires user action or explicit approval
   - AEGIS never stores passwords

### Permissive Owner Assisted — Still Requires Approval

6. **publish_or_send_external** — SNS post, DM send, email send, blog publish
   - SafetyLevel: LEVEL_2_APPROVAL
   - Future: trusted channel / allow-for-session settings

7. **purchase_or_paid_subscription**
   - SafetyLevel: LEVEL_3_RESTRICTED
   - Default deny or explicit approval

### Always Forbidden

8. **captcha_or_anti_bot** — CAPTCHA solving, bot detection evasion, stealth, proxy abuse
   - Never implemented
   - Bulk account creation forbidden

### Risk Reduction Strategy

- Replace "deny everything" with "allow reading, gate publishing"
- AuditLog provides transparency for all actions
- Settings allow user to disable permissive mode at any time
- Risk checks (detect_payment_required, detect_captcha, etc.) gate automated actions

## Consequences

- AEGIS can read user-owned accounts without approval
- Low-risk signups are automated with safety checks
- Publishing/sending still requires user approval
- Payments remain strictly gated
- CAPTCHA/bot evasion is never implemented

## Related

- docs/permissions.md
- docs/settings.md
- docs/browser-safety.md
