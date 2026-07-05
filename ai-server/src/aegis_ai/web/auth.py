"""Token authentication helpers for dashboard-facing Flask apps."""

from __future__ import annotations

import hashlib
import hmac
import os
from urllib.parse import quote

from flask import jsonify, redirect, request, session


TOKEN_ENV = "AEGIS_DASHBOARD_ACCESS_TOKEN"
SESSION_KEY = "aegis_dashboard_authenticated"


def configured_dashboard_token() -> str:
    """Return the configured dashboard token, if token auth is enabled."""
    return os.getenv(TOKEN_ENV, "").strip()


def install_dashboard_token_auth(app, *, exempt_paths: set[str] | None = None) -> None:
    """Install optional token auth on a Flask dashboard or web chat app.

    Auth is disabled when AEGIS_DASHBOARD_ACCESS_TOKEN is unset. When enabled,
    browser pages can authenticate through /login and APIs/SSE can use either
    the Flask session cookie, Authorization: Bearer, or X-AEGIS-Dashboard-Token.
    """
    exempt = set(exempt_paths or {"/health"})
    exempt.add("/login")
    secret = os.getenv("AEGIS_DASHBOARD_SESSION_SECRET", "")
    token = configured_dashboard_token()
    if token and not secret:
        secret = hashlib.sha256(("aegis-dashboard-session:" + token).encode("utf-8")).hexdigest()
    if secret:
        app.secret_key = secret

    @app.before_request
    def _require_dashboard_token():
        token = configured_dashboard_token()
        if not token:
            return None
        path = request.path or "/"
        if path in exempt or path.startswith("/static/"):
            return None
        if session.get(SESSION_KEY) is True:
            return None
        if _request_has_valid_token(token):
            return None
        if path.startswith("/api/") or _wants_json():
            return jsonify({"error": "dashboard authentication required"}), 401
        return redirect(f"/login?next={quote(request.full_path or path)}")

    @app.route("/login", methods=["GET", "POST"])
    def dashboard_login():
        token = configured_dashboard_token()
        if not token:
            session[SESSION_KEY] = True
            return redirect(request.args.get("next") or "/")
        if request.method == "POST":
            supplied = (request.form.get("token") or "").strip()
            if hmac.compare_digest(supplied, token):
                session[SESSION_KEY] = True
                return redirect(request.args.get("next") or "/")
            return _login_page(error="Invalid token"), 401
        return _login_page(error="")


def _request_has_valid_token(expected: str) -> bool:
    header = request.headers.get("Authorization", "")
    supplied = ""
    if header.lower().startswith("bearer "):
        supplied = header[7:].strip()
    supplied = supplied or request.headers.get("X-AEGIS-Dashboard-Token", "").strip()
    return bool(supplied) and hmac.compare_digest(supplied, expected)


def _wants_json() -> bool:
    accept = request.accept_mimetypes
    return accept.best == "application/json" or request.is_json


def _login_page(*, error: str) -> str:
    error_html = f"<p class='error'>{error}</p>" if error else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>AEGIS Login</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #07070c;
      color: #f5f3ff;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    form {{
      width: min(360px, calc(100vw - 32px));
      padding: 24px;
      border: 1px solid #3b2a64;
      background: #11111c;
      border-radius: 8px;
      box-shadow: 0 0 32px rgba(139, 92, 246, .22);
    }}
    h1 {{ margin: 0 0 16px; font-size: 22px; }}
    input, button {{
      box-sizing: border-box;
      width: 100%;
      border-radius: 6px;
      border: 1px solid #3b2a64;
      padding: 12px;
      font: inherit;
    }}
    input {{ background: #090913; color: #f5f3ff; }}
    button {{ margin-top: 12px; background: #8b5cf6; color: white; border: 0; }}
    .error {{ color: #fca5a5; margin: 0 0 12px; }}
  </style>
</head>
<body>
  <form method="post">
    <h1>AEGIS Dashboard</h1>
    {error_html}
    <input name="token" type="password" autocomplete="current-password" placeholder="Access token" autofocus>
    <button type="submit">Login</button>
  </form>
</body>
</html>"""
