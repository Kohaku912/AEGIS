import urllib.request

paths = [
    "/dashboard",
    "/dashboard/",
    "/dashboard/operations",
    "/",
    "/assets/index-DpMu2tRX.js",
    "/assets/index-DDQPWLLG.js",
    "/assets/index-D-wpWsXM.js",
    "/static/ui-v2/index.html",
    "/ui-v2/index.html",
]
for path in paths:
    try:
        req = urllib.request.Request("http://127.0.0.1:8090" + path, method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            body = response.read(500).decode("utf-8", "replace").replace("\n", " ")
            print(path, response.status, response.headers.get("Content-Type"), body[:160])
    except Exception as exc:
        print(path, "ERR", exc)
