import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'src'))
from aegis_ai.llm.factory import create_llm_provider

data = json.loads(sys.stdin.read())
message = data.get("message", "")
if not message:
    print(json.dumps({"ok": False, "error": "No message provided"}))
    sys.exit(1)

llm = create_llm_provider()
result = llm.generate(prompt=message, max_tokens=1000)
if result.success:
    print(json.dumps({"ok": True, "result": result.content}))
else:
    print(json.dumps({"ok": False, "error": result.error or "LLM error"}))
