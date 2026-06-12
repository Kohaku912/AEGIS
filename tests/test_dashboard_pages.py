"""Test all dashboard pages and chat."""

import urllib.request
import json

pages = ['/', '/dashboard/servers', '/dashboard/capabilities', '/dashboard/events', '/dashboard/tasks', '/dashboard/support', '/dashboard/memory', '/dashboard/audit', '/dashboard/errors', '/health']

print('=== Dashboard Pages ===')
for page in pages:
    try:
        r = urllib.request.urlopen('http://127.0.0.1:8090' + page, timeout=5)
        print(f'[PASS] {page}: {r.status}')
    except Exception as e:
        print(f'[FAIL] {page}: {e}')

print()
print('=== Chat Screenshot Test ===')
data = json.dumps({'text': 'screenshot'}).encode()
req = urllib.request.Request(
    'http://127.0.0.1:8090/api/chat/send',
    data=data,
    headers={'Content-Type': 'application/json'}
)
r = urllib.request.urlopen(req, timeout=10)
resp = json.loads(r.read().decode())
has_image = 'image' in resp
print(f'Has image: {has_image}')
print(f'Response: {resp.get("response", "")[:100]}')
if has_image:
    img_len = len(resp['image'])
    print(f'Image data length: {img_len} chars')
