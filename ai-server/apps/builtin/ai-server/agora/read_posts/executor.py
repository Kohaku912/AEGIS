import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..', 'src'))
from aegis_ai.integrations.agora.agora_service import AgoraService

data = json.loads(sys.stdin.read())
limit = data.get("limit", 10)

svc = AgoraService()
if not svc.is_configured:
    print(json.dumps({"ok": False, "error": "AGORA is not configured. Set AGORA_TOKEN."}))
    sys.exit(1)

posts = svc.read_posts(limit=limit)
if hasattr(posts, "posts") and posts.posts:
    lines = []
    for p in posts.posts[-limit:]:
        body = p.body[:100].replace("\n", " ")
        lines.append(f"[{p.id}] {p.author.name}: {body}")
    print(json.dumps({"ok": True, "result": "Recent AGORA posts:\n" + "\n".join(lines)}))
else:
    print(json.dumps({"ok": True, "result": "No recent AGORA posts."}))

