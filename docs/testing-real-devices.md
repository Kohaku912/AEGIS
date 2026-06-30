# Testing Real Devices

## Overview

AEGIS supports real device testing for browser automation and PC control.
Tests are separated into mock (CI) and real-device (opt-in) categories.

## Test Markers

| Marker | Description | Where |
|--------|-------------|-------|
| `mock` | Mock providers only (default) | CI |
| `real_browser` | Real Chromium browser | Docker |
| `real_pc_host` | Real PC Server on Windows host | Windows |
| `e2e` | End-to-end integration | Docker + host |

## Running Tests

### CI Mock Tests (default)

```bash
cd ai-server
pytest -m "not real_browser and not real_pc_host" -q
```

### Real Browser Tests (Docker)

```bash
docker compose --profile real-browser up -d
pytest -m real_browser -v
```

### PC Host Tests (Windows)

```powershell
# Start pc-server on Windows
.\scripts\start-pc-server-host.ps1

# Run tests
cd ai-server
pytest -m real_pc_host -v
```

### Full E2E

```powershell
# Start PC Server
.\scripts\start-pc-server-host.ps1

# Start Docker services
docker compose --profile pc-host --profile real-browser up -d

# Run integration tests
.\scripts\test-real-integration.ps1

# Run pytest
pytest -m e2e -v
```

## PowerShell Scripts

| Script | Purpose |
|--------|---------|
| `scripts/start-pc-server-host.ps1` | Start PC Server on Windows |
| `scripts/start-docker-real.ps1` | Start Docker services |
| `scripts/test-real-integration.ps1` | Run integration tests |
| `scripts/check-ports.ps1` | Check port status |

## Test Categories

### 1. PC Server Health (real_pc_host)

- Health endpoint responds
- OS info returns valid data
- Screenshot returns result
- Active window returns result
- Window list returns result

### 2. Browser Read-Only (real_browser)

- Open local test HTML
- Extract title, text, links
- Screenshot capture

### 3. Integration E2E (e2e)

- Docker AI Server connects to Windows PC Server
- capability registration
- pc.get_screenshot from AI Server
- pc.get_active_window from AI Server
- AuditLog records actions

## Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit with your values
# OPENAI_API_KEY=sk-your-key-here
# PC_SERVER_HOST=host.docker.internal
# PC_SERVER_PORT=50052
```

## Troubleshooting

### PC Server not reachable from Docker

```powershell
# Check firewall
Get-NetFirewallRule -DisplayName "AEGIS*"

# Test connectivity
Test-NetConnection -ComputerName host.docker.internal -Port 50052

## Current Real Device Flow

- Build Docker services first: `docker compose build ai-server browser-server room-server dev-server`.
- Start services: `docker compose up -d ai-server browser-server room-server dev-server`.
- Build Android: `cd android-server && .\gradlew.bat assembleDebug`.
- Install Android: `adb install -r app\build\outputs\apk\debug\app-debug.apk`.
- Start Android with host, port, pairing token, and `auto_connect=true`.
- Verify Home chat syncs with Dashboard chat history and approval requests appear in Action.
- If MediaProjection or Accessibility is missing, a natural permission-needed response is acceptable until the user grants it on-device.
```

### Port conflicts

```powershell
# Check what's using the port
.\scripts\check-ports.ps1
```
