# Local Deployment Guide

> **Status**: Phase 1.2 — Skeleton services (2026-06-11)  
> **Related**: [`architecture.md`](architecture.md), [`../docker-compose.yml`](../docker-compose.yml)

## Quick Start

```bash
# 1. Set up environment (no real secrets needed for placeholders)
cp .env.example .env

# 2. Start all services
docker compose up -d

# 3. Check status
docker compose ps

# 4. View logs
docker compose logs -f ai-server

# 5. Stop all services
docker compose down
```

## Service Map

| Service | Port | Language | Status |
|---------|------|----------|--------|
| `ai-server` | 50051 | Python 3.12 | ✅ gRPC HealthCheck |
| `browser-server` | 50052 | Node.js 22 | ⚠️ Placeholder HTTP |
| `pc-server` | 50053 | Python 3.12 | ⚠️ Placeholder HTTP |
| `room-server` | 50054 | Python 3.12 | ⚠️ Placeholder HTTP |
| `dev-server` | 50055 | Python 3.12 | ⚠️ Placeholder HTTP |
| `android-server` | 50056 | Kotlin | ❌ Runs on device |

All services communicate on the internal `aegis-net` Docker network via gRPC.

## Health Checks

```bash
# AI Server gRPC HealthCheck
docker compose exec ai-server python -c "
from generated.aegis import ai_server_pb2_grpc, common_pb2
import grpc
ch = grpc.insecure_channel('localhost:50051')
stub = ai_server_pb2_grpc.AIServerStub(ch)
r = stub.HealthCheck(common_pb2.HealthCheckRequest(server_id='test'))
print(f'Status: {r.status.code}, Server: {r.server_status}')
"

# Other servers (placeholder HTTP)
curl http://localhost:50052/health  # Browser
curl http://localhost:50053         # PC
curl http://localhost:50054         # Room
curl http://localhost:50055         # Dev
```

## Environment Variables

All configurable via `.env` (copy from `.env.example`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `AEGIS_AI_GRPC_PORT` | 50051 | AI Server gRPC port |
| `AEGIS_BROWSER_GRPC_PORT` | 50052 | Browser Server port |
| `AEGIS_PC_GRPC_PORT` | 50053 | PC Server port |
| `AEGIS_ROOM_GRPC_PORT` | 50054 | Room Server port |
| `AEGIS_DEV_GRPC_PORT` | 50055 | Dev Server port |
| `AEGIS_AI_LOG_LEVEL` | INFO | AI Server log level |

## Security Notes

- **No real secrets** in `.env.example` — only placeholder names
- **Dev Server is sandboxed**: `read_only: true`, no Docker socket, repo mounted `:ro`
- **Network isolation**: all services on internal `aegis-net`, only AI Server port exposed to host by default
- **No host filesystem access** except Dev Server's read-only repo mount
- **No privileged containers**

## Scaling (Future)

When real implementations exist:

```bash
# Scale AI Server workers (stateless services only)
# docker compose up -d --scale ai-server=3  # Requires load balancer

# Run specific services only
docker compose up -d ai-server browser-server
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port already in use | Change ports in `.env` |
| AI Server won't start | Check `docker compose logs ai-server` |
| Health check failing | Service may need more startup time (`start_period`) |
| Cannot connect between services | Ensure they're on `aegis-net` network |
