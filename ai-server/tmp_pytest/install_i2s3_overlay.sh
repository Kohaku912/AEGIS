#!/bin/bash
# Install I2S3 INMP441 overlay on Orange Pi Zero3 and reboot.
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120

sshpass -e scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  /tmp/sun50i-h616-i2s3-inmp441.dts root@$HOST:/tmp/sun50i-h616-i2s3-inmp441.dts

sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
set -e
DTS=/tmp/sun50i-h616-i2s3-inmp441.dts
DTBO_NAME=sun50i-h616-i2s3-inmp441
OUT_DIR=/boot/dtb/allwinner/overlay
USER_DIR=/boot/overlay-user
mkdir -p "$OUT_DIR" "$USER_DIR"
# compile with symbols (-@) for phandle fixups
dtc -@ -I dts -O dtb -o "$OUT_DIR/${DTBO_NAME}.dtbo" "$DTS"
cp -f "$OUT_DIR/${DTBO_NAME}.dtbo" "$USER_DIR/${DTBO_NAME}.dtbo"
# also install short name expected by overlays=i2s3 under overlay_prefix
cp -f "$OUT_DIR/${DTBO_NAME}.dtbo" "$OUT_DIR/sun50i-h616-i2s3.dtbo"
ls -la "$OUT_DIR"/sun50i-h616-i2s3*.dtbo "$USER_DIR"/

ENV=/boot/armbianEnv.txt
cp -a "$ENV" "${ENV}.bak.$(date +%s)"
# ensure overlays line includes i2s3
if grep -q "^overlays=" "$ENV"; then
  grep -q "i2s3" "$ENV" || sed -i "s/^overlays=/overlays=i2s3 /" "$ENV"
else
  echo "overlays=i2s3" >> "$ENV"
fi
# also set user_overlays for the explicit name
if grep -q "^user_overlays=" "$ENV"; then
  grep -q "sun50i-h616-i2s3-inmp441" "$ENV" || sed -i "s/^user_overlays=/user_overlays=sun50i-h616-i2s3-inmp441 /" "$ENV"
else
  echo "user_overlays=sun50i-h616-i2s3-inmp441" >> "$ENV"
fi
echo "=== armbianEnv ==="
cat "$ENV"
sync
echo "REBOOTING for overlay..."
nohup bash -c "sleep 1; reboot" >/dev/null 2>&1 &
'
echo "reboot issued; waiting for host..."
sleep 25
for i in $(seq 1 40); do
  if sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@$HOST "echo UP; uname -a; arecord -l; cat /proc/asound/cards" 2>/dev/null; then
    exit 0
  fi
  echo "wait $i"
  sleep 5
done
echo "host did not return" >&2
exit 1
