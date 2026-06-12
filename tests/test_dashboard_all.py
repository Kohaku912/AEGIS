"""Test all dashboard pages."""
import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

pages = [
    ('/', 'Home'),
    ('/dashboard/servers', 'Servers'),
    ('/dashboard/capabilities', 'Capabilities'),
    ('/dashboard/events', 'Events'),
    ('/dashboard/tasks', 'Tasks'),
    ('/dashboard/support', 'Support'),
    ('/dashboard/memory', 'Memory'),
    ('/dashboard/audit', 'Audit'),
    ('/dashboard/errors', 'Errors'),
    ('/health', 'Health'),
    ('/api/dashboard/overview', 'API Overview'),
    ('/api/dashboard/events', 'API Events'),
    ('/api/dashboard/capabilities', 'API Capabilities'),
    ('/api/servers', 'API Servers'),
]

for page, name in pages:
    try:
        r = urllib.request.urlopen('http://127.0.0.1:8090' + page, timeout=5)
        content = r.read().decode()
        print(f'[PASS] {name} ({page}): {r.status} | {len(content)} bytes')
    except Exception as e:
        print(f'[FAIL] {name} ({page}): {e}')
