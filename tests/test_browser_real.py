"""Test Browser Server with real browser."""
import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print('=== Browser Server Real Test ===')
print()

# Test 1: Chat with browser request
print('[1] Chat: "Open example.com"')
data = json.dumps({'text': 'open https://example.com'}).encode()
req = urllib.request.Request(
    'http://0.0.0.0:8090/api/chat/send',
    data=data,
    headers={'Content-Type': 'application/json'}
)
try:
    r = urllib.request.urlopen(req, timeout=30)
    resp = json.loads(r.read().decode())
    has_image = 'image' in resp
    print(f'  Response: {resp.get("response", "")[:100]}')
    print(f'  Has image: {has_image}')
except Exception as e:
    print(f'  Error: {e}')

# Test 2: Chat with screenshot request
print()
print('[2] Chat: "Take a screenshot"')
data = json.dumps({'text': 'Take a screenshot'}).encode()
req = urllib.request.Request(
    'http://0.0.0.0:8090/api/chat/send',
    data=data,
    headers={'Content-Type': 'application/json'}
)
try:
    r = urllib.request.urlopen(req, timeout=10)
    resp = json.loads(r.read().decode())
    has_image = 'image' in resp
    print(f'  Response: {resp.get("response", "")[:100]}')
    print(f'  Has image: {has_image}')
    if has_image:
        print(f'  Image size: {len(resp["image"])} chars')
except Exception as e:
    print(f'  Error: {e}')

# Test 3: Chat with general question
print()
print('[3] Chat: "What is AEGIS?"')
data = json.dumps({'text': 'What is AEGIS?'}).encode()
req = urllib.request.Request(
    'http://0.0.0.0:8090/api/chat/send',
    data=data,
    headers={'Content-Type': 'application/json'}
)
try:
    r = urllib.request.urlopen(req, timeout=30)
    resp = json.loads(r.read().decode())
    print(f'  Response: {resp.get("response", "")[:200]}')
except Exception as e:
    print(f'  Error: {e}')

print()
print('=== Browser Server tests complete! ===')
