"""Test streaming chat."""
import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

print('=== Test Streaming Chat ===')
data = json.dumps({'text': 'What is Python?'}).encode()
req = urllib.request.Request(
    'http://0.0.0.0:8090/api/chat/stream',
    data=data,
    headers={'Content-Type': 'application/json'}
)
r = urllib.request.urlopen(req, timeout=60)

print('Response:')
for line in r:
    line = line.decode().strip()
    if line.startswith('data: '):
        try:
            d = json.loads(line[6:])
            if d['type'] == 'text':
                print(d['content'], end='', flush=True)
            elif d['type'] == 'done':
                print()
                print('[DONE]')
            elif d['type'] == 'error':
                print('[ERROR:', d['content'], ']')
        except Exception as e:
            pass
