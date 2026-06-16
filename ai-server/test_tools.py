import sys
sys.stdout.reconfigure(encoding='utf-8')

from aegis_ai.web.chat_tools import get_catalog, get_tools_for_chat

catalog = get_catalog()
tools = get_tools_for_chat(catalog)

print('Available tools:')
for t in tools:
    name = t['function']['name']
    desc = t['function']['description'][:100]
    print(f'  - {name}: {desc}')
