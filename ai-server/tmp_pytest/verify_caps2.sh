#!/bin/bash
set -euo pipefail
docker exec aegis-ai-server-1 python -c '
from aegis_ai.runtime import get_runtime
rt = get_runtime()
caps = rt.capability_catalog.list_for_llm()
want = ("room-server.light.set_light", "room-server.ir.send_ir_command")
ids = [c["id"] for c in caps if c["id"] in want]
print("FOUND", ids)
for c in caps:
    if c["id"] in want:
        print("---", c["id"])
        print((c.get("description") or "")[:240])
'
ls -la /app/capabilities/builtin/room-server/light/set_light.json 2>/dev/null || docker exec aegis-ai-server-1 ls -la /app/capabilities/builtin/room-server/light/ /app/capabilities/builtin/room-server/ir/
docker exec aegis-ai-server-1 head -c 200 /app/capabilities/builtin/room-server/light/set_light.json
echo
