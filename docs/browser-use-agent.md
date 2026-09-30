# Browser-Use Agent — Natural Language Browser Automation

> ⚠️ **Goal change (2026-09-27); constraint re-scoped 2026-09-30**: the only constraint is now
> **"*unpermitted* user information must not leave the local environment"** — outbound connections are
> allowed, and user information may be sent externally **with the user's permission**.
> Approval, reversibility, policy, and reliability-proof are **no
> longer constraints**. See [`GOAL-CHANGE.md`](GOAL-CHANGE.md).
>
> **Rewritten 2026-09-28 to match the code.** An earlier revision documented an "Approval Required"
> list, a `BrowserUseSafetyBoundary.check_task()` API that does not exist, and a safety boundary that
> "all browser tasks go through" — the boundary is constructed but **none of its verdict methods are
> called**. Corrections are marked inline.

## Overview

Browser automation uses `browser-use` rather than site-specific functions. The LLM drives the browser
from a natural-language task description.

## How it works

```
User: "Go to GitHub and check my notifications"
    ↓
LLM Task Interpreter → TaskPlan {needs_browser: true}
    ↓
AI Server → browser-server HTTP API (POST /execute)
    ↓
BrowserUseAgent.run_task(task)
  - constructs a BrowserSafetyBoundary from the task
  - drives browser-use (LLM + Playwright/Chromium)
  - egress-gates every navigation target and the LLM endpoint
    ↓
BrowserTaskResult → AEGIS Core → response to user
```

## Usage

### Via the browser server (recommended)

Browser tasks are routed through the browser-server HTTP API from the AI Server chat flow:
`POST /execute` (AI-driven, browser-use) and `POST /browse` (direct Playwright URL fetch).

### Direct execution

```python
from aegis_browser.browser_use_agent import BrowserUseAgent

agent = BrowserUseAgent(llm_client=llm)   # llm_client optional
result = agent.run_task(task)             # task: BrowserTask
```

The constructor is `BrowserUseAgent(llm_client=None, session=None, trace_dir=None, config=None)`;
omitted arguments fall back to `Config()` and a default `AegisBrowserSession`.

## The safety boundary — constructed, but not consulted

`safety_boundary.py` defines `BrowserSafetyBoundary`, and `run_task` does construct one from the task
(line 279). **Its verdict methods are never called by the agent.** The only `boundary.` usage in
`browser_use_agent.py` is `boundary.get_actions_taken()` — a getter — and `record_action()` is never
invoked either, so `BrowserTaskResult.actions_taken` is **always an empty list**.

| Method | Called by the agent? |
|--------|---------------------|
| `check_page_observation(observation)` | ❌ never |
| `check_page_content(content)` | ❌ never |
| `check_action(action, params)` | ❌ never |
| `check_domain(url)` | ❌ never (the egress gate is enforced separately — see below) |
| `record_action(action)` | ❌ never |
| `get_actions_taken()` | ✅ (returns `[]` as a result) |

> The previous revision showed `BrowserUseSafetyBoundary().check_task("...")`. There is no
> `check_task` method and no `BrowserUseSafetyBoundary` class — the class is `BrowserSafetyBoundary`
> and it is constructed **with a `BrowserTask`**, not called with free text. Its
> `{"allowed": True, "risk": "READ", ...}` example output does not correspond to `SafetyCheckResult`,
> which carries `allowed` / `reason` / `risk_level` and uses `"BLOCKED"` (not `"READ"`) as its verdict
> vocabulary.

### What *is* enforced: the egress gate

The single constraint **is** wired, independently of the boundary:

1. `_navigation_egress_denied()` — the agent's own navigation steps.
2. The browser-use LLM endpoint — `egress_allowed()` is checked against the configured `base_url`.

Both route through `egress.py`, where a destination is `local` (allowed), `unknown` (denied — fails
closed) or `external` (allowed only with `AEGIS_EXTERNAL_EGRESS_ALLOWED` **and** a matching
`AEGIS_EGRESS_ALLOWED_HOSTS` entry). See [`browser-safety.md`](browser-safety.md).

## Blocked operations

`BLOCKED_ACTIONS` in `safety.py` — refused at the endpoint regardless of any AI Server decision:

| Action | Why |
|--------|-----|
| `captcha_bypass` | Circumvents a site's access control |
| `bot_evasion` | Circumvents a site's access control |
| `credential_store_read` | Reads a credential store |
| `purchase` | Irreversible spend |
| `contract_acceptance` | Legally binding acceptance |

The agent's prompt additionally instructs it to **stop and report** on CAPTCHA, payment, contract
acceptance, credentials, or identity verification.

> The previous revision listed "Spam/bulk operations" and "Stealth/proxy usage" as blocked actions.
> Neither appears in `BLOCKED_ACTIONS`; conversely `credential_store_read` and `contract_acceptance`
> were missing from its list.

### No approval step

