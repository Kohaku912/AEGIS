# Permissions — AEGIS Permission Management

> **Status**: Implemented
> **Related**: `docs/settings.md`, `docs/architecture.md` §7

## Overview

AEGIS Permissions connect user settings to PolicyEngine and ToolBroker.
The `SettingsPermissionGuard` wraps PolicyEngine to check capability
permissions from user settings.

**Critical**: This does NOT weaken PolicyEngine safety decisions.
Settings can only ADD restrictions, never REMOVE safety gates.

## How It Works

```
User Request → ToolBroker → SettingsPermissionGuard → PolicyEngine → Execute/Deny
```

### Check Order

1. Is the capability disabled in settings?
2. Is the capability in the denylist?
3. Is the capability's server disabled?
4. Is the capability's max safety level exceeded?
5. Are privacy settings blocking this capability?
6. → Delegate to PolicyEngine for safety check

### What Settings CAN Do

- Disable specific capabilities
- Disable entire servers
- Add capabilities to denylist
- Set per-capability max safety level
- Control privacy features (clipboard, camera)

### What Settings CANNOT Do

- Enable forbidden capabilities
- Bypass PolicyEngine safety checks
- Allow Level 3 (FORBIDDEN) operations
- Remove explicit deny patterns
- Weaken approval requirements

## Autonomy Profiles

AEGIS supports three autonomy profiles that control how much freedom the AI has:

| Profile | Read | Low-Risk Actions | Publish/Send | Payment |
|---------|------|-----------------|--------------|---------|
| `conservative` | Approval | Approval | Approval | Deny |
| `balanced` | Auto | Approval | Approval | Deny |
| `permissive_owner_assisted` | **Auto** | **Auto** | Approval | Deny |

### Permissive Owner Assisted

In this profile (default), AEGIS can:

1. **Read owned accounts** — SNS, DM, email, notifications (no approval)
2. **Summarize messages** — DM/email/SNS summaries (no approval)
3. **Draft replies/posts** — Create drafts, not publish (no approval)
4. **Low-risk signup** — Free service signup with risk check (no approval)
5. **Login existing sessions** — Use existing login (password entry needs approval)

Still requires approval:
- Publishing posts, sending DMs/emails
- Purchases and paid subscriptions
- CAPTCHA bypass (always forbidden)

### Configuration

```json
{
  "autonomy": {
    "profile": "permissive_owner_assisted",
    "owned_account_reading_enabled": true,
    "low_risk_signup_enabled": true,
    "external_send_requires_approval": true,
    "payment_requires_approval": true
  }
}
```

## Integration with ToolBroker

```python
from aegis_ai.settings import SettingsStore, SettingsPermissionGuard
from policy_engine import create_default_policy_engine

store = SettingsStore()
policy = create_default_policy_engine()
guard = SettingsPermissionGuard(policy, store)

# Disable a capability via settings
settings = store.get()
settings.capabilities.disabled_capabilities.append("browser.extract_text")
store.update(settings, changed_by="user")

# Guard will deny the disabled capability
cap = get_capability("browser.extract_text")
result = guard.evaluate(cap)
# result.decision == PolicyDecision.DENY
```

## Audit Trail

All permission changes are logged:

```json
{
  "timestamp_ms": 1234567890,
  "changed_by": "user",
  "reason": "Disabled clipboard capture",
  "settings_snapshot": { ... }
}
```
