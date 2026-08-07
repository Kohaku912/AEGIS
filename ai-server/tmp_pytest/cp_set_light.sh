#!/bin/bash
set -euo pipefail
docker cp /tmp/set_light.json aegis-ai-server-1:/app/capabilities/builtin/room-server/light/set_light.json
cp /tmp/set_light.json /opt/aegis/ai-server/capabilities/builtin/room-server/light/set_light.json
docker exec aegis-ai-server-1 python -c 'import json;d=json.load(open("/app/capabilities/builtin/room-server/light/set_light.json"));print(d["description"]);print(d["input_schema"]["properties"]["mode"])'