> The previous revision had an **"Approval Required"** list (SNS posting, DM sending, email sending,
> blog publishing) and an **"Auto-Allowed"** list. There is no approval gate: AEGIS decides, and the
> egress gate plus `BLOCKED_ACTIONS` are the only refusals. When AEGIS *chooses* to ask the user, the
> prompt is a normal capability call (`android-server.approval.request` /
> `pc-server.approval.overlay`) and it unblocks nothing.

## Task statuses — two of them are unreachable

`TaskStatus` declares `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `STOPPED`, `NEEDS_APPROVAL`,
`NEEDS_USER_INPUT`. In `run_task`:

| Status | Reachable? | How |
|--------|-----------|-----|
| `COMPLETED` / `FAILED` / `RUNNING` | ✅ | normal paths |
| `NEEDS_USER_INPUT` | ✅ | `browser_result["needs_user_input"]` (verification detection) |
| `NEEDS_APPROVAL` | ❌ | only from `except ApprovalBoundary` — and **nothing raises `ApprovalBoundary`** |
| `STOPPED` | ❌ | only from `except SafetyStop` — and **nothing raises `SafetyStop`** |

`ApprovalBoundary` and `SafetyStop` are declared (lines 683 and 678) and caught (lines 313 and 307)
but never raised anywhere in `browser-server/`. `result.needs_approval_for` is therefore always empty,
and the safety-boundary *stop* path cannot fire. Whether to delete these three declarations or wire
them up is an open owner decision.

## Verification detection

When browser-use reports a verification step, `run_task` sets `TaskStatus.NEEDS_USER_INPUT` and
`needs_user_input_for = [reason]` (line 297). Detected patterns include identity/phone verification,
QR codes, verification codes, 2FA, CAPTCHA, and "prove you are human". This is a **voluntary hand-off**
to the user, not a gate.

## Docker deployment

```yaml
services:
  browser-server:
    build:
      context: ./browser-server
      dockerfile: Dockerfile
    environment:
      - AEGIS_BROWSER_HEADLESS=true
      - AEGIS_EXTERNAL_EGRESS_ALLOWED=false        # default; keep it false
      - AEGIS_EGRESS_ALLOWED_HOSTS=
```

> The previous revision passed `OPENAI_API_KEY` into the container. The agent *does* read
> `OPENAI_API_KEY` / `OPENAI_BASE_URL` (falling back to `browser-server/config.json`, which ships
> `base_url: https://api.deepseek.com` with an **empty** key), but that is an **external** host: with
> egress disabled by default the LLM endpoint is denied, which is the single constraint working as
> intended. Do not enable external egress for a cloud model without deciding to send the user's data
> off-device.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AEGIS_BROWSER_HEADLESS` | `true` | Run Chromium headless |
| `AEGIS_BROWSER_CHANNEL` | `chrome` | Browser channel |
| `AEGIS_BROWSER_TIMEOUT_MS` | `30000` | Page load timeout |
| `AEGIS_BROWSER_TASK_TIMEOUT_SECONDS` | — | Whole-task timeout |
| `AEGIS_BROWSER_PROFILE_ROOT` / `_PROFILE_NAME` | — | Persistent profile location and name |
| `AEGIS_BROWSER_SESSION_ROOT` | — | Session storage |
| `AEGIS_BROWSER_TRACE_ROOT` | — | Execution traces |
| `AEGIS_BROWSER_START_ATTEMPTS` | — | Startup retry budget |
| `AEGIS_BROWSER_ZOMBIE_DEGRADED` / `_ZOMBIE_CRITICAL` | — | Zombie-process health thresholds |
| `AEGIS_BROWSER_RESOURCE_DEGRADED_RATIO` / `_RESOURCE_CRITICAL_RATIO` | — | cgroup resource thresholds |
| `AEGIS_BROWSER_CLEANUP_TIMEOUT_SECONDS` | — | Stale temp-dir cleanup budget |
| `AEGIS_EXTERNAL_EGRESS_ALLOWED` | `false` | **The single-constraint switch** |
| `AEGIS_EGRESS_ALLOWED_HOSTS` | empty | Comma-separated allowlist (leading dot matches subdomains) |
| `AEGIS_GRPC_PORT` / `AEGIS_GRPC_HOST` | `50053` / `0.0.0.0` | HTTP listen address (field names are historical) |
| `AEGIS_AI_GRPC_ADDR` | `ai-server:50051` | AI Server address |
| `AEGIS_SERVER_ID` | `browser-main` | Server identity |
| `AEGIS_LOG_LEVEL` | `INFO` | Log level |
| `OPENAI_API_KEY` / `OPENAI_BASE_URL` | `config.json` | browser-use model credentials — **external by default** |

## Browser profiles

Profiles, sessions and traces live under the `AEGIS_BROWSER_*_ROOT` paths above and are persisted in
Docker volumes (`browser-profiles`, `browser-sessions`). Cookies **are** saved per profile
(`session.py` → `cookies.json`); `clear_cookies()` and `clear_all()` remove them.
