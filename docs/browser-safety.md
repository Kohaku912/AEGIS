# Browser Server — Safety Design

> **Status**: Phase 2.1  
> **Related**: [`architecture.md`](architecture.md), [`../AGENTS.md`](../AGENTS.md)

## Safety Level Assignment

| Capability | Safety Level | Rationale |
|-----------|-------------|-----------|
| `browser.open_page` | LEVEL_1_SAFE_ACT | Navigates to URLs — safe but may hit external sites |
| `browser.extract_page_text` | LEVEL_0_READ | Read-only text extraction — no side effects |
| `browser.get_screenshot` | LEVEL_0_READ | Read-only screenshot — no side effects |
| `browser.get_current_url` | LEVEL_0_READ | Read-only URL access — no side effects |
| `browser.get_page_title` | LEVEL_0_READ | Read-only title access — no side effects |
| `browser.get_links` | LEVEL_0_READ | Read-only link extraction — no side effects |
| `browser.run_task_readonly` | LEVEL_1_SAFE_ACT | Agent research — may navigate, but no writes |
| `browser.run_task_action` | LEVEL_2_APPROVAL | Agent with actions — requires user approval |

## Blocked Capabilities

These capabilities are NOT implemented. Any attempt to invoke them is denied
by AEGIS Core's PolicyEngine explicit deny patterns.

| Capability | Reason |
|-----------|--------|
| `browser.post_sns` | SNS posting — LEVEL_3_RESTRICTED |
| `browser.send_message` | DM/message — LEVEL_3_RESTRICTED |
| `browser.purchase` | Purchases — LEVEL_3_RESTRICTED |
| `browser.captcha_bypass` | CAPTCHA bypass — FORBIDDEN |
| `browser.tos_bypass` | ToS bypass — FORBIDDEN |
| `browser.credential_fill` | Credential autofill — LEVEL_3_RESTRICTED |

## Data Protection

1. **Redaction**: Authorization, Set-Cookie, Cookie, API key, token, secret, and password values are redacted from all logs and payloads.
2. **No cookie persistence**: Cookies are not stored between sessions.
3. **No credential storage**: Login credentials are never persisted.
4. **Network log masking**: Sensitive headers are stripped from network logs.

## browser-use Agent Safety

When using browser-use Agent tasks:

1. **Read-only by default**: `run_task_readonly` restricts the agent to navigation + text extraction only.
2. **Action tasks require approval**: Any task involving clicks, form fills, or downloads must go through AEGIS Core's PolicyEngine (LEVEL_2_APPROVAL).
3. **No unbounded delegation**: Never pass "do whatever you want" to the agent. AEGIS Core decomposes tasks into specific capability invocations.
4. **No CAPTCHA solving**: browser-use's CAPTCHA handling features are disabled.
5. **No stealth**: proxy, residential proxy, and browser fingerprint evasion are disabled.

## Docker Deployment

- **No privileged mode**: Browser Server runs without `--privileged`.
- **No host network**: Uses Docker bridge network.
- **Read-only rootfs**: Recommended for production.
- **Chromium sandbox**: Playwright's Chromium runs with its own sandbox.
