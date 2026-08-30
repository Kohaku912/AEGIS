#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  echo ".env is required. Copy .env.example and set secrets." >&2
  exit 1
fi

export AEGIS_RUNTIME_MODE="${AEGIS_RUNTIME_MODE:-production}"
export AEGIS_BIND_HOST="${AEGIS_PRODUCTION_BIND_HOST:-127.0.0.1}"
export AEGIS_AUTH_MODE="${AEGIS_AUTH_MODE:-passkey}"
export AEGIS_SOURCE_REVISION="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"

COMPOSE_ARGS=(-f docker-compose.yml -f docker-compose.production.yml)
docker compose "${COMPOSE_ARGS[@]}" build --build-arg "AEGIS_SOURCE_REVISION=${AEGIS_SOURCE_REVISION}" ai-server
docker compose "${COMPOSE_ARGS[@]}" up -d --force-recreate --no-deps ai-server
docker compose "${COMPOSE_ARGS[@]}" up -d browser-server
AEGIS_SKIP_SYSTEMD_ACTIVE_CHECK=1 bash scripts/ubuntu/healthcheck.sh
