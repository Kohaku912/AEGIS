# External Integrations — Safe Gateway

> **Status**: Implemented (Stubs only)
> **Related**: `docs/privacy.md`, `docs/security.md`

## Overview

External Integrations provides a safe gateway for future LINE, Discord, Email,
and Webhook integrations. Currently, all integrations are **stubs only** —
no real external messages are sent.

## Integrations

| Integration | Status | Direction | Default |
|-------------|--------|-----------|---------|
| LINE | Stub | Both | Disabled |
| Discord | Stub | Both | Disabled |
| Email | Stub | Outbound | Disabled |
| Webhook | Stub | Both | Disabled |

## Safety Rules

1. **Default disabled** — all external integrations are disabled by default
2. **No real sending** — stubs return `{"success": false, "stub": true}`
3. **Policy enforcement** — all outbound goes through IntegrationPolicy
4. **Approval required** — send_message, send_email require Level 2 approval
5. **Deny patterns** — send_dm, send_sns, purchase always denied
6. **Settings control** — can be enabled/disabled via Settings
7. **Audit logging** — all attempts logged

## Next Steps (requires user confirmation)

- [ ] LINE Bot real implementation
- [ ] Discord Bot real implementation
- [ ] Email SMTP real implementation
- [ ] Webhook real implementation

Each requires:
1. User confirmation
2. API token/secret configuration
3. Privacy review
4. Rate limiting
5. Error handling
