# Android Server — Safety & Privacy

> ⚠️ **Goal change (2026-09-27); constraint re-scoped 2026-09-30**: the only constraint is now
> **"*unpermitted* user information must not leave the local environment"** — outbound connections are
> allowed, and user information may be sent externally **with the user's permission**.
> Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. There is no approval gate, and none of this server's capabilities requires one.
> See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).
>
> **Rewritten 2026-09-28 to match the code.** An earlier revision used `android.<action>` capability
> IDs (which resolve under no alias rule — `CapabilityCatalog` derives only `app.action` and
> `<prefix>.app.action`), described an "Approval UI → execute" flow, and documented notification
> machinery (`NotificationFilter`, a five-package authenticator denylist, an allowlist,
> `contains_password_field`, `MockAndroidProvider`) that lived **only** in the orphaned
> `ai-server/src/android_server_client.py`. Corrections are marked inline.
>
> ⚠️ **That module was deleted on 2026-09-29** (P1-5, the approval-era residue sweep). This document
> was not updated at the time and said "lives in" throughout, so **every present-tense reference to
> the module below has been corrected to past tense — the machinery is no longer in the
> repository.** What it contained, and why it was deliberately not ported, is recorded in
> `PROJECT_STATUS_REVIEW.md` §5.1 (*`android_server_client.py` の保全対象*); the code itself is
> recoverable with `git show ebe1506^:ai-server/src/android_server_client.py`.

> **Status**: rewritten 2026-09-28 to match the code; corrected 2026-09-30 after
> `android_server_client.py` turned out to have been deleted
> **Related**: [`android-server.md`](android-server.md), [`architecture.md`](architecture.md) §7

## Safety tiers are descriptive, not gates

`Level 0–3` come from the proto `SafetyLevel` enum, which is still live but **descriptive only** —
nothing gates on it. `LEVEL_2_APPROVAL` survives as a historical tier name.

| Tier | `RiskLevel` | `PolicyDecision` |
|------|-------------|------------------|
| 0 | `READ_ONLY` | `ALLOW` |
| 1 | `SAFE_ACTION` | `ALLOW_WITH_AUDIT` |
| 2 | `APPROVAL_REQUIRED` | `ALLOW_WITH_AUDIT` |
| 3 | `HIGH_RISK` / `FORBIDDEN` | `ALLOW_WITH_AUDIT` / `DENY` |

Tiers are derived from each manifest's `risk.level` via `capability_catalog._RISK_LABEL_TO_NAME`.

## Tier 0 — `READ_ONLY` (manifest label `low`)

Only three capabilities sit at this tier:

| Capability | Permission | Notes |
|-----------|-----------|-------|
| `android-server.accessibility.get_status` | — | |
| `android-server.device.get_status` | — | |
| `android-server.permissions.get_status` | — | |

## Tier 1 — `SAFE_ACTION` (executes with audit)

| Capability | Label | Permission |
|-----------|-------|-----------|
| `android-server.notification.get_notifications` | `safe` | `notification_listener` |
| `android-server.screen.get_screenshot` | `safe` | `media_projection` |
| `android-server.screen.get_ui_tree` | `safe` | `accessibility` |
| `android-server.screen.get_current_app` | `safe` | `accessibility` |
| `android-server.overlay.show` | `safe` | `overlay` |
| `android-server.app.open` | `safe` | — |
| `android-server.ui.home` | `safe` | `accessibility` |
| `android-server.ui.back` | `safe` | `accessibility` |
| `android-server.location.get_current` | `safe` | `location` |
| `android-server.safety.emergency_stop` | `safe` | — |
| `android-server.approval.request` | `safe` | `overlay` |
| `android-server.ui.tap` | `audited_action` | `accessibility` |
| `android-server.ui.swipe` | `audited_action` | `accessibility` |
| `android-server.ui.type_text` | `audited_action` | `accessibility` |

> **Reads are not all tier 0.** `notification.get_notifications`,
> `screen.get_screenshot`, `screen.get_ui_tree` and `screen.get_current_app` are *reads*, but their
> manifests declare `safe`, so they resolve to `SAFE_ACTION` → `ALLOW_WITH_AUDIT`. Only the three
> `*_status` capabilities above are `low`.

> **Tier 2 is empty.** `ui.tap`, `ui.swipe` and `ui.type_text` — previously listed as
> "APPROVAL_REQUIRED" — are `audited_action`, which resolves to `SAFE_ACTION`
> (→ `ALLOW_WITH_AUDIT`). `audited_action` was itself missing from `_RISK_LABEL_TO_NAME` until
> 2026-09-28 and was silently falling back to `READ_ONLY` → `ALLOW`; that is fixed.
>
> The earlier revision also listed `android.hide_overlay` and `android.press_home`. There is **no**
> hide capability, and home is `android-server.ui.home`.

## Explicitly denied

