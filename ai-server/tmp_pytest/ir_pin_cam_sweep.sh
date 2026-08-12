#!/bin/bash
# Sweep all Orange Pi Zero3 26-pin header GPIOs with IR-off; measure USB cam brightness.
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
OUT=/tmp/aegis-cam/pin_sweep
mkdir -p "$OUT"

# BOARD -> SOC from providers._ZERO3_BOARD_TO_SOC (skip none; try all header GPIOs)
PINS=(
  "3:PH5"
  "5:PH4"
  "7:PC9"
  "8:PH2"
  "10:PH3"
  "11:PC6"
  "12:PC11"
  "13:PC5"
  "15:PC8"
  "16:PC15"
  "18:PC14"
  "19:PH7"
  "21:PH8"
  "22:PC7"
  "23:PH6"
  "24:PH9"
  "26:PC10"
)

echo "=== BASELINE ==="
python3 /tmp/cam_brightness.py "$OUT" baseline

results="$OUT/results.jsonl"
: > "$results"

for entry in "${PINS[@]}"; do
  board="${entry%%:*}"
  soc="${entry##*:}"
  label="b${board}_${soc}"
  echo "=== PIN board=$board soc=$soc ==="
  # both polarities on this pin
  for al in 0 1; do
    sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST \
      "PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python /tmp/opi_tx_pin.py $soc $al 5"
  done
  sleep 1.0
  python3 /tmp/cam_brightness.py "$OUT" "$label" | tee /tmp/aegis-cam/_last_bright.txt
  python3 - <<PY
import json
from pathlib import Path
lines = [ln for ln in Path("/tmp/aegis-cam/_last_bright.txt").read_text().splitlines() if ln.strip().startswith("{")]
row = json.loads(lines[-1])
row["board"] = $board
row["soc"] = "$soc"
Path("$results").open("a", encoding="utf-8").write(json.dumps(row, ensure_ascii=False) + "\n")
print("recorded", row.get("brightness"))
PY
done

python3 - <<'PY'
import json
from pathlib import Path
out = Path("/tmp/aegis-cam/pin_sweep")
base = None
# baseline from cam script stdout file isn't saved as json line; recompute
import subprocess
def bright(jpg):
    raw = Path(str(jpg) + ".sum.pgm")
    subprocess.run(["ffmpeg","-y","-i",str(jpg),"-vf","scale=160:120,format=gray",str(raw)], capture_output=True)
    pix = raw.read_bytes().split(b"\n", 3)[-1]
    return round(sum(pix) / max(1, len(pix)), 2)

base_b = bright(out / "baseline.jpg")
rows = []
for line in (out / "results.jsonl").read_text().splitlines():
    r = json.loads(line)
    b = float(r.get("brightness") or bright(out / f"{r['label']}.jpg"))
    rows.append({
        "board": r.get("board"),
        "soc": r.get("soc"),
        "brightness": b,
        "delta": round(b - base_b, 2),
    })
rows.sort(key=lambda x: x["delta"])
print(json.dumps({"baseline": base_b, "ranked_by_delta": rows}, ensure_ascii=False, indent=2))
best = rows[0] if rows else None
if best and best["delta"] <= -15:
    print("LIKELY_HIT", best)
else:
    print("NO_CLEAR_HIT (largest drop)", best)
PY
