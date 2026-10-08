# Permissions — AEGIS Permission Management

> ⚠️ **Goal change (2026-09-27)**: the only constraint is now **user-information egress**. Approval,
> reversibility, policy, and reliability-proof are **no longer constraints**. Approval-centric
> language below is **historical**. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).
>
> ⚠️ **Constraint re-scoped (2026-09-30)**: the constraint is **"*unpermitted* user information must
> not leave the local environment"** — outbound connections are allowed, and user information may be
> sent externally **with the user's permission**. So the egress gate is a **permission check**, not a
> deny-all wall, and the **voluntary ask** (`confirmation/`) is what carries it. ✅ That permission
> check is now **implemented** (`aegis_ai/egress/permissions.py`, `4d3f825`): a grant is a
> `(host, purpose)` pair, matched exactly with **no wildcard**, read out of the confirmation store —
> the gate only ever *reads* what the user already decided; it never asks.
>
> ✅ **Wired 2026-10-08.** `ConfirmationGrantSource` is constructed at the composition root —
> `runtime._build_runtime` attaches one over the runtime's own confirmation store via
> `egress_gate.set_permission_source(...)` — so a recorded grant for an exact `(host, purpose)`
> is read on every `check()` and **both** permission paths can open a destination.
>
> ⚠️ **Measured 2026-10-03 — it was implemented but *not wired*.** No `src/` module constructed a
> `ConfirmationGrantSource` and the composition root passed no `permission_source`, so a recorded
> grant was never read: only the standing configuration could open a destination, and a permission
> the user had given changed nothing. Pinned now by
> `tests/test_egress_grant_source_is_wired.py` (which replaced the "stays unwired" pin); the wiring
> decision is `DELEGATION.md` §4 item 22.

> **Status**: Implemented
> **Related**: `docs/settings.md`, `docs/architecture.md` §7

## Overview

AEGIS Permissions connect user settings to PolicyEngine and ToolBroker.
The `SettingsPermissionGuard` wraps PolicyEngine to check capability
permissions from user settings.

**Critical**: This does NOT weaken the egress gate. Settings can only ADD restrictions.

## How It Works

```
User Request → ToolBroker → SettingsPermissionGuard → PolicyEngine → Egress Gate → Execute/Deny
```

### Check Order

1. Is the capability disabled in settings?
2. Is the capability in the denylist?
3. Is the capability's server disabled?
4. Is the capability's max safety level exceeded?
5. Are privacy settings blocking this capability?
6. → Delegate to PolicyEngine (egress + purchase hard stops)

### What Settings CAN Do

- Disable specific capabilities
- Disable entire servers
- Add capabilities to denylist
- Set per-capability max safety level
- Control privacy features (clipboard, camera)

### What Settings CANNOT Do

- Enable forbidden capabilities
- Bypass the **egress gate** (the single constraint)
- Allow purchases / payments (hard stop)
- Remove explicit deny patterns
- **Transmit user information with no permission.** A setting can *open* a destination (master switch
  + per-purpose flag + host allowlist) and a recorded grant authorises one `(host, purpose)` (that path is wired — see above), but
  neither makes an **unpermitted** disclosure go out — the gate denies every destination no path has
  opened. Before the 2026-09-30 re-scope this read "no setting can permit user data to leave the local
  environment"; that absolute is gone, and the permission check replaced it.

## Autonomy Profiles

> ⚠️ **There is no autonomy profile setting.** The `autonomy` settings section was **deleted**
> (P1-3): measured, 10 of its 11 fields had no reader anywhere in `src/`, its ladder described the
> approval mechanism removed in Phase 5b, and its `# Always forbidden (structural)` comment claimed
> a guarantee that nothing enforced. Wiring it would have meant re-introducing a plan-level approval
> surface, which the owner boundary forbids.
> `tests/test_ineffective_flags.py::test_the_retired_autonomy_profile_stays_retired` pins its absence.

What actually governs what AEGIS may do, in order:

