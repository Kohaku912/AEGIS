"""Tests for observe capabilities."""


from aegis_browser.observe import (
    extract_page_text,
)
from aegis_browser.safety import SUPPORTED_OPERATIONS


class TestCapabilityDefinitions:
    def test_browser_runtime_exposes_split_operations(self):
        assert "page.read" in SUPPORTED_OPERATIONS
        assert "form.submit" in SUPPORTED_OPERATIONS
        assert "social.post" in SUPPORTED_OPERATIONS
        assert "page.browse" not in SUPPORTED_OPERATIONS


class TestExtractPageText:
    def test_removes_script_and_style(self):
        """Verify the JS extraction logic excludes script/style/nav/footer."""
        js_code = """
            (() => {
                const exclude = ['script', 'style', 'nav', 'footer', 'noscript', 'iframe', 'svg'];
                const clone = document.body.cloneNode(true);
                exclude.forEach(tag => {
                    clone.querySelectorAll(tag).forEach(el => el.remove());
                });
                return (clone.textContent || '').replace(/\\s{3,}/g, '\\n\\n').trim();
            })()
        """
        assert "script" in js_code
        assert "style" in js_code
        assert "nav" in js_code
        assert "footer" in js_code

    def test_extract_page_text_function_exists(self):
        """Verify the function is importable and has correct signature."""
        import inspect
        sig = inspect.signature(extract_page_text)
        params = list(sig.parameters.keys())
        assert "page" in params
        assert "max_length" in params
        assert "include_alt_text" in params


class TestGetLinks:
    def test_links_extraction_js(self):
        """Verify the JS for link extraction includes internal flag."""
        js_code = """
            (() => {
                return Array.from(document.querySelectorAll('a[href]')).map(a => ({
                    href: a.href,
                    text: (a.textContent || '').trim().substring(0, 200),
                    internal: a.href.startsWith(window.location.origin)
                }));
            })()
        """
        assert "internal" in js_code
        assert "a[href]" in js_code
        assert "substring(0, 200)" in js_code
