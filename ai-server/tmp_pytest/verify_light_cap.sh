#!/bin/bash
set -euo pipefail
docker exec aegis-ai-server-1 python - <<'PY'
from aegis_ai.capability_catalog import CapabilityCatalog
m = CapabilityCatalog().resolve('room-server.light.set_light')
print(m.description)
print((m.input_schema or {}).get('properties', {}).get('mode'))
PY
