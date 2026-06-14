import sys, json, socket

def send_pc_command(cmd, host="localhost", port=50052):
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((host, port))
        s.sendall((cmd + "\n").encode())
        resp = b""
        while True:
            chunk = s.recv(4096)
            if not chunk or b"\n" in chunk:
                resp += chunk
                break
            resp += chunk
        s.close()
        return json.loads(resp.decode().strip())
    except Exception:
        return None

data = json.loads(sys.stdin.read())
pc_result = send_pc_command("screenshot")
if pc_result and "image_base64" in pc_result:
    print(json.dumps({"ok": True, "result": {"image_base64": pc_result["image_base64"]}}))
else:
    print(json.dumps({"ok": False, "error": "Failed to capture screenshot. Is PC Server running?"}))
