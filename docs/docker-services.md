# AEGIS Docker Services

This compose setup runs the containerized AEGIS services:

| Service | Port | Built from |
|---|---|---|
| `ai-server` | gRPC `50051`, Dashboard `8090` (SPA chat at `/chat`) | `infra/docker/ai-server.Dockerfile` |
| `browser-server` | HTTP `50053` | `infra/docker/browser-server.Dockerfile` |
| `room-server` | gRPC `50055` | `infra/docker/room-server.Dockerfile` |
| `jaeger` | UI `16686`, OTLP `4317` | `jaegertracing/all-in-one:1.62` |
| `temporal` | `7233` | `temporalio/auto-setup:1.26.2` |
| `temporal-postgresql` | internal `5432` | `postgres:16-alpine` |

PC Server remains host-native on Windows and is reached from containers through
`host.docker.internal:50052`. Android remains the installed mobile app and
connects to the exposed AI gRPC port.

> **`dev-server` (gRPC `50056`) is gone.** It was deleted in Phase 9 and is not part of this
> topology — no compose file declares it, and `docker-compose.yml.archive` (a frozen rollback
> artefact) is the only file that still names it. `docs/dev-server.md` carries a REMOVED banner.

Every published port binds `127.0.0.1` unless `AEGIS_BIND_HOST` (or the per-service
`*_BIND_HOST`) says otherwise.

## Start

```powershell
docker compose build ai-server browser-server room-server
docker compose up -d ai-server browser-server room-server
```

Or use:

```powershell
.\scripts\start-beta-docker.ps1 -Build
```

`docker-compose.production.yml` is an **overlay** — it adds environment only and declares no
`build:`. Layer it on the base file:

```powershell
docker compose -f docker-compose.yml -f docker-compose.production.yml up -d ai-server browser-server
```

It requires `AEGIS_SESSION_SECRET` (`:?`, so compose refuses to start without it), defaults
`AEGIS_DISABLED_SERVERS` to `room-server`, and puts `room-server` behind `profiles: [room]`.

## Room Server on Orange Pi

Default Room provider is mock:

```powershell
docker compose up -d room-server
```

GPIO IR skeleton can be enabled on the target device with:

```bash
AEGIS_ROOM_LIGHT_PROVIDER=gpio AEGIS_ROOM_IR_PIN=<pin> docker compose up -d room-server
```

Multi-arch build example:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f infra/docker/room-server.Dockerfile \
  -t aegis/room-server:local \
  .
```

## Health Checks

```powershell
docker compose ps
docker compose logs -f ai-server browser-server room-server
```

Expected endpoints:

- Dashboard: `http://localhost:8090`
- Chat: `http://localhost:8090/chat`
- Browser health: `http://localhost:50053/health`
- AI gRPC: `localhost:50051`
- Room gRPC: `localhost:50055`
- Jaeger UI: `http://localhost:16686`

## Current Canonical Topology

- Docker Compose owns `ai-server`, `browser-server` and `room-server`, plus the supporting
  `jaeger` / `temporal` / `temporal-postgresql` services. PC Server and Android are not containers.
- The AI container reaches peer services by Compose DNS: `browser-server` and `room-server`.
- PC Server remains host-native and is reached from containers through `host.docker.internal:50052`.
- Android is not a container. Install the APK on the device and connect it to exposed AI gRPC `50051`.
- Canonical deploy is image rebuild (`scripts/rebuild-ai-server.ps1` or `scripts/ubuntu/start.sh`). Partial `docker cp` is emergency-only.
- `/health` reports `revision` from `AEGIS_SOURCE_REVISION`.
- `AEGIS_MIN_LLM_INTERVAL_MS` is **`60000`** in `docker-compose.yml` (one LLM call per minute under
  high pressure), and **`0`** — no throttle — when the variable is unset outside Docker
  (`autonomous/autonomous_loop.py`). The two defaults are deliberately different; the container
  value is the throttled one.
- `AGORA_TOKEN`, LLM keys, and Android pairing tokens must come from `.env`; never bake them into images.
