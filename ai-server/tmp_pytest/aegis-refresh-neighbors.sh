#!/bin/bash
# Refresh LAN neighbor table into the AI Server data volume for MAC discovery.
set -euo pipefail
OUT_HOST="${AEGIS_NEIGHBOR_OUT:-/var/lib/docker/volumes/aegis_aegis-data/_data/neighbors.json}"
PREFIX="${AEGIS_LAN_SCAN_PREFIX:-192.168.50}"

for ip in "$PREFIX.108" "$PREFIX.120" "$PREFIX.195" "$PREFIX.176" "$PREFIX.198"; do
  ping -c 1 -W 1 "$ip" >/dev/null 2>&1 || true
done

python3 - <<'PY'
import json, re, subprocess, time
from pathlib import Path
import os
out = Path(os.environ.get("AEGIS_NEIGHBOR_OUT", "/var/lib/docker/volumes/aegis_aegis-data/_data/neighbors.json"))
out.parent.mkdir(parents=True, exist_ok=True)
neighbors = []
try:
    text = subprocess.check_output(["ip", "-4", "neigh", "show"], text=True, timeout=3)
except Exception:
    text = ""
for line in text.splitlines():
    parts = line.split()
    if "lladdr" not in parts:
        continue
    ip = parts[0]
    mac = parts[parts.index("lladdr") + 1]
    state = parts[-1]
    if not re.match(r"^\d+\.\d+\.\d+\.\d+$", ip):
        continue
    neighbors.append({"ip": ip, "mac": mac.lower(), "state": state})
payload = {"updated_at_ms": int(time.time() * 1000), "neighbors": neighbors}
out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(f"wrote {len(neighbors)} neighbors to {out}")
PY
