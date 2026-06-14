import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..', 'src'))
from aegis_ai.integrations.agora.agora_service import AgoraService

data = json.loads(sys.stdin.read())
limit = data.get("limit", 10)

svc = AgoraService()
if not svc.is_configured:
    print(json.dumps({"ok": False, "error": "AGORA is not configured. Set AGORA_TOKEN."}))
    sys.exit(1)

mentions = svc.read_mentions(limit=limit)
if hasattr(mentions, "posts") and mentions.posts:
    lines = []
    for p in mentions.posts[-limit:]:
        body = p.body[:100].replace("\n", " ")
        lines.append(f"[{p.id}] {p.author.name}: {body}")
    print(json.dumps({"ok": True, "result": "Your AGORA mentions:\n" + "\n".join(lines)}))
else:
    print(json.dumps({"ok": True, "result": "No recent mentions on AGORA."}))

