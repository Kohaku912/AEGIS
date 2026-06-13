# Browser Server — AGENTS.md

## Purpose

The Browser Server handles **web browsing** for AEGIS:
- Page navigation
- Content extraction
- Link following
- Screenshot capture
- Form interaction

## Technology Stack

- **Language**: Python
- **Framework**: browser-use (primary), Playwright (fallback)
- **Port**: 50053 (gRPC)
- **Testing**: pytest

## Directory Structure

```
browser-server/
├── src/
│   ├── main.py           # Entry point
│   ├── executor.py       # Browser task executor
│   └── safety.py         # Safety boundaries
├── tests/                # Test files
└── requirements.txt      # Dependencies
```

## Key Components

### Browser Task Executor (`src/executor.py`)

**Features**:
- browser-use Agent for natural language tasks
- Playwright fallback for direct automation
- LLM-based content summarization
- Screenshot capture

**API**:
- `execute_task(task)` — Execute browser task
- `get_page_content(url)` — Get page content
- `take_screenshot()` — Capture page screenshot

### Safety Module (`src/safety.py`)

**Features**:
- URL validation
- Content filtering
- Action approval

## Usage

```python
from browser_server.executor import BrowserTaskExecutor

executor = BrowserTaskExecutor(llm_provider=llm)
result = executor.execute_task("Search for Python tutorials")
```

## Dependencies

```txt
browser-use>=0.13.0
playwright>=1.40.0
openai>=1.0.0
```

## Key Design Decisions

1. **browser-use primary**: Use browser-use Agent for natural language tasks
2. **Playwright fallback**: Direct Playwright when browser-use unavailable
3. **LLM summarization**: All content summarized by LLM before returning
4. **Safety boundaries**: URL validation and content filtering
