"""Browser-Use Task Executor — executes browser tasks using Playwright.

Uses Playwright for browser automation and LLM for content analysis.
browser-use Agent is optional (requires compatible langchain-openai version).

Safety: All actions go through safety boundary checks.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aegis_ai.llm.memory_context import build_shared_memory_context

logger = logging.getLogger("aegis_ai.browser_use.executor")
_DATA_DIR = str(Path(__file__).resolve().parent.parent.parent / "data")


@dataclass
class BrowserTaskResult:
    """Result of a browser task execution."""
    success: bool = False
    task_description: str = ""
    result_text: str = ""
    extracted_data: dict[str, Any] = field(default_factory=dict)
    actions_taken: list[str] = field(default_factory=list)
    error: str = ""
    duration_ms: float = 0.0


class BrowserUseSafetyBoundary:
    """Safety boundary for browser tasks."""

    def check_task(self, task_description: str) -> dict[str, Any]:
        """Keyword nannying is forbidden; PolicyEngine owns purchase/policy-bypass."""
        _ = task_description
        return {
            "allowed": True,
            "risk": "ALLOW",
            "reason": "Browser tasks are judged by PolicyEngine, not keyword matching.",
        }


class BrowserUseTaskExecutor:
    """Executes browser tasks using Playwright.

    Uses LLM for content analysis and summarization.
    Falls back to direct Playwright if browser-use is unavailable.

    Usage:
        executor = BrowserUseTaskExecutor(llm_client=llm)
        result = executor.execute("Go to example.com and extract the main text")
    """

    def __init__(self, llm_client: Any = None, safety: BrowserUseSafetyBoundary | None = None) -> None:
        self._llm = llm_client
        self._safety = safety or BrowserUseSafetyBoundary()

    def _summarize_page_content(self, title: str, text: str, task: str) -> str:
        summary = text[:2000]
        if not self._llm or len(text) <= 200:
            return summary
        try:
            memory_context = build_shared_memory_context(
                query=task or title,
                data_dir=_DATA_DIR,
                profile="summary",
            )
            prompt = f"Summarize this webpage content concisely:\n\nTitle: {title}\n\nContent:\n{text[:3000]}"
            if memory_context.text:
                prompt = f"Shared memory context:\n{memory_context.text}\n\n{prompt}"
            llm_result = self._llm.generate(
                prompt=prompt,
                system_prompt="You are a web content summarizer. Be concise and informative.",
                max_tokens=500,
                context_meta=memory_context.audit_detail(),
            )
            if llm_result.success:
                return llm_result.content
        except Exception as exc:
            logger.warning("LLM summarization failed: %s", exc)
        return summary

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
        start = time.perf_counter()

        # Safety check
        safety_check = self._safety.check_task(task)
        if not safety_check["allowed"]:
            return BrowserTaskResult(
                success=False,
                task_description=task,
                error=f"Task blocked by safety: {safety_check['reason']}",
            )

        # Build full task
        full_task = task
        if context:
            full_task = f"Context: {context}\n\nTask: {task}"

        # Add safety instructions
        safety_instructions = (
            "\n\nIMPORTANT SAFETY RULES:"
            "\n- Do NOT solve CAPTCHAs"
            "\n- Do NOT bypass bot detection"
            "\n- Do NOT make purchases or enter payment info"
            "\n- Do NOT create bulk accounts"
            "\n- Do NOT send messages or publish content"
            "\n- Only read and extract information"
        )
        full_task += safety_instructions

        try:
            result = await self._execute_with_playwright(full_task)
            result.duration_ms = (time.perf_counter() - start) * 1000
            return result
        except Exception as e:
            logger.error("Browser execution failed: %s", e)
            return BrowserTaskResult(
                success=False,
                task_description=task,
                error=str(e),
                duration_ms=(time.perf_counter() - start) * 1000,
            )

    async def _execute_with_playwright(self, task: str) -> BrowserTaskResult:
        """Execute with Playwright."""
        from playwright.async_api import async_playwright

        # Extract URL from task
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

                # Extract main content
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

                # Extract links
                links = await page.evaluate("""
                    Array.from(document.querySelectorAll('a[href]')).slice(0, 20).map(a => ({
                        href: a.href,
                        text: a.textContent.trim().substring(0, 100)
                    }))
                """)

                # Use LLM to summarize if available
                summary = self._summarize_page_content(title, text, task)

                return BrowserTaskResult(
                    success=True,
                    task_description=task,
                    result_text=f"**{title}**\n\n{summary}",
                    extracted_data={
                        "title": title,
                        "url": url,
                        "text": text[:5000],
                        "links": links,
                        "char_count": len(text),
                    },
                    actions_taken=["navigate", "extract_text", "extract_links"],
                )
            finally:
                await browser.close()

    async def _execute_with_browser_use(self, task: str) -> BrowserTaskResult:
        """Execute using browser-use Agent (optional)."""
        try:
            from browser_use import Agent
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model="deepseek-v4-flash",
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
        except Exception as e:
            logger.warning("browser-use Agent failed: %s", e)
            raise
