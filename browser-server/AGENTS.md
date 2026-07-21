# Browser Server — AGENTS.md

## Purpose

The Browser Server handles **web browsing** for AEGIS using browser-use:
- Page navigation
- Content extraction
- Form filling
- AI-driven browser automation

## Technology Stack

- **Language**: Python
- **Framework**: browser-use (AI-driven), Playwright (direct)
- **Port**: 50053 (HTTP)
- **LLM**: browser-use with DeepSeek/OpenAI-compatible providers

## Directory Structure

```
browser-server/
├── src/aegis_browser/
│   ├── main.py           # HTTP server entry point
│   ├── browser_use_agent.py  # browser-use integration with DeepSeek compatibility
│   ├── config.py         # Configuration
│   ├── safety.py         # Capability registry / blocked actions
│   ├── safety_boundary.py # Domain and content safety checks
│   ├── observe.py        # Read-only page helpers
│   ├── session.py        # Session/profile persistence
│   ├── task_models.py    # BrowserTask, BrowserTaskResult
│   ├── trace.py          # Execution tracing
│   ├── logging.py        # Redacting logging setup
│   └── redaction.py      # String/header redaction helpers
├── config.json           # LLM API key configuration
└── AGENTS.md
```

## Key Components

### HTTP Server (`main.py`)

Endpoints:
- `GET /health` — Health check
- `GET /capabilities` — List capabilities
- `POST /browse` — URL browsing via Playwright
- `POST /execute` — AI-driven browser tasks via browser-use

The runtime is HTTP-first; proto definitions exist for the shared contract, but the live server exposes these endpoints.

### Browser-Use Agent (`browser_use_agent.py`)

**Features**:
- DeepSeek compatibility via `_patch_browser_use_models()`
- `keep_alive=True` to keep browser open between tasks
- Safety rules (no CAPTCHA bypass, no purchases)
- **Verification detection**: Detects CAPTCHA, phone verification, 2FA and returns `needs_user_input`
- **Pydantic model_validate_json patch**: Normalizes JSON before validation (strips markdown, fixes action format)

**DeepSeek Compatibility**:
- Normalizes `{"click": 811}` → `{"click": {"index": 811}}`
- Handles markdown code blocks in responses
- Monkey-patches `ChatOpenAI.ainvoke()` for JSON normalization
- Monkey-patches `BaseModel.model_validate_json()` for pre-validation normalization

### Configuration (`config.json`)

```json
{
  "llm": {
    "model": "deepseek-v4-flash",
    "api_key": "...",
    "base_url": "https://api.deepseek.com"
  }
}
```

## Capability

Capabilities are split by operation. Read-only operations include `browser-server.search.query`,
`browser-server.page.read`, and `browser-server.page.summarize`. Side-effect operations such as
`browser-server.form.submit`, `browser-server.file.upload`, and `browser-server.social.post` require
approval through the AI Server manifests. The legacy `browser-server.page.browse` endpoint is a
compatibility path and is approval-required.

Accepts natural language task descriptions and executes them using browser-use.

**Verification Detection**:
When the browser agent encounters verification steps (CAPTCHA, phone verification, 2FA), it:
1. Detects the verification pattern in the result text
2. Returns `needs_user_input=True` with the reason
3. The chat system pauses and asks the user to complete the verification
4. After the user responds, the browser task continues

Detected patterns:
- verify your identity / phone
- phone verification
- scan QR code
- verification code / enter the code
- two-factor / 2FA
- CAPTCHA
- prove/verify you are human

## Dependencies

- browser-use>=0.13.1
- playwright>=1.40.0

## Key Design Decisions

1. **browser-use primary**: AI-driven browser automation via browser-use Agent
2. **DeepSeek compatibility**: Monkey-patch for JSON format normalization
3. **keep_alive**: Browser stays open between tasks
4. **Safety rules**: No CAPTCHA bypass, no purchases, no credential filling
5. **HTTP API**: Simple REST API for integration with AI Server
6. **Verification detection**: Detects verification steps and pauses for user intervention
7. **Pydantic patch**: Normalizes JSON before validation to handle DeepSeek's output format
