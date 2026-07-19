#!/usr/bin/env bash
set -euo pipefail

PRIMARY_WIFI="${AEGIS_PRIMARY_WIFI:-ASUS_F8_5G}"
FALLBACK_WIFI="${AEGIS_FALLBACK_WIFI:-ASUS_F8}"
GATEWAY="${AEGIS_NETWORK_GATEWAY:-192.168.50.1}"
HEALTH_URL="${AEGIS_LOCAL_HEALTH_URL:-http://127.0.0.1:8090/health}"
STATE_DIR="${AEGIS_NETWORK_STATE_DIR:-/run/aegis}"
FAILURE_FILE="$STATE_DIR/network-watchdog.failures"

mkdir -p "$STATE_DIR"

gateway_ready() {
  ping -c 1 -W 2 "$GATEWAY" >/dev/null 2>&1
}

core_ready() {
  curl -fsS --max-time 5 "$HEALTH_URL" >/dev/null 2>&1
}

configure_wifi_profile() {
  local profile="$1"
  local priority="$2"
  nmcli connection show "$profile" >/dev/null 2>&1 || return 1
  nmcli connection modify "$profile" \
    connection.autoconnect yes \
    connection.autoconnect-priority "$priority" \
    connection.autoconnect-retries 0 \
    802-11-wireless.powersave 2 \
    802-11-wireless.cloned-mac-address permanent
}

recover_wifi() {
  nmcli radio wifi on
  configure_wifi_profile "$PRIMARY_WIFI" 100 || true
  configure_wifi_profile "$FALLBACK_WIFI" 90 || true
  nmcli connection up "$PRIMARY_WIFI" >/dev/null 2>&1 \
    || nmcli connection up "$FALLBACK_WIFI" >/dev/null 2>&1 \
    || true
}

recover_tunnel() {
  systemctl reset-failed cloudflared.service || true
  systemctl restart cloudflared.service
}

failures=0
if [ -r "$FAILURE_FILE" ]; then
  read -r failures <"$FAILURE_FILE" || failures=0
fi

if gateway_ready; then
  rm -f "$FAILURE_FILE"
  if core_ready && ! systemctl is-active --quiet cloudflared.service; then
    recover_tunnel
  fi
  exit 0
fi

failures=$((failures + 1))
printf '%s\n' "$failures" >"$FAILURE_FILE"
logger -t aegis-network-watchdog "gateway unavailable; recovery attempt $failures"
recover_wifi
sleep 8

if ! gateway_ready && [ "$failures" -ge 3 ]; then
  systemctl restart NetworkManager.service
  sleep 10
  recover_wifi
  sleep 8
fi

if gateway_ready; then
  rm -f "$FAILURE_FILE"
  core_ready && recover_tunnel
  logger -t aegis-network-watchdog "network recovered"
  exit 0
fi

exit 1
