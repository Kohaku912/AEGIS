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
if [ -z "${AEGIS_SESSION_SECRET:-}" ]; then
  echo "AEGIS_SESSION_SECRET is required in production." >&2
  exit 1
fi
export AEGIS_AUTH_MODE="${AEGIS_AUTH_MODE:-passkey}"

COMPOSE_ARGS=(-f docker-compose.yml -f docker-compose.production.yml)
docker compose "${COMPOSE_ARGS[@]}" up -d ai-server browser-server
AEGIS_SKIP_SYSTEMD_ACTIVE_CHECK=1 scripts/ubuntu/healthcheck.sh
