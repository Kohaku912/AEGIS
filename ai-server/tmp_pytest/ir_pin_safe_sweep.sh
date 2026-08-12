#!/bin/bash
# Safe pin sweep: exclude I2C (PH5/PH4 board 3/5) which crashes AXP313a PMIC.
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
OUT=/tmp/aegis-cam/pin_sweep_safe
mkdir -p "$OUT"
RESULTS="$OUT/results.jsonl"
: > "$RESULTS"

# Exclude board 3/5 (PH5/PH4 = TWI/I2C used by AXP313a path).
PINS=(
  "7:PC9" "8:PH2" "10:PH3" "11:PC6" "12:PC11" "13:PC5"
  "15:PC8" "16:PC15" "18:PC14" "19:PH7" "21:PH8" "22:PC7" "23:PH6" "24:PH9" "26:PC10"
)

alive() {
  sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ConnectTimeout=5 -o BatchMode=yes root@$HOST "true" 2>/dev/null
}

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
  if ! alive; then
    echo "OPI_DOWN before $soc"
    exit 2
  fi
  sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ConnectTimeout=10 -o ServerAliveInterval=5 -o ServerAliveCountMax=3 root@$HOST \
    "PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python /tmp/opi_pin_blast_safe.py $soc" \
    || { echo "TX_FAIL $soc"; exit 3; }
  sleep 1.2
  if ! alive; then
    echo "OPI_DOWN after $soc"
    exit 2
  fi
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
print("delta", row["delta"], flush=True)
if row["delta"] <= -20:
    print("LIKELY_HIT_EARLY", row["soc"], row["delta"], flush=True)
    raise SystemExit(0)
PY
done

python3 - <<PY
import json
from pathlib import Path
rows=[json.loads(l) for l in Path("$RESULTS").read_text().splitlines()]
rows.sort(key=lambda r: r["delta"])
print(f"{'board':>5} {'soc':<6} {'bright':>7} {'delta':>7}")
for r in rows:
    print(f"{r['board']:>5} {r['soc']:<6} {r['brightness']:>7.2f} {r['delta']:>+7.2f}")
best=rows[0]
print("baseline", $BASE)
if best["delta"] <= -15:
    print("LIKELY_HIT", best["soc"], best["delta"])
else:
    print("NO_CLEAR_HIT", best["soc"], best["delta"])
PY
