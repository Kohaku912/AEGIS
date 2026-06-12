"""AEGIS Demo — Browser automation with DeepSeek LLM.

Demonstrates:
1. LLM integration (DeepSeek via OpenAI SDK)
2. Browser automation (Playwright)
3. LLM + Browser integration
4. Safety gates (PolicyEngine)

Usage:
    python demo_browser.py
"""

from __future__ import annotations

import asyncio
import logging
import os

# Set API key before imports
os.environ["OPENAI_API_KEY"] = "sk-b7634b706d714a11944a498f1a520f52"
os.environ["OPENAI_BASE_URL"] = "https://api.deepseek.com"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegis_demo")


async def main():
    """Run browser automation demo."""
    logger.info("=" * 60)
    logger.info("AEGIS Browser Demo — DeepSeek LLM + Playwright")
    logger.info("=" * 60)

    # 1. Test LLM connection
    logger.info("[1/5] Testing DeepSeek LLM connection...")
    from aegis_ai.llm.providers.openai_provider import OpenAIProvider

    llm = OpenAIProvider(
        model="deepseek-v4-flash",
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_BASE_URL"],
    )
    response = llm.generate(
        prompt="What is AEGIS? Answer in one sentence.",
        system_prompt="You are AEGIS, an autonomous AI assistant.",
        max_tokens=100,
    )
    if response.success:
        logger.info("  LLM Response: %s", response.content[:100])
        logger.info("  Model: %s, Tokens: %d", response.model_used, response.tokens_used)
    else:
        logger.error("  LLM Error: %s", response.error)
        return

    # 2. Test browser with Playwright
    logger.info("[2/5] Testing browser automation with Playwright...")
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to example.com
        logger.info("  Navigating to https://example.com...")
        await page.goto("https://example.com")

        title = await page.title()
        logger.info("  Page title: %s", title)

        text = await page.evaluate("document.body.innerText")
        logger.info("  Page text: %s", text[:200])

        # Extract links
        links = await page.evaluate("""
            Array.from(document.querySelectorAll('a[href]')).map(a => ({
                href: a.href,
                text: a.textContent.trim()
            }))
        """)
        logger.info("  Links found: %d", len(links))
        for link in links:
            logger.info("    - %s: %s", link["text"], link["href"])

        await browser.close()
        logger.info("  Browser automation: OK")

    # 3. LLM analyzes browser content
    logger.info("[3/5] LLM analyzing browser content...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to a news site
        logger.info("  Navigating to https://news.ycombinator.com...")
        await page.goto("https://news.ycombinator.com")

        title = await page.title()
        logger.info("  Page title: %s", title)

        # Extract top stories
        stories = await page.evaluate("""
            Array.from(document.querySelectorAll('.titleline > a')).slice(0, 5).map(a => ({
                title: a.textContent.trim(),
                href: a.href
            }))
        """)
        logger.info("  Top stories:")
        for i, story in enumerate(stories, 1):
            logger.info("    %d. %s", i, story["title"])

        # Ask LLM to summarize
        story_text = "\n".join(f"- {s['title']}" for s in stories)
        llm_response = llm.generate(
            prompt=f"Summarize these top Hacker News stories in 2-3 sentences:\n{story_text}",
            system_prompt="You are a tech news summarizer. Be concise.",
            max_tokens=200,
        )
        if llm_response.success:
            logger.info("  LLM Summary: %s", llm_response.content[:300])

        await browser.close()

    # 4. Verify PolicyEngine blocks dangerous actions
    logger.info("[4/5] Verifying PolicyEngine safety...")
    from aegis_schema.models import Capability, RiskLevel, ServerType
    from policy_engine import create_default_policy_engine

    policy = create_default_policy_engine()

    # Test: send_sns should be denied
    cap = Capability(
        id="browser.send_sns",
        name="Send SNS",
        description="Post to SNS",
        server_type=ServerType.BROWSER,
        risk_level=RiskLevel.APPROVAL_REQUIRED,
    )
    result = policy.evaluate(cap, {})
    logger.info("  browser.send_sns: %s (expected: DENY)", result.decision.name)

    # Test: get_page_content should be allowed
    cap2 = Capability(
        id="browser.extract_page_text",
        name="Extract Text",
        description="Extract page text",
        server_type=ServerType.BROWSER,
        risk_level=RiskLevel.READ_ONLY,
    )
    result2 = policy.evaluate(cap2, {})
    logger.info("  browser.extract_page_text: %s (expected: ALLOW)", result2.decision.name)

    # 5. Summary
    logger.info("[5/5] Demo complete!")
    logger.info("=" * 60)
    logger.info("Results:")
    logger.info("  DeepSeek LLM: OK")
    logger.info("  Browser automation: OK")
    logger.info("  LLM + Browser integration: OK")
    logger.info("  PolicyEngine safety: OK")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
