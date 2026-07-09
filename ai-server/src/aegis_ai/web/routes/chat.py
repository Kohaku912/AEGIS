"""Dashboard chat routes."""

from __future__ import annotations

import json
import logging
import queue
import time
import uuid
from typing import Any

from flask import Blueprint, Response, jsonify, request

from aegis_ai.web.chat_history import ChatHistoryStore
from aegis_ai.web.dashboard_routes import _build_chat_system_prompt, _call_llm_with_runtime

logger = logging.getLogger("aegis_ai.web.chat_routes")


def init_chat_routes(owner: Any) -> None:
    bp = Blueprint("dashboard_chat", __name__)

    def _run_chat(text: str, *, task_id: str | None = None, original_message: str = "") -> dict[str, Any]:
        from aegis_ai.web.chat_tools import call_llm_with_tools

        system_prompt, memory_meta, _ = _build_chat_system_prompt(text)
        memory_meta = dict(memory_meta)
        memory_meta.update({
            "origin_channel": "dashboard_chat",
            "conversation_id": f"chat_{int(time.time() * 1000)}",
            "original_message": original_message or text,
        })
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
            task = owner._runtime.task_manager.create_task(title=f"Chat: {text[:50]}", goal=text, source="chat")
            task_id = task.get("task_id", "") if isinstance(task, dict) else str(task)
            owner._runtime.task_manager.start_task(task_id)
            return task_id
        except Exception:
            logger.debug("Failed to create chat task", exc_info=True)
            return ""

    def _save_chat(user_msg: str, bot_msg: str, image: str = "") -> None:
        owner._append_chat_history(user_msg, bot_msg, image)

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
                        yield "data: {\"type\":\"heartbeat\"}\n\n"
            finally:
                owner._unregister_chat_client(client_id)

        return Response(generate(), mimetype="text/event-stream")

    @bp.route("/api/chat/send", methods=["POST"])
    def chat_send():
        data = request.get_json(silent=True) or {}
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "No text provided"}), 400
        task_id = _create_chat_task(text)
        try:
            result = _run_chat(text, task_id=task_id)
            if result.get("needs_user_input"):
                pending = result.get("pending_context", {})
                return jsonify({
                    "needs_user_input": True,
                    "question": result.get("question", ""),
                    "options": result.get("options", []),
                    "pending_context": {
                        "original_message": text,
                        "browser_task": pending.get("browser_task", ""),
                    },
                })
            response_text = result["response"]
            _save_chat(text, response_text)
            if task_id and not result.get("approval_needed"):
                owner._runtime.task_manager.complete_task(task_id, result_summary=response_text[:200])
            payload = {"response": response_text}
            if result.get("approval_needed"):
                payload["approval_needed"] = True
                payload["approval_id"] = result.get("approval_id", "")
            if result.get("tool_results"):
                payload["tool_results"] = [
                    {"function": tr.get("function", ""), "success": tr.get("success", False), "result": tr.get("result", "")[:500]}
                    for tr in result["tool_results"]
                ]
            return jsonify(payload)
        except Exception as exc:
            if task_id:
                owner._runtime.task_manager.fail_task(task_id, error=str(exc))
            response_text = f"Error: {exc}"
            _save_chat(text, response_text)
            return jsonify({"response": response_text})

    @bp.route("/api/chat/respond", methods=["POST"])
    def chat_respond():
        data = request.get_json(silent=True) or {}
        user_response = data.get("response", "").strip()
        pending_context = data.get("pending_context", {})
        if not user_response:
            return jsonify({"error": "No response provided"}), 400
        original_message = pending_context.get("original_message", "")
        browser_task = pending_context.get("browser_task", "")
        follow_up = f"{original_message}\n\nUser answered: {user_response}"
        if browser_task:
            follow_up = f"Previous task: {original_message}\n\nUser answered: {user_response}\nContinue the browser task: {browser_task}"
        try:
            result = _run_chat(follow_up, original_message=original_message or follow_up)
            response_text = result["response"]
            _save_chat(follow_up, response_text)
            payload = {"response": response_text}
            if result.get("approval_needed"):
                payload["approval_needed"] = True
                payload["approval_id"] = result.get("approval_id", "")
            return jsonify(payload)
        except Exception as exc:
            return jsonify({"response": f"Error: {exc}"})

    @bp.route("/api/chat/stream", methods=["POST"])
    def chat_stream():
        data = request.get_json(silent=True) or {}
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "No text provided"}), 400
        task_id = _create_chat_task(text)

        def generate():
            try:
                result = _run_chat(text, task_id=task_id)
                response_text = result["response"]
                for i in range(0, len(response_text), 10):
                    yield f"data: {json.dumps({'type': 'text', 'content': response_text[i:i + 10]})}\n\n"
                _save_chat(text, response_text)
                if task_id and not result.get("approval_needed"):
                    owner._runtime.task_manager.complete_task(task_id, result_summary=response_text[:200])
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            except Exception as exc:
                if task_id:
                    owner._runtime.task_manager.fail_task(task_id, error=str(exc))
                yield f"data: {json.dumps({'type': 'error', 'content': str(exc)})}\n\n"

        return Response(generate(), mimetype="text/event-stream")

    owner.app.register_blueprint(bp)
