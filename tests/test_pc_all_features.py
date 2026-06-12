"""Test all PC Server features."""
import socket, json, sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def send_cmd(cmd):
    s = socket.socket()
    s.settimeout(10)
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

print('=== PC Server Real Test ===')
print()

health = send_cmd('health')
print('Health:', health['status'], '| Version:', health['version'])

os_info = send_cmd('os_info')
print('OS:', os_info['os_name'], os_info['os_version'], '| Host:', os_info['hostname'])

screen = send_cmd('screen_size')
print('Screen:', screen['width'], 'x', screen['height'])

active = send_cmd('active_window')
print('Active Window:', active['title'][:50], '| Process:', active['process_name'])

windows = send_cmd('windows')
print('Windows:', len(windows), 'windows')
for w in windows[:3]:
    title = w['title'][:50]
    print(f'  - {title}')

clipboard = send_cmd('clipboard')
clip_text = clipboard[:50] if len(clipboard) > 50 else clipboard
print('Clipboard:', clip_text)

screenshot = send_cmd('screenshot')
print('Screenshot:', screenshot['width'], 'x', screenshot['height'], '| format:', screenshot['format'])
print('Image data:', len(screenshot['image_base64']), 'chars')
