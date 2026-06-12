"""Browser-Use Agent — executes browser tasks using browser-use.

This is the core of the Browser Server.
It receives BrowserTasks from AEGIS Core and executes them
using browser-use (LLM + Playwright).

Architecture:
- Receives natural language BrowserTask
- Creates safety boundary from task constraints
- Passes task to browser-use with safety instructions
- Monitors execution for safety violations
- Returns structured BrowserTaskResult
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Any

from aegis_browser.safety_boundary import BrowserSafetyBoundary, SafetyCheckResult
from aegis_browser.session import BrowserSession
from aegis_browser.task_models import BrowserTask, BrowserTaskResult, TaskStatus
from aegis_browser.trace import BrowserTrace

logger = logging.getLogger("aegis_browser.browser_use_agent")


class BrowserUseAgent:
    """Executes browser tasks using browser-use.

    Usage:
        agent = BrowserUseAgent(llm_client=llm)
        result = agent.run_task(task)
    """

    def __init__(
        self,
        llm_client: Any = None,
        session: BrowserSession | None = None,
        trace_dir: str = "/app/traces",
    ) -> None:
        self._llm = llm_client
        self._session = session or BrowserSession()
        self._trace_dir = trace_dir
        self._current_task: BrowserTask | None = None
        self._current_trace: BrowserTrace | None = None
        self._running = False

    def run_task(self, task: BrowserTask) -> BrowserTaskResult:
        """Run a browser task synchronously."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self._run_task_async(task))
                    return future.result(timeout=300)
            else:
                return loop.run_until_complete(self._run_task_async(task))
        except Exception as e:
            return BrowserTaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
            )

    async def _run_task_async(self, task: BrowserTask) -> BrowserTaskResult:
        """Run a browser task asynchronously."""
        start = time.perf_counter()
        self._current_task = task
        self._running = True

        # Create trace
        trace = BrowserTrace(task_id=task.task_id, output_dir=self._trace_dir)
        self._current_trace = trace

        # Create safety boundary
        boundary = BrowserSafetyBoundary(task)

        result = BrowserTaskResult(
            task_id=task.task_id,
            status=TaskStatus.RUNNING,
            trace_id=trace.task_id,
        )

        try:
            # Build full task with safety instructions
            full_task = self._build_task_with_safety(task)

            # Execute with browser-use
            trace.record("start", f"Starting task: {task.natural_language_goal[:100]}")

            browser_result = await self._execute_with_browser_use(full_task, boundary, trace)

            result.result_text = browser_result.get("text", "")
            result.extracted_data = browser_result.get("data", {})
            result.actions_taken = boundary.get_actions_taken()
            result.status = TaskStatus.COMPLETED
            result.duration_ms = (time.perf_counter() - start) * 1000

            trace.record("complete", f"Task completed in {result.duration_ms:.0f}ms")

        except SafetyStop as e:
            result.status = TaskStatus.STOPPED
            result.stopped_reason = str(e)
            result.duration_ms = (time.perf_counter() - start) * 1000
            trace.record("safety_stop", str(e))

        except ApprovalBoundary as e:
            result.status = TaskStatus.NEEDS_APPROVAL
            result.needs_approval_for = [str(e)]
            result.duration_ms = (time.perf_counter() - start) * 1000
            trace.record("approval_needed", str(e))

        except UserInputNeeded as e:
            result.status = TaskStatus.NEEDS_USER_INPUT
            result.needs_user_input_for = [str(e)]
            result.duration_ms = (time.perf_counter() - start) * 1000
            trace.record("user_input_needed", str(e))

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            result.duration_ms = (time.perf_counter() - start) * 1000
            trace.record("error", str(e))

        finally:
            self._running = False
            # Save trace
            try:
                trace.save()
            except Exception:
                pass

        return result

    def _build_task_with_safety(self, task: BrowserTask) -> str:
        """Build full task description with safety instructions."""
        parts = [
            f"Task: {task.natural_language_goal}",
            "",
            "SAFETY RULES (MUST FOLLOW):",
        ]

        # Add forbidden actions
        if task.forbidden_actions:
            parts.append("\nFORBIDDEN (STOP IMMEDIATELY if encountered):")
            for action in task.forbidden_actions:
                parts.append(f"  - DO NOT {action.replace('_', ' ')}")

        # Add stop conditions
        if task.stop_conditions:
            parts.append("\nSTOP CONDITIONS (STOP if detected):")
            for condition in task.stop_conditions:
                parts.append(f"  - {condition.replace('_', ' ')}")

        # Add allowed actions
        if task.allowed_actions:
            parts.append("\nALLOWED ACTIONS:")
            for action in task.allowed_actions:
                parts.append(f"  - {action.replace('_', ' ')}")

        # Add target domains
        if task.target_domains:
            parts.append(f"\nTARGET DOMAINS: {', '.join(task.target_domains)}")

        # Add user context
        if task.user_context:
            parts.append(f"\nUSER CONTEXT: {task.user_context}")

        # Add privacy constraints
        if task.privacy_constraints:
            parts.append("\nPRIVACY CONSTRAINTS:")
            for constraint in task.privacy_constraints:
                parts.append(f"  - {constraint}")

        parts.append("\nIMPORTANT: If you encounter CAPTCHA, payment, identity verification, or any forbidden action, STOP and report what you found. Do NOT try to bypass or solve it.")

        return "\n".join(parts)

    async def _execute_with_browser_use(
        self,
        task: str,
        boundary: BrowserSafetyBoundary,
        trace: BrowserTrace,
    ) -> dict[str, Any]:
        """Execute task using browser-use."""
        try:
            from langchain_openai import ChatOpenAI
            from browser_use import Agent

            import os
            llm = ChatOpenAI(
                model="deepseek-chat",
                api_key=os.environ.get("OPENAI_API_KEY", ""),
                base_url=os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com"),
            )

            trace.record("browser_use_start", "Starting browser-use agent")

            agent = Agent(task=task, llm=llm)
            result = await agent.run()

            trace.record("browser_use_complete", f"Result: {str(result)[:200]}")

            return {"text": str(result), "data": {}}

        except ImportError:
            logger.warning("browser-use not available, falling back to playwright")
            return await self._execute_with_playwright(task, boundary, trace)

    async def _execute_with_playwright(
        self,
        task: str,
        boundary: BrowserSafetyBoundary,
        trace: BrowserTrace,
    ) -> dict[str, Any]:
        """Fallback: execute with direct playwright."""
        import re
        from playwright.async_api import async_playwright

        # Extract URL from task
        url_match = re.search(r'https?://[^\s]+', task)
        if not url_match:
            raise ValueError("No URL found in task")

        url = url_match.group(0)

        trace.record("playwright_start", f"Navigating to {url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, timeout=30000)
                title = await page.title()

                trace.record("page_loaded", f"Title: {title}", page_url=url, page_title=title)

                # Get page content
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

                # Check safety
                safety_result = boundary.check_page_content(text)
                if safety_result.should_stop:
                    raise SafetyStop(safety_result.reason)
                if safety_result.needs_approval:
                    raise ApprovalBoundary(safety_result.reason)
                if safety_result.needs_user_input:
                    raise UserInputNeeded(safety_result.reason)

                trace.record("content_extracted", f"Text length: {len(text)}")

                return {"text": f"**{title}**\n\n{text[:3000]}", "data": {"title": title, "url": url}}

            finally:
                await browser.close()

    def stop(self) -> None:
        """Stop current task execution."""
        self._running = False
        if self._current_trace:
            self._current_trace.record("stopped", "Task stopped by user")

    def is_running(self) -> bool:
        """Check if agent is running."""
        return self._running


# ── Custom exceptions ──────────────────────────────────────


class SafetyStop(Exception):
    """Raised when safety boundary detects a stop condition."""
    pass


class ApprovalBoundary(Exception):
    """Raised when an approval boundary is hit."""
    pass


class UserInputNeeded(Exception):
    """Raised when user input is needed (password, 2FA)."""
    pass
