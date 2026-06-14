import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'src'))
from aegis_ai.memory.advanced import AdvancedMemory
from aegis_ai.llm.factory import create_llm_provider

data = json.loads(sys.stdin.read())
content = data.get("content", "")
if not content:
    print(json.dumps({"ok": False, "error": "No content provided"}))
    sys.exit(1)

llm = create_llm_provider()
data_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'data', 'memory')
memory = AdvancedMemory(data_dir=os.path.abspath(data_dir), llm_provider=llm)
memory.add_conversation(content, "Saved")
print(json.dumps({"ok": True, "message": f"Saved: {content[:50]}"}))
