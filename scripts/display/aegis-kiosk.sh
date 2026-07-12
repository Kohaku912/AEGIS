#!/usr/bin/env bash
set -euo pipefail

URL="${AEGIS_KIOSK_URL:-http://127.0.0.1:8090/display/presentations}"
PROFILE_DIR="${AEGIS_KIOSK_PROFILE:-$HOME/.config/aegis-kiosk-browser}"
LOG_DIR="${AEGIS_KIOSK_LOG_DIR:-$HOME/.local/state/aegis}"
mkdir -p "$PROFILE_DIR" "$LOG_DIR"
exec >>"$LOG_DIR/kiosk.log" 2>&1

echo "[$(date --iso-8601=seconds)] kiosk supervisor starting for $URL DISPLAY=${DISPLAY:-} WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-}"

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
