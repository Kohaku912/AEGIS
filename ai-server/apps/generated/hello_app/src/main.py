import sys, json

args = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
name = args.get("name", "World")
print(json.dumps({"ok": True, "message": f"Hello, {name}!"}))
