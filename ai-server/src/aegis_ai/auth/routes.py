"""Flask routes for AEGIS passkey authentication."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, Response, g, jsonify, make_response, redirect, request

from aegis_ai.auth.passkey_service import PasskeyService
from aegis_ai.auth.session_store import SessionStore


SESSION_COOKIE = "aegis_session"


def init_auth_routes(app: Any, service: PasskeyService, sessions: SessionStore, *, secure_cookie: bool) -> None:
    bp = Blueprint("aegis_auth", __name__)

    def _current_session():
        return getattr(g, "auth_session", None)

    def _current_user():
        return getattr(g, "auth_user", None)

    def _session_required():
        if _current_session() is None or _current_user() is None:
            return jsonify({"error": "authentication required"}), 401
        return None

    @bp.route("/auth/login")
    def login_page():
        return Response(_login_html(), mimetype="text/html")

    @bp.route("/login")
    def legacy_login_redirect():
        return redirect("/auth/login")

    @bp.route("/dashboard/security/passkeys")
    def passkeys_page():
        return Response(_passkeys_html(), mimetype="text/html")

    @bp.route("/auth/bootstrap/start", methods=["POST"])
    def bootstrap_start():
        data = request.get_json(silent=True) or {}
        token = str(data.get("bootstrap_token") or data.get("token") or "").strip()
        return jsonify({**service.bootstrap_status(), "token_accepted": service.bootstrap_allowed(token)})

    @bp.route("/auth/passkey/register/options", methods=["POST"])
    def register_options():
        data = request.get_json(silent=True) or {}
        session = _current_session()
        user = _current_user()
        try:
            return jsonify(service.registration_options(
                username=str(data.get("username") or "admin"),
                display_name=str(data.get("display_name") or data.get("username") or "Admin"),
                bootstrap_token=str(data.get("bootstrap_token") or ""),
                session_user_id=getattr(user, "user_id", "") if session else "",
            ))
        except PermissionError as exc:
            return jsonify({"error": str(exc)}), 403
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.route("/auth/passkey/register/verify", methods=["POST"])
    def register_verify():
        data = request.get_json(silent=True) or {}
        try:
            result = service.verify_registration(
                challenge_id=str(data.get("challenge_id") or ""),
                credential=data.get("credential") or {},
                origin=_origin(),
            )
            return jsonify(result)
        except PermissionError as exc:
            return jsonify({"error": str(exc)}), 403
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.route("/auth/passkey/login/options", methods=["POST"])
    def login_options():
        try:
            return jsonify(service.authentication_options())
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.route("/auth/passkey/login/verify", methods=["POST"])
    def login_verify():
        data = request.get_json(silent=True) or {}
        try:
            result = service.verify_authentication(
                challenge_id=str(data.get("challenge_id") or ""),
                credential=data.get("credential") or {},
                origin=_origin(),
            )
            old = _current_session()
            if old is not None:
                sessions.revoke(old.session_id)
            session = sessions.create(
                result["user"]["user_id"],
                user_agent=request.headers.get("User-Agent", ""),
                ip_address=request.remote_addr or "",
            )
            user = service.store.get_user(session.user_id)
            payload = SessionStore.to_public_dict(session, user, fresh_window_ms=15 * 60 * 1000)
            response = make_response(jsonify(payload))
            _set_session_cookie(response, session.session_id, secure_cookie)
            return response
        except PermissionError as exc:
            return jsonify({"error": str(exc)}), 403
        except Exception as exc:
            return jsonify({"error": str(exc)}), 400

    @bp.route("/auth/logout", methods=["POST"])
    def logout():
        session = _current_session()
        if session is not None:
            sessions.revoke(session.session_id)
        response = make_response(jsonify({"ok": True}))
        response.delete_cookie(SESSION_COOKIE, path="/", samesite="Lax")
        return response

    @bp.route("/auth/me")
    def me():
        session = _current_session()
        user = _current_user()
        if session is None or user is None:
            return jsonify({
                "authenticated": False,
                "bootstrap": service.bootstrap_status(),
            })
        return jsonify({
            **SessionStore.to_public_dict(session, user, fresh_window_ms=15 * 60 * 1000),
            "bootstrap": service.bootstrap_status(),
        })

    @bp.route("/auth/passkeys")
    def list_passkeys():
        required = _session_required()
        if required:
            return required
        return jsonify({"passkeys": service.list_passkeys(_current_user().user_id)})

    @bp.route("/auth/passkeys/<credential_id>", methods=["DELETE"])
    def delete_passkey(credential_id: str):
        required = _session_required()
        if required:
            return required
        try:
            return jsonify({"deleted": service.delete_passkey(credential_id, _current_user().user_id)})
        except PermissionError as exc:
            return jsonify({"error": str(exc)}), 403

    @bp.route("/auth/passkeys/<credential_id>/rename", methods=["POST"])
    def rename_passkey(credential_id: str):
        required = _session_required()
        if required:
            return required
        data = request.get_json(silent=True) or {}
        try:
            return jsonify({"passkey": service.rename_passkey(
                credential_id,
                _current_user().user_id,
                str(data.get("nickname") or ""),
            )})
        except KeyError:
            return jsonify({"error": "Not found"}), 404

    app.register_blueprint(bp)


def _set_session_cookie(response: Any, session_id: str, secure: bool) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        session_id,
        httponly=True,
        secure=secure,
        samesite="Lax",
        path="/",
    )


def _origin() -> str:
    origin = request.headers.get("Origin", "").strip()
    if origin:
        return origin
    return f"{request.scheme}://{request.host}"


def _login_html() -> str:
    return """<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>AEGIS Passkey Login</title>
  <style>
    body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0b0d12;color:#f8fafc;font-family:system-ui,sans-serif}
    main{width:min(420px,calc(100vw - 32px));display:grid;gap:14px}
    h1{font-size:24px;margin:0}
    button,input{font:inherit;border-radius:8px;border:1px solid #334155;padding:12px;background:#111827;color:#f8fafc}
    button{background:#2563eb;border:0;cursor:pointer}
    .muted{color:#94a3b8;font-size:13px}.error{color:#fecaca}.row{display:grid;gap:8px}
  </style>
</head>
<body>
<main>
  <h1>AEGIS Dashboard</h1>
  <button id="login">パスキーでログイン</button>
  <section id="setup" hidden class="row">
    <p class="muted">初回セットアップ: admin passkeyを登録します。</p>
    <input id="bootstrap" type="password" placeholder="Bootstrap token">
    <input id="username" autocomplete="username webauthn" value="admin" placeholder="Username">
    <button id="register">この端末のパスキーを登録</button>
  </section>
  <p id="status" class="muted"></p>
</main>
<script>
const $ = id => document.getElementById(id);
function b64ToBuf(v){v=v.replace(/-/g,'+').replace(/_/g,'/'); v += '='.repeat((4-v.length%4)%4); return Uint8Array.from(atob(v), c=>c.charCodeAt(0));}
function bufToB64(b){return btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=+$/,'');}
function publicKeyCreateOptions(o){o={...o}; delete o.challenge_id; o.challenge=b64ToBuf(o.challenge); o.user.id=b64ToBuf(o.user.id); if(o.excludeCredentials){o.excludeCredentials=o.excludeCredentials.map(c=>({...c,id:b64ToBuf(c.id)}));} return o;}
function publicKeyGetOptions(o){o={...o}; delete o.challenge_id; o.challenge=b64ToBuf(o.challenge); if(o.allowCredentials){o.allowCredentials=o.allowCredentials.map(c=>({...c,id:b64ToBuf(c.id)}));} return o;}
function regCredential(c){return {id:c.id,rawId:bufToB64(c.rawId),type:c.type,response:{clientDataJSON:bufToB64(c.response.clientDataJSON),attestationObject:bufToB64(c.response.attestationObject)}}}
function authCredential(c){return {id:c.id,rawId:bufToB64(c.rawId),type:c.type,response:{clientDataJSON:bufToB64(c.response.clientDataJSON),authenticatorData:bufToB64(c.response.authenticatorData),signature:bufToB64(c.response.signature),userHandle:c.response.userHandle?bufToB64(c.response.userHandle):null}}}
async function post(url, body){const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body||{})}); const j=await r.json(); if(!r.ok) throw new Error(j.error||r.statusText); return j;}
function returnPath(){const value=new URLSearchParams(location.search).get('next')||'/dashboard'; return value.startsWith('/')&&!value.startsWith('//')?value:'/dashboard';}
async function login(){ $('status').textContent='パスキーを確認しています...'; const o=await post('/auth/passkey/login/options'); const cred=await navigator.credentials.get({publicKey:publicKeyGetOptions(o)}); await post('/auth/passkey/login/verify',{challenge_id:o.challenge_id,credential:authCredential(cred)}); location.href=returnPath();}
async function register(){ $('status').textContent='パスキーを登録しています...'; const o=await post('/auth/passkey/register/options',{username:$('username').value,display_name:$('username').value,bootstrap_token:$('bootstrap').value}); const cred=await navigator.credentials.create({publicKey:publicKeyCreateOptions(o)}); await post('/auth/passkey/register/verify',{challenge_id:o.challenge_id,credential:regCredential(cred)}); await login();}
async function init(){const me=await fetch('/auth/me').then(r=>r.json()); $('setup').hidden=!!me.bootstrap?.has_users; $('status').textContent='「パスキーでログイン」を押して認証してください。';}
$('login').onclick=()=>login().catch(e=>$('status').innerHTML='<span class=error>'+e.message+'</span>');
$('register').onclick=()=>register().catch(e=>$('status').innerHTML='<span class=error>'+e.message+'</span>');
init();
</script>
</body>
</html>"""


def _passkeys_html() -> str:
    return """<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AEGIS Passkeys</title><style>body{font-family:system-ui,sans-serif;margin:24px;background:#0b0d12;color:#f8fafc}button,input{font:inherit;padding:8px;border-radius:6px}li{margin:12px 0}</style></head>
<body><h1>Passkeys</h1><p><a href="/dashboard">Dashboard</a></p><ul id="list"></ul><p id="status"></p>
<script>
let csrf='';
async function refresh(){const me=await fetch('/auth/me').then(r=>r.json()); csrf=me.csrf_token||''; const data=await fetch('/auth/passkeys').then(r=>r.json()); list.innerHTML=(data.passkeys||[]).map(p=>`<li><input value="${p.nickname||'Passkey'}" id="n_${p.credential_id}"> <button onclick="rename('${p.credential_id}')">rename</button> <button onclick="del('${p.credential_id}')">delete</button><br><small>${p.credential_id}</small></li>`).join('');}
async function rename(id){await fetch(`/auth/passkeys/${id}/rename`,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify({nickname:document.getElementById('n_'+id).value})}); refresh();}
async function del(id){const r=await fetch(`/auth/passkeys/${id}`,{method:'DELETE',headers:{'X-CSRF-Token':csrf}}); if(!r.ok) status.textContent=(await r.json()).error; refresh();}
refresh();
</script></body></html>"""
