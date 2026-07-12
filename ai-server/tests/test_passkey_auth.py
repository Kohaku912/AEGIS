from __future__ import annotations

from types import SimpleNamespace

import pytest
from flask import Flask, jsonify

from aegis_ai.auth.passkey_service import PasskeyConfig, PasskeyService, b64url_encode
from aegis_ai.auth.passkey_store import PasskeyStore
from aegis_ai.auth.passkey_store import now_ms
from aegis_ai.auth.session_middleware import install_passkey_auth
from aegis_ai.auth.session_store import SessionStore
from aegis_ai.web.routes.ui_v2 import init_ui_v2_routes


def _service(tmp_path):
    store = PasskeyStore(tmp_path / "auth")
    service = PasskeyService(
        store,
        PasskeyConfig(
            rp_id="localhost",
            rp_name="AEGIS Test",
            origins=["http://localhost"],
            production=False,
        ),
    )
    return store, service


def test_registration_challenge_is_one_time(monkeypatch, tmp_path):
    store, service = _service(tmp_path)
    options = service.registration_options(username="admin", display_name="Admin")

    monkeypatch.setattr(
        "aegis_ai.auth.passkey_service.verify_registration_response",
        lambda **kwargs: SimpleNamespace(
            credential_id=b"cred-1",
            credential_public_key=b"public-key",
            sign_count=1,
            aaguid="aaguid",
            credential_device_type=SimpleNamespace(value="multi_device"),
            credential_backed_up=True,
        ),
    )

    result = service.verify_registration(
        challenge_id=options["challenge_id"],
        credential={"rawId": b64url_encode(b"cred-1")},
        origin="http://localhost",
    )

    assert result["user"]["username"] == "admin"
    with pytest.raises(PermissionError):
        service.verify_registration(
            challenge_id=options["challenge_id"],
            credential={"rawId": b64url_encode(b"cred-1")},
            origin="http://localhost",
        )
    assert store.has_users()


def test_origin_mismatch_rejected(tmp_path):
    _, service = _service(tmp_path)
    options = service.registration_options(username="admin", display_name="Admin")

    with pytest.raises(PermissionError):
        service.verify_registration(
            challenge_id=options["challenge_id"],
            credential={},
            origin="https://evil.example",
        )


def test_challenge_expiry_rejects_registration(tmp_path):
    store, service = _service(tmp_path)
    options = service.registration_options(username="admin", display_name="Admin")
    challenge = store.challenges[options["challenge_id"]]
    challenge.expires_at = now_ms() - 1
    store._save()

    with pytest.raises(PermissionError):
        service.verify_registration(
            challenge_id=options["challenge_id"],
            credential={},
            origin="http://localhost",
        )


def test_session_create_expire_logout(tmp_path):
    store, _ = _service(tmp_path)
    from aegis_ai.auth.models import AuthUser

    store.add_user(AuthUser(user_id="u1", username="admin", display_name="Admin", role="admin", created_at=1))
    sessions = SessionStore(store, lifetime_ms=10)

    session = sessions.create("u1")
    assert sessions.get(session.session_id) is not None
    sessions.revoke(session.session_id)
    assert sessions.get(session.session_id) is None


def test_store_persists_credentials_and_sessions(tmp_path):
    from aegis_ai.auth.models import AuthUser, PasskeyCredential

    store, _ = _service(tmp_path)
    store.add_user(AuthUser(user_id="u1", username="admin", display_name="Admin", created_at=1))
    store.add_credential(PasskeyCredential(credential_id="cred", user_id="u1", public_key="pub", created_at=2))
    session = SessionStore(store).create("u1")

    reloaded = PasskeyStore(tmp_path / "auth")
    assert reloaded.get_user("u1") is not None
    assert reloaded.get_credential("cred") is not None
    assert reloaded.get_session(session.session_id) is not None


def test_dashboard_and_api_require_auth_and_csrf(tmp_path, monkeypatch):
    monkeypatch.setenv("AEGIS_AUTH_MODE", "passkey")
    monkeypatch.delenv("AEGIS_RUNTIME_MODE", raising=False)
    app = Flask(__name__)
    install_passkey_auth(app, data_dir=tmp_path / "auth")

    @app.route("/dashboard")
    def dashboard():
        return "ok"

    @app.route("/api/capabilities/demo/risk", methods=["POST"])
    def risk():
        return jsonify({"ok": True})

    client = app.test_client()
    assert client.get("/dashboard").status_code in {302, 401}
    assert client.post("/api/capabilities/demo/risk", json={}).status_code == 403


