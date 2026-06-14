import sys, json

data = json.loads(sys.stdin.read())
url = data.get("url", "")
if not url:
    print(json.dumps({"ok": False, "error": "No URL provided"}))
    sys.exit(1)

try:
    import asyncio
    from playwright.async_api import async_playwright

    async def browse():
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
                links = await page.evaluate("""
                    Array.from(document.querySelectorAll('a[href]')).slice(0, 10).map(a => ({
                        href: a.href,
                        text: a.textContent.trim().substring(0, 100)
                    }))
                """)
                result_parts = [f"**{title}**\n", f"URL: {url}\n", f"Content:\n{text[:2000]}\n"]
                if links:
                    result_parts.append("\nLinks:")
                    for link in links[:5]:
                        result_parts.append(f"  - {link['text']}: {link['href']}")
                return "\n".join(result_parts)
            finally:
                await browser.close()

    result = asyncio.run(browse())
    print(json.dumps({"ok": True, "result": result}))
except Exception as e:
    print(json.dumps({"ok": False, "error": f"Browser error: {str(e)}"}))
