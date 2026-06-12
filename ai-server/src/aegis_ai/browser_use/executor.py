"""Browser-Use Task Executor — executes browser tasks using browser-use.

Instead of implementing site-specific functions, this module passes
natural language tasks to browser-use which uses LLM to drive the browser.

Safety: All actions go through safety boundary checks.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("aegis_ai.browser_use.executor")


@dataclass
class BrowserTaskResult:
    """Result of a browser-use task execution."""
    success: bool = False
    task_description: str = ""
    result_text: str = ""
    extracted_data: dict[str, Any] = field(default_factory=dict)
    actions_taken: list[str] = field(default_factory=list)
    error: str = ""
    duration_ms: float = 0.0


class BrowserUseSafetyBoundary:
    """Safety boundary for browser-use tasks.

    Defines what browser-use can and cannot do.
    """

    # Always blocked
    BLOCKED_PATTERNS = [
        "captcha", "bypass", "stealth", "proxy",
        "purchase", "buy", "pay", "subscribe",
        "spam", "bulk", "mass",
    ]

    # Requires approval
    APPROVAL_PATTERNS = [
        "post", "publish", "send", "submit",
        "tweet", "dm", "email", "message",
        "upload", "share",
    ]

    # Allowed without approval
    READ_PATTERNS = [
        "read", "extract", "get", "fetch", "browse",
        "navigate", "open", "visit", "search",
        "summarize", "analyze", "list",
    ]

    def check_task(self, task_description: str) -> dict[str, Any]:
        """Check if a browser task is allowed.

        Returns:
            {"allowed": bool, "risk": str, "reason": str}
        """
        task_lower = task_description.lower()

        # Check blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in task_lower:
                return {
                    "allowed": False,
                    "risk": "BLOCKED",
                    "reason": f"Task contains blocked pattern: {pattern}",
                }

        # Check approval patterns
        for pattern in self.APPROVAL_PATTERNS:
            if pattern in task_lower:
                return {
                    "allowed": True,
                    "risk": "APPROVAL_REQUIRED",
                    "reason": f"Task requires approval: {pattern}",
                }

        # Default: read-only, allowed
        return {
            "allowed": True,
            "risk": "READ",
            "reason": "Read-only task, allowed",
        }


class BrowserUseTaskExecutor:
    """Executes browser tasks using browser-use.

    Usage:
        executor = BrowserUseTaskExecutor(llm_client=llm)
        result = executor.execute("Go to example.com and extract the main text")
    """

    def __init__(self, llm_client: Any = None, safety: BrowserUseSafetyBoundary | None = None) -> None:
        self._llm = llm_client
        self._safety = safety or BrowserUseSafetyBoundary()

    def execute(self, task: str, context: str = "") -> BrowserTaskResult:
        """Execute a browser task synchronously."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self._execute_async(task, context))
                    return future.result(timeout=120)
            else:
                return loop.run_until_complete(self._execute_async(task, context))
        except Exception as e:
            return BrowserTaskResult(
                success=False,
                task_description=task,
                error=str(e),
            )

    async def _execute_async(self, task: str, context: str = "") -> BrowserTaskResult:
        """Execute a browser task asynchronously."""
        import time
        start = time.perf_counter()

        # Safety check
        safety_check = self._safety.check_task(task)
        if not safety_check["allowed"]:
            return BrowserTaskResult(
                success=False,
                task_description=task,
                error=f"Task blocked by safety: {safety_check['reason']}",
            )

        # Build full task with constraints
        full_task = task
        if context:
            full_task = f"Context: {context}\n\nTask: {task}"

        # Add safety instructions to task
        safety_instructions = (
            "\n\nIMPORTANT SAFETY RULES:"
            "\n- Do NOT solve CAPTCHAs"
            "\n- Do NOT bypass bot detection"
            "\n- Do NOT make purchases or enter payment info"
            "\n- Do NOT create bulk accounts"
            "\n- Do NOT send messages or publish content"
            "\n- Only read and extract information"
            "\n- If asked to do something blocked, explain why it cannot be done"
        )
        full_task += safety_instructions

        try:
            # Try browser-use first
            result = await self._execute_with_browser_use(full_task)
            result.duration_ms = (time.perf_counter() - start) * 1000
            return result
        except ImportError:
            logger.warning("browser-use not available, falling back to playwright")
            result = await self._execute_with_playwright(full_task)
            result.duration_ms = (time.perf_counter() - start) * 1000
            return result
        except Exception as e:
            logger.error("browser-use execution failed: %s", e)
            result = await self._execute_with_playwright(full_task)
            result.duration_ms = (time.perf_counter() - start) * 1000
            return result

    async def _execute_with_browser_use(self, task: str) -> BrowserTaskResult:
        """Execute using browser-use Agent."""
        from browser_use import Agent
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=self._llm._api_key if hasattr(self._llm, '_api_key') else "",
            base_url=self._llm._base_url if hasattr(self._llm, '_base_url') else "",
        )

        agent = Agent(task=task, llm=llm)
        result = await agent.run()

        return BrowserTaskResult(
            success=True,
            task_description=task,
            result_text=str(result),
        )

    async def _execute_with_playwright(self, task: str) -> BrowserTaskResult:
        """Fallback: execute with direct playwright."""
        # Extract URL from task
        import re

        from playwright.async_api import async_playwright
        url_match = re.search(r'https?://[^\s]+', task)
        if not url_match:
            return BrowserTaskResult(
                success=False,
                task_description=task,
                error="No URL found in task",
            )

        url = url_match.group(0)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, timeout=30000)
                title = await page.title()

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

                return BrowserTaskResult(
                    success=True,
                    task_description=task,
                    result_text=f"**{title}**\n\n{text[:2000]}",
                    extracted_data={"title": title, "text": text[:5000]},
                )
            finally:
                await browser.close()
