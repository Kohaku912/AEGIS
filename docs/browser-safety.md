# Browser Server — Safety Design

> ⚠️ **Goal change (2026-09-27)**: the only constraint is now **"the user's information must never
> leave the local environment."** Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. There is no approval gate in this server, and none of its capabilities
> requires one. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).
>
> This document previously described an eight-capability surface
> (`browser.open_page`, `browser.extract_page_text`, `browser.get_screenshot`, …), a
> `LEVEL_0_READ` / `LEVEL_1_SAFE_ACT` / `LEVEL_2_APPROVAL` / `LEVEL_3_RESTRICTED` scale, and a list of
> "blocked capabilities" that were never implemented. **None of those capability IDs exist in the
> catalog.** They have been replaced below with the operations the server actually accepts and the
> boundaries it actually enforces.

> **Status**: rewritten 2026-09-28 to match the code
> **Related**: [`architecture.md`](architecture.md), [`../browser-server/AGENTS.md`](../browser-server/AGENTS.md)

## Transport and trust boundary

The live server is **HTTP**, not gRPC: `main.py` runs a `ThreadingHTTPServer` on
`AEGIS_GRPC_PORT` (default 50053) and exposes `POST /execute`, `POST /capability/<app>/<action>`,
`POST /browse`, `POST /health`, `GET /health` and `GET /capabilities`. The protos under
`protos/aegis/` exist for the shared contract only; no gRPC servicer is registered here.

The server is **agent-private**. `POST /capability/<app>/<action>` requires a `viewer` of
`agent_private` or `shared`, and pages the user should see must be routed to the PC or Android
server instead — the browser session is not a user-visible surface.

## Accepted operations

The authoritative list is `safety.SUPPORTED_OPERATIONS`; `GET /capabilities` returns it. It is the
short form (`<app>.<action>`) of the AI Server manifests under
`ai-server/capabilities/builtin/browser-server/`.

| Operation | Notes |
|-----------|-------|
| `search.query` | Served by a lightweight DuckDuckGo HTTP path — no browser-use agent is launched |
| `page.read`, `page.summarize`, `page.navigate` | Page-level reads and navigation |
| `feed.monitor`, `session.open`, `session.authenticated` | Session-scoped work |
| `element.click`, `form.fill`, `form.submit` | Page interaction |
| `file.download`, `file.upload` | File transfer |
| `social.react`, `social.post`, `account.create` | Consequential actions |

`POST /execute` also accepts `legacy.page.browse` as a compatibility operation.

`POST /capability/...` additionally requires:

- `purpose` ∈ {`research`, `monitor`, `automate`, `collaborative_review`} — otherwise `PURPOSE_REQUIRED`
- both `success_condition` and `stop_condition` — otherwise `BOUNDS_REQUIRED`

These are **bounds on the task**, not approvals. They exist so an agent task cannot run unbounded;
they do not gate execution on a human.

## Boundaries the server enforces

`BLOCKED_ACTIONS` refuses these at the endpoint, independent of any AI Server decision:

| Action | Why |
|--------|-----|
| `captcha_bypass` | Circumvents a site's access control |
| `bot_evasion` | Circumvents a site's access control |
| `credential_store_read` | Reads a credential store |
| `purchase` | Irreversible spend |
| `contract_acceptance` | Legally binding acceptance |

The browser-use agent is additionally instructed to **stop and report** on CAPTCHA, payment,
contract acceptance, credentials, or identity verification. When it detects a verification step it
returns `needs_user_input` with the reason — a **voluntary** hand-off to the user, not a gate. The
detected patterns include identity/phone verification, QR codes, verification codes, 2FA, CAPTCHA,
and "prove you are human".

No proxy, residential-proxy, or fingerprint-evasion options are configured anywhere in this server.

## The single constraint: the egress gate

`egress.py` is the enforcement point, and it is the only *constraint* this server enforces.
`classify_destination()` sorts a destination into three buckets, and `egress_allowed()` decides:

| Classification | Decision |
|----------------|----------|
| `local` | **Allowed.** Loopback, link-local, RFC1918 private, `100.64.0.0/10` (Tailscale/CGNAT), `fc00::/7`, Unix sockets, single-label hostnames, and `localhost` / `*.local` / `*.localhost` / `*.internal` / `*.lan` / `*.home` |
| `unknown` | **Denied — fails closed.** An unclassifiable destination is never permitted |
| `external` | Allowed **only** when `AEGIS_EXTERNAL_EGRESS_ALLOWED` is truthy **and** the host matches `AEGIS_EGRESS_ALLOWED_HOSTS` (comma-separated; a leading dot matches subdomains) |

The gate is applied at every place a destination can escape:

1. `safety_boundary.check_domain()` — the navigation target, checked **before** task-scope checks so
   the constraint cannot be bypassed by declaring a target domain.
2. `browser_use_agent._navigation_egress_denied()` — the agent's own navigation steps.
3. `browser_use_agent` LLM-endpoint check — the browser-use model endpoint is egress-gated too.
   `config.json` ships `base_url: https://api.deepseek.com` with an **empty** `api_key`; because that
   is an external host, the default configuration denies it until the owner explicitly enables and
   allowlists it. This is the single constraint working as intended.

Egress decisions are **logged**, not audited: `_record()` writes to the server logger with the
comment "Audit belongs to the AI Server; this is visibility only."

## Data protection

1. **Redaction** (`redaction.py`): `Authorization`, `Set-Cookie`, `Cookie`, `api_key`, `token`,
   `secret` and `password` values are replaced with `[REDACTED]`, including token-shaped JSON fields.
   `redact_headers()` strips `authorization`, `cookie`, `set-cookie` and `x-api-key`.
2. **Cookies *are* persisted.** `session.py` saves them to `cookies.json` under the per-session
   profile directory so a login survives between tasks; `clear_cookies()` and `clear_all()` exist to
   remove them. (An earlier revision of this document claimed cookies were not persisted — that was
   wrong.)
3. **Profiles stay local.** Profiles, sessions and traces live under `AEGIS_BROWSER_PROFILE_ROOT`,
   `AEGIS_BROWSER_SESSION_ROOT` and `AEGIS_BROWSER_TRACE_ROOT` — all local paths, by design.

## Deployment

- **No privileged mode**: runs without `--privileged`.
- **No host network**: uses the Docker bridge network.
- **Read-only rootfs**: recommended for production.
- **Chromium sandbox**: Playwright's Chromium runs with its own sandbox.
