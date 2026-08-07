#!/bin/bash
set -euo pipefail
echo "=== /api/status ==="
curl -sS --max-time 10 http://127.0.0.1:8090/api/status -o /tmp/aegis_status.json
python3 - <<'PY'
import json
d=json.load(open("/tmp/aegis_status.json"))
a=None
if isinstance(d, dict):
    a=d.get("android-server")
    if a is None and isinstance(d.get("servers"), dict):
        a=d["servers"].get("android-server")
print(json.dumps(a or {"raw_keys":list(d)[:30]}, ensure_ascii=False)[:2000])
PY

echo "=== /display/overview android ==="
curl -sS --max-time 10 http://127.0.0.1:8090/display/overview -o /tmp/aegis_overview.json
python3 - <<'PY'
import json
d=json.load(open("/tmp/aegis_overview.json"))
items=(((d.get("servers") or {}).get("data") or {}).get("items")) or []
found=False
for it in items:
    if str(it.get("server_id","")).startswith("android"):
        print(json.dumps(it, ensure_ascii=False)[:2000])
        found=True
if not found:
    print("no android item; top keys", list(d.keys())[:20])
PY

echo "=== /api/android or manager ==="
for path in /api/android/status /api/managers/android /api/status/android; do
  code=$(curl -sS -o /tmp/aegis_a.json -w "%{http_code}" --max-time 5 "http://127.0.0.1:8090$path" || true)
  echo "$path -> $code"
  if [ "$code" = "200" ]; then head -c 800 /tmp/aegis_a.json; echo; fi
done

echo "=== docker logs android ==="
docker logs --since 5m aegis-ai-server-1 2>&1 | grep -iE 'android\.(connected|disconnected)|OpenAndroid|reverse_stream|ANDROID_|Stream acknowledged' | tail -40 || true
