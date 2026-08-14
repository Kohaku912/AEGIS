"""Dashboard chat routes."""

from __future__ import annotations

import json
import logging
import queue
import threading
import time
import uuid
from typing import Any

from flask import Blueprint, Response, g, jsonify, request

from aegis_ai.web.chat_history import ChatHistoryStore
from aegis_ai.web.dashboard_routes import _build_chat_system_prompt, _call_llm_with_runtime

logger = logging.getLogger("aegis_ai.web.chat_routes")


def init_chat_routes(owner: Any) -> None:
    bp = Blueprint("dashboard_chat", __name__)
    request_lock = threading.RLock()
    request_cache: dict[str, dict[str, Any]] = {}

    def _request_key(request_id: str) -> str:
        user = getattr(g, "auth_user", None)
        user_id = str(getattr(user, "user_id", "") or request.remote_addr or "local")
        return f"{user_id}:{request_id}"

    def _chat_error(exc: Exception, request_id: str, status: int = 500):
        logger.exception("Dashboard chat request failed")
        return jsonify({
            "error": "chat_execution_failed",
            "message": str(exc),
            "request_id": request_id,
            "retryable": status >= 500,
        }), status

    def _run_chat(text: str, *, task_id: str | None = None, original_message: str = "") -> dict[str, Any]:
        from aegis_ai.web.chat_tools import call_llm_with_tools

        system_prompt, memory_meta, _ = _build_chat_system_prompt(text)
        memory_meta = dict(memory_meta)
        memory_meta.update(
            {
                "origin_channel": "dashboard_chat",
                "conversation_id": f"chat_{int(time.time() * 1000)}",
                "original_message": original_message or text,
            }
        )
        if task_id:
            memory_meta["chat_task_id"] = task_id
        catalog = owner._runtime.tool_broker._catalog
        return _call_llm_with_runtime(
            call_llm_with_tools,
            owner._runtime.llm_gateway,
            text,
            system_prompt,
            catalog=catalog,
            context_meta=memory_meta,
            runtime=owner._runtime,
        )

    def _create_chat_task(text: str) -> str:
        if not hasattr(owner._runtime, "task_manager") or not owner._runtime.task_manager:
            return ""
        try:
            goal_service = getattr(owner._runtime, "goal_service", None)
            if goal_service is not None:
                task = goal_service.create_chat_task(text, source="chat")
            else:
                task = owner._runtime.task_manager.create_task(
                    title=f"Chat: {text[:50]}",
                    goal=text,
                    source="chat",
                )
                owner._runtime.task_manager.start_task(task["task_id"])
            task_id = task.get("task_id", "") if isinstance(task, dict) else str(task)
            return task_id
        except Exception:
            logger.debug("Failed to create chat task", exc_info=True)
            return ""

    def _finalize_chat_task(
        task_id: str,
        user_goal: str,
        result: dict[str, Any],
    ) -> dict[str, str]:
        if not task_id:
            return {}
        goal_service = getattr(owner._runtime, "goal_service", None)
        if goal_service is None:
            owner._runtime.task_manager.complete_task(
                task_id,
                result_summary=str(result.get("response") or "")[:200],
            )
            return {"goal_status": "achieved"}
        evaluation = goal_service.finalize_chat_task(
            task_id,
            user_goal=user_goal,
            response=str(result.get("response") or ""),
            tool_results=list(result.get("tool_results") or []),
        )
        return {
            "goal_status": evaluation.status,
            "goal_reason": evaluation.reason,
        }

    def _save_chat(user_msg: str, bot_msg: str, image: str = "") -> None:
        owner._append_chat_history(user_msg, bot_msg, image)
        try:
            mm = getattr(owner._runtime, "memory_manager", None)
            if mm is not None and hasattr(mm, "encode_conversation"):
                mm.encode_conversation(user_msg, bot_msg, source="dashboard_chat")
            else:
                advanced = None
                if mm is not None and hasattr(mm, "get_backend"):
                    advanced = mm.get_backend("advanced")
                if advanced is not None and hasattr(advanced, "add_conversation"):
                    advanced.add_conversation(user_msg, bot_msg)
        except Exception:
            logger.debug("Chat memory encode failed", exc_info=True)
        try:
            sleep_manager = getattr(owner._runtime, "sleep_manager", None)
            if sleep_manager is not None and hasattr(sleep_manager, "update_activity"):
                sleep_manager.update_activity()
        except Exception:
            logger.debug("Sleep activity update failed", exc_info=True)

    @bp.route("/api/chat/history")
    def chat_history():
        return jsonify(ChatHistoryStore(owner._chat_history_path).load())

    @bp.route("/api/chat/clear", methods=["POST"])
    def chat_clear():
        ChatHistoryStore(owner._chat_history_path).clear()
        return jsonify({"status": "cleared"})

    @bp.route("/api/chat/events")
    def chat_events():
        client_id = f"chat_{uuid.uuid4().hex[:8]}"

        def generate():
            q = owner._register_chat_client(client_id)
            try:
                while True:
                    try:
                        data = q.get(timeout=15)
                        yield f"data: {data}\n\n"
                    except queue.Empty:
                        yield 'data: {"type":"heartbeat"}\n\n'
            finally:
                owner._unregister_chat_client(client_id)

        return Response(generate(), mimetype="text/event-stream")

    @bp.route("/api/chat/send", methods=["POST"])
    def chat_send():
        data = request.get_json(silent=True) or {}
        text = str(data.get("text") or data.get("message") or "").strip()
        request_id = str(data.get("request_id") or uuid.uuid4().hex).strip()[:128]
        if not text:
            return jsonify({
                "error": "invalid_request",
                "message": "No text provided",
                "request_id": request_id,
                "retryable": False,
            }), 400
        key = _request_key(request_id)
        now = time.time()
        with request_lock:
            for cached_key, cached in list(request_cache.items()):
                if now - float(cached.get("created_at") or now) > 900:
                    request_cache.pop(cached_key, None)
            cached = request_cache.get(key)
            if cached is not None:
                if cached.get("status") == "completed":
                    return jsonify(cached["payload"])
                return jsonify({
                    "error": "request_in_progress",
                    "message": "The same chat request is already being processed.",
                    "request_id": request_id,
                    "retryable": True,
                }), 409
            request_cache[key] = {"status": "processing", "created_at": now}
        task_id = _create_chat_task(text)
        try:
            result = _run_chat(text, task_id=task_id)
            if result.get("needs_user_input"):
                pending = result.get("pending_context", {})
                if task_id:
                    owner._runtime.task_manager.pause_task(task_id)
                payload = {
                        "needs_user_input": True,
                        "question": result.get("question", ""),
                        "options": result.get("options", []),
                        "pending_context": {
                            "original_message": text,
                            "browser_task": pending.get("browser_task", ""),
                            "task_id": task_id,
                        },
                        "request_id": request_id,
                    }
                with request_lock:
                    request_cache[key] = {"status": "completed", "created_at": now, "payload": payload}
                return jsonify(payload)
            response_text = result["response"]
            _save_chat(text, response_text)
            if task_id and not result.get("approval_needed"):
                goal_meta = _finalize_chat_task(task_id, text, result)
            else:
                goal_meta = {}
            payload = {"response": response_text, "request_id": request_id, **goal_meta}
            if result.get("approval_needed"):
                payload["approval_needed"] = True
                payload["approval_id"] = result.get("approval_id", "")
            if result.get("tool_results"):
                payload["tool_results"] = [
                    {
                        "function": tr.get("function", ""),
                        "success": tr.get("success", False),
                        "result": tr.get("result", "")[:500],
                    }
                    for tr in result["tool_results"]
                ]
            with request_lock:
                request_cache[key] = {"status": "completed", "created_at": now, "payload": payload}
            return jsonify(payload)
        except Exception as exc:
            if task_id:
                owner._runtime.task_manager.fail_task(task_id, error=str(exc))
            with request_lock:
                request_cache.pop(key, None)
            return _chat_error(exc, request_id)

    @bp.route("/api/chat/respond", methods=["POST"])
    def chat_respond():
        data = request.get_json(silent=True) or {}
        user_response = data.get("response", "").strip()
        pending_context = data.get("pending_context", {})
        if not user_response:
            return jsonify({"error": "No response provided"}), 400
        original_message = pending_context.get("original_message", "")
        browser_task = pending_context.get("browser_task", "")
        task_id = pending_context.get("task_id", "")
        follow_up = f"{original_message}\n\nUser answered: {user_response}"
        if browser_task:
            follow_up = (
                f"Previous task: {original_message}\n\n"
                f"User answered: {user_response}\n"
                f"Continue the browser task: {browser_task}"
            )
        try:
            if task_id:
                owner._runtime.task_manager.start_task(task_id)
            result = _run_chat(
                follow_up,
                task_id=task_id,
                original_message=original_message or follow_up,
            )
            response_text = result["response"]
            _save_chat(follow_up, response_text)
            goal_meta = {}
            if task_id and not result.get("approval_needed") and not result.get("needs_user_input"):
                goal_meta = _finalize_chat_task(
                    task_id,
                    original_message or follow_up,
                    result,
                )
            payload = {"response": response_text, **goal_meta}
            if result.get("approval_needed"):
                payload["approval_needed"] = True
                payload["approval_id"] = result.get("approval_id", "")
            return jsonify(payload)
        except Exception as exc:
            return _chat_error(exc, str(data.get("request_id") or ""))

    owner.app.register_blueprint(bp)
