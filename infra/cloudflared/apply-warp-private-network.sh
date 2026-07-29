#!/usr/bin/env bash
# Publish AEGIS Core as a Zero Trust private network (WARP), not a public gRPC hostname.
#
# Requires API token with:
#   - Account: Cloudflare Tunnel Edit / Cloudflare One Connectors Write
#   - Account: Cloudflare One Networks Write (teamnet routes)
#   - Account: Zero Trust / Warp device policy write
#
# Usage:
#   export CLOUDFLARE_API_TOKEN=...
#   export CLOUDFLARE_ACCOUNT_ID=984d706b177f0a3abdfa2849fe3c1cff
#   bash infra/cloudflared/apply-warp-private-network.sh

set -euo pipefail

TUNNEL_ID="${TUNNEL_ID:-4939347a-cdf3-41f6-bb3e-646b883a54a3}"
API_TOKEN="${CLOUDFLARE_API_TOKEN:?CLOUDFLARE_API_TOKEN is required}"
ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-984d706b177f0a3abdfa2849fe3c1cff}"
PRIVATE_CIDR="${AEGIS_PRIVATE_CIDR:-192.168.50.41/32}"
DASHBOARD_HOSTNAME="${DASHBOARD_HOSTNAME:-kawahara.pp.ua}"
AEGIS_HOSTNAME="${AEGIS_HOSTNAME:-aegis.kawahara.pp.ua}"
DASHBOARD_ORIGIN="${DASHBOARD_ORIGIN:-http://127.0.0.1:8090}"

auth=(-H "Authorization: Bearer ${API_TOKEN}" -H "Content-Type: application/json")
api() {
  local method=$1 path=$2
  shift 2
  curl -fsS -X "$method" "${auth[@]}" "$@" \
    "https://api.cloudflare.com/client/v4${path}"
}

echo "=== ensure teamnet route ${PRIVATE_CIDR} → ${TUNNEL_ID} ==="
EXISTING=$(api GET "/accounts/${ACCOUNT_ID}/teamnet/routes" | python3 -c "
import json,sys
d=json.load(sys.stdin)
cid='${PRIVATE_CIDR}'; tid='${TUNNEL_ID}'
for r in d.get('result') or []:
  if r.get('network')==cid and r.get('tunnel_id')==tid and not r.get('deleted_at'):
    print(r.get('id','')); break
")
if [[ -n "${EXISTING}" ]]; then
  echo "route ok: ${EXISTING}"
else
  api POST "/accounts/${ACCOUNT_ID}/teamnet/routes" \
    --data "{\"network\":\"${PRIVATE_CIDR}\",\"tunnel_id\":\"${TUNNEL_ID}\",\"comment\":\"AEGIS Core gRPC (Android WARP)\"}" \
    | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d); raise SystemExit(0 if d.get("success") else 1)'
fi

echo "=== tunnel config: dashboard ingress + warp-routing ==="
python3 - <<PY > /tmp/aegis-cf-tunnel-config.json
import json
print(json.dumps({
  "config": {
    "ingress": [
      {"hostname": "${DASHBOARD_HOSTNAME}", "service": "${DASHBOARD_ORIGIN}"},
      {"hostname": "${AEGIS_HOSTNAME}", "service": "${DASHBOARD_ORIGIN}"},
      {"service": "http_status:404"},
    ],
    "warp-routing": {"enabled": True},
  }
}))
PY
api PUT "/accounts/${ACCOUNT_ID}/cfd_tunnel/${TUNNEL_ID}/configurations" \
  --data @/tmp/aegis-cf-tunnel-config.json \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps(d, indent=2)[:1500]); raise SystemExit(0 if d.get("success") else 1)'

echo "=== device Split Tunnels Exclude without 192.168.0.0/16 (default + custom profiles) ==="
python3 - <<'PY' > /tmp/aegis-cf-split-exclude.json
import json
print(json.dumps([
  {"address": "10.0.0.0/8"},
  {"address": "100.64.0.0/10"},
  {"address": "169.254.0.0/16", "description": "DHCP Unspecified"},
  {"address": "172.16.0.0/12"},
  {"address": "192.0.0.0/24"},
  {"address": "224.0.0.0/24"},
  {"address": "240.0.0.0/4"},
  {"address": "255.255.255.255/32", "description": "DHCP Broadcast"},
  {"address": "fe80::/10", "description": "IPv6 Link Local"},
  {"address": "fd00::/8"},
  {"address": "ff01::/16"},
  {"address": "ff02::/16"},
  {"address": "ff03::/16"},
  {"address": "ff04::/16"},
  {"address": "ff05::/16"},
]))
PY
api PUT "/accounts/${ACCOUNT_ID}/devices/policy/exclude" \
  --data @/tmp/aegis-cf-split-exclude.json \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps(d, indent=2)[:800]); raise SystemExit(0 if d.get("success") else 1)'

# Custom profiles (e.g. WARP onboarding) take precedence over Default — patch them too.
api GET "/accounts/${ACCOUNT_ID}/devices/policies" > /tmp/aegis-cf-policies.json
API_TOKEN="${API_TOKEN}" ACCOUNT_ID="${ACCOUNT_ID}" python3 - <<'PY'
import json, os, urllib.request
d = json.load(open("/tmp/aegis-cf-policies.json", encoding="utf-8"))
token = os.environ["API_TOKEN"]
account = os.environ["ACCOUNT_ID"]
body = open("/tmp/aegis-cf-split-exclude.json", "rb").read()
for p in d.get("result") or []:
    pid = p.get("policy_id")
    if not pid or p.get("default"):
        continue
    excl = [e.get("address") for e in (p.get("exclude") or [])]
    if "192.168.0.0/16" not in excl:
        print(f"skip {p.get('name')}: already ok")
        continue
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{account}/devices/policy/{pid}/exclude",
        data=body,
        method="PUT",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        out = json.loads(resp.read().decode())
    print(f"patched {p.get('name')} ({pid}) success={out.get('success')}")
PY

echo "Done."
echo "IMPORTANT: On the phone, toggle Cloudflare One OFF then ON so routes refresh."
echo "Confirm dumpsys connectivity VPN routes do NOT contain '192.168.0.0/16 throw'."
echo "Then AEGIS app → ${PRIVATE_CIDR%:*}:50051"
