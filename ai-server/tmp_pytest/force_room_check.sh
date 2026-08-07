#!/bin/bash
set -euo pipefail
docker exec aegis-ai-server-1 python -c "
import json
from aegis_ai.runtime import get_runtime
sm = get_runtime().status_manager
sm.check_now()
print(json.dumps(sm.get_snapshot().get('room-server', {}), ensure_ascii=False, indent=2))
"
