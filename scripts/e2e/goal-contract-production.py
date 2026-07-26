"""Production E2E probe for the MissionContract goal lifecycle.

Run this inside the AI Server container. It reuses an active dashboard session
without printing credentials, exercises the real chat route, and verifies the
persisted Task/GoalGraph plus the configured PC Server connection.
"""

from __future__ import annotations

import json
import os
import socket
import sys
import time
from pathlib import Path
from typing import Any

import requests

from aegis_ai.auth.passkey_store import PasskeyStore
from aegis_ai.auth.session_store import SessionStore

BASE_URL = "http://127.0.0.1:8090"
AUTH_PATH = Path("/app/data/auth/auth.json")
SESSION_COOKIE = "aegis_session"
CSRF_HEADER = "X-CSRF-Token"


def create_temporary_session() -> None:
    """Create a short-lived E2E session before the production process restarts."""
    store = PasskeyStore(AUTH_PATH.parent)
    users = store.list_users()
    if not users:
        raise RuntimeError("No dashboard user exists for the production E2E.")
    SessionStore(store, lifetime_ms=15 * 60 * 1000).create(
        users[0].user_id,
        user_agent="AEGIS production E2E",
        ip_address="127.0.0.1",
    )
    print("E2E_SESSION_CREATED")


def count_temporary_sessions() -> None:
    """Report active E2E sessions without exposing any session material."""
    data = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    now_ms = int(time.time() * 1000)
    active = sum(
        1
        for item in (data.get("sessions") or {}).values()
        if item.get("user_agent") == "AEGIS production E2E"
        and not item.get("revoked")
        and int(item.get("expires_at") or 0) > now_ms
    )
    print(f"ACTIVE_E2E_SESSIONS={active}")


def _active_session() -> tuple[str, str]:
    data = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    now_ms = int(time.time() * 1000)
    sessions = [
        item
        for item in (data.get("sessions") or {}).values()
        if not item.get("revoked") and int(item.get("expires_at") or 0) > now_ms
    ]
    if not sessions:
        raise RuntimeError("No active dashboard session is available for the production E2E.")
    session = max(sessions, key=lambda item: int(item.get("last_seen_at") or 0))
    return str(session["session_id"]), str(session["csrf_token"])


def _request_session() -> requests.Session:
    session_id, csrf = _active_session()
    client = requests.Session()
    client.cookies.set(SESSION_COOKIE, session_id)
    client.headers.update({CSRF_HEADER: csrf, "Accept": "application/json"})
    return client


def _pc_health() -> dict[str, Any]:
    host = os.getenv("PC_SERVER_HOST", "192.168.50.176")
    port = int(os.getenv("PC_SERVER_PORT", "50052"))
    with socket.create_connection((host, port), timeout=5) as connection:
        connection.sendall(b"health\n")
        response = connection.makefile("rb").readline()
    payload = json.loads(response.decode("utf-8"))
    if payload.get("status") != "ok":
        raise AssertionError(f"PC Server health failed: {payload}")
    return payload


def main() -> None:
    marker = f"AEGIS-GOAL-E2E-{int(time.time())}"
    user_goal = (
        f"Respond with the token {marker} and one short sentence confirming "
        "that no tool action was necessary."
    )
    client = _request_session()
    try:
        response = client.post(
            f"{BASE_URL}/api/chat/send",
            json={"text": user_goal},
            timeout=180,
        )
        response.raise_for_status()
        result = response.json()
        if marker not in str(result.get("response") or ""):
            raise AssertionError("Chat response did not preserve the requested E2E token.")
        if result.get("goal_status") != "achieved":
            raise AssertionError(f"Goal verification did not pass: {result.get('goal_reason')}")

        tasks_response = client.get(f"{BASE_URL}/api/tasks", timeout=30)
        tasks_response.raise_for_status()
        tasks_payload = tasks_response.json()
        tasks = (
            tasks_payload.get("tasks", tasks_payload)
            if isinstance(tasks_payload, dict)
            else tasks_payload
        )
        task = next((item for item in tasks if item.get("goal") == user_goal), None)
        if task is None:
            raise AssertionError("The chat Goal was not persisted as a Task.")
        graph = task.get("goal_graph") or {}
        checks = graph.get("verification") or []
        if task.get("status") != "completed" or not checks or checks[0].get("status") != "passed":
            raise AssertionError("The persisted Task/GoalGraph is not verified and completed.")

        pc = _pc_health()
        print(
            json.dumps(
                {
                    "status": "passed",
                    "goal_status": result["goal_status"],
                    "task_status": task["status"],
                    "verification_status": checks[0]["status"],
                    "mission_goal_id": graph.get("goal_id"),
                    "pc_server_status": pc.get("status"),
                    "pc_server_version": pc.get("version"),
                },
                ensure_ascii=False,
            )
        )
    finally:
        client.post(f"{BASE_URL}/auth/logout", timeout=15)


if __name__ == "__main__":
    if "--create-session" in sys.argv:
        create_temporary_session()
    elif "--count-sessions" in sys.argv:
        count_temporary_sessions()
    else:
        main()
