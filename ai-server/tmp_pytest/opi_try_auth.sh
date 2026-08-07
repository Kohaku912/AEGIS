#!/bin/bash
set -euo pipefail
if ! command -v sshpass >/dev/null 2>&1; then
  sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq sshpass
fi
USERS=(root orangepi pi)
PASSWORDS=(tatuki9120 912912 anyway_5346 orangepi 1234 armbian password root admin 12345)
for u in "${USERS[@]}"; do
  for p in "${PASSWORDS[@]}"; do
    if sshpass -p "$p" ssh \
      -o StrictHostKeyChecking=accept-new \
      -o PreferredAuthentications=password \
      -o PubkeyAuthentication=no \
      -o ConnectTimeout=5 \
      "$u@192.168.50.108" 'echo AUTH_OK; whoami; uname -a; . /etc/os-release; echo "$PRETTY_NAME"' 2>/dev/null; then
      echo "SUCCESS_USER=$u"
      printf '%s\n' "$u" > /tmp/opi_user.txt
      printf '%s\n' "$p" > /tmp/opi_pw.txt
      chmod 600 /tmp/opi_pw.txt
      exit 0
    fi
  done
done
echo NO_MATCH
exit 1