def test_display_html_does_not_receive_dashboard_auth_bar(tmp_path, monkeypatch):
    monkeypatch.setenv("AEGIS_AUTH_MODE", "passkey")
    app = Flask(__name__)
    install_passkey_auth(app, data_dir=tmp_path / "auth")

    @app.route("/display/presentations")
    def display():
        return "<html><body>display</body></html>"

    client = app.test_client()
    response = client.get("/display/presentations")

    assert response.status_code == 200
    assert b"display" in response.data
    assert b"__aegisAuthInstalled" not in response.data


def test_display_stream_allows_local_get_without_session(tmp_path, monkeypatch):
    monkeypatch.setenv("AEGIS_AUTH_MODE", "passkey")
    app = Flask(__name__)
    install_passkey_auth(app, data_dir=tmp_path / "auth")

    @app.route("/api/ui/stream")
    def stream():
        return "ok"

    client = app.test_client()
    response = client.get("/api/ui/stream?surface=display", headers={"Accept": "text/event-stream"})

    assert response.status_code == 200
    assert response.data == b"ok"


def test_display_stream_rejects_remote_without_token(tmp_path, monkeypatch):
    monkeypatch.setenv("AEGIS_AUTH_MODE", "passkey")
    monkeypatch.setenv("AEGIS_DISPLAY_TOKEN", "display-secret")
    app = Flask(__name__)
    install_passkey_auth(app, data_dir=tmp_path / "auth")

    @app.route("/api/ui/stream")
    def stream():
        return "ok"

    client = app.test_client()
    denied = client.get(
        "/api/ui/stream?surface=display",
        headers={"Accept": "text/event-stream", "Host": "example.test"},
        environ_overrides={"REMOTE_ADDR": "203.0.113.20"},
    )
    allowed = client.get(
        "/api/ui/stream?surface=display&display_token=display-secret",
        headers={"Accept": "text/event-stream", "Host": "example.test"},
        environ_overrides={"REMOTE_ADDR": "203.0.113.20"},
    )

    assert denied.status_code == 401
    assert allowed.status_code == 200


def test_display_overview_requires_token_when_forwarded_host_is_external(monkeypatch):
    monkeypatch.setenv("AEGIS_UI_VERSION", "v2")
    monkeypatch.setenv("AEGIS_DISPLAY_TOKEN", "display-secret")
    app = Flask(__name__)
    init_ui_v2_routes(SimpleNamespace(app=app, _runtime=SimpleNamespace()))

    client = app.test_client()
    denied = client.get(
        "/display/overview",
        headers={"Host": "127.0.0.1:8090", "X-Forwarded-Host": "kawahara.pp.ua"},
        environ_overrides={"REMOTE_ADDR": "127.0.0.1"},
    )
    allowed = client.get(
        "/display/overview?display_token=display-secret",
        headers={"Host": "127.0.0.1:8090", "X-Forwarded-Host": "kawahara.pp.ua"},
        environ_overrides={"REMOTE_ADDR": "127.0.0.1"},
    )

    assert denied.status_code == 403
    assert allowed.status_code == 200


def test_passkey_session_allows_dashboard_and_fresh_risk_requires_csrf(tmp_path, monkeypatch):
    monkeypatch.setenv("AEGIS_AUTH_MODE", "passkey")
    app = Flask(__name__)
    install_passkey_auth(app, data_dir=tmp_path / "auth")

    store = app.extensions["aegis_passkey_store"]
    sessions = app.extensions["aegis_session_store"]
    from aegis_ai.auth.models import AuthUser

    user = AuthUser(user_id="u1", username="admin", display_name="Admin", created_at=1)
    store.add_user(user)
    session = sessions.create("u1")

    @app.route("/dashboard")
    def dashboard():
        return "ok"

    @app.route("/api/capabilities/demo/risk", methods=["POST"])
    def risk():
        return jsonify({"ok": True})

    client = app.test_client()
    client.set_cookie("aegis_session", session.session_id)
    assert client.get("/dashboard").status_code == 200
    assert client.post("/api/capabilities/demo/risk", json={}).status_code == 403
    assert client.post(
        "/api/capabilities/demo/risk",
        json={},
        headers={"X-CSRF-Token": session.csrf_token},
    ).status_code == 200


def test_production_token_mode_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("AEGIS_RUNTIME_MODE", "production")
    monkeypatch.setenv("AEGIS_AUTH_MODE", "token")
    monkeypatch.setenv("AEGIS_SESSION_SECRET", "secret")
    app = Flask(__name__)

    with pytest.raises(RuntimeError):
        install_passkey_auth(app, data_dir=tmp_path / "auth")
