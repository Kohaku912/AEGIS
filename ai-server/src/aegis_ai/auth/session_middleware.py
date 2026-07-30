"""Flask middleware for passkey-only dashboard sessions."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import g, jsonify, redirect, request

from aegis_ai.auth.csrf import CSRF_HEADER, csrf_valid
from aegis_ai.auth.passkey_service import PasskeyConfig, PasskeyService
from aegis_ai.auth.passkey_store import PasskeyStore, now_ms
from aegis_ai.auth.routes import SESSION_COOKIE, init_auth_routes
from aegis_ai.auth.session_store import SessionStore

FRESH_WINDOW_MS = 15 * 60 * 1000


def install_passkey_auth(app: Any, *, data_dir: str | Path = "data/auth", exempt_paths: set[str] | None = None) -> None:
    """Install passkey-only auth routes and middleware."""

    production = os.getenv("AEGIS_RUNTIME_MODE", "development").strip().lower() == "production"
    auth_mode = os.getenv("AEGIS_AUTH_MODE", "passkey" if production else "passkey").strip().lower()
    if auth_mode != "passkey":
        if production:
            raise RuntimeError("AEGIS_AUTH_MODE=passkey is required in production.")
        return
    if production and not os.getenv("AEGIS_SESSION_SECRET", "").strip():
        raise RuntimeError("AEGIS_SESSION_SECRET is required when AEGIS_RUNTIME_MODE=production")
    app.secret_key = os.getenv("AEGIS_SESSION_SECRET", os.urandom(32).hex())

    store = PasskeyStore(data_dir)
    service = PasskeyService(store, PasskeyConfig.from_env())
    sessions = SessionStore(store)
    app.extensions["aegis_passkey_store"] = store
    app.extensions["aegis_passkey_service"] = service
    app.extensions["aegis_session_store"] = sessions
    init_auth_routes(app, service, sessions, secure_cookie=production)

    local_exempt = set(exempt_paths or {"/health"})

    @app.before_request
    def _load_and_require_auth():
        g.auth_session = None
        g.auth_user = None
        session_id = request.cookies.get(SESSION_COOKIE, "")
        if session_id:
            session = sessions.get(session_id)
            if session is not None:
                user = store.get_user(session.user_id)
                if user is not None:
                    g.auth_session = session
                    g.auth_user = user

        path = request.path or "/"
        if path in local_exempt:
            if production and not _is_local_request():
                return jsonify({"error": "health is local-only"}), 403
            return None
        if path.startswith("/static/"):
            return None
        if _csrf_required(path) and not _csrf_ok():
            return jsonify({"error": "CSRF token required"}), 403
        if path.startswith("/auth/") or path == "/login":
            if _fresh_required(path) and not _fresh_ok():
                return jsonify({"error": "fresh_passkey_required", "fresh_auth_url": "/auth/login"}), 403
            return None
        if _display_read_allowed(path):
            return None

        protected = path == "/" or path.startswith("/dashboard") or path.startswith("/api/") or _is_sse_or_ws()
        if not protected:
            return None
        if not store.has_users():
            if _wants_json():
                return jsonify({"error": "passkey bootstrap required", "setup_url": "/auth/login"}), 401
            return redirect("/auth/login")
        if g.auth_session is None:
            if _wants_json():
                return jsonify({"error": "authentication required", "login_url": "/auth/login"}), 401
            return redirect("/auth/login")
        if _fresh_required(path) and not _fresh_ok():
            return jsonify({"error": "fresh_passkey_required", "fresh_auth_url": "/auth/login"}), 403
        return None

    @app.after_request
    def _inject_auth_ui(response):
        if (request.path or "").startswith("/display/"):
            return response
        if not response.content_type.startswith("text/html") or response.direct_passthrough:
            return response
        try:
            body = response.get_data(as_text=True)
        except Exception:
            return response
        if "</body>" not in body:
            return response
        response.set_data(body.replace("</body>", _auth_header_script() + "</body>"))
        response.headers["Content-Length"] = str(len(response.get_data()))
        return response


def _csrf_required(path: str) -> bool:
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return False
    exempt = {
        "/auth/bootstrap/start",
        "/auth/passkey/register/options",
        "/auth/passkey/register/verify",
        "/auth/passkey/login/options",
        "/auth/passkey/login/verify",
    }
    return path not in exempt


def _csrf_ok() -> bool:
    session = getattr(g, "auth_session", None)
    if session is None:
        return False
    return csrf_valid(session.csrf_token, request.headers.get(CSRF_HEADER, ""))


def _fresh_required(path: str) -> bool:
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return False
    if path.startswith("/api/approvals/") and (
        path.endswith("/approve") or path.endswith("/modify-and-approve") or path.endswith("/cancel")
    ):
        return True
    if path.startswith("/api/llm/") or path.startswith("/api/settings"):
        return True
    if path.startswith("/api/memories/"):
        return True
    if path.startswith("/api/hooks/") or path.startswith("/api/delegations/"):
        return True
    if path == "/api/ui/control-actions":
        return True
    if path.startswith("/auth/passkeys/"):
        return True
    if path.startswith("/api/capabilities/use"):
        return True
    return False


def _fresh_ok() -> bool:
    session = getattr(g, "auth_session", None)
    return session is not None and now_ms() - session.last_auth_at <= FRESH_WINDOW_MS


def _is_sse_or_ws() -> bool:
    accept = request.headers.get("Accept", "")
    upgrade = request.headers.get("Upgrade", "")
    return "text/event-stream" in accept or upgrade.lower() == "websocket"


def _wants_json() -> bool:
    return request.path.startswith("/api/") or request.is_json or request.accept_mimetypes.best == "application/json"


def _is_local_request() -> bool:
    return (request.remote_addr or "") in {"127.0.0.1", "::1", "localhost"}


def _display_read_allowed(path: str) -> bool:
    if request.method != "GET":
        return False
    is_stream = path == "/api/ui/stream" and request.args.get("surface", "").strip().lower() == "display"
    is_overview = path == "/display/overview"
    if not is_stream and not is_overview:
        return False
    token = os.getenv("AEGIS_DISPLAY_TOKEN", "").strip() or os.getenv("AEGIS_DISPLAY_READ_TOKEN", "").strip()
    provided = request.args.get("display_token", "") or request.headers.get("X-AEGIS-Display-Token", "")
    if token and provided == token:
        return True
    host = _request_host_without_port()
    if host in {"127.0.0.1", "::1", "localhost"}:
        return True
    if request.headers.get("X-Forwarded-Host"):
        return False
    return _is_local_request()


def _request_host_without_port() -> str:
    host = (request.headers.get("X-Forwarded-Host") or request.host or "").strip().lower()
    if host.startswith("["):
        return host.split("]", 1)[0].lstrip("[")
    return host.split(":", 1)[0]


def _auth_header_script() -> str:
    return """