| Layer | Where | What it decides |
|-------|-------|-----------------|
| **Egress gate** | `aegis_ai/egress/gate.py` | Whether anything may leave the local environment. **Deny-by-default**, but it is a **permission check**: a destination goes out only if a setting opened it *or* the user granted that exact `(host, purpose)` (`egress/permissions.py`; wired 2026-10-08). A request carrying **no user information** passes without either. |
| **Policy engine** | `aegis_ai/policy_engine.py` | Per-capability decision from the manifest's risk annotation: `ALLOW` / `ALLOW_WITH_AUDIT` / `DENY` / `UNAVAILABLE`. |
| **Explicit deny patterns** | `policy_engine.py` | Purchases/payments, egress-gate bypass, policy self-modification. |
| **Voluntary confirmation** | `ConfirmationStore` | AEGIS *may ask* before acting. It is never *forced* to wait — that gate is gone. |

> A fifth layer used to be listed here: `settings/validation.py`'s 39-entry
> `FORBIDDEN_CAPABILITIES` list. Measurement (B-12) showed it governed nothing, and it was
> **deleted on 2026-09-29** (A-1) along with the unconsumed `CapabilityPermissions.allowlist`
> field. See [the record below](#the-forbidden-capability-list-was-deleted-b-12--a-1).

Behaviour the old table described as profile-dependent is now uniform: AEGIS reads owned accounts,
summarises, drafts, and acts, recording everything for post-hoc visibility (see the irreversibility
ledger). External transmission goes through the **permission check**; payments stay denied.

Still denied, and *why*:

- **External transmission with no permission** — the egress gate (the single constraint). A setting or
  a recorded grant can open a destination (the path is wired — see above); nothing can open an *unpermitted* one.
- **Purchases and paid subscriptions** — explicit deny pattern (hard stop)
- **CAPTCHA / ToS bypass** — **prompt-level only** (`browser_use/executor.py` and
  `llm_task_interpreter.py`). The `FORBIDDEN_CAPABILITIES` half never enforced it, and has been
  **deleted** (B-12 / A-1). See
  [the record below](#the-forbidden-capability-list-was-deleted-b-12--a-1).

### Known gap: the deleted flags claimed more than anything enforced

Three fields asserted `# Always forbidden (structural)`. Deleting them removed the false claim, but
only one of the three behaviours was ever guarded:

| Claim | Actually enforced? |
|-------|--------------------|
| CAPTCHA bypass forbidden | **Prompt-level only** — `browser_use/executor.py` and `llm_task_interpreter.py` prompts. The `FORBIDDEN_CAPABILITIES` half never enforced it and was deleted 2026-09-29 (B-12 / A-1 — see below). This row previously read **"Yes"**; that was wrong |
| Stealth / proxy browser forbidden | **Prompt-level only** — `use_proxy_for_evasion` is in every task's `forbidden_actions` and in `llm_task_interpreter.py`, but the check that would enforce it is **never called** |
| Bulk account creation forbidden | **Prompt-level only** — `bulk_signup` is likewise in `forbidden_actions` and in `browser_use/executor.py`, but nothing consults it |

**All three are now in the same category.** The old table marked CAPTCHA as the one *enforced* claim
because `FORBIDDEN_CAPABILITIES` *looked* like the mechanism — it was the only one of the three with
a name in the source. Measuring it (B-12) showed the name pointed at nothing, and it was deleted
(A-1, 2026-09-29).

### The forbidden-capability list was deleted (B-12 / A-1)

`settings/validation.py` used to hold a 39-entry `FORBIDDEN_CAPABILITIES` id list, and
`CapabilityPermissions` used to carry an `allowlist` field. Both were **deleted on 2026-09-29**. The
measurements below are why the call was *delete* rather than *repair* — recorded here because the
list's absence is only justified by them.

Measured 2026-09-29, before deletion:

- **0 of 39 resolve** through `CapabilityCatalog.resolve()` — the only function that resolves both
  canonical and alias forms. Only **8 are canonical** (all `pc-server.*`); the other **31** are short
  prefixes with no app id (`browser.send_email`), a shape **no manifest produces**.
- **0 of the 128 live capabilities has a forbidden action.** There was nothing for the list to
  forbid — which is exactly why nobody noticed.
- `validate_settings_change` compared by **exact equality**, so the *correct* spelling of the same
  intent passed: `per_capability["browser.send_email"]` was rejected, while
  `per_capability["browser-server.social.send_email"]` produced **no error at all**.
- The consumer (`permissions.py`) keys `per_capability` on the **canonical** id, so the **31
  short-form entries watched a key space nobody writes**, while the **8 canonical ones were in the
  right key space but named a capability that does not exist** — either way the list governed
  nothing.
- Of the three loops in the validator, **one had an empty (`pass`) body** and could not append an
  error; the two that could only rejected settings that were already no-ops.
- `allowlist` had **no consumer anywhere** in `src/`. Its advertised effect — "Capability IDs
  explicitly allowed (bypass other checks)" — was implemented nowhere.

**What refuses these intents instead.** The list was a claim of a control, not a control:
`PolicyEngine.EXPLICIT_DENY_PATTERNS` denies the payment, egress-gate-bypass and
policy-self-modification intents; the egress gate holds the egress intents at the network layer;
`DEFAULT_RISK_MAP` denies anything that declares itself `FORBIDDEN`; CAPTCHA/ToS is prompt-level. The
ToolBroker refuses any id that is not in the live catalog (`NOT_FOUND`, before the policy engine) —
which is why a deny-list keyed on ids nobody can write protected nothing. **The single constraint
never depended on the list.**

The deletion is pinned executably by
`ai-server/tests/test_forbidden_capabilities_stay_retired.py` (11 cases, mutation-proved 14/14 across
both settings pins). A deletion pin must do more than assert a constant is gone — that alone is
satisfied by weakening the system — so the pin also drives the real `ToolBroker`, reads the live
gate, and asserts the deny patterns still match, and would fail if any of those moved.

### Why "prompt-level only" — the browser safety boundary is dormant

The hard checks **exist and are unit-tested**; no execution path consults them.
`BrowserSafetyBoundary` is constructed in `browser_use_agent.py` and only
`get_actions_taken()` is ever read — which always returns `[]`, because `record_action()` is never
called either. So all four `check_*` methods are dead code:

| Method | Why it is not wired |
|--------|--------------------|
| `check_action` | Compares against **our** action vocabulary (`read_page`/`click_button`…); browser-use emits its own names, so wiring it as-is would block *every* action. Needs a translation layer first. |
| `check_page_observation` | Its `APPROVAL_BOUNDARIES` half returns `needs_approval=True` for publish/submit/upload/account-creation — **a forced approval gate**, which the owner boundary forbids. Only the `STOP_BOUNDARIES` half is compatible. |
| `check_domain` | Per-navigation egress check; no approval semantics, so the safest to wire. Declared targets are already covered pre-flight; wiring this needs a browser-use per-action hook. |
| `check_page_content` | Unreachable by design — it rejects unstructured prose so safety is never inferred from page text. Nothing calls it because nothing should. |

Consequence for the single constraint: `_navigation_egress_denied` runs **before the browser
launches** and only over *declared* targets (task `target_domains` + URLs in the goal text). A
mid-task navigation to an arbitrary host is therefore not re-checked by that path — `check_domain`
is exactly the missing per-navigation gate, and it is unreachable.

This is not a design choice that was made; it is a layer that was never connected. It is pinned
executably by `browser-server/tests/test_safety_boundary_dormancy.py`, which **discovers** the
checks and asserts the dormant set *equals* the recorded set — so wiring one forces this table to be
updated in the same change.

The two prompt-level rows are open items, not properties of the system. They are recorded here
because the previous record was a comment in a dead settings class, which is why they went unnoticed.

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
