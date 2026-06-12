# ADR-0004: Permissive Autonomy Policy

## Status

Accepted

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
