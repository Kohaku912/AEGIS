#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${AEGIS_KIOSK_URL:-http://127.0.0.1:8090/display/presentations}"
DISPLAY_TOKEN="${AEGIS_DISPLAY_TOKEN:-}"
URL="$BASE_URL"
if [[ -n "$DISPLAY_TOKEN" ]]; then
  separator="?"
  [[ "$URL" == *"?"* ]] && separator="&"
  encoded_token="$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$DISPLAY_TOKEN")"
  URL="${URL}${separator}display_token=${encoded_token}"
fi
PROFILE_DIR="${AEGIS_KIOSK_PROFILE:-$HOME/.config/aegis-kiosk-browser}"
LOG_DIR="${AEGIS_KIOSK_LOG_DIR:-$HOME/.local/state/aegis}"
mkdir -p "$PROFILE_DIR" "$LOG_DIR"
exec >>"$LOG_DIR/kiosk.log" 2>&1

echo "[$(date --iso-8601=seconds)] kiosk supervisor starting for $BASE_URL token=$([[ -n "$DISPLAY_TOKEN" ]] && echo enabled || echo disabled) DISPLAY=${DISPLAY:-} WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-}"

# The AI Core must never suspend with the desktop session. Display power is
# managed independently by aegis-display-power.service.
if command -v gsettings >/dev/null 2>&1; then
  gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing' || true
  gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type 'nothing' || true
  gsettings set org.gnome.desktop.session idle-delay 0 || true
fi

launch_browser() {
  rm -f "$PROFILE_DIR"/SingletonLock "$PROFILE_DIR"/SingletonSocket "$PROFILE_DIR"/SingletonCookie 2>/dev/null || true
  if command -v chromium-browser >/dev/null 2>&1; then
    chromium-browser --kiosk --no-first-run --disable-session-crashed-bubble --user-data-dir="$PROFILE_DIR" "$URL" &
  elif command -v chromium >/dev/null 2>&1; then
    chromium --kiosk --no-first-run --disable-session-crashed-bubble --user-data-dir="$PROFILE_DIR" "$URL" &
  elif command -v google-chrome >/dev/null 2>&1; then
    google-chrome --kiosk --no-first-run --disable-session-crashed-bubble --user-data-dir="$PROFILE_DIR" "$URL" &
  elif command -v firefox >/dev/null 2>&1; then
    firefox --kiosk --profile "$PROFILE_DIR" "$URL" &
  else
    echo "No supported browser found for AEGIS kiosk" >&2
    return 127
  fi
  echo $!
}

while true; do
  browser_pid="$(launch_browser)" || exit $?
  echo "[$(date --iso-8601=seconds)] browser pid=$browser_pid"
  sleep 10
  "$(dirname "$0")/aegis-kiosk-focus.py" || true
  wait "$browser_pid" || true
  echo "[$(date --iso-8601=seconds)] browser exited; restarting in 5s"
  sleep 5
done
