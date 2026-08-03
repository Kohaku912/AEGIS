from flask import Flask
from aegis_ai.web.routes import ui_v2

app = Flask(__name__)

@app.route("/dashboard/desires")
def legacy():
    return "LEGACY"

class O:
    app = app
    _runtime = object()

ui_v2.init_ui_v2_routes(O())
c = app.test_client()
r = c.get("/dashboard/desires", headers={"Accept": "text/html"})
body = r.data.decode("utf-8", "replace")
print("status", r.status_code)
print("spa", "root" in body or "AEGIS" in body or "doctype" in body.lower())
print("legacy", "LEGACY" in body)
print("cache", r.headers.get("Cache-Control"))
print("snippet", body[:120].replace("\n"," "))
