#!/bin/bash
# Host orchestrates: baseline cam -> per-pin TX on OPi -> cam after each pin.
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
OUT=/tmp/aegis-cam/pin_sweep2
mkdir -p "$OUT"
RESULTS="$OUT/results.jsonl"
: > "$RESULTS"

PINS=(
  "3:PH5" "5:PH4" "7:PC9" "8:PH2" "10:PH3" "11:PC6" "12:PC11" "13:PC5"
  "15:PC8" "16:PC15" "18:PC14" "19:PH7" "21:PH8" "22:PC7" "23:PH6" "24:PH9" "26:PC10"
)

echo "=== ensure room-server ==="
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -o ConnectTimeout=10 root@$HOST 'systemctl start aegis-room-server; systemctl is-active aegis-room-server'

echo "=== BASELINE ==="
python3 /tmp/cam_brightness.py "$OUT" baseline | tee /tmp/aegis-cam/_b.txt
BASE=$(python3 -c "import json; from pathlib import Path; ls=[l for l in Path('/tmp/aegis-cam/_b.txt').read_text().splitlines() if l.startswith('{')]; print(json.loads(ls[-1])['brightness'])")
echo "baseline=$BASE"

for entry in "${PINS[@]}"; do
  board="${entry%%:*}"
  soc="${entry##*:}"
  label="b${board}_${soc}"
  echo "=== PIN board=$board soc=$soc ==="
  sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ConnectTimeout=10 -o ServerAliveInterval=5 root@$HOST \
    "PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python /tmp/opi_all_pins_tx.py $soc"
  sleep 1.2
  python3 /tmp/cam_brightness.py "$OUT" "$label" | tee /tmp/aegis-cam/_b.txt
  python3 - <<PY
import json
from pathlib import Path
ls=[l for l in Path("/tmp/aegis-cam/_b.txt").read_text().splitlines() if l.startswith("{")]
row=json.loads(ls[-1])
row["board"]=$board
row["soc"]="$soc"
row["delta"]=round(float(row["brightness"])-float("$BASE"),2)
Path("$RESULTS").open("a",encoding="utf-8").write(json.dumps(row,ensure_ascii=False)+"\n")
print("delta", row["delta"])
PY
done

python3 - <<'PY'
import json
from pathlib import Path
rows=[json.loads(l) for l in Path("/tmp/aegis-cam/pin_sweep2/results.jsonl").read_text().splitlines()]
rows.sort(key=lambda r: r.get("delta", 0))
print(json.dumps({
  "baseline": float("$BASE") if False else None,
  "ranked": [{"board":r["board"],"soc":r["soc"],"brightness":r["brightness"],"delta":r["delta"]} for r in rows],
  "best": {"board":rows[0]["board"],"soc":rows[0]["soc"],"delta":rows[0]["delta"]} if rows else None,
}, ensure_ascii=False, indent=2))
# fix baseline print
base=None
# re-read from first cam
import subprocess
from pathlib import Path as P
raw=P("/tmp/aegis-cam/pin_sweep2/baseline.sum.pgm")
jpg=P("/tmp/aegis-cam/pin_sweep2/baseline.jpg")
subprocess.run(["ffmpeg","-y","-i",str(jpg),"-vf","scale=160:120,format=gray",str(raw)],capture_output=True)
pix=raw.read_bytes().split(b"\n",3)[-1]
base=round(sum(pix)/max(1,len(pix)),2)
print("BASELINE", base)
print("TABLE")
print(f"{'board':>5} {'soc':<6} {'bright':>7} {'delta':>7}")
for r in rows:
  print(f"{r['board']:>5} {r['soc']:<6} {r['brightness']:>7.2f} {r['delta']:>+7.2f}")
best=rows[0]
if best["delta"] <= -15:
  print("LIKELY_HIT", best["soc"], best["delta"])
else:
  print("NO_CLEAR_HIT", best["soc"], best["delta"])
PY
