#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  echo ".env is required. Copy .env.example and set secrets." >&2
  exit 1
fi

export AEGIS_RUNTIME_MODE="${AEGIS_RUNTIME_MODE:-production}"
docker compose up -d ai-server browser-server room-server dev-server
scripts/ubuntu/healthcheck.sh
