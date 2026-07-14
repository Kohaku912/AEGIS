"""AEGIS Browser Server — entry point.

Usage:
    python -m aegis_browser.main

Uses browser-use for AI-driven browser automation.
"""

from __future__ import annotations

import json
import logging
import sys
import time
import importlib.util
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

from aegis_browser.config import Config
from aegis_browser.safety import CAPABILITIES, BLOCKED_CAPABILITIES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegis_browser.main")

_browser_agent = None


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def get_runtime_health(config: Config | None = None) -> dict[str, Any]:
    """Return dependency and profile status for dashboard health checks."""
    config = config or Config()
    browser_use_available = _module_available("browser_use")
    playwright_available = _module_available("playwright")
    profile_dir = str(Path(config.browser_profile_root) / config.browser_profile_name)

    missing: list[str] = []
    if not browser_use_available:
        missing.append("browser-use")
    if not playwright_available:
        missing.append("playwright")

    mode = "full" if not missing else "fallback"
    return {
        "status": "ok" if mode == "full" else "degraded",
        "server": "browser-server",
        "version": "0.2.0",
        "capabilities": len(CAPABILITIES),
        "mode": mode,
        "browser_use_available": browser_use_available,
        "playwright_available": playwright_available,
        "profile_root": config.browser_profile_root,
        "profile_name": config.browser_profile_name,
        "profile_dir": profile_dir,
        "headless": config.browser_headless,
        "browser_channel": config.browser_channel,
        "degraded_reason": "Missing dependencies: " + ", ".join(missing) if missing else "",
        "recovery_hint": (
            "Install browser dependencies: python -m pip install -e . && python -m playwright install chromium"
            if missing
            else ""
        ),
    }


def get_browser_agent():
    global _browser_agent
    if _browser_agent is None:
        from aegis_browser.browser_use_agent import BrowserUseAgent
        _browser_agent = BrowserUseAgent()
    return _browser_agent


class BrowserHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}

        path = self.path.rstrip("/")

        if path == "/execute":
            result = self._handle_execute(data)
        elif path == "/browse":
            result = self._handle_browse(data)
        elif path == "/health":
            result = self._handle_health()
        else:
            result = {"error": f"Unknown endpoint: {path}"}

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        path = self.path.rstrip("/")
        if path == "/health":
            result = self._handle_health()
        elif path == "/capabilities":
            result = self._handle_capabilities()
        else:
            result = {"error": f"Unknown endpoint: {path}"}

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

    def _handle_health(self) -> dict:
        return get_runtime_health()

    def _handle_capabilities(self) -> dict:
        caps = []
        for cap_id, info in CAPABILITIES.items():
            caps.append({
                "id": cap_id,
                "safety_level": info["safety_level"].name,
                "description": info.get("description", ""),
            })
        return {"capabilities": caps}

    def _handle_execute(self, data: dict) -> dict:
        task_text = data.get("task", "")
        if not task_text:
            return {"error": "No task provided"}

        max_steps = data.get("max_steps", 50)

        try:
            from aegis_browser.task_models import BrowserTask
            task = BrowserTask(
                task_id=f"task_{int(time.time() * 1000)}",
                natural_language_goal=task_text,
                max_steps=max_steps,
            )
            agent = get_browser_agent()
            result = agent.run_task(task)
            return {
                "status": result.status.name,
                "result": result.result_text,
                "data": result.extracted_data,
                "duration_ms": result.duration_ms,
                "error": result.error,
                "needs_user_input": result.status.name == "NEEDS_USER_INPUT",
                "needs_user_input_for": result.needs_user_input_for,
            }
        except Exception as e:
            return {"error": str(e)}

    def _handle_browse(self, data: dict) -> dict:
        url = data.get("url", "")
        if not url:
            return {"error": "No URL provided"}
        selector = str(data.get("selector") or "").strip()
        expect_text = str(data.get("expect_text") or "").strip()

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                response = page.goto(url, timeout=30000)
                title = page.title()
                text = page.evaluate("""
                    (() => {
                        const exclude = ['script', 'style', 'nav', 'footer'];
                        const clone = document.body.cloneNode(true);
                        exclude.forEach(tag => {
                            clone.querySelectorAll(tag).forEach(el => el.remove());
                        });
                        return (clone.textContent || '').replace(/\\s{3,}/g, '\\n\\n').trim();
                    })()
                """)
                selector_found = False
                selector_text = ""
                selector_error = ""
                if selector:
                    try:
                        locator = page.locator(selector)
                        count = locator.count()
                        selector_found = count > 0
                        if selector_found:
                            selector_text = locator.first.text_content(timeout=3000) or ""
                    except Exception as exc:
                        selector_error = str(exc)
                status_code = response.status if response else (200 if url.startswith(("data:", "file:")) else None)
                browser.close()

            text_found = bool(expect_text) and (
                expect_text in text or expect_text in selector_text or expect_text in title
            )
            return {
                "ok": True,
                "http_status": status_code,
                "title": title.encode("utf-8", errors="replace").decode("utf-8"),
                "text": text[:5000].encode("utf-8", errors="replace").decode("utf-8"),
                "url": url,
                "verification": {
                    "selector": selector,
                    "selector_found": selector_found,
                    "selector_text": selector_text[:2000].encode("utf-8", errors="replace").decode("utf-8"),
                    "selector_error": selector_error,
                    "expect_text": expect_text,
                    "text_found": text_found,
                    "passed": (not selector or selector_found) and (not expect_text or text_found),
                },
            }
        except Exception as e:
            return {"error": str(e)}

    def log_message(self, format, *args):
        logger.info(format % args)


def main() -> None:
    config = Config()
    logger.info("AEGIS Browser Server v0.2.0")
    logger.info("HTTP: %s:%d", config.grpc_host, config.grpc_port)
    logger.info("Headless: %s", config.browser_headless)
    logger.info("Browser channel: %s", config.browser_channel)
    logger.info("Browser profile root: %s", config.browser_profile_root)
    logger.info("Browser profile name: %s", config.browser_profile_name)

    logger.info("Registered capabilities: %d", len(CAPABILITIES))

    health = get_runtime_health(config)
    if health["mode"] == "full":
        logger.info("Browser dependencies available; full browser-use mode enabled")
    else:
        logger.warning(
            "Browser Server degraded: %s. %s",
            health["degraded_reason"],
            health["recovery_hint"],
        )

    server = HTTPServer((config.grpc_host, config.grpc_port), BrowserHandler)
    logger.info("Browser Server listening on %s:%d", config.grpc_host, config.grpc_port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutdown requested — stopping.")
        server.shutdown()


if __name__ == "__main__":
    main()
