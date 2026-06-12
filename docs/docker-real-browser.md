# Docker Real Browser Testing

## Overview

Browser Server runs in Docker with headless Chromium for real browser automation.

## Quick Start

```bash
# Build and start
docker compose --profile real-browser up -d

# Check health
docker compose ps

# View logs
docker compose logs browser-server
```

## Architecture

```
┌─────────────────────────────────┐
│  Docker                         │
│  ┌──────────────┐               │
│  │ ai-server    │               │
│  │ :50051       │               │
│  └──────┬───────┘               │
│         │ gRPC                  │
│  ┌──────┴───────┐               │
│  │ browser-     │               │
│  │ server       │               │
│  │ :50052       │               │
│  │ + Chromium   │               │
│  └──────────────┘               │
└─────────────────────────────────┘
```

## Browser Profiles

Browser profiles (cookies, sessions) are stored in Docker volumes:

- `browser-profiles` — Persistent browser profiles
- `browser-sessions` — Session storage

### Managing Profiles

```bash
# List volumes
docker volume ls | grep browser

# Inspect profile volume
docker volume inspect aegis_browser-profiles

# Clear sessions (logout all)
docker volume rm aegis_browser-sessions
```

### Local Browser Profile Mount

To use a local Chrome profile:

```yaml
# docker-compose.override.yml
services:
  browser-server:
    volumes:
      - /path/to/chrome-profile:/app/browser-profiles/default
```

## Cookie / Session Storage

- Cookies are stored per-profile in `/app/browser-profiles/`
- Session storage in `/app/browser-sessions/`
- Delete volumes to clear all sessions
- Individual site cookies can be managed via browser automation

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AEGIS_BROWSER_HEADLESS` | `true` | Run Chromium headless |
| `AEGIS_BROWSER_TIMEOUT_MS` | `30000` | Page load timeout |
| `OPENAI_API_KEY` | — | LLM API key |
| `OPENAI_BASE_URL` | `https://api.deepseek.com` | LLM API base URL |

## Troubleshooting

### Chromium won't start

```bash
# Check if Chromium is installed
docker compose exec browser-server chromium --version

# Rebuild with fresh Chromium
docker compose build --no-cache browser-server
```

### Permission errors

```bash
# Fix volume permissions
docker compose exec browser-server chown -R app:app /app/browser-profiles
```
