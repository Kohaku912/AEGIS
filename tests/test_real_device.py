"""Real device integration test for AEGIS."""

import socket
import json
import urllib.request


def send_pc_cmd(cmd):
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


print('=== AEGIS Real Device Integration Test ===')
print()

# Test 1: AI Server gRPC
print('[1] AI Server gRPC health...')
try:
    import grpc
    channel = grpc.insecure_channel('localhost:50051')
    grpc.channel_ready_future(channel).result(timeout=5)
    print('  [PASS] AI Server gRPC ready on port 50051')
except Exception as e:
    print(f'  [FAIL] AI Server gRPC: {e}')

# Test 2: PC Server health
print('[2] PC Server health...')
try:
    health = send_pc_cmd('health')
    print(f'  [PASS] PC Server: {health["status"]} | Version: {health["version"]}')
except Exception as e:
    print(f'  [FAIL] PC Server: {e}')

# Test 3: Dashboard access
print('[3] Dashboard access...')
try:
    response = urllib.request.urlopen('http://127.0.0.1:8090/', timeout=5)
    print(f'  [PASS] Dashboard: HTTP {response.status}')
except Exception as e:
    print(f'  [FAIL] Dashboard: {e}')

# Test 4: Web Chat access
print('[4] Web Chat access...')
try:
    response = urllib.request.urlopen('http://127.0.0.1:8091/chat', timeout=5)
    print(f'  [PASS] Web Chat: HTTP {response.status}')
except Exception as e:
    print(f'  [FAIL] Web Chat: {e}')

# Test 5: PC Server screenshot
print('[5] PC Server screenshot...')
try:
    result = send_pc_cmd('screenshot')
    print(f'  [PASS] Screenshot: {result["width"]}x{result["height"]}')
except Exception as e:
    print(f'  [FAIL] Screenshot: {e}')

# Test 6: PC Server active window
print('[6] PC Server active window...')
try:
    result = send_pc_cmd('active_window')
    print(f'  [PASS] Active window: {result["title"]}')
except Exception as e:
    print(f'  [FAIL] Active window: {e}')

# Test 7: PC Server mouse move
print('[7] PC Server mouse move...')
try:
    result = send_pc_cmd('mouse_move 100,200')
    print(f'  [PASS] Mouse move: {result["details"]}')
except Exception as e:
    print(f'  [FAIL] Mouse move: {e}')

# Test 8: PC Server keyboard type
print('[8] PC Server keyboard type...')
try:
    result = send_pc_cmd('keyboard_type Hello AEGIS')
    print(f'  [PASS] Keyboard type: {result["details"]}')
except Exception as e:
    print(f'  [FAIL] Keyboard type: {e}')

# Test 9: PC Server overlay
print('[9] PC Server overlay...')
try:
    result = send_pc_cmd('show_overlay AEGIS Test Overlay')
    print(f'  [PASS] Overlay: {result["status"]}')
except Exception as e:
    print(f'  [FAIL] Overlay: {e}')

# Test 10: Browser Server health
print('[10] Browser Server health...')
try:
    s = socket.socket()
    s.settimeout(5)
    s.connect(('localhost', 50053))
    s.sendall(b'health\n')
    resp = s.recv(4096)
    s.close()
    print(f'  [PASS] Browser Server responded')
except Exception as e:
    print(f'  [FAIL] Browser Server: {e}')

print()
print('=== All real device tests complete! ===')
