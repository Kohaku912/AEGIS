import re
import json

content = '<tool_call>{"name": "browser-server__page__browse", "arguments": {"task": "test"}}</tool_call>'

tool_call_pattern = r'<tool_call>(.*?)</tool_call>'
matches = re.findall(tool_call_pattern, content, re.DOTALL)
print('Matches:', len(matches))
if matches:
    tc = json.loads(matches[0].strip())
    print('Parsed:', tc)
