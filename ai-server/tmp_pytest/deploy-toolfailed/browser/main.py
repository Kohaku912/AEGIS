"""AEGIS Browser Server — entry point.

Usage:
    python -m aegis_browser.main

Uses browser-use for AI-driven browser automation.
"""

from __future__ import annotations

import importlib.util
import json
import logging
import os
import shutil
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from aegis_browser.config import Config
from aegis_browser.safety import SUPPORTED_OPERATIONS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegis_browser.main")

_browser_agent = None
_browser_execution_lock = threading.Lock()

_BASE_FORBIDDEN_ACTIONS = [
    "solve_captcha",
    "bypass_bot_detection",
    "use_proxy_for_evasion",
    "enter_password_without_user",
    "enter_2fa_without_user",
    "upload_identity_document",
    "purchase",
    "paid_subscription",
    "accept_contract",
    "spam",
    "bulk_signup",
]

_OPERATION_ACTIONS = {
    "search.query": ["search_web", "read_page", "open_link", "extract_text"],
    "page.read": ["read_page", "open_link", "extract_text"],
    "page.summarize": ["read_page", "open_link", "extract_text", "summarize"],
    "page.navigate": ["open_link", "read_page"],
    "feed.monitor": ["search_web", "read_page", "open_link", "extract_messages"],
    "session.open": ["open_link", "read_page"],
    "session.authenticated": ["open_link", "read_page", "extract_text"],
    "element.click": ["read_page", "click_button"],
    "form.fill": ["read_page", "fill_non_sensitive_form", "input_text"],
    "form.submit": ["read_page", "fill_non_sensitive_form", "input_text", "click_button", "submit_form"],
    "file.download": ["read_page", "open_link", "download_file"],
    "file.upload": ["read_page", "upload_file", "click_button"],
    "social.react": ["read_page", "click_button", "react"],
    "social.post": ["read_page", "input_text", "click_button", "publish"],
    "account.create": ["read_page", "fill_non_sensitive_form", "input_text", "click_button", "create_account"],
}


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

    resources = _cgroup_resource_snapshot()
    resource_status = str(resources.get("status") or "ok")
    mode = "full" if not missing else "fallback"
    status = "critical" if resource_status == "critical" else "ok" if mode == "full" else "degraded"
    if status == "ok" and resource_status == "degraded":
        status = "degraded"
    reasons: list[str] = []
    if missing:
        reasons.append("Missing dependencies: " + ", ".join(missing))
    if resource_status != "ok":
        reasons.append(
            "Browser resource pressure: "
            f"memory={resources.get('memory_ratio')}, "
            f"pids={resources.get('pids_ratio')}, "
            f"temp={resources.get('temp_ratio')}"
        )
    return {
        "status": status,
        "server": "browser-server",
        "version": "0.2.0",
        "capabilities": len(SUPPORTED_OPERATIONS),
        "mode": mode,
        "browser_use_available": browser_use_available,
        "playwright_available": playwright_available,
        "profile_root": config.browser_profile_root,
        "profile_name": config.browser_profile_name,
        "profile_dir": profile_dir,
        "headless": config.browser_headless,
        "browser_channel": config.browser_channel,
        "resources": resources,
        "degraded_reason": "; ".join(reasons),
        "recovery_hint": (
            "Install browser dependencies: python -m pip install -e . && python -m playwright install chromium"
            if missing
            else "Restart Browser Server to reclaim browser-owned temporary files."
            if resource_status != "ok"
            else ""
        ),
    }


