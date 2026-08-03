"""ui-v2 shell must win over legacy Jinja pages on the same /dashboard paths."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template_string


def test_ui_v2_before_request_overrides_legacy_dashboard_html(tmp_path, monkeypatch):
    from aegis_ai.web.routes import ui_v2

    dist = tmp_path / "ui-v2"
    assets = dist / "assets"
    assets.mkdir(parents=True)
    (dist / "index.html").write_text(
        "<!doctype html><html><body>SPA_SHELL</body></html>",
        encoding="utf-8",
    )
    (assets / "app.js").write_text("console.log('spa')", encoding="utf-8")

    monkeypatch.setattr(ui_v2, "_ui_dist_dir", lambda: dist)
    monkeypatch.setenv("AEGIS_UI_VERSION", "v2")

    app = Flask(__name__)

    @app.route("/dashboard/desires")
    def legacy_desires():
        return render_template_string("<html>LEGACY_DESIRES</html>")

    @app.route("/dashboard/memory")
    def legacy_memory():
        return render_template_string("<html>LEGACY_MEMORY</html>")

    class Owner:
        def __init__(self, flask_app: Flask):
            self.app = flask_app
            self._runtime = object()

    ui_v2.init_ui_v2_routes(Owner(app))

    client = app.test_client()
    desires = client.get("/dashboard/desires", headers={"Accept": "text/html"})
    assert desires.status_code == 200
    assert b"SPA_SHELL" in desires.data
    assert b"LEGACY_DESIRES" not in desires.data
    assert desires.headers.get("Cache-Control", "").startswith("no-cache")

    memory = client.get("/dashboard/memory", headers={"Accept": "text/html"})
    assert b"SPA_SHELL" in memory.data
    assert b"LEGACY_MEMORY" not in memory.data

    asset = client.get("/assets/app.js")
    assert asset.status_code == 200
    assert b"spa" in asset.data
