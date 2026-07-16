import json
d = json.load(open("/tmp/display.json"))

attention = d.get("attention", {}).get("data", {}).get("items", [])
print("=== ATTENTION ITEMS ===")
for item in attention:
    print("  severity={}, kind={}, title={}".format(item.get("severity"), item.get("kind"), item.get("title")))

scene = d.get("display_scene", {}).get("data", {})
print("\n=== DISPLAY SCENE ===")
print("  takeover:", scene.get("takeover"))
print("  priority:", scene.get("priority"))

queue = d.get("display_queue", {}).get("data", {}).get("items", [])
print("\n=== DISPLAY QUEUE (first 5) ===")
for item in queue[:5]:
    print("  priority={}, severity={}, title={}".format(item.get("priority"), item.get("severity"), item.get("title")))
