#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [ "${AEGIS_SKIP_SYSTEMD_ACTIVE_CHECK:-}" != "1" ] \
  && command -v systemctl >/dev/null 2>&1 \
  && systemctl list-unit-files aegis.service >/dev/null 2>&1; then
  systemctl is-active --quiet aegis || {
    echo "aegis.service is not active" >&2
    systemctl status aegis --no-pager >&2 || true
    exit 1
  }
fi

docker compose -f docker-compose.yml -f docker-compose.production.yml ps >/tmp/aegis-compose-ps.log || {
  cat /tmp/aegis-compose-ps.log >&2
  exit 1
}

curl -fsS http://127.0.0.1:${AEGIS_DASHBOARD_PORT:-8090}/health >/dev/null
python3 scripts/audit-production-readiness.py --report-dir data/reports >/tmp/aegis-readiness.log || {
  cat /tmp/aegis-readiness.log >&2
  exit 1
}
echo "AEGIS healthcheck passed"
