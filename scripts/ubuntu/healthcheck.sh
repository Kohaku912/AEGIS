#!/usr/bin/env bash
set -euo pipefail

curl -fsS http://127.0.0.1:${AEGIS_DASHBOARD_PORT:-8090}/health >/dev/null
python3 scripts/audit-production-readiness.py --report-dir data/reports >/tmp/aegis-readiness.log || {
  cat /tmp/aegis-readiness.log >&2
  exit 1
}
echo "AEGIS healthcheck passed"
