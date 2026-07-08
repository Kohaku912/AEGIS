# Browser-Use Agent — Natural Language Browser Automation

## Overview

Beta version uses browser-use for browser automation instead of
implementing site-specific functions. The LLM drives the browser
based on natural language task descriptions.

## How It Works

```
User: "Go to GitHub and check my notifications"
    ↓
LLM Task Interpreter → TaskPlan {needs_browser: true}
    ↓
Browser-Use Task Executor
    ↓
browser-use Agent (LLM + Playwright)
  - Opens browser
  - Navigates to GitHub
  - Reads notifications
  - Returns structured result
    ↓
AEGIS Core → Response to user
```

## Usage

### Via Browser Server (Recommended)

Browser tasks are routed through the browser-server HTTP API from the AI Server chat flow.

### Direct Execution

```python
from aegis_browser.browser_use_agent import BrowserUseAgent

agent = BrowserUseAgent(llm_client=llm)
result = agent.run_task(task)
```

## Safety Boundary

All browser tasks go through `BrowserUseSafetyBoundary`:

```python
from aegis_browser.safety_boundary import BrowserUseSafetyBoundary

safety = BrowserUseSafetyBoundary()
check = safety.check_task("Go to twitter.com and read notifications")
# {"allowed": True, "risk": "READ", "reason": "Read-only task"}
```

### Blocked Operations

These are always blocked:
- CAPTCHA solving
- Bot detection evasion
- Stealth/proxy usage
- Purchases
- Spam/bulk operations

### Approval Required

These require Approval UI:
- SNS posting
- DM sending
- Email sending
- Blog publishing

### Auto-Allowed

These run without approval:
- Reading web pages
- Reading owned accounts
- Extracting information
- Creating drafts (local only)

## Docker Deployment

Browser-use runs in Docker with Chromium:

```yaml
# docker-compose.yml
services:
  browser-server:
    build:
      context: ./browser-server
      dockerfile: Dockerfile
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AEGIS_BROWSER_HEADLESS=true
```

## Browser Profiles

Browser profiles (cookies, sessions) are stored in Docker volumes:

- `browser-profiles` — Persistent profiles
- `browser-sessions` — Session storage

To clear sessions: `docker volume rm aegis_browser-sessions`

## Fallback

If browser-use is not available, falls back to direct Playwright:
- Opens URL
- Extracts page content
- Returns text

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | LLM API key for browser-use |
| `OPENAI_BASE_URL` | `https://api.deepseek.com` | LLM API base URL |
| `AEGIS_BROWSER_HEADLESS` | `true` | Run Chromium headless |
| `AEGIS_BROWSER_TIMEOUT_MS` | `30000` | Page load timeout |
