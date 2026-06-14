import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..', 'src'))
from aegis_ai.integrations.agora.agora_service import AgoraService

data = json.loads(sys.stdin.read())
message = data.get("message", "")
if not message:
    print(json.dumps({"ok": False, "error": "No message provided"}))
    sys.exit(1)

svc = AgoraService()
if not svc.is_configured:
    print(json.dumps({"ok": False, "error": "AGORA is not configured. Set AGORA_TOKEN."}))
    sys.exit(1)

result = svc.create_post(thread_id=1, body=message)
if hasattr(result, "id"):
    print(json.dumps({"ok": True, "result": f"Posted to AGORA (ID: {result.id}): {message[:50]}"}))
else:
    print(json.dumps({"ok": False, "error": f"Failed to post: {result}"}))

