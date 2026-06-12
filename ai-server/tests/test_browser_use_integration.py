"""Tests for browser-use integration with DeepSeek LLM."""

from __future__ import annotations

import os

import pytest


class TestBrowserUseIntegration:
    """Browser-use integration tests."""

    def test_playwright_chromium_launch(self):
        """Playwright can launch Chromium."""
        import asyncio
        from playwright.async_api import async_playwright

        async def test():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://example.com")
                title = await page.title()
                text = await page.evaluate("document.body.innerText")
                await browser.close()
                return title, text

        title, text = asyncio.run(test())
        assert "Example" in title
        assert "domain" in text.lower()

    def test_playwright_extract_links(self):
        """Playwright can extract links."""
        import asyncio
        from playwright.async_api import async_playwright

        async def test():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://example.com")
                links = await page.evaluate("""
                    Array.from(document.querySelectorAll('a[href]')).map(a => ({
                        href: a.href,
                        text: a.textContent.trim()
                    }))
                """)
                await browser.close()
                return links

        links = asyncio.run(test())
        assert len(links) >= 1
        assert any("iana.org" in l["href"] for l in links)

    def test_playwright_navigate_and_extract(self):
        """Playwright can navigate and extract content."""
        import asyncio
        from playwright.async_api import async_playwright

        async def test():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto("https://example.com")
                title = await page.title()
                text = await page.evaluate("""
                    (() => {
                        const exclude = ['script', 'style'];
                        const clone = document.body.cloneNode(true);
                        exclude.forEach(tag => {
                            clone.querySelectorAll(tag).forEach(el => el.remove());
                        });
                        return clone.textContent.replace(/\\s{3,}/g, '\\n\\n').trim();
                    })()
                """)
                await browser.close()
                return title, text

        title, text = asyncio.run(test())
        assert "Example" in title
        assert len(text) > 0
