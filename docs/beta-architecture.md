# Beta Architecture — LLM + Browser-Use Native

## Overview

Beta version of AEGIS shifts from fine-grained workflow implementation
to LLM + browser-use based natural autonomous operation.

## Core Design Principles

### 1. LLM-First Task Interpretation

User messages are interpreted by LLM, not keyword classifiers.

```
User: "Check my Twitter notifications and summarize them"
    ↓
LLM Task Interpreter
    ↓
TaskPlan {
  goal: "Check and summarize Twitter notifications",
  task_type: BROWSE,
  actions: [browser_open → browser_read → llm_summarize],
  risk: READ
}
    ↓
Browser-Use Task Executor
    ↓
Response
```

### 2. Browser-Use as Primary Execution Path

Instead of implementing site-specific functions (read_twitter, read_gmail, etc.),
AEGIS passes natural language tasks to browser-use which uses LLM to drive the browser.

```
AEGIS Core → "Go to twitter.com/notifications, read all notifications, summarize them"
    ↓
Browser-Use Agent (LLM + Playwright)
    ↓
Structured Result
    ↓
AEGIS Core → Response to user
```

### 3. Safety Boundary Model

Safety is enforced at boundaries, not at every function:

```
┌─────────────────────────────────────────────┐
│  User Request (natural language)            │
│      ↓                                      │
│  LLM Task Interpreter                       │
│      ↓ TaskPlan with risk levels            │
│  ┌─────────────────────────────────────┐    │
│  │  Safety Boundary Check              │    │
│  │  - READ → allowed                   │    │
│  │  - DRAFT → allowed                  │    │
│  │  - EXTERNAL_SEND → approval         │    │
│  │  - PAYMENT → blocked/approval       │    │
│  │  - BLOCKED → denied                 │    │
│  └─────────────────────────────────────┘    │
│      ↓                                      │
│  Execution (browser-use / tool-broker)      │
│      ↓                                      │
│  PolicyEngine (structural safety gate)      │
│      ↓                                      │
│  Result                                     │
└─────────────────────────────────────────────┘
```

## Module Architecture

```
aegis_ai/
├── interaction/
│   ├── task_interpreter.py    # LLM Task Interpreter (replaces intent.py)
│   ├── router.py              # Routes via TaskPlan (not intent keywords)
│   └── message.py             # Message/Response models
├── browser_use/
│   └── executor.py            # Browser-Use Task Executor
├── llm/
│   └── providers/
│       └── openai_provider.py # DeepSeek/OpenAI LLM
└── [existing modules]
```

## Removed / Deprecated

- `intent.py` — keyword-based intent classifier (kept as compatibility shim only)
- Per-site browser functions — replaced by browser-use tasks
- `permissive_owner_assisted` profile — replaced by simple read/draft/send model
- Fine-grained signup functions — replaced by browser-use tasks

## Safety Model (Simplified)

| Category | Default Behavior |
|----------|-----------------|
| Read (web, owned accounts) | Auto-allowed |
| Draft (posts, replies) | Auto-allowed (local only) |
| External send (post, DM, email) | Approval required |
| Payment | Blocked or approval |
| CAPTCHA/bypass | Always blocked |
| Spam/bulk | Always blocked |

## Docker Deployment

```bash
# AI Server + Browser Server
docker compose --profile real-browser up -d

# With PC Server on Windows host
docker compose --profile pc-host --profile real-browser up -d
```
