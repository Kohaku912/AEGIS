# Browser Server — Safety Design

> **Status**: Phase 2.1 (2026-06-11)  
> **Related**: [`architecture.md`](../docs/architecture.md), [AGENTS.md](../AGENTS.md)

## Security Principles

1. **All observe operations are LEVEL_0_READ** — no side effects, always allowed
2. **Sensitive headers are ALWAYS masked** in network logs
3. **Page content is NEVER treated as system instructions** (prompt injection defense)
4. **Forbidden capabilities are structurally absent** — not implemented, not registerable

## Sensitive Header Masking

The following HTTP headers are **always masked** (value replaced with `[REDACTED]`) in `browser.get_network_log`:

```
Authorization, Cookie, Set-Cookie,
X-API-Key, X-Auth-Token, Proxy-Authorization,
Access-Token, Refresh-Token
```

## Prompt Injection Defense

Page content extracted via `browser.extract_page_text` must NEVER be treated as system instructions for AEGIS Core. The following practices are enforced:

- Extracted text is **data**, not instructions
- LLM prompts must clearly separate page content from system directives
- Page content is wrapped in markup that distinguishes it from agent instructions
- The Context Builder in AEGIS Core is responsible for safe framing

## Capability Safety Levels

| Capability | Level | Justification |
|-----------|-------|---------------|
| `browser.get_screenshot` | LEVEL_0_READ | Pure observation, no side effects |
| `browser.get_dom_snapshot` | LEVEL_0_READ | Pure observation |
| `browser.extract_page_text` | LEVEL_0_READ | Pure observation, script/style/nav/footer excluded |
| `browser.get_current_url` | LEVEL_0_READ | Pure observation |
| `browser.get_page_title` | LEVEL_0_READ | Pure observation |
| `browser.get_links` | LEVEL_0_READ | Pure observation |
| `browser.get_network_log` | LEVEL_0_READ | Observation only, sensitive headers masked |
| `browser.open_page` | LEVEL_1_SAFE_ACT | Sends HTTP request, executes page JS |
| `browser.click` | LEVEL_1_SAFE_ACT | May trigger navigation or state change |
| `browser.fill_form` | LEVEL_1_SAFE_ACT | Modifies form state (does NOT submit) |
| `browser.download_file` | LEVEL_2_APPROVAL | Writes to filesystem |

## Explicitly NOT Implemented

These capabilities are **structurally absent** from the Browser Server:

| Capability | Reason |
|-----------|--------|
| `browser.post_sns` | SNS posting is forbidden by PolicyEngine |
| `browser.send_dm` | DM sending is forbidden |
| `browser.purchase` | Purchases are forbidden |
| `browser.captcha_bypass` | CAPTCHA bypass is forbidden |
| `browser.fill_credentials` | Password automation is forbidden |
| `browser.login` | Credential handling is forbidden |

## Robots.txt Policy

Robots.txt compliance is **not yet implemented** (Phase 2.1). Future phases should:

- Check `robots.txt` before navigating to a domain
- Respect `Disallow` directives for automated browsing
- Allow user to override for explicit research requests
- Log robots.txt violations in audit trail

## Form Submission Policy

`browser.fill_form` fills form fields but does **NOT** submit. Form submission will be
a separate capability (`browser.submit_form`) classified as **LEVEL_2_APPROVAL** in
a future phase.

## Network Log Retention

- Network logs are held **in-memory only** for the duration of the browser session
- Logs are cleared on page navigation
- Logs are NEVER persisted to disk
- Maximum retention: 1,000 entries per page cycle

## Error Handling

All observe functions return structured `BrowserError` objects on failure:

```typescript
interface BrowserError {
  error: string;   // Human-readable error message
  code: string;    // Machine-readable error code
  detail?: string; // Optional diagnostic detail
}
```

Errors never include sensitive information (URLs, headers, cookies).
