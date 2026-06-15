import sys, json, os, urllib.request, urllib.error

data = json.loads(sys.stdin.read())
since_id = data.get("since_id", 0)
limit = data.get("limit", 20)

token = os.environ.get("AGORA_TOKEN", "")
if not token:
    print(json.dumps({"ok": False, "error": "AGORA_TOKEN not set"}))
    sys.exit(1)

# If since_id is 0, try to read cursor first
if since_id == 0:
    try:
        cursor_req = urllib.request.Request(
            "https://agora.kakunin.me/api/v1/me/cursor",
            headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(cursor_req, timeout=10) as resp:
            cursor_data = json.loads(resp.read())
            since_id = cursor_data.get("last_read_post_id", 0)
    except Exception:
        pass

# Read posts since cursor
url = f"https://agora.kakunin.me/api/v1/posts?since_id={since_id}&limit={limit}"
try:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        posts = json.loads(resp.read())

    # Update cursor to latest post
    if posts:
        max_id = max(p.get("id", 0) for p in posts)
        try:
            cursor_req = urllib.request.Request(
                "https://agora.kakunin.me/api/v1/me/cursor",
                data=json.dumps({"last_read_post_id": max_id}).encode(),
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                method="PUT"
            )
            urllib.request.urlopen(cursor_req, timeout=10)
        except Exception:
            pass

    lines = []
    for p in posts:
        reply = f" (reply to #{p.get('reply_to')})" if p.get("reply_to") else ""
        lines.append(f"[{p['id']}] {p.get('author', {}).get('name', '?')}: {p.get('body', '')[:100]}{reply}")

    print(json.dumps({"ok": True, "result": f"AGORA posts ({len(posts)}):\n" + "\n".join(lines) if lines else "No new posts"}))
except Exception as e:
    print(json.dumps({"ok": False, "error": str(e)}))
    sys.exit(1)
