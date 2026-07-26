#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

compose_log="$(mktemp /tmp/aegis-compose-ps.XXXXXX)"
readiness_log="$(mktemp /tmp/aegis-readiness.XXXXXX)"
trap 'rm -f "$compose_log" "$readiness_log"' EXIT

if [ "${AEGIS_SKIP_SYSTEMD_ACTIVE_CHECK:-}" != "1" ] \
  && command -v systemctl >/dev/null 2>&1 \
  && systemctl list-unit-files aegis.service >/dev/null 2>&1; then
  systemctl is-active --quiet aegis || {
    echo "aegis.service is not active" >&2
    systemctl status aegis --no-pager >&2 || true
    exit 1
  }
fi

docker compose -f docker-compose.yml -f docker-compose.production.yml ps >"$compose_log" || {
  cat "$compose_log" >&2
  exit 1
}

if [ "${AEGIS_SKIP_RESOURCE_LIMIT_CHECK:-0}" != "1" ]; then
  for container in aegis-ai-server-1 aegis-browser-server-1; do
    limits="$(docker inspect --format '{{.HostConfig.Memory}} {{.HostConfig.PidsLimit}}' "$container" 2>/dev/null || true)"
    memory_limit="${limits%% *}"
    pids_limit="${limits#* }"
    if [ -z "$limits" ] || [ "${memory_limit:-0}" = "0" ] \
      || [ "${pids_limit:-<nil>}" = "<nil>" ] || [ "${pids_limit:-0}" = "0" ]; then
      echo "$container is missing its production memory/PID limit: ${limits:-not found}" >&2
      exit 1
    fi
  done
fi

dashboard_url="http://127.0.0.1:8090/health"
dashboard_ready=0
for _ in $(seq 1 "${AEGIS_HEALTHCHECK_ATTEMPTS:-40}"); do
  if docker compose \
    -f docker-compose.yml \
    -f docker-compose.production.yml \
    exec -T ai-server \
    curl -fsS --max-time 5 "$dashboard_url" >/dev/null 2>&1; then
    dashboard_ready=1
    break
  fi
  sleep "${AEGIS_HEALTHCHECK_DELAY_SECONDS:-3}"
done
if [ "$dashboard_ready" != "1" ]; then
  echo "AI Server did not become healthy from its local container: $dashboard_url" >&2
  docker compose -f docker-compose.yml -f docker-compose.production.yml ps >&2 || true
  exit 1
fi

docker compose \
  -f docker-compose.yml \
  -f docker-compose.production.yml \
  exec -T browser-server \
  curl -fsS --max-time 5 http://127.0.0.1:50053/health >/dev/null || {
    echo "Browser Server health or cgroup resource guard failed" >&2
    exit 1
  }
if [ "${AEGIS_RUN_READINESS_CHECK:-0}" = "1" ]; then
  python3 scripts/audit-production-readiness.py --report-dir data/reports >"$readiness_log" || {
    cat "$readiness_log" >&2
    exit 1
  }
fi
echo "AEGIS healthcheck passed"