<script>
(function(){
  if(window.__aegisAuthInstalled) return; window.__aegisAuthInstalled = true;
  let csrfToken = '';
  const oldFetch = window.fetch.bind(window);
  window.fetch = async function(input, init){
    init = init || {};
    const method = (init.method || 'GET').toUpperCase();
    if(!['GET','HEAD','OPTIONS'].includes(method)){
      init.headers = new Headers(init.headers || {});
      if(csrfToken && !init.headers.has('X-CSRF-Token')) init.headers.set('X-CSRF-Token', csrfToken);
    }
    return oldFetch(input, init);
  };
  oldFetch('/auth/me').then(r=>r.json()).then(me=>{
    csrfToken = me.csrf_token || '';
    if(!me.authenticated) return;
    const bar = document.createElement('div');
    bar.style.cssText = 'position:sticky;top:0;z-index:9999;background:#111827;color:#e5e7eb;padding:6px 12px;font:12px system-ui;display:flex;gap:12px;align-items:center;justify-content:flex-end';
    bar.innerHTML = `<span>${me.user.display_name || me.user.username}</span><span>${me.fresh ? 'fresh' : 'reauth required'}</span><a style="color:#93c5fd" href="/dashboard/security/passkeys">passkeys</a><button id="aegisLogout" style="font:inherit">logout</button>`;
    document.body.prepend(bar);
    document.getElementById('aegisLogout').onclick = async()=>{await oldFetch('/auth/logout',{method:'POST',headers:{'X-CSRF-Token':csrfToken}}); location.href='/auth/login';};
  }).catch(()=>{});
})();
</script>
"""