These ids used to be listed in `settings/validation.py::FORBIDDEN_CAPABILITIES`, which was
**deleted on 2026-09-29** (B-12 / A-1). They were **deny-list strings, not manifests** — no such
capability is declared, so they followed that set's `android.<action>` spelling rather than the
canonical `server.app.action` form. **The list itself never denied them** — it was written in a
dialect its gate never read (B-12, measured 2026-09-29; see
[`permissions.md`](permissions.md#the-forbidden-capability-list-was-deleted-b-12--a-1)). They are
unbuildable because no manifest declares them:

| Id | Reason |
|-----------|--------|
| `android.send_sms` | SMS — external send |
| `android.send_dm` | DM — external send |
| `android.post_sns` | SNS post — external send |
| `android.access_contacts` | Contacts — privacy |
| `android.make_call` | Call — external action |
| `android.type_password` | Password autofill — credential handling |
| `android.click_payment_button` | Payment — financial |
| `android.captcha_bypass` | CAPTCHA bypass |
| `android.tos_bypass` | ToS bypass |

## Voluntary confirmation

There is no forced approval step. When AEGIS *chooses* to confirm something with the user, the surface is:

**`android-server.approval.request`** — "Ask the User on Android". Its manifest description states the
contract precisely: *"Display a confirmation prompt on the Android overlay and collect the user's
answer. AEGIS chooses to ask; the answer informs the next step and unblocks nothing."*

> The previous revision's "Approval UI → execute" column and its
> `ToolBroker → PolicyEngine → Approval UI (Level 2)` data-flow step described a gate that was
> deleted on 2026-09-28.

## Notification handling

**On device** (`android-server/.../notification/AegisNotificationListener.kt`): notifications from
`IGNORED_PACKAGES` are dropped before anything else runs —

| Package | Reason |
|---------|--------|
| `com.aegis.android` | Self (prevent echo) |
| `android` | System noise |
| `com.android.systemui` | System noise |

The listener keeps at most `MAX_RECENT = 100` items.

**On-device redaction** lives in `UserActivityCollector.kt`, which strips
`password|passcode|otp|verification code|token|secret|認証コード` runs from collected activity text.

> ⚠️ **The notification redaction described in the previous revision is not in the live path.** The
> `NotificationFilter` class, its card/email/phone/OTP patterns, the five-package denylist
> (including `com.google.android.apps.authenticator`, `com.azure.authenticator`,
> `com.duosecurity.duomobile`) and the "always allowed" allowlist all lived in
> **`ai-server/src/android_server_client.py` — an orphaned module with zero importers, since deleted
> (P1-5, 2026-09-29)**. The live Android path is `aegis_ai/integrations/android/`, which contains no
> redaction or denylist logic. So **2FA/authenticator notifications are not filtered by package** the
> way this document used to claim; only the three packages above are. **Whether to reimplement the
> richer filter in the live path is an open owner decision** (register B-4); the original code is
> recoverable from git history rather than rewritten from this description.

## UI tree and password fields

- The UI tree may contain sensitive text (form fields, displayed content) and should not be logged
  without redaction.
- `android-server.ui.type_text` is the input path and carries `audited_action`.
- `contains_password_field()` — the recursive `is_password` walk documented previously — existed
  **only** in `android_server_client.py` (deleted 2026-09-29), never in the live path.
  **Password-field refusal is therefore not enforced server-side today**; the device-side
  accessibility service does not re-check it either.

## Permission requirements

Declared per manifest under `requires_permissions`:

| Permission | User action | Risk |
|-----------|-------------|------|
| `notification_listener` | Settings → Notification access | Low — read-only |
| `media_projection` | App prompt → allow each session | Medium — screen capture |
| `accessibility` | Settings → Accessibility | High — UI interaction |
| `overlay` | No special permission | Low — display only |
| `location` | Runtime prompt | Medium — location |

When a permission is absent, the capability stays registered and invocation returns a permission
error; `web/ui_overview.py` surfaces `permission_missing` from server status. (The
`push_permission_missing_event()` helper that raised an `android.permission_missing` event is in the
same orphaned module — that specific event is not emitted by the live path.)

## Screenshots

- Capture the **entire visible screen**, including sensitive content — treat as ephemeral.
- They are **never transmitted externally**; this is the single constraint, not a policy setting.
- In mock mode they return `[MOCK_SCREENSHOT]` — no real capture.

## Data flow

```
Android device
  ├── NotificationListenerService → notifications   (IGNORED_PACKAGES filter, on device)
  ├── MediaProjection             → screenshots
  ├── AccessibilityService        → UI tree, tap, swipe, home, back
  └── in-app Overlay              → overlay display, approval.request prompt
        ↓  (outbound connection — the app dials the AI Server)
AegisGrpcClient
        ↓
AEGIS Core
  ├── EventBus → TriggerEngine → ContextBuilder
  ├── ToolBroker → PolicyEngine   (no approval step)
  └── AuditLog
```

## Testing

- `MockAndroidProvider` existed **only** in `ai-server/src/android_server_client.py` (deleted
  2026-09-29); the live integration is covered by `ai-server/tests/test_android_integration.py`
  against `aegis_ai/integrations/android/`.
- The `android_local` marker is **not** registered in `pyproject.toml` — the previous revision
  advertised it, but no test uses it. Android-side tests live in `android-server/app/src/test/`.
- No secrets, tokens, or credentials should appear in test fixtures.
