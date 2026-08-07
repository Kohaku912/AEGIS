#!/bin/bash
set -euo pipefail
curl -sS --max-time 10 http://127.0.0.1:8090/display/overview -o /tmp/aegis_overview.json
python3 - <<'PY'
import json
d=json.load(open("/tmp/aegis_overview.json"))
items=(((d.get("servers") or {}).get("data") or {}).get("items")) or []
for it in items:
    if str(it.get("server_id","")).startswith("android"):
        keep={k:it.get(k) for k in [
            "server_id","status","online","connection_mode","last_seen","error",
            "device_model","dependencies","health","summary"
        ] if k in it or True}
        # compact
        out={
            "server_id": it.get("server_id"),
            "status": it.get("status"),
            "summary": it.get("summary"),
            "dependencies": it.get("dependencies"),
            "error": it.get("error"),
            "host": it.get("host"),
            "port": it.get("port"),
        }
        print(json.dumps(out, ensure_ascii=False, indent=2)[:3000])
PY
echo "=== recent ai logs ==="
docker logs --since 10m aegis-ai-server-1 2>&1 | grep -i android | tail -50 || true
echo "=== grpc listen ==="
docker exec aegis-ai-server-1 ss -lntp | grep -E '50051|8090' || true
