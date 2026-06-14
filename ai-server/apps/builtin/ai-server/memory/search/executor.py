import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'src'))
from aegis_ai.memory.advanced import AdvancedMemory
from aegis_ai.llm.factory import create_llm_provider

data = json.loads(sys.stdin.read())
query = data.get("query", "")
if not query:
    print(json.dumps({"ok": False, "error": "No query provided"}))
    sys.exit(1)

llm = create_llm_provider()
data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'memory')
memory = AdvancedMemory(data_dir=os.path.abspath(data_dir), llm_provider=llm)
context = memory.get_context(query)
print(json.dumps({"ok": True, "result": context if context else "No memory found."}))
