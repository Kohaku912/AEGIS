import sys
import json
from pathlib import Path

# Read the autonomous_loop.py file and extract the _generate_default_tasks function
loop_file = Path('src/aegis_ai/autonomous/autonomous_loop.py')
content = loop_file.read_text(encoding='utf-8')

# Find the function
start = content.find('def _generate_default_tasks(')
end = content.find('\n    def ', start + 1)
func_code = content[start:end]

# Execute the function
exec(func_code)

# Test it
low_desires = [
    {'name': 'user_helpfulness', 'value': 2.0, 'expected': 8.0, 'gap': 6.0},
    {'name': 'system_safety', 'value': 4.0, 'expected': 9.0, 'gap': 5.0},
]

# Create a mock self object
class MockSelf:
    _max_tasks = 3

tasks = _generate_default_tasks(MockSelf(), low_desires)
print(f'Generated {len(tasks)} tasks')
for t in tasks:
    desire = t['desire']
    action = t['action'][:50]
    cap_id = t.get('capability_id', 'none')
    print(f'  - {desire}: {action}...')
    print(f'    capability_id: {cap_id}')
