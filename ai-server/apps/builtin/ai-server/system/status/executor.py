import sys, json, socket

def check_port(host, port, timeout=2.0):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

data = json.loads(sys.stdin.read())
pc_status = "Online" if check_port("localhost", 50052) else "Offline"
browser_status = "Online" if check_port("localhost", 50053) else "Offline"
print(json.dumps({
    "ok": True,
    "result": f"System Status:\n- PC Server: {pc_status}\n- Browser: {browser_status}"
}))
