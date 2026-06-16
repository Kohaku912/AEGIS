"""Test AEGIS Dashboard and Chat."""

import urllib.request
import json

print('=== AEGIS Dashboard Test ===')
print()

# Test Dashboard
try:
    r = urllib.request.urlopen('http://0.0.0.0:8090/health', timeout=5)
    print('Dashboard:', r.status, r.read().decode())
except Exception as e:
    print('Dashboard Error:', e)

# Test API servers endpoint
try:
    r = urllib.request.urlopen('http://0.0.0.0:8090/api/servers', timeout=5)
    data = json.loads(r.read().decode())
    print('Servers:', data['summary'])
    for s in data['servers']:
        sid = s['server_id']
        st = s['status']
        caps = s['registered_capabilities']
        print(f'  - {sid}: {st} ({caps} caps)')
except Exception as e:
    print('Servers Error:', e)

# Test Chat with PC command
try:
    data = json.dumps({'text': 'Take a screenshot'}).encode()
    req = urllib.request.Request(
        'http://0.0.0.0:8090/api/chat/send',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    r = urllib.request.urlopen(req, timeout=10)
    resp = json.loads(r.read().decode())
    print()
    print('Chat (screenshot):')
    print(resp['response'][:300])
except Exception as e:
    print('Chat Error:', e)

# Test Chat with general question
try:
    data = json.dumps({'text': 'What is AEGIS?'}).encode()
    req = urllib.request.Request(
        'http://0.0.0.0:8090/api/chat/send',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    r = urllib.request.urlopen(req, timeout=30)
    resp = json.loads(r.read().decode())
    print()
    print('Chat (What is AEGIS?):')
    print(resp['response'][:300])
except Exception as e:
    print('Chat Error:', e)

print()
print('=== Test complete! ===')
