"""Observe capabilities for Browser Server.

Implements Level-0 read-only operations:
- browser.get_screenshot
- browser.extract_page_text
- browser.get_current_url
- browser.get_page_title
- browser.get_links
- browser.get_dom_snapshot

All observe capabilities are LEVEL_0_READ — always safe, no side effects.
"""

from __future__ import annotations

import base64
import logging
from typing import Any

from playwright.async_api import Page

logger = logging.getLogger("aegis_browser.observe")


async def get_screenshot(page: Page, full_page: bool = False, quality: int = 90) -> dict[str, Any]:
    """Capture a screenshot of the current page.

    Returns PNG bytes as base64-encoded string with dimensions.
    """
    screenshot_bytes = await page.screenshot(full_page=full_page, type="png")
    viewport = page.viewport_size or {"width": 0, "height": 0}
    return {
        "image_base64": base64.b64encode(screenshot_bytes).decode("utf-8"),
        "width": viewport["width"],
        "height": viewport["height"],
        "format": "png",
        "full_page": full_page,
    }


async def extract_page_text(page: Page, max_length: int = 50000,
                           include_alt_text: bool = True) -> dict[str, Any]:
    """Extract readable text from the page, excluding scripts, styles, nav, and footer."""
    text = await page.evaluate("""
        (() => {
            const exclude = ['script', 'style', 'nav', 'footer', 'noscript', 'iframe', 'svg'];
            const clone = document.body.cloneNode(true);
            exclude.forEach(tag => {
                clone.querySelectorAll(tag).forEach(el => el.remove());
            });
            return (clone.textContent || '').replace(/\\s{3,}/g, '\\n\\n').trim();
        })()
    """)
    if include_alt_text:
        alt_texts = await page.evaluate("""
            (() => {
                return Array.from(document.querySelectorAll('img[alt]'))
                    .map(img => img.getAttribute('alt')).filter(Boolean).join('\\n');
            })()
        """)
        if alt_texts:
            text = text + "\n\n[Image descriptions]\n" + alt_texts

    truncated = len(text) > max_length
    return {
        "text": text[:max_length],
        "char_count": len(text),
        "truncated": truncated,
    }


async def get_current_url(page: Page) -> dict[str, Any]:
    """Get the current page URL."""
    return {"url": page.url}


async def get_page_title(page: Page) -> dict[str, Any]:
    """Get the current page title."""
    title = await page.title()
    return {"title": title}


async def get_links(page: Page) -> dict[str, Any]:
    """Extract all hyperlinks from the page with href and text."""
    links = await page.evaluate("""
        (() => {
            return Array.from(document.querySelectorAll('a[href]')).map(a => ({
                href: a.href,
                text: (a.textContent || '').trim().substring(0, 200),
                internal: a.href.startsWith(window.location.origin)
            }));
        })()
    """)
    return {"links": links, "count": len(links)}


async def get_dom_snapshot(page: Page, selector: str = "") -> dict[str, Any]:
    """Get the HTML content of the page or a specific element."""
    if selector:
        element = await page.query_selector(selector)
        if element is None:
            return {"html": "", "error": f"Selector '{selector}' not found"}
        html = await element.inner_html()
    else:
        html = await page.content()
    return {"html": html, "char_count": len(html)}
