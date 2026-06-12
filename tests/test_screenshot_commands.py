"""Test screenshot commands."""

import urllib.request
import json

tests = [
    ('screenshot', True),
    ('take a screenshot', True),
    ('active window', False),
    ('os info', False),
]

for text, expect_image in tests:
    data = json.dumps({'text': text}).encode()
    req = urllib.request.Request(
        'http://127.0.0.1:8090/api/chat/send',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    r = urllib.request.urlopen(req, timeout=10)
    resp = json.loads(r.read().decode())
    has_image = 'image' in resp
    status = 'OK' if has_image == expect_image else 'FAIL'
    print(f'[{status}] {text}: image={has_image}')
