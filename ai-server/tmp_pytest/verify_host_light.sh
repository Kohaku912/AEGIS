#!/bin/bash
set -euo pipefail
docker ps --filter name=aegis-ai-server-1 --format '{{.ID}} {{.Names}} {{.Status}}'
docker exec aegis-ai-server-1 ls /app/src/aegis_ai/net
docker exec aegis-ai-server-1 python -c "from aegis_ai.net.endpoint_resolver import resolve_tcp_endpoint; print(resolve_tcp_endpoint('pc-server', port=50052, timeout=0.3))"
docker exec aegis-ai-server-1 python -c "import json; from aegis_ai.runtime import get_runtime; sm=get_runtime().status_manager; s=sm.check_now(); print(json.dumps({k:s.get(k) for k in ('pc-server','room-server')}, ensure_ascii=False, indent=2))"
docker exec aegis-ai-server-1 python -c "from aegis_ai.capability_catalog import CapabilityCatalog; c=CapabilityCatalog(); m=c.resolve('room-server.light.set_light'); print(m.description[:120] if m else None); print((m.input_schema or {}).get('properties',{}).get('mode'))"
