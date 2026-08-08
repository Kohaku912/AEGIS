import socket
import time
import subprocess

print("ethernet", subprocess.getoutput('powershell -NoProfile -Command "(Get-NetAdapter -Name Ethernet).Status"'))
deadline = time.time() + 60
seen = set()
while time.time() < deadline:
    for i in range(1, 255):
        ip = f"192.168.50.{i}"
        s = socket.socket()
        s.settimeout(0.04)
        try:
            s.connect((ip, 22))
            if ip not in seen:
                seen.add(ip)
                print("ssh", ip, flush=True)
        except Exception:
            pass
        finally:
            s.close()
    print("tick seen=", sorted(seen), flush=True)
    time.sleep(3)
print("FINAL", sorted(seen))
