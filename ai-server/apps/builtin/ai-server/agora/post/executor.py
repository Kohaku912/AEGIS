import sys, json, os, urllib.request

data = json.loads(sys.stdin.read())
body = data.get("body", "")
reply_to = data.get("reply_to")

if not body:
    print(json.dumps({"ok": False, "error": "body is required"}))
    sys.exit(1)

token = os.environ.get("AGORA_TOKEN", "")
if not token:
    print(json.dumps({"ok": False, "error": "AGORA_TOKEN not set"}))
    sys.exit(1)

payload = {"body": body, "reply_to": reply_to}
try:
    req = urllib.request.Request(
        "https://agora.kakunin.me/api/v1/threads/1/posts",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    print(json.dumps({"ok": True, "result": f"Posted #{result.get('id')}: {body[:80]}"}))
except Exception as e:
    print(json.dumps({"ok": False, "error": str(e)}))
    sys.exit(1)
