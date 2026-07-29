#!/usr/bin/env bash
# Apply AEGIS Dashboard + gRPC public hostnames to the remotely-managed Cloudflare Tunnel.
# Requires API token with:
#   - Account: Cloudflare Tunnel Edit (or Cloudflare One Connectors Write)
#   - Zone: DNS Edit
#
# Usage:
#   export CLOUDFLARE_API_TOKEN=...
#   export CLOUDFLARE_ACCOUNT_ID=984d706b177f0a3abdfa2849fe3c1cff
#   bash infra/cloudflared/apply-grpc-ingress.sh

set -euo pipefail

TUNNEL_ID="${TUNNEL_ID:-4939347a-cdf3-41f6-bb3e-646b883a54a3}"
API_TOKEN="${CLOUDFLARE_API_TOKEN:?CLOUDFLARE_API_TOKEN is required}"
ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-984d706b177f0a3abdfa2849fe3c1cff}"

DASHBOARD_HOSTNAME="${DASHBOARD_HOSTNAME:-kawahara.pp.ua}"
AEGIS_HOSTNAME="${AEGIS_HOSTNAME:-aegis.kawahara.pp.ua}"
GRPC_HOSTNAME="${GRPC_HOSTNAME:-grpc.kawahara.pp.ua}"
DASHBOARD_ORIGIN="${DASHBOARD_ORIGIN:-http://127.0.0.1:8090}"
GRPC_ORIGIN="${GRPC_ORIGIN:-http://192.168.50.41:50051}"

echo "Updating tunnel ${TUNNEL_ID}"
echo "  ${DASHBOARD_HOSTNAME} / ${AEGIS_HOSTNAME} -> ${DASHBOARD_ORIGIN}"
echo "  ${GRPC_HOSTNAME} -> ${GRPC_ORIGIN} (http2Origin)"

python3 - <<PY > /tmp/aegis-cf-tunnel-config.json
import json
print(json.dumps({
  "config": {
    "ingress": [
      {
        "hostname": "${DASHBOARD_HOSTNAME}",
        "service": "${DASHBOARD_ORIGIN}",
      },
      {
        "hostname": "${AEGIS_HOSTNAME}",
        "service": "${DASHBOARD_ORIGIN}",
      },
      {
        "hostname": "${GRPC_HOSTNAME}",
        "service": "${GRPC_ORIGIN}",
        "originRequest": {"http2Origin": True, "connectTimeout": 30},
      },
      {"service": "http_status:404"},
    ],
    "warp-routing": {"enabled": False},
  }
}))
PY

curl -fsS -X PUT \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data @/tmp/aegis-cf-tunnel-config.json \
  "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/cfd_tunnel/${TUNNEL_ID}/configurations" \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps(d, indent=2)); raise SystemExit(0 if d.get("success") else 1)'

echo "Done. In Cloudflare zone Network settings, enable gRPC if Android TLS/gRPC fails."
echo "Optionally create Access Service Auth for ${GRPC_HOSTNAME}."