def _cgroup_resource_snapshot() -> dict[str, Any]:
    """Read cgroup v2 resource counters without spawning helper processes."""

    memory_current = _read_cgroup_number("/sys/fs/cgroup/memory.current")
    memory_max = _read_cgroup_number("/sys/fs/cgroup/memory.max")
    pids_current = _read_cgroup_number("/sys/fs/cgroup/pids.current")
    pids_max = _read_cgroup_number("/sys/fs/cgroup/pids.max")
    events = _read_cgroup_events("/sys/fs/cgroup/memory.events")
    zombie_processes = _zombie_process_count()
    temp_total, temp_used, temp_free = _disk_usage(tempfile.gettempdir())
    memory_ratio = _ratio(memory_current, memory_max)
    pids_ratio = _ratio(pids_current, pids_max)
    temp_ratio = _ratio(temp_used, temp_total)
    critical_ratio = float(os.getenv("AEGIS_BROWSER_RESOURCE_CRITICAL_RATIO", "0.9"))
    degraded_ratio = float(os.getenv("AEGIS_BROWSER_RESOURCE_DEGRADED_RATIO", "0.75"))
    highest = max(memory_ratio or 0.0, pids_ratio or 0.0, temp_ratio or 0.0)
    zombie_critical = int(os.getenv("AEGIS_BROWSER_ZOMBIE_CRITICAL", "64"))
    zombie_degraded = int(os.getenv("AEGIS_BROWSER_ZOMBIE_DEGRADED", "8"))
    status = "critical" if highest >= critical_ratio else "degraded" if highest >= degraded_ratio else "ok"
    if zombie_processes >= zombie_critical:
        status = "critical"
    elif zombie_processes >= zombie_degraded and status == "ok":
        status = "degraded"
    return {
        "status": status,
        "memory_current_bytes": memory_current,
        "memory_max_bytes": memory_max,
        "memory_ratio": memory_ratio,
        "pids_current": pids_current,
        "pids_max": pids_max,
        "pids_ratio": pids_ratio,
        "temp_total_bytes": temp_total,
        "temp_used_bytes": temp_used,
        "temp_free_bytes": temp_free,
        "temp_ratio": temp_ratio,
        "oom_events": int(events.get("oom", 0)),
        "oom_kill_events": int(events.get("oom_kill", 0)),
        "zombie_processes": zombie_processes,
    }


def _disk_usage(path: str) -> tuple[int | None, int | None, int | None]:
    try:
        usage = shutil.disk_usage(path)
        return usage.total, usage.used, usage.free
    except OSError:
        return None, None, None


def _zombie_process_count() -> int:
    count = 0
    for stat_path in Path("/proc").glob("[0-9]*/stat"):
        try:
            stat = stat_path.read_text(encoding="utf-8")
            state = stat.rsplit(")", maxsplit=1)[1].strip().split(maxsplit=1)[0]
        except (IndexError, OSError):
            continue
        if state == "Z":
            count += 1
    return count


def _read_cgroup_number(path: str) -> int | None:
    try:
        value = Path(path).read_text(encoding="utf-8").strip()
        return None if value == "max" else int(value)
    except (OSError, ValueError):
        return None


def _read_cgroup_events(path: str) -> dict[str, int]:
    try:
        return {
            key: int(value)
            for key, value in (
                line.split(maxsplit=1) for line in Path(path).read_text(encoding="utf-8").splitlines() if " " in line
            )
        }
    except (OSError, ValueError):
        return {}


