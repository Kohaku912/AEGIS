"""Test memory dashboard page."""
import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

r = urllib.request.urlopen('http://127.0.0.1:8090/dashboard/memory', timeout=5)
content = r.read().decode()

checks = ['Persons', 'Semantic (Chroma)', 'Conversations', 'Episodic']
for check in checks:
    found = check in content
    status = 'PASS' if found else 'FAIL'
    print(f'[{status}] {check}')

print(f'Page size: {len(content)} bytes')
