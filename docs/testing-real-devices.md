# Testing Real Devices

## Overview

AEGIS supports real device testing for browser automation and PC control.
Tests are separated into mock (CI) and real-device (opt-in) categories.

> ⚠️ **Status (2026-09-30): most of this document describes test infrastructure that was never
> built.** Of the five markers in the table below, **three are not registered at all**; of the
> registered ones, **three are used by no test**; the pytest files it names **do not exist**; and
> its `docker compose --profile …` flags name **profiles that no compose file declares**. **The
> Android section is the part that is real.** Each claim is corrected in place below; the
> measurements are in `PROJECT_STATUS_REVIEW.md` §0.1.

## Test Markers

Only **two** markers are both *registered* (`ai-server/pyproject.toml`) and *used* by a test:

| Marker | Description | What it actually selects |
|--------|-------------|--------------------------|
| `android_local` | Real Android companion app via ADB + reverse stream | **4 tests** (`ai-server/tests/test_android_local.py`) |
| `egress` | Guards the single constraint — user information is not sent outside without the user's permission | **320 tests**; `scripts/test-ai-server.ps1` enforces a floor |

**Registered but used by no test:** `pc_local`, `room_local`, `e2e`. `pytest -m <one of these>`
collects nothing and exits **5** with `no tests collected (2714 deselected)`.

**Not registered at all:** `mock`, `real_browser`, `real_pc_host`. This table used to list those
three and the sections below used to give commands for them. pytest does not know those names, so
the commands did not do what they said. The worst case is the "CI mock" command:
`pytest -m "not real_browser and not real_pc_host"` selects **all 2714 tests** — it filters
nothing, because no test carries either marker.

## Running Tests

### The suite as it actually runs (default)

```bash
cd ai-server
pytest -q                                       # the whole suite — already hermetic
pytest -m egress --require-egress-tests=160 -q  # the constraint subset, with its floor
```

There is no marker-filtered "mock only" run, because there is nothing to filter out: the suite is
hermetic by default, so plain `pytest -q` *is* the CI run. `scripts/test-ai-server.ps1` does exactly
these two steps.

### Real Browser Tests (Docker) — **no such pytest tests, and no such profile**

`real_browser` is not a registered marker and no test carries it, so `pytest -m real_browser -v`
collects nothing and exits 5. **`real-browser` is also not a declared compose profile** — the only
`profiles:` entry in any compose file is `room`, in `docker-compose.production.yml`. The browser
suite is `cd browser-server && pytest`.

### PC Host Tests (Windows) — **no such pytest tests**

`real_pc_host` is not a registered marker and no test carries it, so `pytest -m real_pc_host -v`
collects nothing and exits 5. `scripts/start-pc-server-host.ps1` does exist and does start the
server, but there are no Python E2E tests for it — `docs/pc-server.md` documents the same gap. The
nearest registered marker, `pc_local`, is also used by no test.

### Android Device Tests

```powershell
# Preferred: try USB reverse first.
.\scripts\test-android-real.ps1 -TryUsbReverse

# If the device rejects adb reverse, use the PC LAN address.
.\scripts\test-android-real.ps1 -HostAddress 192.168.50.41

# Run opt-in pytest checks.
cd ai-server
$env:AEGIS_ANDROID_LOCAL = "1"
$env:AEGIS_ANDROID_TEST_HOST = "192.168.50.41"
uv run pytest -m android_local -q
```

For a production Core whose authenticated Dashboard API is not directly
reachable, pass the read-only Display overview URL through an SSH tunnel or a
display-token protected endpoint. The runner derives Android online state and
device-reported reconnect metrics from that contract:

```powershell
.\scripts\test-android-real.ps1 `
  -HostAddress 192.168.50.41 `
  -StatusUrl http://127.0.0.1:18090/display/overview `
  -RequireOnline -ScreenOff -RestartAndroidApp
```

Use `-TestWifiOff` only together with `-TailscaleHost`. Cutting the only LAN
route is not a valid LAN-outside reconnect test.

### Full E2E

```powershell
# Start PC Server
.\scripts\start-pc-server-host.ps1

# Start Docker services (no profiles: docker-compose.yml declares none)
docker compose up -d

# Run integration tests
.\scripts\test-real-integration.ps1
```

**The `pytest -m e2e -v` step is gone**: `e2e` is registered but no test carries it, so it collected
nothing and exited 5. `scripts/test-real-integration.ps1` is the integration run.

## PowerShell Scripts

| Script | Purpose |
|--------|---------|
| `scripts/start-pc-server-host.ps1` | Start PC Server on Windows |
| `scripts/start-docker-real.ps1` | Start Docker services |
| `scripts/test-real-integration.ps1` | Run integration tests |
| `scripts/check-ports.ps1` | Check port status |

## Test Categories

**This section used to tabulate three pytest categories — PC Server Health (`real_pc_host`), Browser
Read-Only (`real_browser`) and Integration E2E (`e2e`) — with the individual checks each would make.
None of those test files was ever committed, and none of the three markers is used by a test.** What
the listed checks describe is what the *scripts and the other suites* exercise:

| Category | Exercised by | As pytest? |
|---|---|---|
| PC Server health | `scripts/start-pc-server-host.ps1` + the Rust unit tests in `pc-server/` | no |
| Browser read-only | `cd browser-server && pytest` | no `real_browser` marker |
| Integration E2E | `scripts/test-real-integration.ps1` | no `e2e` marker |
| Android companion | `android_local` — 4 tests, `scripts/test-android-real.ps1` | **yes — the real one** |

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
- Start Android with host, port, pairing token when needed, and `auto_connect=true`.
- Preferred local transport is `adb reverse tcp:50051 tcp:50051` with Android host `127.0.0.1`.
- Some vendor Android builds reject `adb reverse`; use the PC LAN IP in that case.
- Verify Home chat syncs with Dashboard chat history and approval requests appear in Action.
- If MediaProjection or Accessibility is missing, a natural permission-needed response is acceptable until the user grants it on-device.
```

### Port conflicts

```powershell
# Check what's using the port
.\scripts\check-ports.ps1
```
