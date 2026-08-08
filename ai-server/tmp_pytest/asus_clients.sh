#!/bin/bash
set -euo pipefail
# Attempt ASUS login with known WiFi password / common admin
GW=192.168.50.1
PASSWORDS=(anyway_5346 admin password tatuki9120 912912)
USERS=(admin)

login() {
  local user="$1" pass="$2"
  # asuswrt login.cgi style
  curl -s -m 5 -c /tmp/asus_cj -b /tmp/asus_cj \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "login_authorization=$(printf '%s:%s' "$user" "$pass" | openssl base64 -A)" \
    "http://$GW/login.cgi" -o /tmp/asus_login.txt -w '%{http_code}'
}

for u in "${USERS[@]}"; do
  for p in "${PASSWORDS[@]}"; do
    code=$(login "$u" "$p" || true)
    echo "login $u code=$code"
    body=$(cat /tmp/asus_login.txt 2>/dev/null || true)
    echo "body=${body:0:120}"
    # fetch client list
    curl -s -m 5 -b /tmp/asus_cj "http://$GW/appGet.cgi?hook=get_clientlist()" -o /tmp/asus_clients.txt || true
    if grep -q 'mac' /tmp/asus_clients.txt 2>/dev/null || grep -qi 'orangepi\|192.168.50' /tmp/asus_clients.txt 2>/dev/null; then
      echo "CLIENTS_OK"
      python3 - <<'PY'
import json,re
t=open('/tmp/asus_clients.txt','r',errors='ignore').read()
print(t[:2000])
PY
      exit 0
    fi
  done
done
echo NO_ROUTER_LOGIN
# still print login page title
head -c 200 /tmp/asus_login.txt || true
