# AEGIS Docker Services

This compose setup runs the containerized AEGIS services:

- `ai-server`: gRPC `50051`, Dashboard `8090`, Web Chat `8091`
- `browser-server`: HTTP `50053`
- `room-server`: gRPC `50055`
- `dev-server`: gRPC `50056`

PC Server remains host-native on Windows and is reached from containers through
`host.docker.internal:50052`. Android remains the installed mobile app and
connects to the exposed AI gRPC port.

## Start

```powershell
docker compose build ai-server browser-server room-server dev-server
docker compose up -d ai-server browser-server room-server dev-server
```

Or use:

```powershell
.\scripts\start-beta-docker.ps1 -Build
```

## Dev Server Mount

`dev-server` mounts the repository at `/workspace` with write access. This is
intentional for self-development workflows. The Docker socket is not mounted.

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
docker compose logs -f ai-server browser-server room-server dev-server
```

Expected endpoints:

- Dashboard: `http://localhost:8090`
- Web Chat: `http://localhost:8091`
- Browser health: `http://localhost:50053/health`
- AI gRPC: `localhost:50051`
- Room gRPC: `localhost:50055`
- Dev gRPC: `localhost:50056`

## Current Canonical Topology

- Docker Compose owns `ai-server`, `browser-server`, `room-server`, and `dev-server`.
- The AI container reaches peer services by Compose DNS: `browser-server`, `room-server`, and `dev-server`.
- PC Server remains host-native and is reached from containers through `host.docker.internal:50052`.
- Android is not a container. Install the APK on the device and connect it to exposed AI gRPC `50051`.
- `AEGIS_MIN_LLM_INTERVAL_MS` defaults to `60000` so high-pressure autonomous desire cycles can ask the LLM once per minute.
- `AGORA_TOKEN`, LLM keys, and Android pairing tokens must come from `.env`; never bake them into images.

## Current Canonical Topology

- Docker Compose owns `ai-server`, `browser-server`, `room-server`, and `dev-server`.
- The AI container reaches peer services by Compose DNS: `browser-server`, `room-server`, and `dev-server`.
- PC Server remains host-native and is reached from containers through `host.docker.internal:50052`.
- Android is not a container. Install the APK on the device and connect it to exposed AI gRPC `50051`.
- `AEGIS_MIN_LLM_INTERVAL_MS` defaults to `60000` so high-pressure autonomous desire cycles can ask the LLM once per minute.
- `AGORA_TOKEN`, LLM keys, and Android pairing tokens must come from `.env`; never bake them into images.
