import sys
sys.stdout.reconfigure(encoding='utf-8')

from aegis_ai.llm.factory import create_llm_provider

llm = create_llm_provider()

tools_desc = """Available tools:
- browser-server__page__browse: Execute browser tasks using AI agent
- pc-server__screenshot__get_screenshot: Capture screenshot"""

prompt = f"""Googleのホームページにアクセスして、ページのタイトルを教えて

{tools_desc}

To use a tool, respond with:
<tool_call>{{"name": "tool_name", "arguments": {{"key": "value"}}}}</tool_call>

If no tool is needed, respond normally."""

result = llm.generate(prompt=prompt, system_prompt='You are AEGIS.', max_tokens=500)
print('Response:')
print(repr(result.content[:1000]))
