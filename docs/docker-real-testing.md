# Docker Real Testing — Beta

## Overview

AEGIS Beta runs AI Server and Browser Server in Docker,
with PC Server on Windows host. Browser Server uses browser-use
for natural language browser automation.

## Quick Start

```powershell
# 1. Copy environment
cp .env.example .env
# Edit .env with your API key

# 2. Start Beta Docker environment
.\scripts\start-beta-docker.ps1 -Build

# 3. Start PC Server (Windows)
.\scripts\start-pc-server-host.ps1

# 4. Test integration
.\scripts\test-beta-real.ps1
```

## Docker Compose Profiles

| Profile | Services | Use Case |
|---------|----------|----------|
| `mock` | ai-server, mock-pc, mock-android, mock-room | CI testing |
| `real-browser` | ai-server, browser-server (real Chromium) | Browser testing |
| `pc-host` | ai-server, browser-server | With Windows PC Server |
| `beta` | ai-server, browser-server, mock-android, mock-room | **Full Beta testing** |

## Beta Profile Architecture

```
┌─────────────────────────────────────────────────────┐
│  Docker (beta profile)                              │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │ ai-server    │  │ browser-     │                 │
│  │ :50051       │──│ server       │                 │
│  │ :8090 (dash) │  │ :50053       │                 │
│  │ :8091 (chat) │  │ + Chromium   │                 │
│  └──────────────┘  └──────────────┘                 │
│         │                                           │
│         │ host.docker.internal:50052                 │
└─────────┼───────────────────────────────────────────┘
          │
┌─────────┼───────────────────────────────────────────┐
│  Windows Host                                        │
│  ┌──────────────┐                                   │
│  │ pc-server    │                                   │
│  │ :50052       │                                   │
│  └──────────────┘                                   │
└─────────────────────────────────────────────────────┘
```

## Browser-Use in Docker

Browser Server runs browser-use with headless Chromium:

```python
from browser_use import Agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="deepseek-v4-flash", api_key="...", base_url="...")
agent = Agent(task="Go to example.com and extract text", llm=llm)
result = await agent.run()
```

## Environment Variables

```bash
# .env
OPENAI_API_KEY=sk-your-key
OPENAI_BASE_URL=https://api.deepseek.com
PC_SERVER_HOST=host.docker.internal
PC_SERVER_PORT=50052
AEGIS_BROWSER_HEADLESS=true
```

## Volumes

| Volume | Purpose |
|--------|---------|
| `aegis-data` | AI Server data |
| `aegis-reports` | Evaluation reports |
| `browser-profiles` | Browser profiles (cookies) |
| `browser-sessions` | Browser sessions |
| `browser-traces` | Browser action traces |

## Managing Browser Sessions

```bash
# List volumes
docker volume ls | grep aegis

# Clear browser sessions
docker volume rm aegis_browser-sessions

# Clear browser profiles (logout all)
docker volume rm aegis_browser-profiles

# View traces
docker compose exec browser-server ls /app/traces/
```

## Troubleshooting

### Browser Server won't start

```bash
docker compose --profile beta logs browser-server
docker compose --profile beta build --no-cache browser-server
```

### Can't reach PC Server

```powershell
# Check PC Server is running
.\scripts\check-ports.ps1

# Test connectivity from Docker
docker compose exec ai-server python -c "
import socket
s = socket.socket()
s.settimeout(2)
s.connect(('host.docker.internal', 50052))
print('Connected!')
s.close()
"
```

### browser-use not available

```bash
# Check browser-use is installed
docker compose exec browser-server python -c "import browser_use; print('OK')"

# Rebuild with browser-use
docker compose --profile beta build --no-cache browser-server
```
