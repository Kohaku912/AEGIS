import sys, json
sys.path.insert(0, 'src')
from aegis_ai.llm.factory import create_llm_provider
llm = create_llm_provider()
prompt = '''Generate a plan with 1 subtask to review AGORA posts.
Respond with JSON: {"subtasks": [{"description": "Read AGORA posts", "capability_id": "ai.agora.read_posts", "arguments": {}, "depends_on": []}]}'''
r = llm.generate(prompt=prompt, max_tokens=200)
print(f'success={r.success}')
print(f'content={repr(r.content[:500])}')
