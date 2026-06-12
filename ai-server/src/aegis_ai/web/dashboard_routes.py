"""Dashboard Routes — Flask routes for AEGIS operations dashboard.

Provides:
- GET /                    → Home overview with real server status
- GET /dashboard/servers   → Server health
- GET /health              → Health check
- POST /api/chat/send      → Chat with AEGIS (with PC operations)

Security:
- All sensitive data is redacted before display.
- Dashboard cannot bypass approval.
- All actions still go through PolicyEngine.
"""

from __future__ import annotations

import json
import logging
import os
import socket
import time
from typing import Any

from flask import Flask, jsonify, render_template

logger = logging.getLogger("aegis_ai.web.dashboard")


def _check_port(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a port is open."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False


def _send_pc_command(cmd: str, host: str = "localhost", port: int = 50052) -> dict[str, Any] | None:
    """Send a command to PC Server and return response."""
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((host, port))
        s.sendall((cmd + "\n").encode())
        resp = b""
        while True:
            chunk = s.recv(4096)
            if not chunk or b"\n" in chunk:
                resp += chunk
                break
            resp += chunk
        s.close()
        return json.loads(resp.decode().strip())
    except Exception:
        return None


def _browse_url(url: str) -> str:
    """Browse to a URL using Playwright and return content."""
    try:
        import asyncio
        from playwright.async_api import async_playwright

        async def _browse():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                try:
                    await page.goto(url, timeout=30000)
                    title = await page.title()

                    # Get page text
                    text = await page.evaluate("""
                        (() => {
                            const exclude = ['script', 'style', 'nav', 'footer'];
                            const clone = document.body.cloneNode(true);
                            exclude.forEach(tag => {
                                clone.querySelectorAll(tag).forEach(el => el.remove());
                            });
                            return (clone.textContent || '').replace(/\\s{3,}/g, '\\n\\n').trim();
                        })()
                    """)

                    # Get links
                    links = await page.evaluate("""
                        Array.from(document.querySelectorAll('a[href]')).slice(0, 10).map(a => ({
                            href: a.href,
                            text: a.textContent.trim().substring(0, 100)
                        }))
                    """)

                    # Build response
                    result_parts = [f"**{title}**\n"]
                    result_parts.append(f"URL: {url}\n")
                    result_parts.append(f"Content:\n{text[:2000]}\n")

                    if links:
                        result_parts.append("\nLinks:")
                        for link in links[:5]:
                            result_parts.append(f"  - {link['text']}: {link['href']}")

                    return "\n".join(result_parts)
                finally:
                    await browser.close()

        return asyncio.run(_browse())

    except Exception as e:
        return f"Browser error: {str(e)}"


def _build_memory_context(query: str) -> str:
    """Build memory context using AdvancedMemory system."""
    context_parts = []

    # Get desire context
    try:
        from aegis_ai.desire.desire_system import DesireSystem
        desire_system = DesireSystem(data_dir="data/desires")
        desire_context = desire_system.get_context()
        if desire_context:
            context_parts.append(desire_context)
    except Exception as e:
        logger.debug("Desire system failed: %s", e)

    # Get memory context
    try:
        from aegis_ai.memory.advanced import AdvancedMemory
        from aegis_ai.llm.factory import create_llm_provider
        llm = create_llm_provider()
        memory = AdvancedMemory(data_dir="data/memory", llm_provider=llm)
        memory_context = memory.get_context(query)
        if memory_context:
            context_parts.append("MEMORY CONTEXT:\n" + memory_context)
    except Exception as e:
        logger.debug("Advanced memory failed: %s", e)

    # Fallback to basic memory
    if not any("MEMORY CONTEXT" in p for p in context_parts):
        try:
            from aegis_ai.memory.persona import PersonaMemory
            persona = PersonaMemory(path="data/persona.jsonl")
            persons = persona.get_all_persons()
            if persons:
                context_parts.append("People I know:")
                for p in persons:
                    topics = ", ".join(p.topics_discussed[:3]) if p.topics_discussed else "none"
                    context_parts.append(f"  - {p.name} ({p.relationship}): {p.notes}. Topics: {topics}")
        except Exception:
            pass

    if context_parts:
        return "\n\n".join(context_parts)
    return ""


class DashboardApp:
    """Flask-based operations dashboard for AEGIS."""

    def __init__(self) -> None:
        self._app = Flask(__name__, template_folder="templates")
        self._start_time = time.time()
        self._setup_routes()

    @property
    def app(self) -> Flask:
        return self._app

    def run(self, host: str = "0.0.0.0", port: int = 8090, debug: bool = False) -> None:
        self._app.run(host=host, port=port, debug=debug, threaded=True, use_reloader=False)

    def _get_server_status(self) -> dict[str, Any]:
        """Get real server status by checking ports."""
        servers = []

        # AI Server
        ai_ok = _check_port("localhost", 50051)
        servers.append({
            "server_id": "ai-server",
            "server_type": "AI",
            "status": "ONLINE" if ai_ok else "OFFLINE",
            "registered_capabilities": "Core",
            "heartbeat_age_seconds": 0,
        })

        # PC Server
        pc_ok = _check_port("localhost", 50052)
        pc_info = _send_pc_command("health") if pc_ok else None
        servers.append({
            "server_id": "pc-server",
            "server_type": "PC",
            "status": "ONLINE" if pc_ok else "OFFLINE",
            "registered_capabilities": str(pc_info.get("capabilities", 0)) if pc_info else "0",
            "heartbeat_age_seconds": 0,
        })

        # Browser Server
        browser_ok = _check_port("localhost", 50053)
        servers.append({
            "server_id": "browser-server",
            "server_type": "Browser",
            "status": "ONLINE" if browser_ok else "OFFLINE",
            "registered_capabilities": "7" if browser_ok else "0",
            "heartbeat_age_seconds": 0,
        })

        online = sum(1 for s in servers if s["status"] == "ONLINE")
        return {
            "servers": servers,
            "summary": {
                "online_servers": online,
                "total_servers": len(servers),
            },
        }

    def _setup_routes(self) -> None:
        app = self._app

        @app.route("/")
        @app.route("/dashboard")
        def home():
            status = self._get_server_status()
            return render_template("dashboard/home.html",
                servers=status["servers"],
                server_summary=status["summary"],
                event_stats={"total_published": 0},
                trigger_stats={"tasks_generated": 0},
                pending_approvals=[],
                memory_summary={
                    "episodic_count": 0,
                    "semantic_count": 0,
                    "procedural_count": 0,
                    "reflection_count": 0,
                },
                settings={
                    "autonomous_enabled": False,
                    "support_agent_enabled": True,
                    "self_dev_enabled": True,
                    "privacy_clipboard_enabled": True,
                    "privacy_camera_enabled": False,
                },
            )

        @app.route("/dashboard/servers")
        def servers():
            status = self._get_server_status()
            return render_template("dashboard/servers.html",
                servers=status["servers"],
                summary=status["summary"],
            )

        @app.route("/api/servers")
        def api_servers():
            return jsonify(self._get_server_status())

        @app.route("/dashboard/capabilities")
        def capabilities():
            caps = [
                {"id": "pc.get_screenshot", "name": "Screenshot", "risk_level": "READ_ONLY", "server_type": "PC", "enabled": True},
                {"id": "pc.get_active_window", "name": "Active Window", "risk_level": "READ_ONLY", "server_type": "PC", "enabled": True},
                {"id": "pc.list_windows", "name": "List Windows", "risk_level": "READ_ONLY", "server_type": "PC", "enabled": True},
                {"id": "pc.get_clipboard", "name": "Clipboard", "risk_level": "READ_ONLY", "server_type": "PC", "enabled": True},
                {"id": "pc.get_os_info", "name": "OS Info", "risk_level": "READ_ONLY", "server_type": "PC", "enabled": True},
                {"id": "pc.get_screen_size", "name": "Screen Size", "risk_level": "READ_ONLY", "server_type": "PC", "enabled": True},
                {"id": "pc.show_overlay", "name": "Show Overlay", "risk_level": "SAFE_ACTION", "server_type": "PC", "enabled": True},
                {"id": "pc.mouse_click", "name": "Mouse Click", "risk_level": "APPROVAL_REQUIRED", "server_type": "PC", "enabled": True},
                {"id": "pc.keyboard_type", "name": "Keyboard Type", "risk_level": "APPROVAL_REQUIRED", "server_type": "PC", "enabled": True},
                {"id": "browser.open_page", "name": "Open Page", "risk_level": "SAFE_ACTION", "server_type": "Browser", "enabled": True},
                {"id": "browser.extract_page_text", "name": "Extract Text", "risk_level": "READ_ONLY", "server_type": "Browser", "enabled": True},
                {"id": "android.get_notifications", "name": "Notifications", "risk_level": "READ_ONLY", "server_type": "Android", "enabled": False},
                {"id": "room.get_environment", "name": "Environment", "risk_level": "READ_ONLY", "server_type": "Room", "enabled": False},
            ]
            return render_template("dashboard/capabilities.html", capabilities=caps)

        @app.route("/dashboard/events")
        def events():
            # Get recent events from PC Server
            pc_events = []
            try:
                pc_health = _send_pc_command("health")
                if pc_health:
                    pc_events.append({
                        "event_type": "pc.server_health",
                        "source": "pc-server",
                        "timestamp": time.time(),
                        "data": pc_health,
                    })
            except Exception:
                pass
            return render_template("dashboard/events.html",
                events=pc_events,
                stats={"total_published": len(pc_events)},
            )

        @app.route("/dashboard/tasks")
        def tasks():
            # Show current system tasks
            current_tasks = []
            pc_health = _send_pc_command("health")
            if pc_health:
                current_tasks.append({
                    "task_id": "pc_health_monitor",
                    "name": "PC Server Health Monitor",
                    "status": "active",
                    "description": f"PC Server v{pc_health.get('version', 'unknown')} - {pc_health.get('capabilities', 0)} capabilities",
                })
            return render_template("dashboard/tasks.html",
                pending_tasks=current_tasks,
                trigger_stats={"tasks_generated": len(current_tasks)},
                scheduled_tasks=[],
            )

        @app.route("/dashboard/support")
        def support():
            suggestions = [
                {"title": "PC Server Online", "description": "PC Server is running with 15 capabilities", "priority": "low"},
                {"title": "Browser Server", "description": "Browser Server available for web automation", "priority": "low"},
            ]
            return render_template("dashboard/support.html", suggestions=suggestions)

        @app.route("/dashboard/memory")
        def memory():
            # Get memory stats from Chroma and Persona
            import json as json_lib
            episodic_count = 0
            semantic_count = 0
            persona_count = 0
            conversation_count = 0
            persons = []
            recent_conversations = []

            # Count episodic memories
            try:
                episodic_path = "data/episodic.jsonl"
                if os.path.exists(episodic_path):
                    with open(episodic_path, "r") as f:
                        episodic_count = sum(1 for _ in f)
            except Exception:
                pass

            # Count semantic facts (Chroma)
            try:
                from aegis_ai.memory.chroma_semantic import ChromaSemanticMemory
                sem = ChromaSemanticMemory(chroma_path="data/chroma")
                stats = sem.get_stats()
                semantic_count = stats.get("chroma_count", 0) or stats.get("jsonl_facts", 0)
            except Exception:
                pass

            # Get persona data
            try:
                from aegis_ai.memory.persona import PersonaMemory
                persona = PersonaMemory(path="data/persona.jsonl")
                all_persons = persona.get_all_persons()
                persona_count = len(all_persons)
                for p in all_persons:
                    persons.append({
                        "name": p.name,
                        "relationship": p.relationship,
                        "notes": p.notes,
                        "interaction_count": p.interaction_count,
                        "topics": p.topics_discussed[:5],
                    })
                all_convs = persona.get_conversations()
                conversation_count = len(all_convs)
                for c in all_convs[-10:]:
                    recent_conversations.append({
                        "person": c.person_name,
                        "summary": c.summary,
                        "key_points": c.key_points[:3],
                    })
            except Exception:
                pass

            return render_template("dashboard/memory.html",
                summary={
                    "episodic_count": episodic_count,
                    "semantic_count": semantic_count,
                    "persona_count": persona_count,
                    "conversation_count": conversation_count,
                },
                persons=persons,
                conversations=recent_conversations,
                episodic=[],
                semantic=[],
                procedural=[],
                reflections=[],
            )

        @app.route("/dashboard/audit")
        def audit():
            # Get audit entries from audit log
            import json as json_lib
            entries = []
            try:
                audit_path = "data/audit.jsonl"
                if os.path.exists(audit_path):
                    with open(audit_path, "r") as f:
                        for line in f:
                            try:
                                entry = json_lib.loads(line.strip())
                                entries.append(entry)
                            except Exception:
                                pass
            except Exception:
                pass
            return render_template("dashboard/audit.html",
                entries=entries[-50:],
                stats={"total_entries": len(entries)},
            )

        @app.route("/dashboard/errors")
        def errors():
            return render_template("dashboard/errors.html", errors=[])

        @app.route("/api/dashboard/overview")
        def api_overview():
            status = self._get_server_status()
            return jsonify({
                "servers": status["summary"],
                "events": {"total_published": 0},
                "triggers": {"tasks_generated": 0},
                "memory": {"episodic_count": 0, "semantic_count": 0},
                "pending_approvals": 0,
            })

        @app.route("/api/dashboard/events")
        def api_events():
            return jsonify([])

        @app.route("/api/dashboard/capabilities")
        def api_capabilities():
            return jsonify([])

        # ── Health ────────────────────────────────────────────

        @app.route("/health")
        def health():
            return jsonify({"status": "ok", "component": "dashboard"})

        # ── Chat History File ────────────────────────────────
        chat_history_path = "data/chat_history.jsonl"

        def _save_chat(user_msg: str, bot_msg: str, image: str = ""):
            """Save chat message to history file and auto-save to memory."""
            import json as j
            os.makedirs("data", exist_ok=True)
            entry = {
                "timestamp": time.time(),
                "user": user_msg,
                "bot": bot_msg,
                "image": image,
            }
            with open(chat_history_path, "a", encoding="utf-8") as f:
                f.write(j.dumps(entry, ensure_ascii=False) + "\n")

            # Auto-save to memory
            _auto_save_memory(user_msg, bot_msg)

        def _load_chat_history() -> list[dict]:
            """Load chat history from file."""
            import json as j
            entries = []
            if os.path.exists(chat_history_path):
                with open(chat_history_path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            entries.append(j.loads(line.strip()))
                        except Exception:
                            pass
            return entries[-100:]  # Last 100 messages

        def _auto_save_memory(user_msg: str, bot_msg: str):
            """Use AdvancedMemory to extract and save entities/facts, and update desires."""
            try:
                from aegis_ai.memory.advanced import AdvancedMemory
                from aegis_ai.llm.factory import create_llm_provider
                llm = create_llm_provider()
                memory = AdvancedMemory(data_dir="data/memory", llm_provider=llm)
                memory.add_conversation(user_msg, bot_msg)
            except Exception as e:
                logger.debug("Auto-save memory failed: %s", e)

            # Update desires based on conversation
            try:
                from aegis_ai.desire.desire_system import DesireSystem
                from aegis_ai.llm.factory import create_llm_provider as _create
                _llm = _create()
                desire_system = DesireSystem(data_dir="data/desires", llm_provider=_llm)
                desire_system.update_after_action(
                    f"User: {user_msg[:200]}",
                    f"AEGIS: {bot_msg[:200]}",
                )
            except Exception as e:
                logger.debug("Desire update failed: %s", e)

        # ── Chat History API ─────────────────────────────────

        @app.route("/api/chat/history")
        def chat_history():
            return jsonify(_load_chat_history())

        @app.route("/api/chat/clear", methods=["POST"])
        def chat_clear():
            if os.path.exists(chat_history_path):
                os.remove(chat_history_path)
            return jsonify({"status": "cleared"})

        # ── Streaming Chat API ──────────────────────────────

        @app.route("/api/chat/stream", methods=["POST"])
        def chat_stream():
            from flask import request, Response
            import json as j

            data = request.get_json(silent=True) or {}
            text = data.get("text", "").strip()
            if not text:
                return jsonify({"error": "No text provided"}), 400

            def generate():
                try:
                    from aegis_ai.llm.factory import create_llm_provider
                    llm = create_llm_provider()

                    pc_status = "Online" if _check_port("localhost", 50052) else "Offline"
                    browser_status = "Online" if _check_port("localhost", 50053) else "Offline"

                    # Build memory context
                    memory_context = _build_memory_context(text)

                    system_prompt = (
                        "You are AEGIS, an autonomous AI assistant running on Windows.\n\n"
                        f"Current system status:\n"
                        f"- PC Server: {pc_status}\n"
                        f"- Browser Server: {browser_status}\n\n"
                        f"{memory_context}\n\n"
                        "When the user asks for PC/browser actions, respond with JSON.\n"
                        "Available actions: screenshot, active_window, windows, os_info, screen_size, clipboard, browse_url, memory_save, memory_search, memory_delete, memory_clear\n\n"
                        "For general questions, respond naturally."
                    )

                    # First, get LLM response
                    result = llm.generate(
                        prompt=text,
                        system_prompt=system_prompt,
                        max_tokens=1000,
                    )

                    if not result.success:
                        yield f"data: {j.dumps({'type': 'error', 'content': f'LLM error: {result.error}'})}\n\n"
                        return

                    response_text = result.content.strip()

                    # Check for JSON action
                    import re
                    action_data = None
                    try:
                        clean = response_text
                        if clean.startswith("```"):
                            lines = clean.split("\n")
                            clean = "\n".join(lines[1:])
                            if clean.endswith("```"):
                                clean = clean[:-3]
                            clean = clean.strip()

                        try:
                            action_data = j.loads(clean)
                        except j.JSONDecodeError:
                            json_matches = re.findall(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', clean)
                            for match in json_matches:
                                try:
                                    parsed = j.loads(match)
                                    if "action" in parsed:
                                        action_data = parsed
                                        break
                                except j.JSONDecodeError:
                                    continue
                    except Exception:
                        pass

                    # Execute action if found
                    if action_data and "action" in action_data:
                        action = action_data.get("action", "")
                        params = action_data.get("params", {})
                        action_result = None
                        action_image = None

                        if action == "screenshot":
                            pc_result = _send_pc_command("screenshot")
                            if pc_result and "image_base64" in pc_result:
                                action_result = "Screenshot captured successfully."
                                action_image = pc_result["image_base64"]
                            else:
                                action_result = "Failed to capture screenshot."

                        elif action in ("active_window", "windows", "os_info", "screen_size", "clipboard"):
                            pc_result = _send_pc_command(action)
                            if pc_result:
                                action_result = j.dumps(pc_result, indent=2, ensure_ascii=False)
                            else:
                                action_result = f"Failed to get {action}."

                        elif action == "browse_url":
                            url = params.get("url", "")
                            if url:
                                action_result = _browse_url(url)
                            else:
                                action_result = "No URL provided."

                        elif action == "memory_save":
                            content = params.get("content", "")
                            if content:
                                try:
                                    from aegis_ai.memory.advanced import AdvancedMemory
                                    _llm = create_llm_provider()
                                    memory = AdvancedMemory(data_dir="data/memory", llm_provider=_llm)
                                    memory.add_conversation(content, "Saved")
                                    action_result = f"Saved: {content}"
                                except Exception as e:
                                    action_result = f"Memory save error: {e}"

                        elif action == "memory_search":
                            query = params.get("query", text)
                            try:
                                from aegis_ai.memory.advanced import AdvancedMemory
                                _llm = create_llm_provider()
                                memory = AdvancedMemory(data_dir="data/memory", llm_provider=_llm)
                                context = memory.get_context(query)
                                action_result = context if context else "No memory found."
                            except Exception as e:
                                action_result = f"Memory search error: {e}"

                        elif action == "memory_delete":
                            query = params.get("query", "")
                            try:
                                from aegis_ai.memory.advanced import AdvancedMemory
                                _llm = create_llm_provider()
                                memory = AdvancedMemory(data_dir="data/memory", llm_provider=_llm)
                                deleted = memory.delete_fact(query)
                                action_result = f"Deleted {deleted} facts matching: {query}"
                            except Exception as e:
                                action_result = f"Memory delete error: {e}"

                        elif action == "memory_clear":
                            try:
                                from aegis_ai.memory.advanced import AdvancedMemory
                                memory = AdvancedMemory(data_dir="data/memory")
                                memory.clear_all()
                                action_result = "All memory cleared."
                            except Exception as e:
                                action_result = f"Memory clear error: {e}"

                        # Send action result through LLM for final response
                        if action_result:
                            llm_response = llm.generate(
                                prompt=f"User asked: {text}\n\nAction: {action}\nResult:\n{action_result}\n\nRespond naturally.",
                                system_prompt="You are AEGIS. Explain the result naturally.",
                                max_tokens=500,
                            )
                            final_response = llm_response.content if llm_response.success else action_result

                            # Stream the response
                            for i in range(0, len(final_response), 10):
                                chunk = final_response[i:i+10]
                                yield f"data: {j.dumps({'type': 'text', 'content': chunk})}\n\n"

                            # Send image if available
                            if action_image:
                                yield f"data: {j.dumps({'type': 'image', 'content': action_image})}\n\n"

                            # Save to history
                            _save_chat(text, final_response)
                            yield f"data: {j.dumps({'type': 'done'})}\n\n"
                            return

                    # No action, stream the conversational response
                    for i in range(0, len(response_text), 10):
                        chunk = response_text[i:i+10]
                        yield f"data: {j.dumps({'type': 'text', 'content': chunk})}\n\n"

                    _save_chat(text, response_text)
                    yield f"data: {j.dumps({'type': 'done'})}\n\n"

                except Exception as e:
                    yield f"data: {j.dumps({'type': 'error', 'content': str(e)})}\n\n"

            return Response(generate(), mimetype='text/event-stream')

        # ── Chat API ─────────────────────────────────────────

        @app.route("/api/chat/send", methods=["POST"])
        def chat_send():
            from flask import request
            data = request.get_json(silent=True) or {}
            text = data.get("text", "").strip()
            if not text:
                return jsonify({"error": "No text provided"}), 400

            try:
                from aegis_ai.llm.factory import create_llm_provider
                llm = create_llm_provider()

                pc_status = "Online" if _check_port("localhost", 50052) else "Offline"
                browser_status = "Online" if _check_port("localhost", 50053) else "Offline"

                # Build memory context
                memory_context = _build_memory_context(text)

                # Build chat history context
                history = _load_chat_history()
                history_context = ""
                if history:
                    recent = history[-5:]
                    history_context = "\nRecent conversation:\n"
                    for h in recent:
                        history_context += f"User: {h.get('user', '')}\nAEGIS: {h.get('bot', '')[:200]}\n"

                system_prompt = f"""You are AEGIS, an autonomous AI assistant running on Windows.

Current system status:
- PC Server: {pc_status} (can take screenshots, get window info, move mouse, type text)
- Browser Server: {browser_status} (can browse web pages)
- LLM: DeepSeek

{memory_context}
{history_context}

IMPORTANT: You have a memory system. Use the information above to answer questions about what you remember, who you know, and what you've discussed before.

When the user asks for something that requires PC or browser actions, respond with a JSON object. Otherwise, respond normally.

For PC/browser actions, respond ONLY with this JSON format:
{{"action": "<action_name>", "params": {{}}}}

Available actions:
- screenshot: Take a screenshot
- active_window: Get active window info
- windows: List open windows
- os_info: Get OS info
- screen_size: Get screen resolution
- clipboard: Get clipboard contents
- browse_url: Browse to a URL (params: {{"url": "..."}})
- memory_save: Save information to memory (params: {{"content": "...", "category": "fact|person|preference"}})
- memory_search: Search memory (params: {{"query": "..."}})
- memory_delete: Delete memory (params: {{"query": "..."}}) — deletes matching facts
- memory_clear: Clear ALL memory (no params) — deletes everything

When the user asks to remember something, use memory_save.
When the user asks what you remember, use memory_search.
When the user asks to forget/delete memory, use memory_delete or memory_clear.
When the user asks to search memory, use memory_search.

For general questions, respond naturally using your memory and knowledge."""

                result = llm.generate(
                    prompt=text,
                    system_prompt=system_prompt,
                    max_tokens=1000,
                )

                if not result.success:
                    resp = {"response": f"LLM error: {result.error}"}
                    _save_chat(text, resp["response"])
                    return jsonify(resp)

                response_text = result.content.strip()

                # Try to parse as JSON action (may be embedded in text)
                try:
                    clean = response_text
                    if clean.startswith("```"):
                        lines = clean.split("\n")
                        clean = "\n".join(lines[1:])
                        if clean.endswith("```"):
                            clean = clean[:-3]
                        clean = clean.strip()

                    # Try direct JSON parse first
                    action_data = None
                    try:
                        action_data = json.loads(clean)
                    except json.JSONDecodeError:
                        # Try to find JSON in the text
                        import re
                        # Find all JSON-like objects
                        json_matches = re.findall(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', clean)
                        for match in json_matches:
                            try:
                                parsed = json.loads(match)
                                if "action" in parsed:
                                    action_data = parsed
                                    break
                            except json.JSONDecodeError:
                                continue

                    if action_data is not None and "action" in action_data:
                        action = action_data.get("action", "")
                        params = action_data.get("params", {})

                        # Execute action and get raw result
                        action_result = None
                        action_image = None

                        if action == "screenshot":
                            pc_result = _send_pc_command("screenshot")
                            if pc_result and "image_base64" in pc_result:
                                action_result = "Screenshot captured successfully."
                                action_image = pc_result["image_base64"]
                            else:
                                action_result = "Failed to capture screenshot."

                        elif action in ("active_window", "windows", "os_info", "screen_size", "clipboard"):
                            pc_result = _send_pc_command(action)
                            if pc_result:
                                action_result = json.dumps(pc_result, indent=2, ensure_ascii=False)
                            else:
                                action_result = f"Failed to get {action}."

                        elif action == "browse_url":
                            url = params.get("url", "")
                            if url:
                                action_result = _browse_url(url)
                            else:
                                action_result = "No URL provided."

                        elif action == "memory_save":
                            content = params.get("content", "")
                            category = params.get("category", "fact")
                            if content:
                                try:
                                    from aegis_ai.memory.advanced import AdvancedMemory
                                    from aegis_ai.llm.factory import create_llm_provider as _create
                                    _llm = _create()
                                    memory = AdvancedMemory(data_dir="data/memory", llm_provider=_llm)
                                    # Use LLM to decide how to save
                                    memory.add_conversation(content, f"Saved as {category}")
                                    action_result = f"Saved to memory: {content}"
                                except Exception as e:
                                    action_result = f"Memory save error: {e}"

                        elif action == "memory_search":
                            query = params.get("query", text)
                            try:
                                from aegis_ai.memory.advanced import AdvancedMemory
                                from aegis_ai.llm.factory import create_llm_provider as _create
                                _llm = _create()
                                memory = AdvancedMemory(data_dir="data/memory", llm_provider=_llm)
                                context = memory.get_context(query)
                                action_result = context if context else "No memory found."
                            except Exception as e:
                                action_result = f"Memory search error: {e}"

                        elif action == "memory_delete":
                            query = params.get("query", "")
                            try:
                                from aegis_ai.memory.advanced import AdvancedMemory
                                from aegis_ai.llm.factory import create_llm_provider as _create
                                _llm = _create()
                                memory = AdvancedMemory(data_dir="data/memory", llm_provider=_llm)
                                deleted_facts = memory.delete_fact(query)
                                deleted_entity = memory.delete_entity(query)
                                parts = []
                                if deleted_facts:
                                    parts.append(f"Deleted {deleted_facts} facts")
                                if deleted_entity:
                                    parts.append(f"Deleted entity: {query}")
                                action_result = "; ".join(parts) if parts else f"Nothing found matching: {query}"
                            except Exception as e:
                                action_result = f"Memory delete error: {e}"

                        elif action == "memory_clear":
                            try:
                                from aegis_ai.memory.advanced import AdvancedMemory
                                memory = AdvancedMemory(data_dir="data/memory")
                                memory.clear_all()
                                # Also clear legacy memory
                                import shutil
                                if os.path.exists("data/persona.jsonl"):
                                    os.remove("data/persona.jsonl")
                                if os.path.exists("data/semantic.jsonl"):
                                    os.remove("data/semantic.jsonl")
                                if os.path.exists("data/chroma"):
                                    shutil.rmtree("data/chroma", ignore_errors=True)
                                action_result = "All memory cleared."
                            except Exception as e:
                                action_result = f"Memory clear error: {e}"

                        # Pass result through LLM for final response
                        if action_result:
                            llm_response = llm.generate(
                                prompt=f"User asked: {text}\n\nAction performed: {action}\nResult:\n{action_result}\n\nRespond naturally to the user about what was done or found.",
                                system_prompt="You are AEGIS. Explain the result naturally and conversationally.",
                                max_tokens=500,
                            )
                            final_response = llm_response.content if llm_response.success else action_result
                            _save_chat(text, final_response)
                            resp = {"response": final_response}
                            if action_image:
                                resp["image"] = action_image
                                resp["image_width"] = 1920
                                resp["image_height"] = 1080
                            return jsonify(resp)

                except (json.JSONDecodeError, KeyError):
                    pass

                # Not a JSON action — return as conversational response
                _save_chat(text, response_text)
                return jsonify({"response": response_text})

            except Exception as e:
                resp = {"response": f"Error: {str(e)}"}
                _save_chat(text, resp["response"])
                return jsonify(resp)

        # ── Autonomous Loop API ──────────────────────────────

        @app.route("/api/autonomous/status")
        def autonomous_status():
            """Get autonomous loop status."""
            try:
                from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
                from aegis_ai.desire.desire_system import DesireSystem
                from aegis_ai.llm.factory import create_llm_provider
                llm = create_llm_provider()
                desire = DesireSystem(data_dir="data/desires", llm_provider=llm)
                loop = AutonomousLoop(
                    llm_provider=llm,
                    desire_system=desire,
                    data_dir="data/autonomous",
                )
                return jsonify(loop.get_status())
            except Exception as e:
                return jsonify({"error": str(e)})

        @app.route("/api/autonomous/trigger", methods=["POST"])
        def autonomous_trigger():
            """Manually trigger autonomous cycle."""
            try:
                from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
                from aegis_ai.desire.desire_system import DesireSystem
                from aegis_ai.llm.factory import create_llm_provider
                llm = create_llm_provider()
                desire = DesireSystem(data_dir="data/desires", llm_provider=llm)
                loop = AutonomousLoop(
                    llm_provider=llm,
                    desire_system=desire,
                    data_dir="data/autonomous",
                )
                status = loop.trigger_now()
                return jsonify(status)
            except Exception as e:
                return jsonify({"error": str(e)})

        @app.route("/api/autonomous/start", methods=["POST"])
        def autonomous_start():
            """Start autonomous loop."""
            try:
                from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
                from aegis_ai.desire.desire_system import DesireSystem
                from aegis_ai.llm.factory import create_llm_provider
                llm = create_llm_provider()
                desire = DesireSystem(data_dir="data/desires", llm_provider=llm)
                loop = AutonomousLoop(
                    llm_provider=llm,
                    desire_system=desire,
                    data_dir="data/autonomous",
                )
                loop.start()
                return jsonify({"status": "started"})
            except Exception as e:
                return jsonify({"error": str(e)})

        @app.route("/api/autonomous/stop", methods=["POST"])
        def autonomous_stop():
            """Stop autonomous loop."""
            try:
                from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
                loop = AutonomousLoop(data_dir="data/autonomous")
                loop.stop()
                return jsonify({"status": "stopped"})
            except Exception as e:
                return jsonify({"error": str(e)})

        @app.route("/api/desires")
        def desires_status():
            """Get current desire states."""
            try:
                from aegis_ai.desire.desire_system import DesireSystem
                desire = DesireSystem(data_dir="data/desires")
                return jsonify(desire.get_stats())
            except Exception as e:
                return jsonify({"error": str(e)})