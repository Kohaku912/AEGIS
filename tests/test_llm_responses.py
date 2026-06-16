"""Test all LLM responses."""
import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

tests = [
    ('screenshot', 'Take a screenshot'),
    ('memory', 'What do you know about me?'),
    ('general', 'What is Python?'),
]

for name, text in tests:
    print(f'=== {name} ===')
    data = json.dumps({'text': text}).encode()
    req = urllib.request.Request(
        'http://0.0.0.0:8090/api/chat/send',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    r = urllib.request.urlopen(req, timeout=60)
    resp = json.loads(r.read().decode())
    has_image = 'image' in resp
    print(f'  Image: {has_image}')
    response_text = resp.get('response', '')[:200]
    print(f'  Response: {response_text}')
    print()
