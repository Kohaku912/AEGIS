import socket
import json

def send_cmd(cmd):
    s = socket.socket()
    s.settimeout(5)
    s.connect(('localhost', 50052))
    s.sendall((cmd + '\n').encode())
    resp = b''
    while True:
        chunk = s.recv(4096)
        if not chunk or b'\n' in chunk:
            resp += chunk
            break
        resp += chunk
    s.close()
    return json.loads(resp.decode().strip())

print('=== PC Server Test ===')
print()

# Health
health = send_cmd('health')
print('Health:', health['status'])
print('Version:', health['version'])
print('Capabilities:', health['capabilities'])
print()

# Mouse move
result = send_cmd('mouse_move 100,200')
print('Mouse move:', result['details'])
print()

# Mouse click (real action enabled)
result = send_cmd('mouse_click 500,500,left')
print('Mouse click:', result['details'])
print()

# Keyboard type
result = send_cmd('keyboard_type Hello AEGIS')
print('Keyboard type:', result['details'])
print()

# Hotkey
result = send_cmd('press_hotkey ctrl+c')
print('Hotkey:', result['details'])
print()

print('=== All tests passed! ===')
