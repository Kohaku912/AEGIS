#!/bin/bash
set -euo pipefail
SSHPASS=$(cat /tmp/opi_pw.txt); export SSHPASS
HOST=192.168.50.120
sshpass -e ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$HOST '
set -e
PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python - <<PY
import mmap, struct, subprocess, os, math
BASE=0x0300B000
STRIDE=0x24
def mode(pin):
    bank=ord(pin[1])-ord("A"); bit=int(pin[2:])
    off=bank*STRIDE+(bit//8)*4; shift=(bit%8)*4
    with open("/dev/mem","r+b",buffering=0) as f:
        m=mmap.mmap(f.fileno(),0x1000,offset=BASE)
        cfg=struct.unpack_from("<I",m,off)[0]
        m.close()
    return (cfg>>shift)&0xF
print("modes before", {p:mode(p) for p in ("PH5","PH6","PH7","PH8","PH9","PC11")})
# capture while checking mid-stream via background
subprocess.run(["arecord","-D","hw:2,0","-f","S32_LE","-r","48000","-c","2","-d","2","-t","raw","/tmp/mic3.raw"], check=False)
print("modes after", {p:mode(p) for p in ("PH5","PH6","PH7","PH8","PH9")})
raw=open("/tmp/mic3.raw","rb").read()
n=len(raw)//4
samples=struct.unpack(f"<{n}i", raw[:n*4])
peak=max(abs(s) for s in samples) if samples else 0
rms=math.sqrt(sum(s*s for s in samples)/len(samples)) if samples else 0
nonzero=sum(1 for s in samples if s!=0)
print("bytes", len(raw), "peak", peak, "rms", rms, "nonzero", nonzero, "of", len(samples))
print("first16", samples[:16])
PY
# update room-server sound device to hw:2,0 and restart
UNIT=/etc/systemd/system/aegis-room-server.service
sed -i "s/Environment=AEGIS_ROOM_SOUND_ALSA_DEVICE=.*/Environment=AEGIS_ROOM_SOUND_ALSA_DEVICE=hw:2,0/" "$UNIT"
grep SOUND "$UNIT" || true
systemctl daemon-reload
systemctl restart aegis-room-server
sleep 1
systemctl is-active aegis-room-server
AEGIS_ROOM_SOUND_PROVIDER=alsa AEGIS_ROOM_SOUND_ALSA_DEVICE=hw:2,0 \
PYTHONPATH=/opt/aegis/room-server/src /opt/aegis/room-server/.venv/bin/python -c \
"from aegis_room.sound_inmp441 import create_sound_provider; s=create_sound_provider(); x=s.sample(1000); print(x.available, x.rms, x.peak, x.db_fs, x.warning)"
'