def _ratio(current: int | None, maximum: int | None) -> float | None:
    if current is None or maximum is None or maximum <= 0:
        return None
    return round(current / maximum, 4)


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
        elif path.startswith("/capability/"):
            operation = path.removeprefix("/capability/").replace("/", ".")
            result = self._handle_capability(operation, data)
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

        status_code = 503 if path == "/health" and result.get("status") == "critical" else 200
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

    def _handle_health(self) -> dict:
        return get_runtime_health()

    def _handle_capabilities(self) -> dict:
        return {
            "operations": sorted(SUPPORTED_OPERATIONS),
            "capability_source": "ai-server JSON manifests",
        }

    def _handle_capability(self, operation: str, data: dict) -> dict:
        if operation not in SUPPORTED_OPERATIONS:
            return {"error": "Unsupported browser operation", "code": "OPERATION_UNSUPPORTED"}
        viewer = str(data.get("viewer") or "")
        purpose = str(data.get("purpose") or "")
        success_condition = str(data.get("success_condition") or "")
        stop_condition = str(data.get("stop_condition") or "")
        if viewer not in {"agent_private", "shared"}:
            return {
                "error": "Browser Server is agent-private. Route user-visible pages to PC or Android.",
                "code": "USER_VISIBLE_HANDOFF_REQUIRED",
            }
        if purpose not in {
            "research",
            "monitor",
            "automate",
            "collaborative_review",
        }:
            return {"error": "A valid browser purpose is required", "code": "PURPOSE_REQUIRED"}
        if not success_condition or not stop_condition:
            return {
                "error": "success_condition and stop_condition are required",
                "code": "BOUNDS_REQUIRED",
            }
        # search.query: prefer lightweight HTTP search — browser-use agent often
        # burns the full HTTP timeout on search-engine CAPTCHA / Cloudflare.
        if operation == "search.query":
            return self._handle_fast_search(data, operation=operation)
        return self._handle_execute(data, operation=operation)

    def _handle_fast_search(self, data: dict, *, operation: str) -> dict:
        """Run DuckDuckGo-backed search without launching browser-use."""
        started = time.time()
        task_text = str(data.get("task") or data.get("query") or "").strip()
        if not task_text:
            return {"error": "No task provided", "code": "TASK_REQUIRED"}
        max_results = min(max(int(data.get("max_results") or data.get("max_steps") or 5), 1), 12)
        results: list[dict[str, str]] = []
        backend = "none"
        error = ""

        try:
            from ddgs import DDGS

            with DDGS(timeout=12) as ddgs:
                raw = list(ddgs.text(task_text, max_results=max_results))
            for item in raw:
                results.append(
                    {
                        "title": str(item.get("title") or ""),
                        "url": str(item.get("href") or item.get("link") or ""),
                        "snippet": str(item.get("body") or item.get("snippet") or ""),
                    }
                )
            backend = "ddgs"
        except Exception as exc:
            error = str(exc)
            logger.info("ddgs search unavailable (%s); trying HTML fallback", error)
            try:
                import html as html_lib
                import re
                import urllib.parse
                import urllib.request

                url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": task_text})
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; AEGIS-Browser/1.0)"},
                    method="GET",
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    body = resp.read().decode("utf-8", errors="replace")
                link_pattern = re.compile(
                    r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                    re.IGNORECASE | re.DOTALL,
                )
                snippet_pattern = re.compile(
                    r'class="result__snippet[^"]*"[^>]*>(.*?)</(?:a|td|div)>',
                    re.IGNORECASE | re.DOTALL,
                )
                pairs = link_pattern.findall(body)
                snippets = snippet_pattern.findall(body)
                for index, (href, title_html) in enumerate(pairs[:max_results]):
                    title = html_lib.unescape(re.sub(r"<[^>]+>", "", title_html))
                    title = re.sub(r"\s+", " ", title).strip()
                    snippet = ""
                    if index < len(snippets):
                        snippet = html_lib.unescape(re.sub(r"<[^>]+>", "", snippets[index]))
                        snippet = re.sub(r"\s+", " ", snippet).strip()
                    resolved = href
                    parsed = urllib.parse.urlparse(href)
                    if "duckduckgo.com" in (parsed.netloc or "") and parsed.path.startswith("/l/"):
                        qs = urllib.parse.parse_qs(parsed.query)
                        uddg = qs.get("uddg") or qs.get("u")
                        if uddg:
                            resolved = urllib.parse.unquote(uddg[0])
                    results.append({"title": title, "url": resolved, "snippet": snippet})
                backend = "html"
                error = ""
            except Exception as html_exc:
                error = f"ddgs={error}; html={html_exc}"

        duration_ms = int((time.time() - started) * 1000)
        if not results:
            return {
                "status": "FAILED",
                "result": f"Search failed for '{task_text}': {error or 'no results'}",
                "data": {"results": [], "backend": backend},
                "duration_ms": duration_ms,
                "error": error or "no results",
                "needs_user_input": False,
                "needs_user_input_for": "",
                "operation": operation,
                "viewer": data.get("viewer", "agent_private"),
                "purpose": data.get("purpose", "research"),
                "success_condition": data.get("success_condition", ""),
                "stop_condition": data.get("stop_condition", ""),
            }

        lines = [f"Search results for '{task_text}' ({backend}):"]
        for item in results:
            lines.append(f"- {item['title']}: {item['snippet'][:160]}")
            lines.append(f"  {item['url']}")
        return {
            "status": "COMPLETED",
            "result": "\n".join(lines),
            "data": {"results": results, "backend": backend, "query": task_text},
            "duration_ms": duration_ms,
            "error": "",
            "needs_user_input": False,
            "needs_user_input_for": "",
            "operation": operation,
            "viewer": data.get("viewer", "agent_private"),
            "purpose": data.get("purpose", "research"),
            "success_condition": data.get("success_condition", ""),
            "stop_condition": data.get("stop_condition", ""),
        }

    def _handle_execute(self, data: dict, *, operation: str = "legacy.page.browse") -> dict:
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
                user_context=json.dumps(
                    {
                        "operation": operation,
                        "viewer": data.get("viewer", "agent_private"),
                        "purpose": data.get("purpose", "automate"),
                    },
                    ensure_ascii=False,
                ),
                stop_conditions=[str(data.get("stop_condition") or "task goal reached")],
                expected_output_schema=str(data.get("success_condition") or "task result"),
                allowed_actions=list(_OPERATION_ACTIONS.get(operation, _OPERATION_ACTIONS["page.read"])),
                forbidden_actions=list(_BASE_FORBIDDEN_ACTIONS),
                approval_boundaries=[],
            )
            with _browser_execution_lock:
                agent = get_browser_agent()
                result = agent.run_task(task)
            response = {
                "status": result.status.name,
                "result": result.result_text,
                "data": result.extracted_data,
                "duration_ms": result.duration_ms,
                "error": result.error,
                "needs_user_input": result.status.name == "NEEDS_USER_INPUT",
                "needs_user_input_for": result.needs_user_input_for,
                "operation": operation,
                "viewer": data.get("viewer", "agent_private"),
                "purpose": data.get("purpose", "automate"),
                "success_condition": data.get("success_condition", ""),
                "stop_condition": data.get("stop_condition", ""),
            }
            if data.get("viewer") == "shared":
                response["handoff"] = {
                    "required": True,
                    "viewer": "user_visible",
                    "kind": "show_url",
                    "preferred_server_ids": ["pc-server", "android-server"],
                    "url": str(data.get("handoff_url") or data.get("url") or ""),
                    "purpose": str(data.get("purpose") or "collaborative_review"),
                    "source_operation": operation,
                }
            return response
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
    from aegis_browser.browser_use_agent import BrowserUseAgent

    removed_temp_dirs = BrowserUseAgent._cleanup_browser_temp_dirs()
    if removed_temp_dirs:
        logger.info("Removed %d stale browser temporary directories", removed_temp_dirs)
    logger.info("AEGIS Browser Server v0.2.0")
    logger.info("HTTP: %s:%d", config.grpc_host, config.grpc_port)
    logger.info("Headless: %s", config.browser_headless)
    logger.info("Browser channel: %s", config.browser_channel)
    logger.info("Browser profile root: %s", config.browser_profile_root)
    logger.info("Browser profile name: %s", config.browser_profile_name)

    logger.info("Supported browser operations: %d", len(SUPPORTED_OPERATIONS))

    health = get_runtime_health(config)
    if health["mode"] == "full":
        logger.info("Browser dependencies available; full browser-use mode enabled")
    else:
        logger.warning(
            "Browser Server degraded: %s. %s",
            health["degraded_reason"],
            health["recovery_hint"],
        )

    server = ThreadingHTTPServer((config.grpc_host, config.grpc_port), BrowserHandler)
    server.daemon_threads = True
    logger.info("Browser Server listening on %s:%d", config.grpc_host, config.grpc_port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutdown requested — stopping.")
        server.shutdown()


if __name__ == "__main__":
    main()
