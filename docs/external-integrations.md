# External Integrations — Safe Gateway

> ⚠️ **Goal change (2026-09-27); constraint re-scoped 2026-09-30**: the only constraint is now
> **"*unpermitted* user information must not leave the local environment"** — outbound connections are
> allowed, and user information may be sent externally **with the user's permission**.
> Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. Any "requires approval" / "Level 2" language below is a **risk annotation**,
> not a gate. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).


> **Status**: Outbound implemented, closed by default (the gate refuses until the user permits)
> **Related**: `docs/egress-gate.md`, `docs/notification-gateway.md`, `docs/privacy.md`

## Overview

External Integrations is the outbound path for sending the user's own content (a notification
body, a message) to a destination outside the local environment. The controlling rule is the
single constraint: a body is the user's own information, so it leaves **only** when the user has
permitted that destination.

Every send goes through the egress gate (`aegis_ai/egress/`). Nothing in this subsystem decides
permission for itself — the channels ask the gate and obey the answer.

## Implemented outbound channels

All three are real senders. Each is **refused by the gate with the shipped default settings**,
which is the correct resting state, not a stub.

| Channel | Class | Egress purpose | Credentials (env) | Destination asked of the gate |
|---------|-------|----------------|-------------------|-------------------------------|
| LINE | `LineNotificationChannel` | `messaging.line` | `AEGIS_LINE_CHANNEL_ACCESS_TOKEN`, `AEGIS_LINE_TO` | `https://api.line.me` |
| Discord | `DiscordNotificationChannel` | `messaging.discord` | `AEGIS_DISCORD_WEBHOOK_URL` | the webhook **origin** (never the full URL — it contains the token) |
| Email | `EmailNotificationChannel` | `messaging.email` | `AEGIS_SMTP_HOST`, `AEGIS_SMTP_TO` | `smtp://host:port` |

Shared machinery lives in `notification/channels/outbound.py`; see
[`notification-gateway.md`](notification-gateway.md) for the send ordering and the
credential-hygiene rules.

## How a send is permitted

Two paths, both evaluated by the gate. Neither is checked inside the channel.

1. **Standing configuration** — all three of:
   - `privacy.external_egress_allowed` (the master switch), **and**
   - `privacy.external_messaging_allowed` (the purpose flag), **and**
   - the destination host in `privacy.egress_allowed_hosts`.

2. **A recorded grant** — the user permitted this exact `(host, purpose)` pair. The gate reads it
   from the confirmation store; it never asks. A grant substitutes for the *standing pair* (the
   flag and the allowlist entry), **not** for the master switch: the master switch bounds every
   external request, so a grant with the switch off is still refused.

   ⚠️ **Measured 2026-10-03: path 2 is not wired in the running system.** `ConfirmationGrantSource` is implemented and the gate does consult it on every `check()`, but no `src/` module ever constructs one and the composition root supplies no `permission_source`, so path 2 never fires today — **path 1 is the only path that can permit a send**. See [`permissions.md`](permissions.md).

A destination that is *local* by the gate's own definition — loopback, RFC1918, a single-label
hostname, `.local`, a `unix:` path — needs no permission. This is the constraint working as
written, not a hole: the rule is about information leaving the **local environment**. It is why an
SMTP server on the LAN is sendable without any settings change.

## Safety rules

1. **Closed by default** — every lock ships closed; the gate refuses.
2. **One control** — the gate is the only decision point. There is no per-channel bypass and no
   parameter that skips the check.
3. **A body always carries user information** — the channels pass `carries_user_information=True`
   unconditionally, and that value is deliberately *not* a parameter of the call.
4. **Deny patterns** — `policy_engine.EXPLICIT_DENY_PATTERNS` refuses payments/purchases,
   egress-gate bypass, and policy self-modification on every `evaluate()`. (Note: `send_dm` and
   `send_sns` are **not** in that list — they appear only as `forbidden_actions` in the
   `evaluation/` scenarios, which is a different mechanism.)
5. **Credentials stay in the process** — read at send time; never in a result, a log line, or an
   exception message. A transport exception is reported by its *type* only.
6. **Audited** — every gate decision is recorded.

## Not implemented

- **Inbound** LINE/Discord — nothing receives or routes external messages into the Interaction
  Hub. The `interaction/channels/` modules are inbound-side placeholders.
- **`IntegrationRegistry`** (`integrations/registry.py`) — no caller; declared but unwired.
- **Webhook** — `WebhookSender` (`integrations/webhook_sender.py`) is real and is used by
  `personal_ai/social_proxy.py`; it is not routed through `NotificationRouter`.
